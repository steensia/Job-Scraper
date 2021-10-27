from datetime import datetime, timedelta
import boto3
from boto3.dynamodb.conditions import Key
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
    def __init__(self):
        """
        Initialize job list, Selenium Chrome Driver, BeautifulSoup, and DynamoDB objects
        """
        self.URL = 'https://www.levels.fyi/still-hiring/'

        # Initialize main objects
        self.jobs = []
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.soup = BeautifulSoup(self.filter_website(), "html.parser")
        self.dynamodb = boto3.resource("dynamodb", region_name='us-west-2')

    def filter_website(self):
        """
        Go to website and filter by SWE jobs
        Return the page source for soup to parse
        :return:
        """
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
        """
        Web scrape for new jobs and send notifications
        """
        # Retrieve the table of job listings
        table = self.soup.find("table", attrs={"class": "hiring-companies-table"})

        # Iterate through each row and grab data except column headers row
        for row in table.find_all("tr")[1:]:
            # Extract valid job listing values, otherwise ignore
            try:
                company = row.find("th").text.strip()
            except:
                continue

            locations, date, url = row.find_all("td")[1:]

            locations = self.__parse_locations(locations)

            # Show new job listings in Utah or Remote only
            if not locations:
                continue

            # Parse out date and format to mm/dd/yyyy
            date = self.__parse_date(date)

            url = url.find("a")['href']

            job = [company, ', '.join(locations), datetime.strftime(date, "%m/%d/%Y"), url]

            # Only show new job listings and check if it's not in database
            if self.is_new(date, days_before_today=0) and not self.job_exists(job):
                self.jobs.append(job)

        # Send notifications if there are new jobs available
        if self.jobs:
            print("{} new job(s) available".format(len(self.jobs)))
            self.send_text()
            self.send_email()
        else:
            print("No new jobs available")

    def send_email(self):
        """
        Send email to apply to new job(s)
        """

        html = self.__display_data(self.jobs).to_html()
        message = Mail(From("steensia101@gmail.com"),
                       To("steensia101@gmail.com"),
                       Subject("Levels.fyi Job Alerts"),
                       PlainTextContent("Your job alert for Software Engineer"),
                       HtmlContent("<h2>Your job alert for software engineer</h2>" + html))
        try:
            sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
            sg.client.mail.send.post(request_body=message.get())
            print("Email sent successfully")
        except Exception as e:
            print(e)

    def send_text(self):
        """
        Send text alert to notify of new job(s)
        """
        account_sid = os.environ['TWILIO_ACCOUNT_SID']
        auth_token = os.environ['TWILIO_AUTH_TOKEN']
        client = Client(account_sid, auth_token)

        try:
            client.messages \
                .create(body="{} new Software Engineer jobs from Levels.fyi".format(len(self.jobs)),
                        from_='+13852179269',
                        to='+18019797937')
            print("Text sent successfully")
        except Exception as e:
            print(e)

    def is_new(self, date, days_before_today):
        """
        Return true if new jobs are available, false otherwise
        :param days_before_today:
        :param date:
        :return:
        """
        today = datetime.combine(datetime.today(), datetime.min.time()) - timedelta(days_before_today)
        return date >= today

    def job_exists(self, job):
        """
        Check if job already exists in database
        Return true if exists, otherwise false
        :param job:
        :return:
        """
        table = self.dynamodb.Table('Jobs')

        company, location, date, link = job

        # Grab job to check if it exists
        db_jobs = table.query(
            KeyConditionExpression=Key('company').eq(company)
        )['Items']

        # Add job if it doesn't exist
        if not db_jobs:
            table.put_item(
                Item={
                    'company': company,
                    'location': location,
                    'date': date,
                    'link': link
                }
            )
            return False
        else:
            return True


    def __parse_locations(self, locations):
        """
        Helper function to parse and return locations: Remote/Utah
        :param locations:
        :return:
        """
        locations = locations.text.strip().split(',')
        new_locations = set()
        for location in set(locations):
            if "Remote" in location:
                new_locations.add("Remote")
            elif "UT" in location:
                new_locations.add("Utah")
        return new_locations

    def __parse_date(self, date):
        """
        Helper function to parse and format date to mm/dd/yyyy
        :param date:
        :return:
        """
        date = date .text.strip().split(' ')
        month = datetime.strptime(date[0], '%b').month
        day = int(date[1])
        year = int(date[2]) if len(date) > 2 else datetime.today().year

        return datetime(year=year, month=month, day=day)

    def __display_data(self, job_list):
        """
        Helper function to print out data in a formatted table
        :param job_list:
        """
        pd.set_option('display.max_rows', 500)
        pd.set_option('display.max_columns', 500)
        pd.set_option('display.width', 1000)

        df = pd.DataFrame(job_list, columns=["Company", "Location", "Date", "Link"])

        return df


if __name__ == '__main__':
    js = JobScraper()
    js.scrape_jobs()
