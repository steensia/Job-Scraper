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


class JobScraper:
    """
        Initialize Selenium Chrome Driver and BeautifulSoup objects
    """

    def __init__(self):
        self.URL = 'https://www.levels.fyi/still-hiring/'

        # Initialize main objects
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.soup = BeautifulSoup(self.filter_website(), "html.parser")

    """ Go to website and filter by SWE jobs
        Return the page source for soup to parse
    """

    def filter_website(self):
        # Navigate to the link
        self.driver.get(self.URL)

        # Filter by Software Engineer
        roles_dropdown = self.driver.find_element(by="id", value="dropdownMenuButton")
        roles_dropdown.click()

        # Select Software Engineer and click out of dropdown
        swe = self.driver.find_element(by="xpath",
                                       value="/html/body/div[2]/div[1]/div[1]/div[1]/div/div/div[1]/label/input")
        swe.click()
        roles_dropdown.click()

        # Save page source to return before closing driver
        page_source = self.driver.page_source
        self.driver.close()

        return page_source

    def scrape_jobs(self):
        # Retrieve the table of job listings
        table = self.soup.find("table", attrs={"class": "hiring-companies-table"})

        # Iterate through each row and grab data except column headers row
        job_list = []
        for row in table.find_all("tr")[1:14]:
            # Extract valid job listing values, otherwise ignore
            try:
                company = row.find("th").text.strip()
            except:
                continue

            data = row.find_all("td")[1:]

            locations = data[0].text.strip().split(' ')
            new_locations = []
            for location in locations:
                if "UT" in location and "Utah" not in new_locations:
                    new_locations.append("Utah")
                elif "Remote" in locations and "Remote" not in new_locations:
                    new_locations.append("Remote")

            #print(new_locations)

            #locations = [location.strip() for location in locations if "UT" in location or "Remote" in location]
            #print(locations)

            # Show new job listings in Utah or Remote only
            if not new_locations:
                None
                #continue

            # Parse out date and format to mm/dd/yyyy
            date = parse_date(data[1].text.strip().split(' '))

            url = data[2].find("a")['href']

            # Only show new job listings
            if new_jobs(date, 14):
                job_list.append([company, ', '.join(new_locations), datetime.strftime(date, "%m/%d/%Y"), url])

        return job_list


def new_jobs(date, days_back):
    """
    Helper method to parse and format date to mm/dd/yyyy
    :param days_back:
    :param date:
    :return:
    """
    today = datetime.combine(datetime.today(), datetime.min.time()) - timedelta(days_back)

    return date >= today


def parse_date(date):
    """
    Return true if new jobs are available, false otherwise
    :param date:
    :return:
    """
    month = datetime.strptime(date[0], '%b').month
    day = int(date[1])
    year = int(date[2]) if len(date) > 2 else datetime.today().year

    return datetime(year=year, month=month, day=day)


def display_data(job_list):
    """
    Helper function ti print out data using pandas
    :param job_list:
    """
    # TODO: Perform data export
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    df = pd.DataFrame(job_list, columns=["Company", "Locations", "Date", "Link/Email"])
    if not df.empty:
        print(df)

    return df


def send_email(job_list):
    """
    Send email to apply to new job(s)
    """

    html = display_data(job_list).to_html()
    message = Mail(From("steensia101@gmail.com"),
                   To("steensia101@gmail.com"),
                   Subject("Levels.fyi Job Alerts"),
                   PlainTextContent("Your job alert for Software Engineer"),
                   HtmlContent(html))
    try:
        sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
        sg.client.mail.send.post(request_body=message.get())
        print("Email sent successfully")
    except Exception as e:
        print(e.body)


def send_text(job_list):
    """
    Send text alert to notify of new job(s)
    """
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    client = Client(account_sid, auth_token)

    try:
        client.messages \
            .create(body="{} new Software Engineer jobs from Levels.fyi".format(len(job_list)),
                    from_='+13852179269',
                    to='+18019797937')
        print("Text message sent successfully")
    except Exception as e:
        print(e)


if __name__ == '__main__':
    js = JobScraper()
    jobs = js.scrape_jobs()
    display_data(jobs)
    # send_text(jobs)
    # send_email(jobs)
