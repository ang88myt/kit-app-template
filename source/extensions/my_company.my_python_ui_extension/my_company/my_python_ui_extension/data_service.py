# data_service.py
__all__ = ["DataService"]

import requests
import logging
import csv
from collections import defaultdict
from typing import Optional, Tuple, Dict, Any, List
from pxr import Usd, UsdGeom, Gf, Sdf, Kind, UsdShade
import carb
import omni.usd

# Setup logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DataService:
    BASE_URL = "https://digital-twin.expangea.com/"
    HEADERS = {'X-API-KEY': '2c38e689-8bac-4ec6-9e0e-70e98222dc2d'}
    CRITICAL_STATUS_CODES = ["NE", "DMG", "EX", "QAF"]
    MATERIAL_PATHS = {
        "DMG": "/Environment/Looks/Glass_Color_Mat/Blue_Glass",
        "NE": "/Environment/Looks/Glass_Color_Mat/Cyan_Glass",
        "QAF": "/Environment/Looks/Glass_Color_Mat/Purple_Glass",
        "EX": "/Environment/Looks/Glass_Color_Mat/Red_Glass"
    }

    def __init__(self):
        self.session = requests.Session()
        self.critical_status_count = {code: 0 for code in self.CRITICAL_STATUS_CODES}
        self.result_dict = {}

    def construct_api_url(self, endpoint: str) -> str:
        return f"{self.BASE_URL}{endpoint}"

    def handle_api_request(self, api_url: str) -> Optional[requests.Response]:
        try:
            response = self.session.post(api_url, headers=self.HEADERS)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logging.error(f"Error occurred during API request: {e}")
            return None

    def fetch_stock_info(self, endpoint: str) -> Dict:
        api_url = self.construct_api_url(endpoint)
        response = self.handle_api_request(api_url)
        if response:
            return response.json().get("data", {})
        return {}

    def fetch_coordinates(self, endpoint: str) -> Optional[Tuple[float, float, float]]:
        api_url = self.construct_api_url(endpoint)
        response = self.handle_api_request(api_url)
        if not response:
            return None

        try:
            data = response.json().get("data", {})
            coordinates = data.get("rack_location", {}).get("coordinates", {})
            if all(coordinates.get(axis) is not None for axis in ['x', 'y', 'z']):
                return coordinates['x'], coordinates['y'], coordinates['z']
        except ValueError:
            logging.error(f"Invalid JSON response from {api_url}.")
        return None

    def fetch_rack_data(self, rack_no: int) -> Optional[Dict]:
        url = f"{self.BASE_URL}rack/5BTG/3/{rack_no}/"
        response = self.handle_api_request(url)
        if response:
            return response.json()
        return None

    def fetch_status_code_data(self) -> Tuple[Dict[str, int], Dict[int, List[Dict[str, Any]]]]:
        critical_pallets_by_rack = defaultdict(list)

        for rack_no in range(20, 41):
            rack_data = self.fetch_rack_data(rack_no)
            if not rack_data:
                logging.warning(f"No data found for Rack {rack_no}.")
                continue

            rack_locations = rack_data.get("data", {}).get("rack_locations", [])
            for location in rack_locations:
                location_id = location.get("location_id")
                for pallet in location.get("pallets", []):
                    self.process_pallet(pallet, location_id, rack_no, critical_pallets_by_rack)

        flat_data_for_csv = [
            {**{"rack_no": rack_no}, **pallet}
            for rack_no, pallets in critical_pallets_by_rack.items()
            for pallet in pallets
        ]
        save_to_csv(flat_data_for_csv, "critical_pallets_by_rack.csv")

        return self.critical_status_count, critical_pallets_by_rack

    def process_pallet(self, pallet: Dict, location_id: str, rack_no: int, critical_pallets_by_rack: Dict[int, List[Dict]]):
        pallet_id = pallet.get("pallet_id")
        stock_status_code = pallet.get("inventory", {}).get("Stock Status Code", "N/A")

        if stock_status_code in self.CRITICAL_STATUS_CODES:
            critical_pallets_by_rack[rack_no].append({
                "pallet_id": pallet_id,
                "location_id": location_id,
                "stock_status_code": stock_status_code
            })
            self.critical_status_count[stock_status_code] += 1

            coordinates = self.fetch_coordinates(f"pallet/{pallet_id}/")
            if coordinates:
                self.spawn_cube("Critical_Items", pallet_id, coordinates, material_path=self.MATERIAL_PATHS[stock_status_code], location_id=location_id, group=f"Status_Code_{stock_status_code}")

    def spawn_cube(self, prim_name: str, pallet_id: str, coordinates: Tuple[float, float, float], material_path: str, location_id: str, group: str):
        stage = omni.usd.get_context().get_stage()
        if not stage:
            logging.error("Stage is not initialized.")
            return

        pallet_id = pallet_id.replace(".", "_").lstrip("0")
        if not coordinates:
            logging.error(f"Coordinates are None for Pallet ID {pallet_id}. Skipping.")
            return

        parent_xform_path_str = f"/{prim_name}"
        parent_xform_path = Sdf.Path(parent_xform_path_str)
        if not stage.GetPrimAtPath(parent_xform_path).IsValid():
            parent_xform = UsdGeom.Xform.Define(stage, parent_xform_path)
            parent_xform.AddTranslateOp().Set(Gf.Vec3f(0, 0, 0))
            logging.info(f"Created parent Xform: {parent_xform_path_str}")

        pallet_prim_path_str = f"{parent_xform_path_str}/{group}/_{location_id}/{pallet_id}"
        pallet_prim_path = Sdf.Path(pallet_prim_path_str)
        if not stage.GetPrimAtPath(pallet_prim_path).IsValid():
            pallet_xform = UsdGeom.Xform.Define(stage, pallet_prim_path)
            pallet_xform.AddTranslateOp().Set(Gf.Vec3f(*coordinates))

            cube_prim_path_str = f"{pallet_prim_path_str}/Cube"
            cube_prim = UsdGeom.Cube.Define(stage, Sdf.Path(cube_prim_path_str))
            cube_prim.GetSizeAttr().Set(120.0)
            cube_prim.AddTranslateOp().Set(Gf.Vec3f(0, 0, 60))

            Usd.ModelAPI(pallet_xform).SetKind(Kind.Tokens.assembly)
            _apply_material_to_prim(stage, cube_prim_path_str, material_path)
            logging.info(f"Spawned cube for Pallet {pallet_id} under {prim_name} at coordinates {coordinates}")
        else:
            logging.info(f"Pallet {pallet_id} already exists under {prim_name}.")

    def calculate_storage_utilization(self) -> Tuple[float, float]:
        total_slots, used_slots = 0, 0

        for rack_no in range(19, 41):
            rack_data = self.fetch_rack_data(rack_no)
            if not rack_data:
                continue

            rack_locations = rack_data.get("data", {}).get("rack_locations", [])
            for location in rack_locations:
                total_slots += 1
                if any(pallet.get("pallet_id") for pallet in location.get("pallets", [])):
                    used_slots += 1

        used_percentage = (used_slots / total_slots) * 100 if total_slots else 0
        free_percentage = 100 - used_percentage
        return round(used_percentage), round(free_percentage)

    def close(self):
        self.session.close()
        logging.info("API connection closed")

def _apply_material_to_prim(stage, prim_path, material_path):
    """Applies the specified material to the given prim."""
    material_prim = stage.GetPrimAtPath(material_path)
    if not material_prim:
        logging.error(f"Material not found at path: {material_path}")
        return

    prim = stage.GetPrimAtPath(prim_path)
    if not prim:
        logging.error(f"Prim not found at path: {prim_path}")
        return

    material_binding_api = UsdShade.MaterialBindingAPI(prim)
    material_binding_api.Bind(UsdShade.Material(material_prim))
    logging.info(f"Material {material_path} applied to {prim_path}")

def save_to_csv(data: List[Dict], file_name: str, group_by_key: Optional[str] = None):
    """Save a list of dictionaries to a CSV file, with optional support for grouping."""
    if not data:
        logging.error("No data provided to save to CSV.")
        return

    headers = data[0].keys()
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
            for group_key, items in grouped_data.items():
                first = True
                for item in items:
                    row = {**item}
                    if not first and group_by_key:
                        row[group_by_key] = ""
                    writer.writerow(row)
                    first = False
        logging.info(f"Data successfully saved to {file_name}")
    except Exception as e:
        logging.error(f"Failed to save data to CSV: {e}")

