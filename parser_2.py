import json
import requests


def pars_working_hours(workdays, saturday, sunday):
    work = f"пн-пт {workdays['startStr']}-{workdays['endStr']}"
    weekend = ""
    if not saturday['isDayOff'] and not sunday['isDayOff']:
        if saturday == sunday:
            weekend = f"сб-вс {saturday['startStr']}-{sunday['endStr']}"
        else:
            weekend = f"сб {saturday['startStr']}-{saturday['endStr']}, вс {sunday['startStr']}-{sunday['endStr']}"
    if saturday['isDayOff'] is False and sunday['isDayOff'] is True:
        weekend = f"сб {saturday['startStr']}-{saturday['endStr']}"
    return ", ".join(filter(None, [work, weekend]))


def main():
    base_url = "https://apigate.tui.ru/api/office/list?cityId=1&subwayId=&hoursFrom=&hoursTo=&serviceIds=all&toBeOpenOnHolidays=false"
    response = requests.get(base_url)
    shops = json.loads(response.text)
    shop_list = []
    for shop in shops['offices']:
        address = shop['address']
        if address[0:6].isdigit():
            address = address[8:]
        latitude = shop['latitude']
        longitude = shop['longitude']
        name = shop['name']
        phones = shop['phone']
        working_hours = shop['hoursOfOperation']
        workdays = working_hours['workdays']
        saturday = working_hours['saturday']
        sunday = working_hours['sunday']

        shop_list.append({
            "address": address,
            "latlon": [latitude, longitude],
            "name": name,
            "phones": [phones],
            "working_hours": pars_working_hours(workdays, saturday, sunday)
        })

    shop_list_json = json.dumps(shop_list, ensure_ascii=False)
    print(shop_list_json)


if __name__ == "__main__":
    main()
