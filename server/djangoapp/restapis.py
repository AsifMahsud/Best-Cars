import requests
import random
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth

# Create a `get_request` to make HTTP GET requests
def get_request(url, api_key=None, **kwargs):
    if api_key:
        response = requests.get(url, params=kwargs, headers={'Content-Type': 'application/json'},
                                auth=HTTPBasicAuth('apikey', api_key))
    else:
        response = requests.get(url, params=kwargs, headers={'Content-Type': 'application/json'})
    if response.status_code == 200:
        return response.json()
    return None

# Create a `post_request` to make HTTP POST requests
def post_request(url, api_key=None, json_payload=None, **kwargs):
    if api_key:
        response = requests.post(url, params=kwargs, json=json_payload, headers={'Content-Type': 'application/json'},
                                 auth=HTTPBasicAuth('apikey', api_key))
    else:
        response = requests.post(url, params=kwargs, json=json_payload, headers={'Content-Type': 'application/json'})
    return response.json()

# Create a get_dealers_from_cf method to get dealers from a cloud function
def get_dealers_from_cf(url):
    results = get_request(url)
    if results:
        return [CarDealer(**dealer) for dealer in results]
    return []

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
def get_dealer_reviews_from_cf(url, dealer_id):
    results = get_request(url, dealerId=dealer_id)
    if results:
        return [DealerReview(**review) for review in results]
    return []

def extract_car_details(car_string):
    parts = car_string.split('-')
    make = parts[0]
    model = parts[1]
    year = int(parts[2])
    return make, model, year

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
def analyze_review_sentiments(url, api_key, text):
    payload = {
        "text": text,
        "features": {
            "sentiment": {}
        }
    }
    response = post_request(url, api_key=api_key, json_payload=payload)
    if 'sentiment' in response and 'document' in response['sentiment']:
        return response['sentiment']['document']['label']
    return None

def post_review_to_cloudant(car, dealership, purchase, purchase_date, review):
    car_make, car_model, car_year = extract_car_details(car)

    payload = {
        "id": random.randint(33, 333),
        "car_make": car_make,
        "car_model": car_model,
        "car_year": car_year,
        "dealership": dealership,
        "name": car,
        "purchase": purchase,
        "purchase_date": purchase_date,
        "review": review
    }

    url = "https://asifmahsud54-5000.theiadocker-2-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/review"

    response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
    
    return response
