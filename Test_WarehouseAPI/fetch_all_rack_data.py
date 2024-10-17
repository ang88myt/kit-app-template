import json
import requests

# Base URL template
url_template = "https://digital-twin.expangea.com/rack/5BTG/3/{rack_no}/"

# Headers for the API request
headers = {
    'X-API-KEY': '2c38e689-8bac-4ec6-9e0e-70e98222dc2d',
    'Cookie': 'csrftoken=lHpcpgZPy4wo2tW9BoHeOtTsklHWj3r2'
}

# Initialize an empty list to store rack data
rack_data = []

# Loop through rack numbers from 1 to 35
for rack_no in range(1, 36):
    url = url_template.format(rack_no=rack_no)

    try:
        response = requests.request("POST", url, headers=headers)

        # Check if the response is valid (status code 200)
        if response.status_code == 200:
            try:
                data = response.json()
                # Save the returned data in the JSON output
                rack_data.append({
                    "rack_no": rack_no,
                    "data": data if data else None  # Add data if exists, otherwise None
                })
            except json.JSONDecodeError:
                # Handle cases where the response is not valid JSON
                rack_data.append({
                    "rack_no": rack_no,
                    "data": None
                })
        else:
            # If the server returns an error status code
            rack_data.append({
                "rack_no": rack_no,
                "data": None
            })

    except requests.RequestException as e:
        # If there is an error with the request itself (e.g., connection issues)
        rack_data.append({
            "rack_no": rack_no,
            "data": None
        })

# Write the collected data to a JSON file
output_file = "rack_data_output_1_35.json"
with open(output_file, "w") as f:
    json.dump(rack_data, f, indent=4)


