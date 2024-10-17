import requests
class DataService:
    def __init__(self):
        self.base_url = "https://digital-twin.expangea.com/"
        self.headers = {
            'X-API-KEY': '2c38e689-8bac-4ec6-9e0e-70e98222dc2d'
        }
        # Individual counters for each critical status code

    class RackService:
        def __init__(self, base_url, headers, critical_status_codes):
            self.base_url = base_url
            self.headers = headers
            self.critical_status_codes = critical_status_codes
            self.critical_status_count = {
                "NE": 0,  # Near Expiry
                "DMG": 0,  # Damaged
                "EX": 0,  # Expired
                "QAF": 0  # Quality Assurance Frozen
            }

        def fetch_rack_data(self, rack_no):
            """
            Fetches data for a specific rack number.
            """
            url = f"{self.base_url}rack/5BTG/3/{rack_no}/"
            try:
                response = requests.post(url, headers=self.headers)
                if response.status_code == 200:
                    return response.json()
                else:
                    return None
            except Exception as e:
                print(f"Error fetching data for Rack {rack_no}: {e}")
                return None

        def process_racks(self, data_service):
            critical_pallets_by_rack = {}  # Dictionary to store critical pallets by rack

            for rack_no in range(9, 41):  # Loop through rack numbers 9 to 40
                rack_data = self.fetch_rack_data(rack_no)

                if rack_data and "data" in rack_data:
                    print(f"Processing Rack {rack_no}...")

                    rack_locations = rack_data["data"].get("rack_locations", [])
                    if not rack_locations:
                        print(f"No data found for Rack {rack_no}. Moving to next.")
                        continue  # No data, move to the next rack

                    critical_found = False  # Flag to track if any critical items are found

                    for location in rack_locations:
                        location_id = location.get("location_id")
                        pallets = location.get("pallets", [])

                        for pallet in pallets:
                            pallet_id = pallet.get("pallet_id")
                            inventory = pallet.get("inventory", {})
                            stock_status_code = inventory.get("Stock Status Code", "N/A")

                            if stock_status_code in self.critical_status_codes:
                                # Add the critical pallet to the corresponding rack in critical_pallets_by_rack
                                if rack_no not in critical_pallets_by_rack:
                                    critical_pallets_by_rack[rack_no] = []

                                critical_pallets_by_rack[rack_no].append({
                                    "pallet_id": pallet_id,
                                    "location_id": location_id,
                                    "stock_status_code": stock_status_code
                                })

                                self.display_critical_pallet(pallet_id, location_id, stock_status_code)
                                critical_found = True  # Set flag to True if a critical item is found
                                self.critical_status_count[
                                    stock_status_code] += 1  # Increment the individual critical status counter

                    if not critical_found:
                        print(f"No critical status found in Rack {rack_no}.")
            self.display_total_critical_count()

        def display_critical_pallet(self, pallet_id, location_id, stock_status_code):
            """
            Displays critical pallet details including pallet ID, location, and stock status.
            """
            print(f"Critical Pallet Found: Pallet ID: {pallet_id}, Location ID: {location_id}, Status: {stock_status_code}")

        def display_total_critical_count(self):
            """
            Displays the total number of critical statuses found, broken down by individual status codes.
            """
            total_critical_count = sum(self.critical_status_count.values())
            print(f"\nTotal critical statuses found: {total_critical_count}")
            for status_code, count in self.critical_status_count.items():
                print(f"{status_code}: {count}")

# Instantiate the data service and the rack service
data_service = DataService()
rack_service = data_service.RackService(data_service.base_url, data_service.headers, ["NE", "DMG", "EX", "QAF"])

# Process racks using the RackService subclass
rack_service.process_racks(data_service)
