__all__ = ["ProximityChecker"]

import requests
import math
import logging
import csv
from collections import defaultdict

# Setup logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ProximityChecker:
    BASE_URL = "https://digital-twin-dev.expangea.com/"
    HEADERS = {'X-API-KEY': '2c38e689-8bac-4ec6-9e0e-70e98222dc2d'}
    PRODUCT_GROUPS = ["FOODS", "HPC"]
    CSV_HEADERS = ["food_pallet_id", "hpc_pallet_id", "distance", "food_location_id", "hpc_location_id"]

    def __init__(self, racks_range=(21, 41), distance_threshold=200.0):
        self.racks_range = racks_range
        self.distance_threshold = distance_threshold
        self.violations = []

    def calculate_distance(self, coords_a, coords_b):
        """Calculate Euclidean distance between two sets of coordinates."""
        return math.sqrt(sum((coords_a[axis] - coords_b[axis]) ** 2 for axis in ['x', 'y', 'z']))

    def fetch_rack_data(self, rack_number):
        """Fetch data from a specific rack number using the API."""
        url = f"{self.BASE_URL}rack/5BTG/3/{rack_number}/"
        logging.info(f"Fetching data for rack {rack_number} from {url}")
        try:
            response = requests.post(url, headers=self.HEADERS)
            response.raise_for_status()
            logging.info(f"Successfully fetched data for rack {rack_number}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to fetch data for rack {rack_number}: {e}")
            return None

    def filter_pallets_by_group(self, rack_data, group_name):
        """Filter pallets by product group and return their coordinates."""
        pallets = []
        rack_locations = rack_data.get("data", {}).get("rack_locations", [])
        for location in rack_locations:
            for pallet in location.get("pallets", []):
                if pallet.get("inventory", {}).get("Product Group", "") == group_name:
                    pallets.append({
                        "pallet_id": pallet["pallet_id"],
                        "location_id": location["location_id"],
                        "coordinates": location.get("coordinates", {})
                    })
        logging.info(f"Filtered {len(pallets)} pallets for product group {group_name}")
        return pallets

    def proximity_check_all_racks(self):
        """Perform proximity check between FOODS and HPC pallets across all racks."""
        violations_dict = defaultdict(list)

        for rack_no in range(self.racks_range[0], self.racks_range[1]):
            rack_data = self.fetch_rack_data(rack_no)
            if not rack_data:
                logging.warning(f"No data found for rack {rack_no}. Skipping...")
                continue

            food_pallets = self.filter_pallets_by_group(rack_data, "FOODS")
            hpc_pallets = self.filter_pallets_by_group(rack_data, "HPC")

            for food_pallet in food_pallets:
                for hpc_pallet in hpc_pallets:
                    distance = self.calculate_distance(food_pallet["coordinates"], hpc_pallet["coordinates"])
                    logging.info(f"Distance between Food Pallet {food_pallet['pallet_id']} and HPC Pallet {hpc_pallet['pallet_id']}: {distance:.2f} units")
                    if distance < self.distance_threshold:
                        violations_dict[food_pallet["pallet_id"]].append({
                            "rack_no": rack_no,
                            "food_pallet_id": food_pallet["pallet_id"],
                            "hpc_pallet_id": hpc_pallet["pallet_id"],
                            "distance": distance,
                            "food_location_id": food_pallet["location_id"],
                            "hpc_location_id": hpc_pallet["location_id"]
                        })

        self.violations = [item for sublist in violations_dict.values() for item in sublist]
        return self.violations

    def get_total_violations(self):
        """Return the count of unique Food pallets involved in violations."""
        return len({violation["food_pallet_id"] for violation in self.violations})

    def save_violations_to_csv(self, filename="source/extensions/my_company.my_python_ui_extension/docs/violations.csv"):
        """Save the violations data to a CSV file."""
        with open(filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(self.CSV_HEADERS)

            for violation in self.violations:
                writer.writerow([
                    violation["food_pallet_id"],
                    violation["hpc_pallet_id"],
                    violation["distance"],
                    violation["food_location_id"],
                    violation["hpc_location_id"]
                ])

        logging.info(f"Saved {len(self.violations)} violations to {filename}")

