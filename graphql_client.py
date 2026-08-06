from __future__ import annotations

import json
import logging
from http import HTTPStatus
from pathlib import Path
from threading import local
from typing import Any

import certifi
import requests
import urllib3
from requests import Response, Session
from tenacity import Retrying, retry_if_exception_type, stop_after_attempt, wait_exponential

from config import Settings


class AuthenticationExpiredError(RuntimeError):
    pass


class TransientHTTPError(RuntimeError):
    pass


class HTTPStatusError(RuntimeError):
    def __init__(self, response: Response) -> None:
        self.response = response
        message = f"HTTP {response.status_code} {response.reason} for {response.url}"
        super().__init__(message)


class GraphQLClient:
    def __init__(self, settings: Settings, logger: logging.Logger) -> None:
        self.settings = settings
        self.logger = logger
        self.query = self._load_query(settings.graphql_query_file)
        self.verify = self._resolve_ssl_verify()
        self._thread_local = local()

    def get_order_details(self, order_code: str) -> dict[str, Any]:
        return self._post({
            "operationName": "getOrderDetails",
            "query": self.query,
            "variables": {
                "merchantUid": self.settings.merchant_uid,
                "orderCode": str(order_code),
                "skipCustomerPhone": False,
            },
        })

    def _session(self) -> Session:
        session = getattr(self._thread_local, "session", None)
        if session is None:
            session = requests.Session()
            session.headers.update({
                "Content-Type": "application/json",
                "Origin": self.settings.kaspi_origin,
                "Referer": self.settings.kaspi_referer,
                "Accept": "*/*",
                "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
                "User-Agent": self.settings.user_agent,
                "X-Requested-With": "XMLHttpRequest",
            })
            self._load_cookies(session, self.settings.storage_state_file)
            self._thread_local.session = session
        return session

    def _post(self, body: dict[str, Any]) -> dict[str, Any]:
        retryer = Retrying(
            retry=retry_if_exception_type(
                (requests.RequestException, TimeoutError, TransientHTTPError)
            ),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            stop=stop_after_attempt(self.settings.retry_count),
            reraise=True,
            before_sleep=lambda state: self.logger.warning(
                "Retry %s after %s",
                state.attempt_number,
                state.outcome.exception() if state.outcome else "error",
            ),
        )
        last_method_error: HTTPStatusError | None = None
        for endpoint in self.settings.graphql_endpoints:
            try:
                return self._post_with_retries(retryer, endpoint, body)
            except HTTPStatusError as exc:
                if exc.response.status_code == HTTPStatus.METHOD_NOT_ALLOWED:
                    last_method_error = exc
                    self.logger.warning("Endpoint rejected POST with HTTP 405: %s", endpoint)
                    continue
                raise
        if last_method_error is not None:
            raise last_method_error
        raise RuntimeError("No GraphQL endpoints are configured")

    def _post_with_retries(
        self,
        retryer: Retrying,
        endpoint: str,
        body: dict[str, Any],
    ) -> dict[str, Any]:
        for attempt in retryer:
            with attempt:
                response = self._session().post(
                    endpoint,
                    json=body,
                    timeout=self.settings.request_timeout,
                    verify=self.verify,
                )
                self.logger.info("HTTP %s", response.status_code)
                self._raise_for_unusable_response(response)
                payload = response.json()
                if payload.get("errors"):
                    self.logger.warning("GraphQL errors: %s", payload["errors"])
                return payload
        raise RuntimeError("GraphQL request retry loop exited unexpectedly")

    def _raise_for_unusable_response(self, response: Response) -> None:
        if response.status_code in {HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN}:
            raise AuthenticationExpiredError("Kaspi authentication has expired")
        if response.status_code == HTTPStatus.TOO_MANY_REQUESTS or response.status_code >= 500:
            raise TransientHTTPError(f"HTTP {response.status_code} from Kaspi GraphQL")
        if response.status_code >= 400:
            raise HTTPStatusError(response)

    def _resolve_ssl_verify(self) -> bool | str:
        if not self.settings.verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            self.logger.warning(
                "SSL verification is disabled. Use this only for local diagnostics; "
                "prefer SSL_CA_BUNDLE for corporate certificates."
            )
            return False
        if self.settings.ssl_ca_bundle is not None:
            return str(self.settings.ssl_ca_bundle)
        return certifi.where()

    def _load_cookies(self, session: Session, storage_state_file: Path) -> None:
        with storage_state_file.open(encoding="utf-8") as file:
            storage_state = json.load(file)
        for cookie in storage_state.get("cookies", []):
            session.cookies.set(
                cookie["name"],
                cookie["value"],
                domain=cookie.get("domain"),
                path=cookie.get("path", "/"),
            )

    def _load_query(self, query_file: Path) -> str:
        return query_file.read_text(encoding="utf-8")
