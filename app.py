from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

from auth import AuthService
from config import Settings
from excel import ExcelService
from graphql_client import AuthenticationExpiredError, GraphQLClient
from logger import LoggerService
from models import Order
from parser import OrderParser


def process_order(
    order_code: str,
    client: GraphQLClient,
    parser: OrderParser,
    logger: logging.Logger,
) -> Order | None:
    try:
        logger.info("Processing order %s", order_code)
        payload = client.get_order_details(order_code)
        order = parser.parse(payload, order_code)
        if order.phone:
            logger.info("Phone extracted for order %s", order_code)
        return order
    except AuthenticationExpiredError:
        raise
    except requests.exceptions.SSLError as exc:
        logger.error(
            "SSL certificate verification failed for order %s: %s. "
            "Install/update certifi or set SSL_CA_BUNDLE in .env to your corporate/root CA bundle.",
            order_code,
            exc,
        )
        return None
    except Exception:
        logger.exception("Failed to process order %s", order_code)
        return None


def main() -> int:
    settings = Settings.from_env()
    logger = LoggerService(settings.log_file).configure()
    auth = AuthService(settings, logger)
    auth.ensure_storage_state()
    excel = ExcelService(logger)
    order_codes = excel.read_order_codes(settings.input_file)
    parser = OrderParser()
    client = GraphQLClient(settings, logger)
    orders: list[Order] = []
    try:
        with ThreadPoolExecutor(max_workers=settings.max_workers) as executor:
            futures = [executor.submit(process_order, code, client, parser, logger) for code in order_codes]
            for future in as_completed(futures):
                if order := future.result():
                    orders.append(order)
    except AuthenticationExpiredError:
        logger.error("Authentication expired; run python auth.py and retry")
        return 2
    excel.write_orders(settings.output_file, orders)
    logger.info("Finished: %s/%s orders exported", len(orders), len(order_codes))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
