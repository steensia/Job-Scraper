from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import sendgrid
import os
from sendgrid.helpers.mail import *
from twilio.rest import Client


# TODO: Create class and methods for readability
def send_email():
    message = Mail(From('steensia101@gmail.com'),
                   To('steensia101@gmail.com'),
                   Subject('Sending with SendGrid is Fun'),
                   PlainTextContent('and easy to do anywhere, even with Python'))
    try:
        sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
        response = sg.client.mail.send.post(request_body=message.get())
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)


def send_text():
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    client = Client(account_sid, auth_token)

    message = client.messages \
        .create(body="Join Earth's mightiest heroes. Like Kevin Bacon.",
                from_='+13852179269',
                to='+18019797937')

    print(message.sid)


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

    jobs = []
    # Iterate through each row and grab data except column headers row
    for row in table.find_all("tr")[1:]:
        # Extract valid job listing values, otherwise ignore
        try:
            company = row.find("th").text.strip()
        except:
            continue

        data = row.find_all("td")[1:]
        locations = data[0].text.strip()

        # Show new job listings in Utah or Remote only
        if not any(location in locations.split(' ') for location in ["UT", "Remote"]):
            continue

        # Parse out date and format to mm/dd/yyyy
        split_date = data[1].text.strip().split(' ')

        month = datetime.strptime(split_date[0], '%b').month
        day = int(split_date[1])
        year = int(split_date[2]) if len(split_date) > 2 else datetime.today().year

        date = datetime(year=year, month=month, day=day)
        today = datetime.combine(datetime.today(), datetime.min.time()) - timedelta(4)

        url = data[2].find("a")['href']

        # Only show new job listings
        if date >= today:
            jobs.append([company, datetime.strftime(date, "%m/%d/%Y"), url])

    # Dispose chrome browser after scraping data
    driver.quit()

    # TODO: Perform data export
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    df = pd.DataFrame(jobs, columns=["Company", "Date", "Link/Email"])
    if not df.empty:
        # send_email()
        send_text()
        print(df)


if __name__ == '__main__':
    # TODO: Instantiate class and call methods
    main()
