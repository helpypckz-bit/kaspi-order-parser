from __future__ import annotations

import logging
from pathlib import Path

from playwright.sync_api import sync_playwright

from config import Settings
from logger import LoggerService


class AuthService:
    def __init__(self, settings: Settings, logger: logging.Logger) -> None:
        self.settings = settings
        self.logger = logger

    def login(self) -> None:
        self.logger.info("Launching browser for manual Kaspi authentication")
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            page.goto(self.settings.auth_url, wait_until="domcontentloaded")
            input("Complete login in the browser, then press Enter here to save the session...")
            self.settings.storage_state_file.parent.mkdir(parents=True, exist_ok=True)
            context.storage_state(path=str(self.settings.storage_state_file))
            browser.close()
        self.logger.info("Storage state saved to %s", self.settings.storage_state_file)

    def ensure_storage_state(self) -> None:
        if self.settings.storage_state_file.exists():
            return
        self.logger.warning("Storage state is missing; login is required")
        self.login()


if __name__ == "__main__":
    app_settings = Settings.from_env()
    app_logger = LoggerService(app_settings.log_file).configure()
    AuthService(app_settings, app_logger).login()
