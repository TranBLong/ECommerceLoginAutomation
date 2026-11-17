import configparser
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


class BrowserSetup:
    """Setup WebDriver with support for local chromedriver or webdriver-manager."""

    @staticmethod
    def get_driver(headless: bool = False):
        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(__file__), "..", "config.ini")
        config.read(config_path, encoding="utf-8")

        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-infobars")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        if headless:
            options.add_argument("--headless=new")

        driver_path = config.get("webdriver", "driver_path", fallback="").strip()

        if driver_path and os.path.exists(driver_path):
            service = Service(driver_path)
            driver = webdriver.Chrome(service=service, options=options)
        else:
            # Tự động tải chromedriver phù hợp với Chrome đang cài
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)

        driver.implicitly_wait(5)
        return driver
