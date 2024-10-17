# data_service.py
__all__ = ["DataService"]

import requests
import re
import json
import carb
from requests import Response

import omni
import omni.usd

from pxr import UsdGeom
from pxr import Usd, UsdGeom, Gf, Sdf, Kind, UsdShade
from typing import Optional, Tuple, Dict, Any

from datetime import datetime, timedelta
import time
stage = omni.usd.get_context().get_stage()

# from paho.mqtt import client as mqtt_client
# from .custom_events import CustomEvents
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
class DataService:
    def __init__(self):
        self.base_url = "https://digital-twin.expangea.com/"
        self.headers = {
            'X-API-KEY': '2c38e689-8bac-4ec6-9e0e-70e98222dc2d'
        }
        self.stage = stage
        self.status_counters=0
        self.session = requests.Session()
        self.result_dict = {}

        self.critical_status_count = {
            "NE": 0,  # Near Expiry
            "DMG": 0,  # Damaged
            "EX": 0,  # Expired
            "QAF": 0  # Quality Assurance Frozen
        }
        self.critical_status_codes = ["NE", "DMG", "EX", "QAF"]
        # Stores critical pallets per rack number
        self.critical_pallets_by_rack = {}
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
        return f"{self.base_url}{endpoint}"

    def handle_api_request(self, api_url: str) -> Response | dict[Any, Any]:
        try:
            response = requests.post(api_url, headers=self.headers)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            return response
        except requests.RequestException as e:

            return {}


    def fetch_stock_info(self, endpoint: str) -> dict:
        api_url = self.construct_api_url(endpoint)
        response = self.handle_api_request(api_url)
        return response.json().get("data", {})
        # api_url = self.construct_api_url(endpoint)
        # stock_info = self.handle_api_request(api_url)
        # CustomEvents.emit_stock_info(stock_info)  # Emit the custom event with stock info
        # return stock_info

    def fetch_coordinates(self, endpoint: str) -> tuple:
        api_url = self.construct_api_url(endpoint)
        response = self.handle_api_request(api_url)
        data = response.json().get("data", {})
        coordinates = data.get("rack_location", {}).get("coordinates", {})
        # print(coordinates)
        return coordinates.get('x'), coordinates.get('y'), coordinates.get('z')

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

    def fetch_status_code_data(self):
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
                            material_path = "/Environment/Looks/Light_1900K_Yellow"
                            endpoint = f'rack-location/5BTG/{location_id}/'
                            coordinates = self.fetch_coordinates(endpoint)

                            # self.spawn_cube(stage, pallet_id, coordinates=coordinates, material_path=material_path)
                            self.display_critical_pallet(pallet_id, location_id, stock_status_code)
                            print(coordinates)
                            critical_found = True  # Set flag to True if a critical item is found
                            self.critical_status_count[
                                stock_status_code] += 1  # Increment the individual critical status counter

                if not critical_found:
                    print(f"No critical status found in Rack {rack_no}.")

        self.display_total_critical_count()
        return self.critical_status_count, critical_pallets_by_rack

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
            self.process_expired_items(expired_items, date, other_date, stage, material_path=material_path)
        else:
            carb.log_error(f"Failed to retrieve data: {data.status_code} - {data.text}")

        pallet_ids = [item['pallet_id'] for item in self.result_dict.values()]
        pallet_id_string = ", ".join(pallet_ids)
        _show_notification(title="Expired item list", message=pallet_id_string)

    def process_expired_items(self, expired_items, date, other_date, stage, material_path=None):
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

                self.spawn_cube(stage, pallet_id, coordinates, date, other_date,material_path=material_path)
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

    def spawn_cube(self, stage, pallet_id, coordinates, date=None, other_date=None, material_path=None):
        # If date is provided, use it to format the path; otherwise, default to 'no_date'.
        formatted_date = date.replace('-', '_') if date else "no_date"
        other_formatted_date = other_date.replace('-', '_') if other_date else "date"
        xform_prim_path = f"/pallet_expired_{formatted_date}_to_{other_formatted_date}/{pallet_id}"

        if not stage.GetPrimAtPath(xform_prim_path).IsValid():
            xform = UsdGeom.Xform.Define(stage, xform_prim_path)
            xform.AddTranslateOp().Set(Gf.Vec3f(coordinates['x'], coordinates['y'], coordinates['z']))

            cube_prim_path = f"{xform_prim_path}/Cube"
            cube_prim = UsdGeom.Cube.Define(stage, cube_prim_path)
            cube_prim.GetSizeAttr().Set(120.0)
            cube_prim.AddTranslateOp().Set(Gf.Vec3f(0, 0, 60))
            Usd.ModelAPI(xform).SetKind(Kind.Tokens.assembly)

            _apply_material_to_prim(stage, prim_path=cube_prim_path, material_path=material_path)

            carb.log_warn(
                f"Spawned cube for Pallet {pallet_id} at coordinates ({coordinates['x']}, {coordinates['y']}, {coordinates['z']})")

        else:
            carb.log_warn(f"Xform already exists for {xform_prim_path}")
        # Notification showing the expired item list
        # pallet_ids = [item['pallet_id'] for item in self.result_dict.values()]
        # pallet_id_string = ", ".join(pallet_ids)
        # _show_notification(title="Expired item list", message=pallet_id_string)

    def check_expired(self):
        pass
    #     stage = omni.usd.get_context().get_stage()
    #
    #     # Set to keep track of processed location IDs
    #     processed_locations = set()
    #     endpoint = "expiry/5BTG/"
    #     api_url = self.construct_api_url(endpoint)
    #     data = self.handle_api_request(api_url)
    #
    #     # Check if the request was successful
    #     if data.status_code == 200:
    #         data = data.json()
    #         expired_items = data.get('expired', [])
    #
    #         for item in expired_items:
    #             pallet_id = item.get('pallet_id')
    #             if pallet_id and isinstance(pallet_id, str):
    #                 pallet_id = re.sub(r'^\d+', '', pallet_id)
    #
    #             location_id = item.get('location_id')
    #             rack_no = item.get('rack_no')
    #             floor_no = item.get('floor_no')
    #             ref_prim_path = f"/expired_pallet/{pallet_id}"
    #             filepath = "D:/Toll Innovation/TC Level 3 Demo/_Update/cube.usd"
    #             balance_shelf_life_days = item['inventory'].get('Balance Shelf Life to Expiry (days)')
    #
    #             # Extracting the coordinates from the data, using default values if None
    #             coordinates = item.get('coordinates', {})
    #             x = coordinates.get('x', 0.0) if coordinates is not None else 0.0
    #             y = coordinates.get('y', 0.0) if coordinates is not None else 0.0
    #             z = coordinates.get('z', 0.0) if coordinates is not None else 0.0
    #
    #             # Check if location_id has already been processed
    #             if location_id not in processed_locations:
    #                 # Add the location_id to the set
    #                 processed_locations.add(location_id)
    #                 self.result_dict[location_id] = {
    #                     'pallet_id': pallet_id,
    #                     'rack_no': rack_no,
    #                     'floor_no': floor_no,
    #                     'balance_shelf_life_days': balance_shelf_life_days,
    #                     'coordinates': {'x': x, 'y': y, 'z': z}
    #                 }
    #
    #                 # Log the information, including coordinates
    #                 carb.log_warn(f"Pallet ID: {pallet_id}, Location ID: {location_id}, Rack No: {rack_no}, "
    #                               f"Balance Shelf Life (days): {balance_shelf_life_days}, Floor No: {floor_no}, Coordinates: ({x}, {y}, {z})")
    #
    #
    #                 # Spawn an Xform and then the cube at the given coordinates
    #                 if not stage.GetPrimAtPath(ref_prim_path).IsValid():
    #                     # Create an Xform for the pallet at the location
    #                     xform = UsdGeom.Xform.Define(stage, ref_prim_path)
    #                     xform.AddTranslateOp().Set(Gf.Vec3f(x, y, z))
    #
    #                     # _load_usd_file(file_path=filepath, ref_prim_path=ref_prim_path)
    #
    #                     # Spawn a cube as a child of the Xform
    #                     cube_prim_path = f"{ref_prim_path}/Cube"
    #                     cube_prim = UsdGeom.Cube.Define(stage, cube_prim_path)
    #                     cube_prim.GetSizeAttr().Set(120.0)  # Set the cube size
    #                     cube_prim.AddTranslateOp().Set(
    #                         Gf.Vec3f(0, 0, 60))  # Adjust Z to position the cube above the ground
    #
    #                     material_path = "/Environment/Looks/Light_1900K_Red"
    #
    #                     _apply_material_to_prim(stage, prim_path=cube_prim_path, material_path=material_path)
    #
    #                     Usd.ModelAPI(xform).SetKind(Kind.Tokens.assembly)
    #                     carb.log_warn(f"Spawned cube for Pallet {pallet_id} at coordinates ({x}, {y}, {z})")
    #                 else:
    #                     carb.log_warn(f"Xform already exists for {ref_prim_path}")
    #             else:
    #                 carb.log_warn(f"Duplicate location_id {location_id} detected, skipping...")
    #     else:
    #         carb.log_error(f"Failed to retrieve data: {data.status_code} - {data.text}")
    #
    #     # Notification showing the expired item list
    #     pallet_ids = [item['pallet_id'] for item in self.result_dict.values()]
    #     pallet_id_string = ", ".join(pallet_ids)
    #     _show_notification(title="Expired item list", message=pallet_id_string)

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

            location_id = stock_info.get("rack_location").get("location_id")
            location_endpoint = f"rack-location/{location_id}/"
            print(f"Fetching coordinates from endpoint: {location_endpoint}")

            x, y, z = self.fetch_coordinates(endpoint)
            print(x, y, z)
            if x is not None and y is not None and z is not None:
                _move_camera(x, y, z)
            else:
                carb.log_warn("Failed to fetch stock info")

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

