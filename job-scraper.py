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

    rolesList = driver.find_element(by="xpath", value="/html/body/div[2]/div[1]/div[1]/div[1]/div/div")
    # SWE = rolesList.find_elements(by="tag", value="label")
    # for element in  SWE:
    #    print(element.text)
    #    print(element.tag_name)
    #    print(element.parent)
    #    print(element.location)
    #    print(element.size)


if __name__ == '__main__':
    main()
