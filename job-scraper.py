from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
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
    roles_dropdown = driver.find_element(by="id", value="dropdownMenuButton")
    roles_dropdown.click()

    # Select Software Engineer and click out of dropdown
    swe = driver.find_element(by="xpath", value="/html/body/div[2]/div[1]/div[1]/div[1]/div/div/div[1]/label/input")
    swe.click()
    roles_dropdown.click()

    # Begin extracting data by passing web driver page
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Retrieve the table of job listings
    table = soup.find("table", attrs={"class": "hiring-companies-table"})

    # Iterate through each row and grab data
    for row in table.find_all("tr")[1:5]:
        # Extract valid job listing values, otherwise ignore
        try:
            company = row.find("th").text.strip()
        except:
            continue

        data = row.find_all("td")[1:20]
        locations = data[0].text.strip()

        # Parse out date and format to mm/dd/yyyy
        split_date = data[1].text.strip().split(' ')
        month = datetime.strptime(split_date[0], '%b').month
        day = int(split_date[1])

        date = datetime(year=datetime.today().year, month=month, day=day)
        today = datetime.combine(datetime.today(), datetime.min.time())

        url = data[2].find("a")['href']

        # Only show new job listings
        if date >= today:
            print("Company: {} \tLocations: {} \tDate: {} \tLink: {}"
                  .format(company, locations, datetime.strftime(date, "%m/%d/%Y"), url))

    # TODO: Perform data export


if __name__ == '__main__':
    # TODO: Instantiate class and call methods
    main()
