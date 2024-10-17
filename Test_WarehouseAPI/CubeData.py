import time
import logging
import requests

# Set up logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger()

# Define the API URL and headers (replace these with your actual values)
HTTP_ENDPOINT = "https://digital-twin.expangea.com/device/Cube/"
API_HEADERS = {
    'X-API-KEY': '2c38e689-8bac-4ec6-9e0e-70e98222dc2d'
}

def fetch_device_data():
    try:
        # Send a POST request to the device-specific API
        response = requests.post(url=HTTP_ENDPOINT, headers=API_HEADERS)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()  # Parse JSON response
        logger.warning(f"API Data Received: {data}")
        return data  # Return the parsed JSON response
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data from API: {e}")
        return None

def display_coordinates():
    while True:
        # Fetch device data from the API
        device_data = fetch_device_data()

        if device_data:
            data = device_data.get("data", {})
            if "coordinates" in data:
                # Log the exact coordinates received from the API
                logger.warning(f"Coordinates Received: {data['coordinates']}")

                # Get the new position from the API data
                new_position = {
                    "x": data["coordinates"].get("x", 0.0),
                    "y": data["coordinates"].get("y", 0.0),
                    "z": data["coordinates"].get("z", 0.0)
                }

                # Print the new position
                print(f"X: {new_position['x']}, Y: {new_position['y']}, Z: {new_position['z']}")

        # Wait for 3 seconds before fetching the data again
        time.sleep(3)

# Start displaying coordinates every 3 seconds
display_coordinates()

# import logging
# import requests
#
# # Set up logging
# logging.basicConfig(level=logging.WARNING)
# logger = logging.getLogger()
#
#
# class CubeDataFetcher:
#     def __init__(self, api_url, api_headers):
#         self.api_url = api_url
#         self.api_headers = api_headers
#
#     def fetch_xyz(self):
#         try:
#             # Send a POST request to the device-specific API
#             response = requests.post(url=self.api_url, headers=self.api_headers)
#             response.raise_for_status()  # Raise an exception for HTTP errors
#             data = response.json()  # Parse JSON response
#             logger.warning(f"API Data Received: {data}")
#
#             # Extract the coordinates
#             coordinates = data.get("data", {}).get("coordinates", {})
#             x = coordinates.get("x", 0.0)
#             y = coordinates.get("y", 0.0)
#             z = coordinates.get("z", 0.0)
#             return x, y, z
#         except requests.exceptions.RequestException as e:
#             logger.error(f"Error fetching data from API: {e}")
#             return 0.0, 0.0, 0.0  # Return default coordinates in case of failure
