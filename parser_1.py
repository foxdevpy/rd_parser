import requests
from lxml import html
import json
import re

URL = 'https://www.mebelshara.ru/contacts'
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0', 'accept': '*/*'}
HOST = 'https://www.mebelshara.ru'

response = requests.get(URL, headers=HEADERS)
page = html.fromstring(response.text)
city_items = page.xpath("//div[@class='city-item']")
shop_list = []
for city_item in city_items:
    city = city_item.xpath(".//h4[@class='js-city-name']/text()")
    shops = city_item.xpath('.//div[@class="shop-list"]/div')
    for shop in shops:
        address = shop.xpath('./@data-shop-address')
        latitude = shop.xpath('./@data-shop-latitude')[0]
        longitude = shop.xpath('./@data-shop-longitude')[0]
        name = shop.xpath('./@data-shop-name')
        phones = shop.xpath('./@data-shop-phone')


        working_hours_1 = shop.xpath('./@data-shop-mode1')
        if working_hours_1[0].lower() == 'без выходных:':
            working_hours_1[0] = 'пн-вс'
        else:
            working_template = '([А-я\-?]{1,5}):[\s+]+?[с|С]?[\s+]?(\d?\d.\d\d)[\s+\-]+(\d?\d.\d\d)' # проверить регулярку и укоротить
            found_working = re.findall(working_template, working_hours_1[0])
            working_time = []
            for period in found_working:
                day = period[0]
                start_time = period[1]
                end_time = period[2]
                work_time = f'{day} {start_time}-{end_time}'
                working_time.append(work_time)
                working_hours_1 = working_time


        working_hours_2 = shop.xpath('./@data-shop-mode2')  # добавить регулярку
        weekend_template = '([А-я\-?]{1,5}):[\s+]+?[с|С]?[\s+]?(\d?\d.\d\d)[\s+\-]+(\d?\d.\d\d)'
        found_weekend = re.findall(weekend_template, working_hours_2[0])
        weekend_time = []
        for period in found_weekend:
            day = period[0]
            start_time = period[1]
            end_time = period[2]
            work_time = f'{day} {start_time}-{end_time}'
            weekend_time.append(work_time)
            working_hours_2 = working_time
        shop_list.append({
            "address": ", ".join(city + address),
            "latlon": [float(latitude), float(longitude)],
            "name": name[0],
            "phones": phones,
            "working_hours": [" ".join(working_hours_1 + working_hours_2)]
        })

shop_list_json = json.dumps(shop_list, ensure_ascii=False)
print(shop_list_json)
