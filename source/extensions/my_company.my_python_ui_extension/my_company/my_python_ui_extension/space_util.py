import requests

# The API endpoint
url = "https://digital-twin.expangea.com/rack/5BTG/3/23/"

# Make a GET request to the endpoint
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    data = response.json()

    # Extract rack locations
    rack_locations = data.get('data', {}).get('rack_locations', [])

    # Print the coordinates (x, y, z) for each location
    for location in rack_locations:
        coordinates = location.get('coordinates', {})
        x = coordinates.get('x')
        y = coordinates.get('y')
        z = coordinates.get('z')
        print(f"Location ID: {location['location_id']} - Coordinates: x={x}, y={y}, z={z}")
else:
    print(f"Failed to retrieve data. Status code: {response.status_code}")
