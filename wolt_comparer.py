import requests
import json

from geopy.geocoders import Nominatim
from langdetect import detect

search_venues_url = "https://restaurant-api.wolt.com/v1/pages/search"
default_lat = 32.087900
default_lon = 34.772890


# Check if both product name and desired product are in Hebrew or English
def compare_language(t1, t2):
    l1 = detect(t1)
    l2 = detect(t2)

    return (l1 == 'he' and l2 == 'he') or (l1 != 'he' and l2 != 'he')


# Get item page's link
def generate_link(venue_link, product_id):
    return f'{venue_link}/itemid-{product_id}'


# Get lat and lon from address string
def get_lon_lat_from_address(address):
    # calling the Nominatim tool and create Nominatim class
    loc = Nominatim(user_agent="Geopy Library")

    # entering the location name
    get_loc = loc.geocode(address)

    try:
        return get_loc.latitude, get_loc.longitude
    except AttributeError as e:
        print(f'[!] Error in get_lon_lat_from_address: {str(e)}')
        return default_lat, default_lon


# Search all venues that sell the desired product
def get_venues_by_product(product_name, lat, lon):
    payload = {}
    headers = {"Platform": "Web"}
    params = {"q": product_name, "target": "venues", "lat": lat, "lon": lon}

    url = search_venues_url + '?' + "".join([p + '=' + str(params[p]) + '&' for p in params.keys()])[:-1]

    response = requests.request("GET", url, headers=headers, data=payload)

    try:
        response = json.loads(response.text)

        venues = response['sections'][0]['items']
        venues = list(filter(lambda v: "overlay" not in v.keys(), venues))

        venues = [{'title': r['title'], 'track_id': r['track_id'].split('venue-')[1], "link": r["link"]["target"]} for r
                  in venues]

    except KeyError as e:
        print(f'[!] Error in get_venues_by_product: {str(e)}')
        return []

    return venues


# Filter names for a product name that contains more than one word for more precise results
def check_names(p, product_name):
    if not compare_language(p, product_name):
        return True

    product_name = product_name.lower()

    if all([w in p.split(' ') for w in product_name.split(' ')]):
        return True

    return False


# Get all products matching from specific venue
def get_product_from_venue(track_id, product_name):
    url = f"https://restaurant-api.wolt.com/v4/venues/slug/{track_id}/menu/items?unit_prices=true&show_weighted_items=true&q={product_name}"

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    response = json.loads(response.text)
    products = [{'id': p['id'], 'name': p['name'], 'price': p['baseprice'] / 100, 'image': p['image']} for p in
                response['items']]
    products = list(filter(lambda p: check_names(p['name'], product_name), products))

    return products


# Main function
def get_results(product_name, lat, lon):
    options_to_compare = []
    avg_price = 0

    venues = get_venues_by_product(product_name, lat, lon)
    if len(venues) == 0:
        return [], 0

    for venue in venues:
        options_to_add = get_product_from_venue(venue['track_id'], product_name)

        for o in options_to_add:
            options_to_compare.append({'venue': venue['title'], 'product_name': o['name'],
                                       'price': o['price'], 'image-path': o['image'],
                                       'link': generate_link(venue['link'], o['id'])})
            avg_price += o['price']

    if len(options_to_compare) == 0:
        return [], 0
    options_to_compare = sorted(options_to_compare, key=lambda x: x['price'])
    avg_price /= len(options_to_compare)

    return options_to_compare, avg_price


if __name__ == "__main__":
    # For testing the module
    print(get_results(input('Enter Product Name:'), default_lat, default_lon))
