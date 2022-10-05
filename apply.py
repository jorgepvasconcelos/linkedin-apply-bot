import time
from typing import Callable
from datetime import datetime
from enum import Enum, auto

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium_toolkit import SeleniumToolKit
from selenium_toolkit.auto_wait import AutoWait
from selenium_stealth import stealth

from settings import USERNAME, PASSWORD, KEYWORD, LOCATION, RESUME_NAME


class StepException(Exception):
    ...


class ApplyStepEnum(Enum):
    CONTACT_INFO = auto()
    RESUME = auto()
    SCREENING_QUESTIONS = auto()
    SEND_CANDIDACY = auto()
    SEND_CANDIDACY_CONFIRM = auto()
    UNDEFINED_STEP = auto()


class LinkedinApplyBot:
    def __init__(self, selenium_kit: SeleniumToolKit):
        self.sk = selenium_kit
        AutoWait.change_wait_time(range_time=(1, 3))

    @staticmethod
    def call_step(func: Callable) -> bool:
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
        if not self.call_step(self.login):
            raise StepException("Error in step [login]")

        if not self.call_step(self.search_jobs):
            raise StepException("Error in step [search_jobs]")

        if not self.call_step(self.loop_though_jobs_list):
            raise StepException("Error in step [search_jobs]")

    def login(self) -> bool:
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

    def search_jobs(self) -> bool:
        search_url = 'https://www.linkedin.com/jobs'
        self.sk.goto(url=search_url)

        qs_seach_keywords_box = 'input[class="jobs-search-box__text-input jobs-search-box__keyboard-text-input"]'
        self.sk.fill_in_random_time(text=KEYWORD, query_selector=qs_seach_keywords_box)

        qs_seach_location_box = 'input[class="jobs-search-box__text-input"]'
        self.sk.fill_in_random_time(text=LOCATION, query_selector=qs_seach_location_box)

        # Press Enter to start searching
        self.sk.query_selector(query_selector=qs_seach_location_box).send_keys(Keys.ENTER)

        qs_job_list = '[id="results-list__title"]'
        in_job_list_page = self.sk.element_is_present(wait_time=5, query_selector=qs_job_list)
        if not in_job_list_page:
            return False

        job_url = self.sk.driver.current_url
        job_url_easy_apply = job_url + '&f_AL=true'
        self.sk.goto(url=job_url_easy_apply)

        return self.sk.element_is_present(wait_time=5, query_selector=qs_job_list)

    def loop_though_jobs_list(self) -> bool:
        next_page_number = 1
        last_ppagination_number = None

        qs_list_pagination_div = '[class="jobs-search-results-list__pagination pv5 artdeco-pagination ember-view"]'
        has_pagination = self.sk.element_is_present(wait_time=1, query_selector=qs_list_pagination_div)
        if has_pagination:
            qs_last_ppagination = 'li[data-test-pagination-page-btn]:last-child > button > span'
            last_ppagination_number = int(self.sk.get_text(query_selector=qs_last_ppagination))

        while True:
            if not has_pagination and next_page_number > 1:
                break

            if has_pagination and next_page_number > last_ppagination_number:
                break

            # Go to the next page
            if has_pagination and next_page_number > 1:
                qs_page_number = f'li[data-test-pagination-page-btn="{next_page_number}"]'
                self.sk.click(query_selector=qs_page_number)
                time.sleep(10)

            # Start aplying
            jobs_list_elements = self.sk.query_selector_all('li.jobs-search-results__list-item')
            for job_element in jobs_list_elements:
                job_element.click()

                # qs_job_section = 'section[class^="scaffold-layout__detail"] > div'
                # job_section = self.sk.query_selector(query_selector=qs_job_section)

                if not self.job_description_matchs_search():
                    continue

                self.apply_job()

            next_page_number += 1

        return True

    def job_description_matchs_search(self) -> bool:
        qs_job_description = 'article[class^="jobs-description__container"]'
        job_description_text = self.sk.get_text(query_selector=qs_job_description)
        return True

    def __click_next_botton(self):
        qs_next_button = '[class="artdeco-button artdeco-button--2 artdeco-button--primary ember-view"]'
        self.sk.click(query_selector=qs_next_button)

    def __identify_apply_step(self) -> ApplyStepEnum:
        # [STEP] Contact info
        qs_contact_info = 'h3[class="t-16 t-bold"]'
        if self.sk.text_is_present(wait_time=2, query_selector=qs_contact_info, text="Contact info"):
            return ApplyStepEnum.CONTACT_INFO

        # [STEP] Add Resume step
        qs_add_resume_step = '[class="ui-attachment__download-button"]'
        if self.sk.element_is_present(wait_time=2, query_selector=qs_add_resume_step):
            return ApplyStepEnum.RESUME

        # [STEP] Screening questions
        qs_screening_questiopns = 'h3[class="t-16 t-bold"]'
        if self.sk.text_is_present(wait_time=2, query_selector=qs_screening_questiopns, text="Screening questions"):
            return ApplyStepEnum.CONTACT_INFO

        # [STEP] Send Candidacy
        qs_follow_company = 'label[for="follow-company-checkbox"]'
        if self.sk.element_is_present(wait_time=2, query_selector=qs_follow_company):
            return ApplyStepEnum.SEND_CANDIDACY

        # [STEP] Send Candidacy Confirm
        qs_send_candidacy_confirm = 'h3[class="jpac-modal-header t-24"]'
        if self.sk.element_is_present(wait_time=2, query_selector=qs_send_candidacy_confirm):
            return ApplyStepEnum.SEND_CANDIDACY_CONFIRM

        return ApplyStepEnum.UNDEFINED_STEP

    def apply_job(self) -> bool:
        # Click in button apply to load easy aplly page
        qs_easy_apply_button = 'button[class="jobs-apply-button artdeco-button artdeco-button--3 artdeco-button--primary ember-view"]'
        self.sk.click(query_selector=qs_easy_apply_button)

        apply_step = self.__identify_apply_step()

        if apply_step == ApplyStepEnum.CONTACT_INFO:
            self.__click_next_botton()

        if apply_step == ApplyStepEnum.RESUME:
            qs_name = 'h3[class="ui-attachment__filename jobs-document-upload__attachment-filename"]'
            dafault_resume_name = self.sk.get_text(query_selector=qs_name)
            if dafault_resume_name == RESUME_NAME:
                self.__click_next_botton()
            # qs_remove_pdf = '[class="artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--1 artdeco-button--tertiary ember-view"]'
            # self.sk.click(query_selector=qs_remove_pdf)

        if apply_step == ApplyStepEnum.SCREENING_QUESTIONS:
            self.__click_next_botton()
            currently_step = self.__identify_apply_step()
            if currently_step == ApplyStepEnum.SCREENING_QUESTIONS:
                self.__quite_apply()

        if apply_step == ApplyStepEnum.SEND_CANDIDACY:
            qs_follow_company = 'label[for="follow-company-checkbox"]'
            self.sk.click(query_selector=qs_follow_company)
            self.__click_next_botton()

        if apply_step == ApplyStepEnum.SEND_CANDIDACY_CONFIRM:
            qs_close_apply = '.artdeco-modal__dismiss.artdeco-button'
            self.sk.click(query_selector=qs_close_apply)
            return True

    def __quite_apply(self):
        qs_dismiss_button = '.artdeco-modal__dismiss.artdeco-button'
        self.sk.click(query_selector=qs_dismiss_button)

        self.sk.element_is_present(wait_time=2, query_selector='h2[data-test-dialog-title]')
        qs_discard_button = '[data-control-name="discard_application_confirm_btn"]'
        self.sk.click(query_selector=qs_discard_button)


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
