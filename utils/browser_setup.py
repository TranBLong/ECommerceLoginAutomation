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
        browser = os.environ.get("BROWSER", "chrome").lower()

        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(__file__), "..", "config.ini")
        config.read(config_path, encoding="utf-8")

        if browser == "firefox":
            from selenium.webdriver.firefox.options import Options as FFOptions

            ff = FFOptions()
            if headless:
                ff.add_argument("-headless")
            return webdriver.Firefox(options=ff)

        if browser == "edge":
            from selenium.webdriver.edge.options import Options as EdgeOptions

            edge = EdgeOptions()
            edge.add_argument("--start-maximized")
            edge.add_argument("--disable-notifications")
            edge.add_argument("--no-sandbox")
            edge.add_argument("--disable-dev-shm-usage")
            if headless:
                edge.add_argument("--headless=new")
            return webdriver.Edge(options=edge)

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

        return driver
