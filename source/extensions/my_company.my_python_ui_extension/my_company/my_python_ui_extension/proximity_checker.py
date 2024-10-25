__all__ = ["ProximityChecker"]

import requests
import math
import logging

# Setup logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class ProximityChecker:
    BASE_URL = "https://digital-twin.expangea.com/"
    HEADERS = {
        'X-API-KEY': '2c38e689-8bac-4ec6-9e0e-70e98222dc2d'  # Your API key
    }

    def __init__(self, racks_range=(21, 40), distance_threshold=200.0):
        self.racks_range = racks_range
        self.distance_threshold = distance_threshold
        self.food_pallets = []
        self.hpc_pallets = []
        self.violations = []

    def calculate_distance(self, coords_a, coords_b):
        """Calculate Euclidean distance between two sets of coordinates."""
        return math.sqrt((coords_a['x'] - coords_b['x']) ** 2 +
                         (coords_a['y'] - coords_b['y']) ** 2 +
                         (coords_a['z'] - coords_b['z']) ** 2)

    def fetch_rack_data(self, rack_number):
        """Fetch data from a specific rack number using the API."""
        url = f"{self.BASE_URL}rack/5BTG/3/{rack_number}/"
        logging.info(f"Fetching data for rack {rack_number} from {url}")

        try:
            response = requests.post(url, headers=self.HEADERS)
            response.raise_for_status()  # Raise error if request fails
            logging.info(f"Successfully fetched data for rack {rack_number}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to fetch data for rack {rack_number}: {e}")
            return None

    def filter_pallets_by_group(self, rack_data, group_name):
        """Filter pallets by product group (e.g., FOODS, HPC) and return their coordinates."""
        pallets = []
        try:
            rack_locations = rack_data.get("data", {}).get("rack_locations", [])
            for location in rack_locations:
                for pallet in location.get("pallets", []):
                    product_group = pallet.get("inventory", {}).get("Product Group", "")
                    if product_group == group_name:
                        coordinates = location.get("coordinates", {})
                        pallets.append({
                            "pallet_id": pallet["pallet_id"],
                            "location_id": location["location_id"],
                            "coordinates": coordinates
                        })
            logging.info(f"Filtered {len(pallets)} pallets for product group {group_name}")
        except TypeError as e:
            logging.error(f"Error processing rack data: {e}. Skipping this entry.")
        return pallets

    def proximity_check_all_racks(self):
        """Perform proximity check between FOODS and HPC pallets across all racks."""
        self.food_pallets = []
        self.hpc_pallets = []
        self.violations = []

        # Loop through all racks in the given range
        for rack_no in range(self.racks_range[0], self.racks_range[1] + 1):
            rack_data = self.fetch_rack_data(rack_no)
            if not rack_data:
                logging.warning(f"No data found for rack {rack_no}. Skipping...")
                continue

            # Append "FOODS" and "HPC" pallets to respective lists
            self.food_pallets += self.filter_pallets_by_group(rack_data, "FOODS")
            self.hpc_pallets += self.filter_pallets_by_group(rack_data, "HPC")

        # logging.info(f"Total food pallets found: {len(self.food_pallets)}")
        # logging.info(f"Total HPC pallets found: {len(self.hpc_pallets)}")

        # Check proximity between each food pallet and each HPC pallet
        for food_pallet in self.food_pallets:
            for hpc_pallet in self.hpc_pallets:
                try:
                    distance = round(self.calculate_distance(food_pallet["coordinates"], hpc_pallet["coordinates"]), 2)
                    logging.info(
                        f"Checking distance between Food Pallet {food_pallet['pallet_id']} and HPC Pallet {hpc_pallet['pallet_id']}: {distance:.2f} units")
                    if distance < self.distance_threshold:  # Check if the distance is less than the threshold
                        self.violations.append({
                            "food_pallet_id": food_pallet["pallet_id"],
                            "hpc_pallet_id": hpc_pallet["pallet_id"],
                            "distance": distance,
                            "food_location_id": food_pallet["location_id"],
                            "hpc_location_id": hpc_pallet["location_id"]
                        })
                except TypeError as e:
                    logging.error(f"Error calculating distance: {e}. Skipping these pallets.")
                    # Log skipped pallet details
                    logging.error(
                        f"Skipped Food Pallet - ID: {food_pallet.get('pallet_id', 'N/A')}, Location: {food_pallet.get('location_id', 'N/A')}, Coordinates: {food_pallet.get('coordinates', 'N/A')}")
                    logging.error(
                        f"Skipped HPC Pallet - ID: {hpc_pallet.get('pallet_id', 'N/A')}, Location: {hpc_pallet.get('location_id', 'N/A')}, Coordinates: {hpc_pallet.get('coordinates', 'N/A')}")

        return self.violations

    def get_total_violations(self):
        """Return the total number of violations found."""
        return len(self.violations)
