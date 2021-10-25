from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import requests
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# TODO: Create class and methods for readability

def main():
    URL = 'https://www.levels.fyi/still-hiring/'

    # Allow chrome driver to stay open until closed
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)

    # Navigate to the link
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.maximize_window()
    driver.get(URL)

    # Filter by Software Engineer
    rolesDropdown = driver.find_element(by="id", value="dropdownMenuButton")
    rolesDropdown.click()

    # Select Software Engineer and click out of dropdown
    SWE = driver.find_element(by="xpath", value="/html/body/div[2]/div[1]/div[1]/div[1]/div/div/div[1]/label/input")
    SWE.click()
    rolesDropdown.click()

    # Begin extracting data by passing web driver page
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Retrieve the table of job listings
    table = soup.find("table", attrs={"class": "hiring-companies-table"})

    # Iterate through each row and grab data
    for row in table.find_all("tr")[1:2]:
        company = row.find("th").text.strip()

        data = row.find_all("td")[1:]
        locations = data[0].text.strip()
        date = data[1].text.strip()
        url = data[2].find("a")['href']

        # Ignores none job listings
        if company:
            print("Company: {} \tLocations: {} \tDate: {} \tLink: {}".format(company, locations, date, url))

    # TODO: Perform some data extraction

if __name__ == '__main__':
    # TODO: Initialize class and call methods
    main()
