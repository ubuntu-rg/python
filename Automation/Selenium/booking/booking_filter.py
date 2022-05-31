# This file will help to filter the right results
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from time import sleep


class BookingFilter:
    def __init__(self, driver: WebDriver):
        self.driver = driver

    def apply_star_rating(self, *star_values):
        star_box = self.driver.find_element(by=By.CSS_SELECTOR, value='div[data-filters-group="class"]')
        star_element = star_box.find_elements(by=By.CSS_SELECTOR, value='*')

        for star_value in star_values:
            print(star_value)
            for star in star_element:
                if str(star.get_attribute('innerHTML')).strip() == f"{star_value} star":
                    star.click()
                    sleep(1)
                if str(star.get_attribute('innerHTML')).strip() == f"{star_value} stars":
                    star.click()
                    sleep(1)

    def show_lowest_price(self):
        lowest_price_button = self.driver.find_element(by=By.CSS_SELECTOR, value='a[data-type="price"]')
        lowest_price_button.click()
