import requests
from bs4 import BeautifulSoup
import lxml
import time


def get_html(url):
    try:
        data = requests.get(url)
        soup = BeautifulSoup(data.text, "lxml")
        data = [link for link in soup.find_all("a")]
        for line in data:
            print(line) if "Api" in line.text else print("nO")
        return soup
    except requests.exceptions.ConnectionError:
        print("Connection Error, trying again.. ")
        time.sleep(1)
        get_html(url)


html = get_html("https://stackoverflow.com/users")

# users_grid = html.find_all("div", class_="grid--item")
# for user in users_grid:
#     user_details = user.find("div", class_="user-details")
#     users_location = user.find("span", class_="user-location").text
#     users_link = user_details.a["href"]
#     username = str((str(users_link).splitlines())).split("/")[3].replace("']", "")
#     location_list = [location for location in str(users_location).splitlines()]
#     print(location_list, username)