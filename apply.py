from typing import Callable
from datetime import datetime

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium_toolkit import SeleniumToolKit
from selenium_stealth import stealth

from settings import USERNAME, PASSWORD, KEYWORD, LOCATION


class StepException(Exception):
    ...


class LinkedinApplyBot:
    def __init__(self, selenium_kit: SeleniumToolKit):
        self.sk = selenium_kit

    @staticmethod
    def step(func: Callable):
        start_time = datetime.now()
        step_name = func.__name__
        print(f"Start step [{step_name}] at {start_time}")

        success = func()
        if not success:
            print(f"Error in step [{step_name}]")

        end_time = datetime.now()
        print(f"End step [{step_name}] at {end_time} | Duration {end_time - start_time}")

    def run(self):
        if not self.step(self.login):
            raise StepException("Error in step [login]")

        if not self.step(self.search_jobs):
            raise StepException("Error in step [search_jobs]")

    def login(self):
        login_url = 'https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin'
        self.sk.goto(url=login_url)

        self.sk.fill(text=USERNAME, locator=(By.CSS_SELECTOR, '[id="username"]'))
        self.sk.fill(text=PASSWORD, locator=(By.CSS_SELECTOR, '[id="password"]'))
        self.sk.click(locator=(By.CSS_SELECTOR, '[type="submit"]'))

        in_next_page = self.sk.element_is_present(wait_time=5, query_selector='.identity-headline')
        return in_next_page

    def search_jobs(self):
        search_url = 'https://www.linkedin.com/jobs/search'
        self.sk.goto(url=search_url)

        self.sk.fill(text=KEYWORD, locator=(By.CSS_SELECTOR, '[id="jobs-search-box-keyword-id-ember24"]'))
        self.sk.fill(text=LOCATION, locator=(By.CSS_SELECTOR, '[id="jobs-search-box-location-id-ember24"]'))
        self.sk.click(locator=(By.CSS_SELECTOR, '.jobs-search-box__submit-button'))

        in_next_page = self.sk.element_is_present(wait_time=5, query_selector='.identity-headline')
        return in_next_page

    def search_jobs2(self):
        search_url = 'https://www.linkedin.com/jobs/search/?keywords=python&location=Portugal&refresh=true'
        self.sk.goto(url=search_url)

        self.sk.fill(text=KEYWORD, locator=(By.CSS_SELECTOR, '[id="jobs-search-box-keyword-id-ember24"]'))
        self.sk.fill(text=LOCATION, locator=(By.CSS_SELECTOR, '[id="jobs-search-box-location-id-ember24"]'))
        self.sk.click(locator=(By.CSS_SELECTOR, '.jobs-search-box__submit-button'))

        in_next_page = self.sk.element_is_present(wait_time=5, query_selector='.identity-headline')
        return in_next_page


if __name__ == '__main__':
    options = Options()
    options.add_argument('--start-maximized')

    driver = Chrome(options=options)
    stealth(driver=driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )
    selenium_toolkit = SeleniumToolKit(driver=driver)

    bot = LinkedinApplyBot(selenium_kit=selenium_toolkit)
    bot.run()
