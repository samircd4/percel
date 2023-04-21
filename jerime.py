import requests
from selectolax.parser import HTMLParser
from datetime import datetime
import json
import pandas as pd

# Get location from maps.clarkcountynv.gov
def get_location(percel_num):
    address = []
    url = f'https://maps.clarkcountynv.gov/assessor/AssessorParcelDetail/ParcelDetail.aspx?hdnParcel={percel_num}&hdnInstance=pcl7'
    
    res = requests.get(url)
    html = HTMLParser(res.text)
    street_address = html.css_first('span#lblLocation').text().replace('  ', ' ')
    city = html.css_first('span#lblTown').text().strip()
    address.append(street_address)
    address.append(city)
    address.append(percel_num)
    return address


# Get full address from https://postalcode.globefeed.com/
def get_zip_code(address):
    full_address = {}
    street_address = address[0]
    city_clark = address[1]
    address_city = f'{street_address} {city_clark}'
    url = f"https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/suggest?f=pjson&countrycode=US&text={address_city}"
    print(address_city)
    response = requests.get(url)

    data = json.loads(response.text)['suggestions'][0]['text'].split(',')
    full_address['percel_number'] = address[2]
    try:
        full_address['address'] = data[0].strip()
        full_address['city'] = data[-4].strip()
        full_address['state'] = data[-3].strip()
        full_address['zip'] = data[-2].strip()
    except:
        with open('error.txt', 'a') as f:
            f.write(f'{address[2]}\n')
    
    
    return full_address



def get_p_number():
    filename = 'p_number.txt'
    data = []
    with open(filename) as f:
        lines = f.readlines()
        for line in lines:
            data.append(line.strip())
    return data


def save_csv(data):
    df = pd.DataFrame(data)
    today = datetime.today().strftime('%m-%d-%Y')
    df.to_csv(f'{today}.csv', index=False)


def main():
    p_number = get_p_number()
    # p_number = ['040-13-701-001']
    data = []
    for idx, number in enumerate(p_number):
        try:
            address = get_location(number)
        except:
            with open('error.txt', 'a') as f:
                f.write(f'{number}\n')
                continue
        full_address = get_zip_code(address)
        print(f'{idx}: {full_address}')
        data.append(full_address)
    save_csv(data)


if __name__ == '__main__':
    main()