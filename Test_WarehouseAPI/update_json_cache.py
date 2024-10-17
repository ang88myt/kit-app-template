import os
import requests
from pxr import Usd, UsdGeom, Gf
import omni.usd
import csv

# Function to fetch stock information from the API
def fetch_stock_info(base_url, endpoint, headers):
    api_url = f"{base_url}{endpoint}"
    response = requests.post(api_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

# Function to fetch coordinates from API
def fetch_coordinates(base_url, endpoint, headers):
    api_url = f"{base_url}{endpoint}"
    try:
        response = requests.post(api_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # Navigate through the JSON structure to get the coordinates
            coordinates = data.get('data', {}).get('coordinates', {})
            return coordinates.get('x'), coordinates.get('y'), coordinates.get('z')
        else:
            print(f"Failed to fetch coordinates: {response.status_code}")
            return None, None, None
    except Exception as e:
        print(f"Error fetching coordinates: {e}")
        return None, None, None

def save_to_csv(data):
    directory = os.path.join(os.environ['USERPROFILE'], 'Documents', 'test')
    filename = os.path.join(directory, "current_stock.csv")
    os.makedirs(directory, exist_ok=True)

    if not data:
        print("No data provided to save.")
        return

    # Ensure data is a list of dictionaries
    if isinstance(data, dict):
        data = [data]

    # Get the keys from the first item in the response to be used as CSV headers
    keys = data[0].keys()
    print(keys)

    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

    print(f"Data successfully saved to {filename}")

base_url = "https://digital-twin.expangea.com/"
stock_endpoint = "pallet/UINT0000038586/"
location_endpoint = "rack-location/3012011/"
headers = {
    'X-API-KEY': '2c38e689-8bac-4ec6-9e0e-70e98222dc2d'
}

stock_info = fetch_stock_info(base_url, stock_endpoint, headers)
for key, value in stock_info.items():
    print(f"{key}: {value}")

x, y, z = fetch_coordinates(base_url, location_endpoint, headers)
print(x, y, z)
