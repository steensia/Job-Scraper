from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def main():
    URL = 'https://www.levels.fyi/still-hiring/'

    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(URL)

    # Filter by Software Engineer
    rolesDropdown = driver.find_element(by="id", value="dropdownMenuButton")
    rolesDropdown.click()
    driver.implicitly_wait(30)

    # Select Software Engineer and click out of dropdown
    SWE = driver.find_element(by="xpath", value="/html/body/div[2]/div[1]/div[1]/div[1]/div/div/div[1]/label/input")
    SWE.click()
    driver.implicitly_wait(30)
    rolesDropdown.click()


if __name__ == '__main__':
    main()
