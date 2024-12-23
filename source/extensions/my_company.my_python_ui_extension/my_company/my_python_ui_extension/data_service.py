
# data_service.py
__all__ = ["DataService"]

from collections import defaultdict

import requests
import re
#import json
import carb
from requests import Response

import omni
import omni.usd

#from pxr import UsdGeom
from pxr import Usd, UsdGeom, Gf, Sdf, Kind, UsdShade

from typing import Optional, Tuple, Dict, Any
import csv
import logging
from typing import List, Dict
# from datetime import datetime, timedelta
# import time

# from paho.mqtt import client as mqtt_client
# from .custom_events import CustomEvents
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
class DataService:
    def __init__(self):
        stage = omni.usd.get_context().get_stage()
        self.api_base_url = "https://digital-twin.expangea.com/"
        self.headers = {
            'X-API-KEY': '2c38e689-8bac-4ec6-9e0e-70e98222dc2d'
        }
        self.stage = stage
        self.status_counters=0
        self.session = requests.Session()
        self.result_dict = {}
        self.pallet_usd_path = "D:/Toll Innovation/TC Level 3 Demo/_Update/Pallet_Asm_A04_120x122x75cm_PR_V_NVD_01.usd"
        self.critical_status_count = {
            "NE": 0,  # Near Expiry
            "DMG": 0,  # Damaged
            "EX": 0,  # Expired
            "QAF": 0  # Quality Assurance Frozen
        }
        self.critical_status_codes = ["NE", "DMG", "EX", "QAF"]
        # Stores critical pallets per rack number
        self.critical_pallets_by_rack = {}
        self.COLORS = {
            "DMG": "blue",
            "NE": "yellow",
            "QAF": "purple",
            "EX": "red"
        }
    @staticmethod
    def manage_extension():
        try:
            # Get the extension manager from the application
            extension_manager = omni.kit.app.get_app().get_extension_manager()

            # Enable the extension immediately
            extension_manager.set_extension_enabled_immediate("omni.example.ui_scene.widget_info", False)

            # Get the path of the extension by its module name
            widget_extension_path = extension_manager.get_extension_path_by_module("omni.example.ui_scene.widget_info")

            if widget_extension_path:
                carb.log_info(f"Extension path for 'omni.example.ui_scene.widget_info': {widget_extension_path}")
            else:
                carb.log_error(f"Could not retrieve path for 'omni.example.ui_scene.widget_info'")

            # Optionally check if the extension is enabled
            is_enabled = extension_manager.is_extension_enabled("omni.example.ui_scene.widget_info")
            if is_enabled:
                carb.log_warn("'omni.example.ui_scene.widget_info' is Enabled")
            else:
                carb.log_error("'omni.example.ui_scene.widget_info' is Disabled")

        except Exception as e:
            carb.log_error(f"An error occurred while managing the extension: {str(e)}")

    def construct_api_url(self, endpoint: str) -> str:
        return f"{self.api_base_url}{endpoint}"

    def handle_api_request(self, api_url: str) -> requests.Response | dict:
        try:
            response = requests.post(api_url, headers=self.headers)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            return response
        except requests.RequestException as e:
            print(f"Error occurred during API request: {e}")
            return {}  # Return an empty dict to indicate failure


    def fetch_stock_info(self, endpoint: str) -> dict:
        api_url = self.construct_api_url(endpoint)
        response = self.handle_api_request(api_url)
        return response.json().get("data", {})

    def fetch_coordinates(self, endpoint: str) -> tuple:
        api_url = self.construct_api_url(endpoint)
        response = self.handle_api_request(api_url)

        # Handle the case where the response is a dictionary (indicating failure)
        if isinstance(response, dict):
            print(f"Failed to fetch data from {api_url}.")
            return None

        # Parse the response as JSON
        try:
            data = response.json().get("data", {})
        except ValueError:
            print(f"Invalid JSON response from {api_url}.")
            return None

        # Determine which coordinates to use based on the endpoint
        if "rack_location" in endpoint:
            coordinates = data.get("rack_location", {}).get("coordinates", {})
            carb.log_warn(endpoint)
        else:
            coordinates = data.get("coordinates", {})

        # If coordinates are None or incomplete, return None or handle accordingly
        if not coordinates or coordinates.get('x') is None or coordinates.get('y') is None or coordinates.get('z') is None:
            print(f"No valid coordinates found at {endpoint}. Skipping.")
            return None

        # Return the coordinates (x, y, z) if they are valid
        return coordinates.get('x'), coordinates.get('y'), coordinates.get('z')

    def fetch_pallet_data(self, pallet_id):
        import requests
        try:
            api_url = f"{self.api_base_url}/pallet/{pallet_id}/"
            print(f"Fetching pallet data from: {api_url}")  # Debug statement
            response = requests.post(api_url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching pallet data for pallet {pallet_id}: {e}")
            return None

    def fetch_location_data(self, warehouse_code, location_id):
        import requests
        try:
            api_url = f"{self.api_base_url}/rack-location/{warehouse_code}/{location_id}/"
            print(f"Fetching location data from: {api_url}")  # Debug statement
            response = requests.post(api_url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching location data for location {location_id}: {e}")
            return None

    def fetch_rack_data(self, warehouse_code, floor_no, rack_number):
        import requests
        try:
            api_url = f"{self.api_base_url}/rack/{warehouse_code}/{floor_no}/{rack_number}/"
            print(f"Fetching rack data from: {api_url}")  # Debug statement
            response = requests.post(api_url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching rack data for rack {rack_number}: {e}")
            return None

    def spawn_pallet_at_location(self, rack_number, location, pallet_id):
        if location is None:
            print("Invalid location data.")
            return

        location_id = location.get("location_id", "unknown")
        rack_path = f"/All_Racks/Rack_{rack_number}"
        xform_path = f"{rack_path}/_{location_id}"

        coordinates = location.get("coordinates", {})
        if not all(k in coordinates for k in ("x", "y", "z")):
            print(f"Invalid coordinates for location {location_id}.")
            return

        xform = UsdGeom.Xform.Define(self.stage, xform_path)
        xform.AddTranslateOp().Set(Gf.Vec3d(coordinates["x"], coordinates["y"], coordinates["z"]))
        pallet_path = f"{xform_path}/{pallet_id}"

        if not self.stage.GetPrimAtPath(pallet_path):
            pallet_prim = self.stage.DefinePrim(pallet_path, "Xform")
            pallet_prim.GetReferences().AddReference(self.pallet_usd_path)

    def spawn_all_pallets(self):
        success = True
        warehouse_code = "5BTG"
        floor_no = "3"
        for rack_number in range(19, 41):
            print(f"Processing rack {rack_number}")  # Debug statement
            rack_data = self.fetch_rack_data(warehouse_code, floor_no, rack_number)
            if not rack_data:
                print(f"Failed to fetch data for rack {rack_number}")  # Debug statement
                success = False
                continue

            locations = rack_data.get("data", {}).get("rack_locations", [])
            for location in locations:
                pallets = location.get("pallets", [])
                for pallet in pallets:
                    self.spawn_pallet_at_location(rack_number, location, pallet.get("pallet_id", "unknown"))
        return success

    def fetch_status_code_data(self):
        critical_pallets_by_rack = {}  # Dictionary to store critical pallets by rack

        for rack_no in range(20, 41):  # Loop through rack numbers 9 to 40
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

                            # Check stock status code and assign material path accordingly
                            if stock_status_code == "DMG":
                                material_path = "/Environment/Looks/Glass_Color_Mat/Blue_Glass" #DMG
                            elif stock_status_code == "NE":
                                material_path = "/Environment/Looks/Glass_Color_Mat/Cyan_Glass" #NE
                            elif stock_status_code == "QAF":
                                material_path = "/Environment/Looks/Glass_Color_Mat/Purple_Glass" #QAF
                            else:
                                material_path = "/Environment/Looks/Glass_Color_Mat/Red_Glass" #EX

                            # Fetch coordinates for the pallet
                            endpoint = f"pallet/{pallet_id}/"
                            coordinates = self.fetch_coordinates(endpoint)

                            # Spawn the cube with the appropriate material based on stock status code
                            self.spawn_cube( prim_name=f"Critical_Items",group=f"Status_Code_{stock_status_code}",
                                             location_id=location_id, pallet_id=pallet_id, coordinates=coordinates,
                                            material_path=material_path)

                            # Set flag to True if a critical item is found
                            critical_found = True
                            self.critical_status_count[
                                stock_status_code] += 1  # Increment the individual critical status counter

                if not critical_found:
                    print(f"No critical status found in Rack {rack_no}.")

            # Flatten and save critical pallets by rack
        flat_data_for_csv = [
            {**{"rack_no": rack_no}, **pallet}
            for rack_no, pallets in critical_pallets_by_rack.items()
            for pallet in pallets
        ]
        save_to_csv(flat_data_for_csv, "critical_pallets_by_rack.csv")

        return self.critical_status_count, critical_pallets_by_rack

    # def display_critical_pallet(self, pallet_id, location_id, stock_status_code):
    #     """
    #     Displays critical pallet details including pallet ID, location, and stock status.
    #     """
    #     print(f"Critical Pallet Found: Pallet ID: {pallet_id}, Location ID: {location_id}, Status: {stock_status_code}")

    def display_total_critical_count(self):
        """
        Displays the total number of critical statuses found, broken down by individual status codes.
        """
        total_critical_count = sum(self.critical_status_count.values())
        carb.log_warn(f"\nTotal critical statuses found: {total_critical_count}")
        for status_code, count in self.critical_status_count.items():
            carb.log_warn(f"{status_code}: {count}")

    def check_expiry_date(self, date=None, other_date=None,rack_no=None,material_path=None):
        stage = omni.usd.get_context().get_stage()

        # Check which endpoint to use based on the presence of the dates
        if other_date:
            # If other_date is provided, use the new endpoint
            endpoint = f"expiry/5BTG/?from={date}&date={other_date}"
        else:
            # Default endpoint for the original date parameter
            endpoint = f"expiry/5BTG/?date={date}" if date else "expiry/5BTG/"

        api_url = self.construct_api_url(endpoint)
        data = self.handle_api_request(api_url)

        if data.status_code == 200:
            data = data.json()
            expired_items = data.get('expired', [])
            self.process_expired_items(expired_items, date, other_date, material_path=material_path)
        else:
            carb.log_error(f"Failed to retrieve data: {data.status_code} - {data.text}")

        pallet_ids = [item['pallet_id'] for item in self.result_dict.values()]
        pallet_id_string = ", ".join(pallet_ids)
        _show_notification(title="Expired item list", message=pallet_id_string)

    def process_expired_items(self, expired_items, date, other_date, material_path=None):
        processed_locations = set()
        for item in expired_items:
            pallet_id, location_id, rack_no, floor_no, balance_shelf_life_days, coordinates = self.extract_item_details(
                item)

            if location_id not in processed_locations:
                processed_locations.add(location_id)
                self.result_dict[location_id] = {
                    'pallet_id': pallet_id,
                    'rack_no': rack_no,
                    'floor_no': floor_no,
                    'balance_shelf_life_days': balance_shelf_life_days,
                    'coordinates': coordinates
                }

                carb.log_warn(f"Pallet ID: {pallet_id}, Location ID: {location_id}, Rack No: {rack_no}, "
                              f"Balance Shelf Life (days): {balance_shelf_life_days}, Floor No: {floor_no}, Coordinates: ({coordinates['x']}, {coordinates['y']}, {coordinates['z']})")

                self.spawn_cube(pallet_id, coordinates, date, other_date,material_path=material_path)
            else:
                carb.log_warn(f"Duplicate location_id {location_id} detected, skipping...")

    def extract_item_details(self, item):
        if not item:
            return None, None, None, None, None, {'x': 0.0, 'y': 0.0, 'z': 0.0}

        pallet_id = item.get('pallet_id')
        if pallet_id and isinstance(pallet_id, str):
            pallet_id = re.sub(r'^\d+', '', pallet_id)

        location_id = item.get('location_id')
        rack_no = item.get('rack_no')
        floor_no = item.get('floor_no')
        balance_shelf_life_days = item['inventory'].get('Balance Shelf Life to Expiry (days)')

        coordinates = item.get('coordinates', {})
        x = coordinates.get('x', 0.0)
        y = coordinates.get('y', 0.0)
        z = coordinates.get('z', 0.0)

        return pallet_id, location_id, rack_no, floor_no, balance_shelf_life_days, {'x': x, 'y': y, 'z': z}

    def spawn_cube(self, prim_name, pallet_id, coordinates, date=None, other_date=None,
                   material_path=None, location_id=None, group=None):
        stage = omni.usd.get_context().get_stage()

        pallet_id= pallet_id.replace(".","_")
        if pallet_id.startswith("0"):
            pallet_id = pallet_id.lstrip("0")

        # Construct the log message by combining the arguments into a single string
        # log_message = f"Prim Name: {prim_name},location ID:{location_id}, Pallet ID: {pallet_id}, Coordinates: {coordinates}"

        # Log the warning message with the concatenated string
        # carb.log_warn(log_message)

        # Check if the stage is properly initialized
        if stage is None:
            carb.log_error("Stage is not initialized.")
            return

        # Check if coordinates is None before trying to access its elements
        if coordinates is None:
            carb.log_error(f"Coordinates are None for Pallet ID {pallet_id}. Skipping.")
            return

            # Construct the prim path for the parent Xform (using the prim_name parameter)
        parent_xform_path_str = f"/{prim_name}"
        parent_xform_path = Sdf.Path(parent_xform_path_str)

        # Ensure the parent Xform exists, or create it
        if not stage.GetPrimAtPath(parent_xform_path).IsValid():
            # Create the parent Xform
            parent_xform = UsdGeom.Xform.Define(stage, parent_xform_path)
            parent_xform.AddTranslateOp().Set(Gf.Vec3f(0, 0, 0))  # Default translation for the parent Xform
            carb.log_warn(f"Created parent Xform: {parent_xform_path_str}")

        # Construct the prim path for the cube under the parent Xform, named after the pallet_id
        pallet_prim_path_str = f"{parent_xform_path_str}/{group}/_{location_id}/{pallet_id}"
        pallet_prim_path = Sdf.Path(pallet_prim_path_str)

        # Check if the pallet prim already exists
        if not stage.GetPrimAtPath(pallet_prim_path).IsValid():
            # Create the Xform for the pallet cube under the parent Xform
            pallet_xform = UsdGeom.Xform.Define(stage, pallet_prim_path)
            pallet_xform.AddTranslateOp().Set(Gf.Vec3f(coordinates[0], coordinates[1], coordinates[2]))

            # Create the Cube prim under the pallet Xform
            cube_prim_path_str = f"{pallet_prim_path_str}/Cube"
            cube_prim = UsdGeom.Cube.Define(stage, Sdf.Path(cube_prim_path_str))
            cube_prim.GetSizeAttr().Set(120.0)
            cube_prim.AddTranslateOp().Set(Gf.Vec3f(0, 0, 60))

            # Mark the Xform as an assembly
            Usd.ModelAPI(pallet_xform).SetKind(Kind.Tokens.assembly)

            # Apply material to the cube if provided
            if material_path:
                _apply_material_to_prim(stage, prim_path=cube_prim_path_str, material_path=material_path)

            # Log the creation of the cube
            carb.log_warn(f"Spawned cube for Pallet Rack{group} under {pallet_id} under {prim_name} at coordinates {coordinates}")
        else:
            carb.log_warn(f"Pallet {pallet_id} already exists under {prim_name}.")



    def show_pallet_info(self, pallet_id):
        endpoint = f"pallet/{pallet_id}/"
        print(f"Fetching stock info from endpoint: {endpoint}")

        _find_prim_then_select(pallet_id)

        stock_info = self.fetch_stock_info(endpoint)

        if stock_info:
            limited_items = list(stock_info.items())[:11]
            info_text = "\n".join([f"{key}: {value}" for key, value in limited_items])

            # print(info_text)
            # self.info_label.text = info_text

            location_id = stock_info.get("rack_location", {}).get("location_id")
            location_endpoint = f"rack-location/5BTG/{location_id}/"
            print(f"Fetching coordinates from endpoint: {location_endpoint}")

            coordinates = self.fetch_coordinates(location_endpoint)
            if coordinates:
                x, y, z = coordinates
                print(x, y, z)
                _move_camera(x, y, z)
            else:
                carb.log_warn("Failed to fetch valid coordinates.")
        else:
            carb.log_warn("Failed to fetch stock info.")

    def show_location_info(self, location_id):
        endpoint = f"rack-location/5BTG/{location_id}/"
        # _find_prim_then_select(f"_{location_id}")
        location_info = self.fetch_stock_info(endpoint)
        if location_info:
            # location_endpoint=f"rack-location/{location_id}/"
            x, y, z = self.fetch_coordinates(endpoint)
            if x is not None and y is not None and z is not None:
                _move_camera(x, y, z)
            else:
                carb.log_warn("Failed to fetch stock info")

    def calculate_storage_utilization(self):
        """
        Calculate storage utilization across racks, counting slots with a pallet ID as used and without as free.

        Returns:
            used_percentage (float): Percentage of storage used.
            free_percentage (float): Percentage of storage free.
        """
        total_slots = 0
        used_slots = 0

        # Loop through racks 19 to 40 to count used and free storage slots
        for rack_num in range(19, 41):
            rack_data = self.fetch_rack_data(rack_num)
            if not rack_data:
                continue  # Skip if no data is found for the rack

            # Extract rack locations
            rack_locations = rack_data.get("data", {}).get("rack_locations", [])
            for location in rack_locations:
                total_slots += 1  # Every location is considered a storage slot

                # Check if there’s a pallet ID in the location’s pallets
                pallets = location.get("pallets", [])
                if any(pallet.get("pallet_id") for pallet in pallets):
                    used_slots += 1  # Increment used slots if a pallet ID is found

        # Calculate used and free storage percentages
        used_percentage = (used_slots / total_slots) * 100 if total_slots else 0
        free_percentage = 100 - used_percentage

        return round(used_percentage), round(free_percentage)

    def calculate_staging_space_utilization(self):
        stage_path = "/World/Non_Rack_Areas"
        """Calculate used and free space percentages in combined staging areas."""
        stage = omni.usd.get_context().get_stage()
        if not stage:
            print("No valid stage loaded.")
            return

        # Staging areas to calculate
        staging_areas = ["Area1", "Area2", "Area3"]
        total_items = 0
        hidden_items = 0

        for area in staging_areas:
            area_path = f"{stage_path}/{area}"
            area_prim = stage.GetPrimAtPath(area_path)
            if not area_prim.IsValid():
                print(f"Staging area '{area}' not found.")
                continue

            # Traverse children under the area
            for child in area_prim.GetChildren():
                total_items += 1
                visibility_attr = UsdGeom.Imageable(child).GetVisibilityAttr()
                if visibility_attr.Get() == UsdGeom.Tokens.invisible:
                    hidden_items += 1

        # Calculate percentages for the combined staging area
        used_percentage = ((total_items - hidden_items) / total_items) * 100 if total_items > 0 else 0
        free_percentage = 100 - used_percentage

        # Return the combined space utilization
        space_utilization = {
            "Combined Staging Area": {
                "Total Items": total_items,
                "Used Space %": round(used_percentage, 2),
                "Free Space %": round(free_percentage, 2)
            }
        }

        return space_utilization
    def update_warehouse(self):
        pass

    def close(self):
        self.session.close()
        carb.log_info("API connection closed")

def _apply_material_to_prim(stage, prim_path, material_path):
    """Applies the specified material to the given prim."""
    material_prim = stage.GetPrimAtPath(material_path)
    if not material_prim:
        carb.log_error(f"Material not found at path: {material_path}")
        return

    # Get the prim at the ref_prim_path and apply the material binding
    prim = stage.GetPrimAtPath(prim_path)
    if not prim:
        carb.log_error(f"Prim not found at path: {prim_path}")
        return

    # Bind the material to the prim using UsdShade.MaterialBindingAPI
    material_binding_api = UsdShade.MaterialBindingAPI(prim)
    material_binding_api.Bind(UsdShade.Material(stage.GetPrimAtPath(material_path)))
    carb.log_info(f"Material {material_path} applied to {prim_path}")


def _move_camera(x: float, y: float, z: float):
    xform_path = "/Environment/Camera"
    view_camera_path = "/Environment/Camera/Camera_001/Camera_001"
    new_xyz_location = Gf.Vec3d(x , y + -200, z + 75)
    new_rotation = Gf.Vec3f(80, 0.0, 0.0)
    focal_length = 20

    _move_xform_and_set_view(xform_path, view_camera_path, new_xyz_location, new_rotation, focal_length=focal_length)
    carb.log_warn(f"Moved camera to location: {new_xyz_location}, with rotation: {new_rotation}, focal length: {focal_length}")


def _move_xform_and_set_view(xform_path: str, view_camera_path: str, new_location: Optional[Gf.Vec3f] = None,
                            new_rotation: Optional[Gf.Vec3f] = None, focal_length: float = 20.0):
    xform_api = _get_xform_by_path(xform_path)
    if not xform_api:
        carb.log_warn(f"Camera xform at '{xform_path}' not found or invalid!")
        return

    if new_location is not None:
        xform_api.SetTranslate(new_location)
    if new_rotation is not None:
        xform_api.SetRotate(new_rotation)
    stage = omni.usd.get_context().get_stage()
    view_camera_prim = stage.GetPrimAtPath(view_camera_path)
    if not view_camera_prim:
        carb.log_warn(f"View camera at '{view_camera_path}' not found!")
        return

    if not view_camera_prim.IsA(UsdGeom.Camera):
        carb.log_warn(f"Prim at '{view_camera_path}' is not a camera!")
        return

    view_camera = UsdGeom.Camera(view_camera_prim)
    view_camera.GetFocalLengthAttr().Set(focal_length)

    viewport_api = omni.kit.viewport.utility.get_active_viewport()
    viewport_api.camera_path = view_camera_prim.GetPath().pathString
    carb.log_warn(
        f"Moved xform of '{xform_api.GetPrim().GetName()}' and viewport is now viewing from '{view_camera_prim.GetName()}' with focal length {focal_length}")


def _get_xform_by_path(prim_path: str) -> Optional[UsdGeom.XformCommonAPI]:
    stage = omni.usd.get_context().get_stage()
    prim = stage.GetPrimAtPath(prim_path)
    if prim.IsValid() and prim.IsA(UsdGeom.Xform):
        return UsdGeom.XformCommonAPI(prim)
    return None


def _traverse(prim, name):
    if prim.GetName() == name:
        return prim
    for child in prim.GetAllChildren():
        result = _traverse(child, name)
        if result:
            return result
    return None


def _find_prim_by_name(stage, name):
    root_prim = stage.GetPseudoRoot()
    return _traverse(root_prim, name)


def _find_prim_then_select(name: str):
    # Get the stage from the Omniverse context
    stage = omni.usd.get_context().get_stage()

    # Find the prim by name
    prim = _find_prim_by_name(stage, name)
    if not prim:
        carb.log_error(f"Prim with name '{name}' not found!")
        return

    # Get the selection context
    selection = omni.usd.get_context().get_selection()

    # Select the item
    selection.clear_selected_prim_paths()
    selection.set_selected_prim_paths([prim.GetPath().pathString], True)

    carb.log_warn(f"Selected item with name '{name}' at path: '{prim.GetPath()}'")


def _load_usd_file(file_path, ref_prim_path):
    context = omni.usd.get_context()
    if not context:
        print("Failed to get USD context.")
        return

    stage = context.get_stage()
    if not stage:
        carb.log_error("Failed to get the USD stage. Ensure a stage is open or created.")
        return

    try:
        # Set the stage up axis and orientation
        UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
        UsdGeom.SetStageMetersPerUnit(stage, 1.0)  # Optional: set scale to meters

        # Ensure the root is an Xform
        stage.DefinePrim(ref_prim_path, 'Xform')
        ref_prim = stage.GetPrimAtPath(ref_prim_path)
        if not ref_prim.IsValid():
            carb.log_error(f"Failed to define or get the reference prim at {ref_prim_path}.")
            return

        ref_prim.GetReferences().AddReference(file_path)
        carb.log_info(f"Successfully referenced USD file at {file_path}")

        # Additional handling might be needed to ensure X is front orientation
        """
            Adjusts the orientation of the root prim to ensure Z is up and X is front in the scene.
            """
        xform = UsdGeom.Xformable(ref_prim)

        # Apply rotation to align orientations properly if needed.
        # Assuming that Z-up and X-front might require rotations.
        # For some scenes, importing USD with correct orientation might be enough.
        rotation = (0, 0, 0)  # This depends on how the USD is set up. Adjust as needed.
        xform.AddRotateXYZOp().Set(rotation)
    except Exception as e:
        carb.log_error(f"An error occurred while referencing the USD file: {str(e)}")

def _apply_material_to_prim(stage, prim_path, material_path):
    """Applies the specified material to the given prim."""
    material_prim = stage.GetPrimAtPath(material_path)
    if not material_prim:
        carb.log_error(f"Material not found at path: {material_path}")
        return

    # Get the prim at the ref_prim_path and apply the material binding
    prim = stage.GetPrimAtPath(prim_path)
    if not prim:
        carb.log_error(f"Prim not found at path: {prim_path}")
        return

    # Bind the material to the prim using UsdShade.MaterialBindingAPI
    material_binding_api = UsdShade.MaterialBindingAPI(prim)
    material_binding_api.Bind(UsdShade.Material(stage.GetPrimAtPath(material_path)))
    carb.log_info(f"Material {material_path} applied to {prim_path}")


def _show_notification(title: str, message: str, status: str):
    # Map the status to the appropriate NotificationStatus
    status_mapping = {
        "INFO": omni.kit.notification_manager.NotificationStatus.INFO,
        "WARNING": omni.kit.notification_manager.NotificationStatus.WARNING,
        # "ERROR": omni.kit.notification_manager.NotificationStatus.ERROR,
    }

    # Default to INFO if the status isn't recognized
    notification_status = status_mapping.get(status.upper(), omni.kit.notification_manager.NotificationStatus.INFO)

    ok_button = omni.kit.notification_manager.NotificationButtonInfo("OK", on_complete=None)
    omni.kit.notification_manager.post_notification(
        text=f"{title}: {message}",
        hide_after_timeout=True,
        duration=5,
        status=notification_status,
        button_infos=[ok_button]
    )


def log_status(pallet_id, stock_status_code, level):
    """
    Logs the stock status based on severity using carb logging functions.
    """
    if level == "CRITICAL":
        carb.log_error(f"Pallet ID {pallet_id} has stock status {stock_status_code}.")
    elif level == "WARNING":
        carb.log_warn(f"Pallet ID {pallet_id} has stock status {stock_status_code}.")


def save_to_csv(data: List[Dict], file_name: str, group_by_key: str = None):
    """
    Save a list of dictionaries to a CSV file, with optional support for grouping.

    Args:
        data (List[Dict]): A list of dictionaries, each containing data for one row.
        file_name (str): The name of the output CSV file.
        group_by_key (str, optional): Key to group data by, leaving subsequent rows blank for that group.
    """
    if not data:
        logging.error("No data provided to save to CSV.")
        return

    # Use the keys of the first dictionary as the CSV headers
    headers = data[0].keys()

    # If a grouping key is provided, organize data by that key
    grouped_data = defaultdict(list)
    if group_by_key:
        for item in data:
            grouped_data[item[group_by_key]].append(item)
    else:
        grouped_data[None] = data

    try:
        with open(file_name, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()

            # Write rows, handling grouping if needed
            for group_key, items in grouped_data.items():
                first = True
                for item in items:
                    row = {**item}  # Copy item data to modify for grouping

                    # Blank out grouped columns if not the first row in the group
                    if not first and group_by_key:
                        row[group_by_key] = ""
                    writer.writerow(row)
                    first = False

        logging.info(f"Data successfully saved to {file_name}")

    except Exception as e:
        logging.error(f"Failed to save data to CSV: {e}")


def _isolate_selected_parent(xform_parent_name):
    """Handle isolation of the selected parent by name."""
    logging.info(f"Isolation mode activated for: {xform_parent_name}")

    # Get the USD stage
    stage = omni.usd.get_context().get_stage()

    if not xform_parent_name or xform_parent_name == "Show All":
        logging.info("No valid selection or 'Show All' selected. Resetting visibility for all parents.")
        # Reset visibility to inherited for all parents
        for prim in stage.Traverse():
            if prim.IsA(UsdGeom.Imageable):
                geom_prim = UsdGeom.Imageable(prim)
                geom_prim.GetVisibilityAttr().Set(UsdGeom.Tokens.inherited)
        return

    # Find the prim to isolate using the _traverse function
    root_prim = stage.GetPseudoRoot()
    target_prim = _traverse(root_prim, xform_parent_name)

    if not target_prim:
        logging.warn(f"Prim '{xform_parent_name}' not found!")
        return

    # Isolate the selected parent and hide all others
    for prim in stage.Traverse():
        if prim.IsA(UsdGeom.Imageable):
            geom_prim = UsdGeom.Imageable(prim)
            # Set visibility based on the selected parent
            visibility = UsdGeom.Tokens.inherited if prim == target_prim else UsdGeom.Tokens.invisible
            geom_prim.GetVisibilityAttr().Set(visibility)

    logging.info(f"Isolation applied for: {xform_parent_name}")



