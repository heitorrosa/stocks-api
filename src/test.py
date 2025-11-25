import requests
import os
import sys
from dotenv import load_dotenv

load_dotenv()

API = {
    'KEY': os.getenv('STOCKSAPI_PRIVATE.KEY'),
}

BASE_URL = "http://localhost:3200"
API_KEY = API['KEY']
headers = {"X-API-Key": API_KEY}

# Historical data by ticker
response = requests.get(
    f"{BASE_URL}/api/historical",
    params={
        "ticker": "PETR4",
        "fields": "DY,LUCRO LIQUIDO,MARGEM BRUTA",
        "dates": "2020-01-01,2024-12-31"
    },
    headers=headers
)
print("Historical by ticker:")
print(response.json())
print("\n")

# Historical data by ticker
response = requests.get(
    f"{BASE_URL}/api/historical",
    params={
        "ticker": "PETR4",
        "fields": "DY,LUCRO LIQUIDO,MARGEM BRUTA",
        "dates": "2020-01-01,2024-12-31"
    },
    headers=headers
)
print("Historical by ticker:")
print(response.json())
print("\n")

# Historical data by stock name
response = requests.get(
    f"{BASE_URL}/api/historical",
    params={
        "ticker": "Petróleo Brasileiro",
        "fields": "DY,LUCRO LIQUIDO,MARGEM BRUTA",
        "dates": "2020-01-01,2024-12-31"
    },
    headers=headers
)
print("Historical by stock name:")
print(response.json())
print("\n")

# Fundamental data by ticker
response = requests.get(
    f"{BASE_URL}/api/fundamental",
    params={
        "ticker": "VALE3",
        "fields": "ROE,P/L,PRECO",
        "dates": "2024-01-01,2024-12-31"
    },
    headers=headers
)
print("Fundamental by ticker:")
print(response.json())
print("\n")

# Fundamental data by stock name
response = requests.get(
    f"{BASE_URL}/api/fundamental",
    params={
        "ticker": "Vale",
        "fields": "ROE,P/L,PRECO,DY MEDIO 5 ANOS",
        "dates": "2024-01-01,2024-12-31"
    },
    headers=headers
)
print("Fundamental by stock name:")
print(response.json())