import time
import json
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_phones(text):
    text = text.replace('\xa0', '')
    code = re.search('\(([0-9]{3,5})\)', text).group(1)
    nums = re.findall("\d?\d?\d[−|-]?\d\d[−|-]?\d\d|\d{7}", text)
    return [f"+7{code}{i.replace('−', '').replace('-', '')}" for i in nums]


def parse_info():
    driver = webdriver.Chrome(executable_path='./pskb_selenium/chromedriver/chromedriver')
    driver.get("https://pskb.com/offices/")
    towns_list = []
    elements = driver.find_elements_by_xpath('//a[contains(@href,"/ajax/setcity.php?city=")]')
    for element in elements:
        towns_list.append(element.get_attribute('href'))

    offices_url_list = []
    for num in range(1, len(towns_list) + 1):
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, '//a[@href="#city-change" and @class="nav-link f-XS"]'))).click()
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, f'(//a[contains(@href, "/ajax/setcity.php?city=")])[{num}]'))).click()
        offices = driver.find_elements_by_xpath('//div[@class="mb-1"]//a[contains(@href, "/offices/")]')
        for office in offices:
            offices_url_list.append(office.get_attribute('href'))

    office_list = []
    for url_office in offices_url_list:
        driver.get(f'{url_office}')
        name = driver.find_element_by_xpath('//div[@class="col-2"]/a[@alt]').get_attribute('alt')
        script_coord = driver.find_element_by_xpath('//script[text()[contains(., "myMap")]]').get_attribute('innerText')
        found_coord = re.search('\"coord\":(\{.+?\})', script_coord).group(1)
        coord_dict = json.loads(found_coord)
        latitude, longitude = coord_dict['VALUE'].split(',')
        raw_address = driver.find_element_by_xpath('//div[@class="container mb-3"]//p[1]').text
        address = raw_address.strip()[8:].replace('\xa0', ' ')
        raw_phones = driver.find_element_by_xpath('//div[@class="container mb-3"]//p[2]').text
        phones = get_phones(raw_phones)
        working_hours = driver.find_elements_by_xpath(
            '//h4[text()="Услуги частным лицам"]/following-sibling::ul[1]//li')
        timeworks_template = '([А-яA-z\.\-?]{1,7}):[\s+]+?[с|С]?[\s+]?(\d?\d.\d\d)[\s+\-]?[до|ДО]{0,2}[\s+\-](\d?\d.\d\d)'
        working_time = []
        for working_hour in working_hours:
            working_hour = working_hour.text
            working_hour = working_hour.replace('.', '')
            if len(re.findall(timeworks_template, working_hour)) < 1:
                continue
            day, time_start, time_stop = re.findall(timeworks_template, working_hour)[0]
            working_time.append(f"{day.lower()} {time_start}-{time_stop}")
        working_time = list(set(working_time))

        office_list.append({
            "address": address,
            "latlon": [float(latitude), float(longitude)],
            "name": name,
            "phones": phones,
            "working_hours": working_time
        })
        time.sleep(1)
    driver.close()
    return office_list


if __name__ == "__main__":
    office_list = parse_info()
    with open('data.txt', 'w') as outfile:
        json.dump(office_list, outfile, ensure_ascii=False)