def _fetch_and_move_camera(self):
    """Fetch stock info from endpoint and move the camera"""
    pallet_id = self._pallet_info_widget.get_input_value()
    endpoint = f"pallet/{pallet_id}/"
    print(f"Fetching stock info from endpoint: {endpoint}")

    _find_prim_then_select(pallet_id)

    stock_info = self._data_service.fetch_stock_info(endpoint)
    if stock_info:
        limited_items = list(stock_info.items())[:11]
        info_text = "\n".join([f"{key}: {value}" for key, value in limited_items])
        print(info_text)

        if "rack_location" in stock_info and stock_info["rack_location"]:
            location_id = stock_info["rack_location"].get("location_id")
            location_endpoint = f"rack-location/{location_id}/"
            print(f"Fetching coordinates from endpoint: {location_endpoint}")

            x, y, z = self._data_service.fetch_coordinates(location_endpoint)
            print(x, y, z)
            if x is not None and y is not None and z is not None:
                _move_camera(y, z)
            else:
                print("Failed to fetch coordinates")
        else:
            print("Failed to fetch stock info")


def _show_notification(title: str, message: str):
    status = omni.kit.notification_manager.NotificationStatus.INFO
    ok_button = omni.kit.notification_manager.NotificationButtonInfo("OK", on_complete=None)
    omni.kit.notification_manager.post_notification(text=message,
                                                    hide_after_timeout=False,
                                                    duration=0,
                                                    status=status,
                                                    button_infos=[ok_button])


def log_status(pallet_id, stock_status_code, level):
    """
    Logs the stock status based on severity using carb logging functions.
    """
    if level == "CRITICAL":
        carb.log_error(f"Pallet ID {pallet_id} has stock status {stock_status_code}.")
    elif level == "WARNING":
        carb.log_warn(f"Pallet ID {pallet_id} has stock status {stock_status_code}.")

