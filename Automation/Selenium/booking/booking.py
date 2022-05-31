from selenium import webdriver
from selenium.webdriver.common.by import By
from .constants import *
from .booking_filter import *
import os
from time import sleep


# The class will inherit from webdriver.Chrome in order to use its methods
class Booking(webdriver.Chrome):
    def __init__(self, driver_path=r"/bin/chromedriver", teardown=False):
        super(Booking, self).__init__()
        self.driver_path = driver_path
        self.teardown = teardown
        self.implicitly_wait(10)
        self.maximize_window()
        os.environ['PATH'] += self.driver_path

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.teardown:
            self.quit()

    def land_first_page(self):
        self.get(URL)

    def change_currency(self, currency="ILS"):
        currency_element = self.find_element(by=By.CSS_SELECTOR,
                                             value='button[data-tooltip-text="Choose your currency"]')
        currency_element.click()
        currency_type = self.find_element(by=By.CSS_SELECTOR,
                                          value=f'a[data-modal-header-async-url-param="changed_currency=1;selected_currency={currency}"]')
        currency_type.click()

    def select_place(self, place_to_go):
        search_field = self.find_element(by=By.ID, value="ss")
        search_field.clear()
        search_field.send_keys(place_to_go)
        select_first_result = self.find_element(by=By.CSS_SELECTOR, value='li[data-i="0"]')
        select_first_result.click()

    def dates(self, check_in, check_out):
        select_check_in = self.find_element(by=By.CSS_SELECTOR, value=f'td[data-date="{check_in}"]')
        select_check_in.click()
        select_check_out = self.find_element(by=By.CSS_SELECTOR, value=f'td[data-date="{check_out}"]')
        select_check_out.click()

    def guests_and_rooms(self, adults=2, children=0, rooms=1):
        rooms_and_people_element = self.find_element(by=By.ID, value="xp__guests__toggle")
        rooms_and_people_element.click()
        if adults < 2:
            adults_amount = self.find_element(by=By.CLASS_NAME,
                                              value='bui-stepper__subtract-button')
            for _ in range(2 - adults):
                adults_amount.click()
        if adults > 2:
            adults_amount = self.find_element(by=By.CLASS_NAME,
                                              value='bui-stepper__add-button')
            for _ in range(adults - 2):
                adults_amount.click()

    def search(self):
        search_button = self.find_element(by=By.CSS_SELECTOR, value='button[type="submit"]')
        search_button.click()

    def apply_filter(self):
        filters = BookingFilter(driver=self)
        filters.apply_star_rating(4, 5)
        filters.show_lowest_price()

    def show_results(self):
        sleep(3)
        # container = self.find_element(by=By.CLASS_NAME, value="d4924c9e74")
        properties = self.find_elements(by=By.CLASS_NAME, value='da89aeb942')
        for element in properties:
            # print(element.get_attribute('innerHTML').strip())
            print(element.find_element(by=By.CLASS_NAME, value='a23c043802').get_attribute("innerHTML").strip())
            try:
                if element.find_element(by=By.CLASS_NAME, value='d10a6220b4'):
                    print(element.find_element(by=By.CLASS_NAME, value='d10a6220b4').get_attribute('innerHTML').strip())
            except Exception as e:
                pass
        print(len(properties))
