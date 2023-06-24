import time
from contextlib import contextmanager
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import staleness_of
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class SeleniumDriver:
    # assumes self.browser is a selenium webdriver
    def __init__(self):
        self.browser = webdriver.Firefox()

    # https://stackoverflow.com/questions/26566799/wait-until-page-is-loaded-with-selenium-webdriver-for-python
    @contextmanager
    def wait_for_page_load(self, timeout: int = 90):
        old_page = self.browser.find_element(
            By.ID, "itemPricesContainer"
        )  # '(By.TAG_NAME, 'html')
        # print(old_page.text)
        # https://stackoverflow.com/questions/27112731/selenium-common-exceptions-nosuchelementexception-message-unable-to-locate-ele
        # try:
        #     WebDriverWait(self.browser, 10).until(
        #         EC.presence_of_element_located((By.TAG_NAME, "html"))
        #     )
        #     old_page = self.browser.find_element(By.TAG_NAME, 'html')
        # finally:
        #     print('Finally')

        yield WebDriverWait(self.browser, timeout).until(staleness_of(old_page))

    def get_html(self, blueprint: bool = False):
        self.browser.get("https://rl.insider.gg/en/pc")
        # example use
        try:
            if blueprint:
                time.sleep(3)
                settings = self.browser.find_element(By.CLASS_NAME, "settingsField")
                action = webdriver.ActionChains(self.browser)
                action.move_to_element(settings).move_to_element(
                    self.browser.find_element(By.XPATH, "//div[@data-pv='3']")
                ).click().perform()
            with self.wait_for_page_load(timeout=30):
                return self.browser.page_source
        finally:
            return self.browser.page_source

    def close(self) -> None:
        self.browser.close()
