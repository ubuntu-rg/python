import selenium.common.exceptions
from booking.booking import Booking

try:
    with Booking(teardown=False) as bot:
        bot.land_first_page()
        bot.change_currency(currency="USD")
        bot.select_place("Israel")
        bot.dates(check_in="2022-06-03", check_out="2022-06-13")
        bot.guests_and_rooms()
        bot.search()
        bot.apply_filter()
        bot.show_results()
        print("Finished the automation. Exiting..")
except selenium.common.exceptions.WebDriverException as e:
    if "PATH" in str(e):
        print("This program cannot be run within the command line")
    else:
        print(e)
