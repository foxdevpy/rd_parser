from selenium import webdriver
# from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


driver = webdriver.Chrome(executable_path='/home/fox/PycharmProjects/rd_parser/parser_5/chromedriver/chromedriver')
driver.get("https://pskb.com/offices/")

towns_list = []
time.sleep(1)
elements = driver.find_elements_by_xpath('//*[contains(@href,"/ajax/setcity.php?city=")]')
for element in elements:
    towns_list.append(element.get_attribute('href'))

offices_url_list = []
for town in towns_list:
    WebDriverWait(driver, 100).until(EC.element_to_be_clickable((By.LINK_TEXT, f"{town}"))).click()
    time.sleep(1)
    offices = driver.find_elements_by_xpath('//div[@class="mb-1"]//@href')
    for office in offices:
        offices_url_list.append(office.get_attribute('href'))

office_list = []
for office in offices_url_list:
    driver.get(f'{office}')
    time.sleep(1)
    name = driver.find_element_by_xpath('//div[@class="col-2"]//@alt')
    name1 = name.get_attribute('alt')
    office_list.append(name1)
    print(name1)