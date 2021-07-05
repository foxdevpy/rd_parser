"""
This parser is implemented with requests and the lxml library.
The parser implemented with selenium is located at this link:
https://github.com/foxdevpy/rd_parser/blob/main/parser_pskb_selenium.py
"""

import requests
from lxml import html
import time
import json
import re


base_url = 'https://pskb.com'
url_offices = 'https://pskb.com/offices/'
HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0',
    'accept': '*/*'
}
headers_change_town = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
    'Host': 'pskb.com',
    'Referer': 'https://pskb.com/offices/',
    'sec-ch-ua': 'Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    'sec-ch-ua-mobile': '?0',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
}

def get_phones(text):
    text = text.replace('\xa0', '')
    code = re.search('\(([0-9]{3,5})\)', text).group(1)
    nums = re.findall("\d?\d?\d[−|-]?\d\d[−|-]?\d\d|\d{7}", text)
    return [f"+7{code}{i.replace('−', '').replace('-','')}" for i in nums]

def parse_info():
    response = requests.get(url_offices, headers=HEADERS)
    page = html.fromstring(response.text)
    towns = page.xpath('//div[@class="row city-list"]//@href')
    towns_ids = []
    for town in towns:
        towns_ids.append(town[23:28])

    offices_url_list = []
    for town_id in towns_ids:
        with requests.Session() as session:
            session.get(f'https://pskb.com/ajax/setcity.php?city={town_id}', headers=headers_change_town, allow_redirects=True)
            response_offices = session.get(url_offices)
            page_offices = html.fromstring(response_offices.text)
            offices = page_offices.xpath('//div[@class="mb-1"]//@href')
            for office in offices:
                offices_url_list.append(office)
            time.sleep(0.5)

    office_list = []
    for office in offices_url_list:
        response_office = requests.get(base_url+office, headers=HEADERS)
        page_office = html.fromstring(response_office.text)
        name = page_office.xpath('//div[@class="col-2"]//@alt')
        script_coord = page_office.xpath('//div[@class="container"]/script[@type="text/javascript"]/text()')[0]
        found_coord = re.search('\"coord\":(\{.+?\})', script_coord).group(1)
        coord_dict = json.loads(found_coord)
        latitude, longitude = coord_dict['VALUE'].split(',')
        raw_address = page_office.xpath('//div[@class="container mb-3"]//p[1]/text()')[0]
        address = raw_address.strip()[8:].replace('\xa0', ' ')
        raw_phones = page_office.xpath('//div[@class="container mb-3"]//p[2]/text()')[0]
        phones = get_phones(raw_phones)
        working_hours = page_office.xpath('//h4[text()="Услуги частным лицам"]/following-sibling::ul[1]//li/text()')
        timeworks_template = '([А-яA-z\.\-?]{1,7}):[\s+]+?[с|С]?[\s+]?(\d?\d.\d\d)[\s+\-]?[до|ДО]{0,2}[\s+\-](\d?\d.\d\d)'
        working_time = []
        for working_hour in working_hours:
            working_hour = working_hour.replace('.', '')
            if len(re.findall(timeworks_template, working_hour)) < 1:
                continue
            day, time_start, time_stop = re.findall(timeworks_template, working_hour)[0]
            working_time.append(f"{day.lower()} {time_start}-{time_stop}")

        working_time = list(set(working_time))

        office_list.append({
            "address": address,
            "latlon": [float(latitude), float(longitude)],
            "name": name[0],
            "phones": phones,
            "working_hours": working_time
        })
        time.sleep(0.5)
    return office_list


if __name__ == "__main__":
    office_list = parse_info()
    with open('data.txt', 'w') as outfile:
        json.dump(office_list, outfile, ensure_ascii=False)
