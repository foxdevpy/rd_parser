import requests
from lxml import html
import json
import re


URL = 'https://www.tvoyaapteka.ru/bitrix/ajax/modal_geoip.php'
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0',
           'accept': '*/*'}
HOST = 'https://www.tvoyaapteka.ru'

response = requests.get(URL, headers=HEADERS)
page = html.fromstring(response.text)
regions = page.xpath('//div[@class=" col-xs-6 regions"]//li/@data-id')

towns_id = []
for region in regions:
    url_town = f'https://www.tvoyaapteka.ru/bitrix/ajax/modal_geoip.php?action=get_towns&region_id={region}'
    response_towns = requests.get(url_town, headers=HEADERS)
    towns = json.loads(response_towns.text)
    for town in towns:
        towns_id.append(town['ID'])
        town_name = town['NAME']

pharmacy_list = []
for town_id in towns_id:
    geopip_url = 'https://www.tvoyaapteka.ru/bitrix/ajax/modal_geoip.php'
    base_url = 'https://www.tvoyaapteka.ru/adresa-aptek/'
    with requests.Session() as session:
        session.post(geopip_url, data={'town': town_id, 'action': 'change_town'}, headers=HEADERS)
        response_pharmacy = session.get(base_url, headers=HEADERS)
        page_pharmacy = html.fromstring(response_pharmacy.text)
        pharmacies = page_pharmacy.xpath('//div[starts-with(@class,"apteka_item")]')
        phones = page_pharmacy.xpath('//div[starts-with(@class,"number")]/text()')
        phone = phones[0].strip()
        for pharmacy in pharmacies:
            city = page_pharmacy.xpath('.//@data-city')
            address = pharmacy.xpath('.//div[@class="apteka_address"]/span/text()')
            latitude = pharmacy.xpath('./@data-lat')[0]
            longitude = pharmacy.xpath('./@data-lon')[0]
            name = pharmacy.xpath('.//div[@class="apteka_title"]/span/text()')
            working_days = pharmacy.xpath('.//div[@class="apteka_time"]/span/text()')
            stripped_working_days = [i.strip() for i in working_days]
            working_time = []
            if stripped_working_days[0].lower() == 'круглосуточно':
                working_time = ['пн-вс 0:00-24:00']
            else:
                timework_template = '([А-я\-?]{1,5}):[\s+]+?[с|С]?[\s+]?(\d?\d.\d\d)[\s+\-]?[до|ДО]{0,2}[\s+\-](\d?\d.\d\d)'
                found_timeworks = re.findall(timework_template, stripped_working_days[1])
                if found_timeworks:
                    working_time = []
                    for period in found_timeworks:
                        day = period[0].lower()
                        start_time = period[1]
                        end_time = period[2]
                        work_time = f'{day} {start_time}-{end_time}'
                        working_time.append(work_time)
                else:
                    timework_template = '(с|С)[\s]+(\d\d?.\d\d)[\s]+(до|ДО)[\s]+(\d\d.\d\d)'
                    found_timeworks = re.findall(timework_template, stripped_working_days[1])
                    working_time = [f'пн-вс {found_timeworks[0][1]}-{found_timeworks[0][3]}']

            pharmacy_list.append({
                "address": ", ".join(city + address),
                "latlon": [float(latitude), float(longitude)],
                "name": name[0],
                "phones": [phone],
                "working_hours": working_time
            })

pharmacy_list_json = json.dumps(pharmacy_list, ensure_ascii=False)
print(pharmacy_list_json)
