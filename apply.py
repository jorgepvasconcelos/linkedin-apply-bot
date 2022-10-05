from typing import Callable
from datetime import datetime

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium_toolkit import SeleniumToolKit
from selenium_toolkit.auto_wait import AutoWait
from selenium_stealth import stealth

from settings import USERNAME, PASSWORD, KEYWORD, LOCATION


class StepException(Exception):
    ...


class LinkedinApplyBot:
    def __init__(self, selenium_kit: SeleniumToolKit):
        self.sk = selenium_kit
        AutoWait.change_wait_time(range_time=(1, 3))

    @staticmethod
    def step(func: Callable):
        start_time = datetime.now()
        step_name = func.__name__
        print(f"Start step [{step_name}] at {start_time}")

        error = False
        success = func()
        if not success:
            print(f"Error in step [{step_name}]")
            error = True

        end_time = datetime.now()
        print(f"End step [{step_name}] at {end_time} | Duration {end_time - start_time}")

        if error:
            return False
        else:
            return True

    def run(self):
        if not self.step(self.login):
            raise StepException("Error in step [login]")

        if not self.step(self.search_jobs):
            raise StepException("Error in step [search_jobs]")

    def login(self):
        login_url = 'https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin'
        self.sk.goto(url=login_url)

        self.sk.fill_in_random_time(text=USERNAME, query_selector='[id="username"]')
        self.sk.fill_in_random_time(text=PASSWORD, query_selector='[id="password"]')
        self.sk.click(query_selector='[type="submit"]')

        # Confirm your account information
        if self.sk.text_is_present(wait_time=5, query_selector='html', text="Confirm your account information"):
            self.sk.click(query_selector='button[class="primary-action-new"]')

        in_logged_page = self.sk.element_is_present(wait_time=5, query_selector='.identity-headline')
        return in_logged_page

    def search_jobs(self):
        search_url = 'https://www.linkedin.com/jobs'
        self.sk.goto(url=search_url)

        we_seach_keywords_box = 'input[class="jobs-search-box__text-input jobs-search-box__keyboard-text-input"]'
        self.sk.fill_in_random_time(text=KEYWORD, query_selector=we_seach_keywords_box)

        we_seach_location_box = 'input[class="jobs-search-box__text-input"]'
        self.sk.fill_in_random_time(text=LOCATION, query_selector=we_seach_location_box)

        # Press Enter to start searching
        self.sk.query_selector(query_selector=we_seach_location_box).send_keys(Keys.ENTER)

        we_job_list = '[id="results-list__title"]'
        in_next_page = self.sk.element_is_present(wait_time=5, query_selector=we_job_list)
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
