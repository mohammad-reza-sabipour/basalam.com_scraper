import requests
import json
import sys
from bs4 import BeautifulSoup
from selenium import webdriver


# vendors = ['apparel', 'kitchen-appliances', 'electronic-devices', 'sport-travel', 'cultural-educational-entertainment']
vendors = ['electronic-devices']
all_vendors = []
initial_cursor = 'rBGx3Twy2ksw6EXSygBZtj8bWuw7NZH4V3oFkalLcZVMI4jXOioGqjHoQ4N'
next_cursor = None

for v in vendors:
    url = f"https://api.basalam.com/explore/api_v1.0/component/category-landing-{v}-top-selling-vendors/0"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Python script",
    }
    payload = {
        'size': 12,
        'cursor': initial_cursor,
    }

    while next_cursor != payload['cursor']:
        response = requests.post(url, headers=headers, json=payload)
        #print(json.dumps(response.json(), indent=4, ensure_ascii=False))
        if response.status_code == 200:
            data = response.json()
            next_cursor = data.get("meta", {}).get("cursor")
            items = data.get('items', [])
            results = items[0].get('result', [])
            for vendor in results:
                vendor_payload = {
                    'from' : 0
                }
                user = vendor.get('user', {})
                vendor_name = user.get('vendorName', 'Unknown Vendor')
                vendor_page = vendor.get('identifier')
                vendor_data = {
                    'vendor_name': vendor_name,
                    'products': []
                }
                try:
                    vendor_url = f'https://search.basalam.com/ai-engine/api/v2.0/product/search?from=0&f.vendorIdentifier={vendor_page}&dynamicFacets=true&size=12&adsImpressionDisable=false&filters.vendorIdentifier={vendor_page}&vendor_sort=6050'
                    vendor_req = requests.get(vendor_url, json=vendor_payload)
                    count = vendor_req.json().get("meta", {}).get("count")
                    if response.status_code == 200:
                        while vendor_payload['from'] <= count:
                            vendor_url = f'https://search.basalam.com/ai-engine/api/v2.0/product/search?from={vendor_payload['from']}&f.vendorIdentifier={vendor_page}&dynamicFacets=true&size=12&adsImpressionDisable=false&filters.vendorIdentifier={vendor_page}&vendor_sort=6050'
                            r = requests.get(vendor_url, json=vendor_payload).json()['products']
                            for product in r:
                                if product.get('name'):
                                    product_data = {
                                        'product_name': product.get('name'),
                                        'product_id': product.get('id'),
                                        'vendor_identifier': product.get('vendor', {}).get('identifier'),
                                        'product_img': product.get('photo', {}).get('SMALL'),
                                    }
                                    vendor_data['products'].append(product_data)


                            vendor_payload['from'] += 12
                    else:
                        raise Exception

                except:
                    break
                all_vendors.append(vendor_data)
            payload['cursor'] = next_cursor
        else:
            print(f"Failed to fetch data: {response.status_code}")
            break

with open("output.json", "w", encoding="utf-8") as file:
    json.dump(all_vendors, file, ensure_ascii=False, indent=4)

print(f"Data scraped successfully")
