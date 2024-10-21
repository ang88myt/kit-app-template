import requests
import math
import logging

# Setup logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_URL = "https://digital-twin.expangea.com/"
HEADERS = {
    'X-API-KEY': '2c38e689-8bac-4ec6-9e0e-70e98222dc2d'  # Your API key
}


# Define the Euclidean distance calculation
def calculate_distance(coords_a, coords_b):
    return math.sqrt((coords_a['x'] - coords_b['x']) ** 2 +
                     (coords_a['y'] - coords_b['y']) ** 2 +
                     (coords_a['z'] - coords_b['z']) ** 2)


# Function to fetch data from a rack endpoint
def fetch_rack_data(rack_number):
    url = f"{BASE_URL}rack/5BTG/3/{rack_number}/"
    logging.info(f"Fetching data for rack {rack_number} from {url}")

    try:
        response = requests.post(url, headers=HEADERS)
        response.raise_for_status()  # Raise error if request fails
        logging.info(f"Successfully fetched data for rack {rack_number}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch data for rack {rack_number}: {e}")
        return None


# Function to filter pallets by product group and return their coordinates
def filter_pallets_by_group(rack_data, group_name):
    pallets = []
    try:
        rack_locations = rack_data.get("data", {}).get("rack_locations", [])
        for location in rack_locations:
            for pallet in location.get("pallets", []):
                product_group = pallet.get("inventory", {}).get("Product Group", "")
                if product_group == group_name:
                    coordinates = location.get("coordinates", {})
                    pallets.append({"pallet_id": pallet["pallet_id"], "location_id": location["location_id"],
                                    "coordinates": coordinates})
        logging.info(f"Filtered {len(pallets)} pallets for product group {group_name}")
    except TypeError as e:
        logging.error(f"Error processing rack data: {e}. Skipping this entry.")
    return pallets


# Perform proximity check between "FOODS" and "HPC" pallets across all racks
def proximity_check_all_racks():
    food_pallets = []
    hpc_pallets = []

    # Loop through all racks from 21 to 39
    for rack_no in range(21, 40):
        rack_data = fetch_rack_data(rack_no)
        if not rack_data:
            logging.warning(f"No data found for rack {rack_no}. Skipping...")
            continue

        # Append "FOODS" and "HPC" pallets to respective lists
        food_pallets += filter_pallets_by_group(rack_data, "FOODS")
        hpc_pallets += filter_pallets_by_group(rack_data, "HPC")

    logging.info(f"Total food pallets found: {len(food_pallets)}")
    logging.info(f"Total HPC pallets found: {len(hpc_pallets)}")

    # Check proximity between each food pallet and each HPC pallet
    violations = []
    for food_pallet in food_pallets:
        for hpc_pallet in hpc_pallets:
            try:
                distance = calculate_distance(food_pallet["coordinates"], hpc_pallet["coordinates"])
                logging.info(
                    f"Checking distance between Food Pallet {food_pallet['pallet_id']} and HPC Pallet {hpc_pallet['pallet_id']}: {distance:.2f} units")
                if distance < 200.0:  # Check if the distance is less than 200 units
                    violations.append((food_pallet["pallet_id"], hpc_pallet["pallet_id"], distance))
            except TypeError as e:
                logging.error(f"Error calculating distance: {e}. Skipping these pallets.")
                # Print out skipped pallet details
                logging.info(
                    f"Skipped Food Pallet - ID: {food_pallet.get('pallet_id', 'N/A')}, Location: {food_pallet.get('location_id', 'N/A')}, Coordinates: {food_pallet.get('coordinates', 'N/A')}")
                logging.info(
                    f"Skipped HPC Pallet - ID: {hpc_pallet.get('pallet_id', 'N/A')}, Location: {hpc_pallet.get('location_id', 'N/A')}, Coordinates: {hpc_pallet.get('coordinates', 'N/A')}")

    return violations


# Perform the proximity check across all racks
violations = proximity_check_all_racks()

# Display results
if violations:
    logging.info(f"Total violations found: {len(violations)}")
    for food_pallet_id, hpc_pallet_id, distance in violations:
        logging.warning(
            f"Violation: Food pallet {food_pallet_id} is {distance:.2f} units from HPC pallet {hpc_pallet_id}.")
else:
    logging.info("No proximity violations found.")
