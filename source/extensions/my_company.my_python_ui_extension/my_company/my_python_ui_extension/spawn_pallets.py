import asyncio
import aiohttp
import omni.usd
from pxr import Usd, UsdGeom, Gf, Sdf, Kind
import logging
import json
import csv

import pathlib
import omni.kit.app

EXTENSION_FOLDER_PATH = pathlib.Path(
    omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RackDataHandler:
    API_BASE_URL = "https://digital-twin-dev.expangea.com/rack/5BTG/3/{rack_number}/"
    HEADERS = {"X-API-KEY": "2c38e689-8bac-4ec6-9e0e-70e98222dc2d"}

    def __init__(self):
        self.PALLET_USD_PATH = "D:/Toll Innovation/TC Level 3 Demo/_Update/Pallet_Asm_A04_120x122x75cm_PR_V_NVD_01.usd"

    async def fetch_rack_data_async(self, rack_number: int, session: aiohttp.ClientSession) -> dict:
        """Fetch data from the API asynchronously for a given rack number."""
        url = self.API_BASE_URL.format(rack_number=rack_number)
        try:
            async with session.post(url, headers=self.HEADERS) as response:
                response.raise_for_status()
                data = await response.json()
                logger.info(f"Fetched data for rack {rack_number}")
                return data
        except Exception as e:
            logger.error(f"Error fetching data for rack {rack_number} from API: {e}")
            return None

    async def process_racks_async(self, start_rack: int = 21, end_rack: int = 40):
        """Concurrently fetch data for racks and process each rack's data sequentially."""
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_rack_data_async(rack, session) for rack in range(start_rack, end_rack + 1)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for rack_number, data in zip(range(start_rack, end_rack + 1), results):
                if isinstance(data, Exception) or data is None:
                    continue
                self.process_rack_data(rack_number, data)

    def process_rack_data(self, rack_number: int, data: dict):
        """Process the fetched data for one rack and spawn pallets."""
        stage = omni.usd.get_context().get_stage()
        if not stage:
            logger.error("No valid USD stage loaded.")
            return

        rack_locations = data.get("data", {}).get("rack_locations", [])
        if not rack_locations:
            logger.error(f"No rack locations data found for rack {rack_number}.")
            return

        for location in rack_locations:
            pallets = location.get("pallets", [])
            if pallets is not None:
                for pallet in pallets:
                    inventory = pallet.get("inventory", {})
                    product_dict = {
                        "pallet_id": pallet.get("pallet_id", "unknown"),
                        "owner": inventory.get("Owner"),
                        "product": inventory.get("Product"),
                        "location": inventory.get("Location"),
                        "discription": inventory.get("Description1"),
                        "product_group": inventory.get("Product Group"),
                        "status_code": inventory.get("Stock Status Code"),
                        "product_shelf_life": inventory.get("Product Shelf Life"),
                        "pallet_domination": inventory.get("Pallet Denomination"),
                        "qty_available_in_loose": inventory.get("Qty Available in Loose"),
                        "balance_shelf_life_percentage": inventory.get("Balance Shelf Life Percentage"),
                        "balance_shelf_life_to_expiry": inventory.get("Balance Shelf Life to Expiry (days)")
                    }
                    self.spawn_pallet_at_location(rack_number, location, pallet.get("pallet_id", "unknown"), product_dict)
            else:
                logger.error(f"No pallets found for location {location.get('location_id', 'unknown')} in rack {rack_number}.")

    def spawn_pallet_at_location(self, rack_number, location, pallet_id, product_dict):
        """Spawn a pallet at a specific location and set product attributes."""
        stage = omni.usd.get_context().get_stage()
        product_code = product_dict.get("product", "UNKNOWN_PRODUCT")

        if location is None:
            logger.error("Location is None, cannot spawn pallet.")
            return

        location_id = location.get("location_id", "unknown")
        coordinates = location.get("coordinates", {})

        # Build the USD hierarchy paths
        root_path = Sdf.Path("/Root")
        warehouse_path = root_path.AppendChild("WH_5BTG")
        rack_path = warehouse_path.AppendChild(f"RACK_{rack_number}")
        xform_prim_path = rack_path.AppendChild(f"LOCATION_{location_id}")
        product_code_path = xform_prim_path.AppendChild(f"SKU_{product_code}")
        pallet_prim_path = product_code_path.AppendChild(pallet_id)

        try:
            # Ensure parent prims exist
            for path in [root_path, warehouse_path, rack_path, xform_prim_path, product_code_path]:
                if not stage.GetPrimAtPath(path).IsValid():
                    UsdGeom.Xform.Define(stage, path)

            # Apply translation and rotation if coordinates are valid
            if all(k in coordinates for k in ["x", "y", "z"]):
                xform = UsdGeom.Xform.Get(stage, xform_prim_path)
                self._set_xform_op(xform, UsdGeom.XformOp.TypeTranslate, coordinates)
                self._set_xform_op(xform, UsdGeom.XformOp.TypeRotateXYZ, {"x": 0.0, "y": 0.0, "z": 90.0})
            else:  # Ensure this is preceded by a valid `if` or loop condition
                logger.error(f"No valid coordinates found for location {location_id}")
                TEMP_DIR = EXTENSION_FOLDER_PATH.joinpath("temp")
                TEMP_DIR.mkdir(parents=True, exist_ok=True)  # Create the temp folder if it doesn’t exist

                MISSING_COORDS_FILE = TEMP_DIR.joinpath("missing_coordinates.csv")
                try:
                    with MISSING_COORDS_FILE.open("a", newline="", encoding="utf-8") as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow([rack_number, location_id, pallet_id, product_code, json.dumps(coordinates)])
                    logger.info(f"Missing coordinates logged to {MISSING_COORDS_FILE}")
                except Exception as csv_e:
                    logger.exception(f"Failed to write to CSV: {csv_e}")

            # Create or reference the pallet prim
            self._create_or_reference_pallet_prim(pallet_prim_path)

            pallet_prim = stage.GetPrimAtPath(pallet_prim_path)
            if not pallet_prim.IsValid():
                logger.error(f"Failed to retrieve pallet prim at {pallet_prim_path}")
                return

            # Set product attributes on the pallet prim
            for key, value in product_dict.items():
                attr_name = f"userProperties:{key}"
                usd_attr = pallet_prim.GetAttribute(attr_name)
                if not usd_attr:
                    usd_attr = pallet_prim.CreateAttribute(attr_name, Sdf.ValueTypeNames.String)
                usd_attr.Set(str(value))
                logger.info(f"Set attribute {attr_name} = {value}")

            logger.info(f"Successfully spawned pallet {pallet_id} at location {location_id}.")

        except Exception as e:
            if "Path must be an absolute path:" in str(e):
                logger.warning(f"Skipping spawn_pallet_at_location due to invalid path: {e}")
            else:
                logger.error(f"Unexpected error in spawn_pallet_at_location: {e}")

    def _set_xform_op(self, xform, op_type, coordinates):
        """Sets (or updates) a transform operation on a prim."""
        op = next((o for o in xform.GetOrderedXformOps() if o.GetOpType() == op_type), None)
        coord_vec = Gf.Vec3d(coordinates["x"], coordinates["y"], coordinates["z"])
        if op:
            op.Set(coord_vec)
            logger.warning(f"Updated existing {op_type} op at {xform.GetPath()}")
        else:
            new_op = xform.AddTranslateOp() if op_type == UsdGeom.XformOp.TypeTranslate else xform.AddRotateXYZOp()
            new_op.Set(coord_vec)
            logger.warning(f"Created new {op_type} op at {xform.GetPath()}")

    def _create_or_reference_pallet_prim(self, pallet_prim_path):
        """Creates a pallet prim if it does not exist or adds a reference if it does."""
        if not pallet_prim_path.IsAbsolutePath():
            logger.error(f"Path must be an absolute path: {pallet_prim_path}")
            return

        stage = omni.usd.get_context().get_stage()
        prim = stage.GetPrimAtPath(pallet_prim_path)
        if not prim.IsValid():
            pallet_prim = stage.DefinePrim(pallet_prim_path, "Xform")
            pallet_prim.GetReferences().AddReference(self.PALLET_USD_PATH)
            from pxr import Kind
            pallet_prim.SetMetadata("kind", Kind.Tokens.assembly)
            logger.warning(f"Spawned Pallet at {pallet_prim_path}")
        else:
            logger.info(f"Pallet already exists at {pallet_prim_path}")

    async def process_racks_async(self, start_rack=21, end_rack=40):
        """Asynchronously process racks and spawn pallets based on API data."""
        import aiohttp

        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_rack_data_async(rack, session) for rack in range(start_rack, end_rack + 1)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for rack_number, data in zip(range(start_rack, end_rack + 1), results):
                if isinstance(data, Exception) or data is None:
                    continue
                self.process_rack_data(rack_number, data)

    async def fetch_rack_data_async(self, rack_number, session):
        """Fetch rack data asynchronously using aiohttp."""
        try:
            api_url = self.API_BASE_URL.format(rack_number=rack_number)
            async with session.post(api_url, headers=self.HEADERS) as response:
                response.raise_for_status()
                logger.info(f"Fetched data for rack {rack_number}")
                return await response.json()
        except Exception as e:
            logger.error(f"Error fetching data for rack {rack_number}: {e}")
            return None

    def process_rack_data(self, rack_number, data):
        """Process a single rack's data and spawn pallets."""
        stage = omni.usd.get_context().get_stage()
        if not stage:
            logger.error("No valid USD stage loaded.")
            return

        rack_locations = data.get("data", {}).get("rack_locations", [])
        if not rack_locations:
            logger.error(f"No rack locations data found for rack {rack_number}.")
            return

        for location in rack_locations:
            pallets = location.get("pallets", [])
            if pallets is not None:
                for pallet in pallets:
                    inventory = pallet.get("inventory", {})
                    product_dict = {
                        "pallet_id": pallet.get("pallet_id", "unknown"),
                        "owner": inventory.get("Owner"),
                        "product": inventory.get("Product"),
                        "location": inventory.get("Location"),
                        "discription": inventory.get("Description1"),
                        "product_group": inventory.get("Product Group"),
                        "status_code": inventory.get("Stock Status Code"),
                        "product_shelf_life": inventory.get("Product Shelf Life"),
                        "pallet_domination": inventory.get("Pallet Denomination"),
                        "qty_available_in_loose": inventory.get("Qty Available in Loose"),
                        "balance_shelf_life_percentage": inventory.get("Balance Shelf Life Percentage"),
                        "balance_shelf_life_to_expiry": inventory.get("Balance Shelf Life to Expiry (days)")
                    }
                    self.spawn_pallet_at_location(rack_number, location, pallet.get("pallet_id", "unknown"), product_dict)
            else:
                logger.error(f"No pallets found for location {location.get('location_id', 'unknown')} in rack {rack_number}.")

# Usage Example:
# In an async environment, for instance in a script editor:
#
#   import asyncio
#   handler = RackDataHandler()
#   asyncio.ensure_future(handler.process_racks_async())


# Usage:
# Create an instance of RackDataHandler and run process_racks() asynchronously.
# For example, in an async environment:
#
#   import asyncio
#   handler = RackDataHandler()
#   asyncio.ensure_future(handler.process_racks())


# import omni.usd
# from pxr import Usd, UsdGeom, Gf, Sdf, Kind
# import logging
# import requests
# import json
# import csv
#
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
#
# class RackDataHandler:
#     API_BASE_URL = "https://digital-twin-dev.expangea.com/rack/5BTG/3/{rack_number}/"
#     HEADERS = {
#         "X-API-KEY": "2c38e689-8bac-4ec6-9e0e-70e98222dc2d"
#     }
#
#     def __init__(self):
#
#         self.PALLET_USD_PATH = "D:/Toll Innovation/TC Level 3 Demo/_Update/Pallet_Asm_A04_120x122x75cm_PR_V_NVD_01.usd"
#
#     def fetch_rack_data(self, rack_number):
#         """Fetch data from the API for a specific rack number."""
#         try:
#             api_url = self.API_BASE_URL.format(rack_number=rack_number)
#             response = requests.post(api_url, headers=self.HEADERS)
#             response.raise_for_status()
#             return response.json()
#         except requests.exceptions.RequestException as e:
#             logger.error(f"Error fetching data for rack {rack_number} from API: {e}")
#             return None
#
#     def spawn_pallet_at_location(self, rack_number, location, pallet_id, product_dict):
#         """Spawn a pallet at a specific location with translation and rotation applied,
#         and write product_dict attributes as USD attributes on the pallet prim.
#
#         If valid coordinates (x, y, z) are not found in the location, the function logs an error
#         and appends the missing coordinate information to a CSV file.
#         """
#         stage = omni.usd.get_context().get_stage()
#         product_code = product_dict.get("product", "UNKNOWN_PRODUCT")
#
#         if location is None:
#             logger.error("Location is None, cannot spawn pallet.")
#             return
#
#         location_id = location.get("location_id", "unknown")
#         coordinates = location.get("coordinates", {})
#
#         # Build the USD hierarchy paths with /Root as the top-level path
#         root_path = Sdf.Path("/Root")
#         warehouse_path = root_path.AppendChild("WH_5BTG")
#         rack_path = warehouse_path.AppendChild(f"RACK_{rack_number}")
#         xform_prim_path = rack_path.AppendChild(f"LOCATION_{location_id}")
#         product_code_path = xform_prim_path.AppendChild(f"SKU_{product_code}")
#         pallet_prim_path = product_code_path.AppendChild(pallet_id)
#
#         try:
#             # Ensure the /Root prim exists
#             root_xform = UsdGeom.Xform.Get(stage, root_path)
#             if not root_xform:
#                 root_xform = UsdGeom.Xform.Define(stage, root_path)
#
#             # Ensure the /WH_5BTG prim exists
#             warehouse_xform = UsdGeom.Xform.Get(stage, warehouse_path)
#             if not warehouse_xform:
#                 warehouse_xform = UsdGeom.Xform.Define(stage, warehouse_path)
#
#             # Ensure the rack prim exists
#             rack_xform = UsdGeom.Xform.Get(stage, rack_path)
#             if not rack_xform:
#                 rack_xform = UsdGeom.Xform.Define(stage, rack_path)
#
#             # Ensure the location prim exists
#             location_xform = UsdGeom.Xform.Get(stage, xform_prim_path)
#             if not location_xform:
#                 location_xform = UsdGeom.Xform.Define(stage, xform_prim_path)
#
#             # Ensure the product code prim exists
#             product_xform = UsdGeom.Xform.Get(stage, product_code_path)
#             if not product_xform:
#                 product_xform = UsdGeom.Xform.Define(stage, product_code_path)
#                 logger.info(f"Created Product Xform: {product_code_path}")
#
#             # Check if valid coordinates are available:
#             if all(k in coordinates for k in ["x", "y", "z"]):
#                 self._set_xform_op(location_xform, UsdGeom.XformOp.TypeTranslate, coordinates)
#                 self._set_xform_op(location_xform, UsdGeom.XformOp.TypeRotateXYZ, {"x": 0.0, "y": 0.0, "z": 90.0})
#             else:
#                 logger.error(f"No valid coordinates found for location {location_id}")
#                 try:
#                     with open("D:\\Git\\kit-app-template\\Temp\\missing_coordinates.csv", "a", newline="") as csvfile:
#                         writer = csv.writer(csvfile)
#                         writer.writerow([rack_number, location_id, pallet_id, product_code, json.dumps(coordinates)])
#                     logger.info("Missing coordinates logged to missing_coordinates.csv")
#                 except Exception as csv_e:
#                     logger.error(f"Failed to write to CSV: {csv_e}")
#
#             # Create or reference the pallet prim
#             self._create_or_reference_pallet_prim(pallet_prim_path)
#             # logger.info(f"Processed Pallet Prim: {pallet_prim_path}")
#
#             # Retrieve the pallet prim from the stage
#             pallet_prim = stage.GetPrimAtPath(pallet_prim_path)
#             if not pallet_prim.IsValid():
#                 logger.error(f"Failed to retrieve pallet prim at {pallet_prim_path}")
#                 return
#
#             # Write product attributes from product_dict as USD attributes on the pallet prim.
#             for key, value in product_dict.items():
#                 attr_name = f"userProperties:{key}"
#                 usd_attr = pallet_prim.GetAttribute(attr_name)
#                 if not usd_attr:
#                     usd_attr = pallet_prim.CreateAttribute(attr_name, Sdf.ValueTypeNames.String)
#                 usd_attr.Set(str(value))
#                 logger.info(f"Set attribute {attr_name} = {value}")
#
#             logger.info(f"Successfully spawned pallet {pallet_id} at location {location_id}.")
#
#         except Exception as e:
#             if "Path must be an absolute path:" in str(e):
#                 logger.warning(f"Skipping spawn_pallet_at_location due to invalid path: {e}")
#                 return
#             else:
#                 logger.error(f"Unexpected error in spawn_pallet_at_location: {e}")
#
#     def spawn_all_pallets(self):
#         for rack_number in range(21, 41):
#             rack_data = self.fetch_rack_data(rack_number)
#             if not rack_data:
#                 continue
#
#             locations = rack_data.get("data", {}).get("rack_locations", [])
#             for location in locations:
#                 pallets = location.get("pallets", [])
#                 for pallet in pallets:
#                     self.spawn_pallet_at_location(rack_number, location, pallet.get("pallet_id", "unknown"), pallet.get("inventory", {}))
#
#     def _set_xform_op(self, xform, op_type, coordinates):
#         """Check for an existing transform operation; add one if it does not exist."""
#         op = next((o for o in xform.GetOrderedXformOps() if o.GetOpType() == op_type), None)
#         coord_vec = Gf.Vec3d(coordinates["x"], coordinates["y"], coordinates["z"])
#         if op:
#             op.Set(coord_vec)
#             logger.warning(f"Updated existing {op_type} op at {xform.GetPath()}")
#         else:
#             new_op = xform.AddTranslateOp() if op_type == UsdGeom.XformOp.TypeTranslate else xform.AddRotateXYZOp()
#             new_op.Set(coord_vec)
#             logger.warning(f"Created new {op_type} op at {xform.GetPath()}")
#
#     def _create_or_reference_pallet_prim(self, pallet_prim_path):
#         """Create a pallet prim if it does not exist, or add a reference to it if it does."""
#         if not pallet_prim_path.IsAbsolutePath():
#             logger.error(f"Path must be an absolute path: {pallet_prim_path}")
#             return
#         stage = omni.usd.get_context().get_stage()
#         prim = stage.GetPrimAtPath(pallet_prim_path)
#         if not prim.IsValid():
#             pallet_prim = stage.DefinePrim(pallet_prim_path, "Xform")
#             pallet_prim.GetReferences().AddReference(self.PALLET_USD_PATH)
#             Usd.ModelAPI(pallet_prim).SetKind(Kind.Tokens.assembly)
#             logger.warning(f"Spawned Pallet at {pallet_prim_path}")
#         else:
#             logger.info(f"Pallet already exists at {pallet_prim_path}")
#
    # def process_racks(self, start_rack=21, end_rack=40):
    #     count = 0
    #     """Process racks and spawn pallets based on API data."""
    #     for rack_number in range(start_rack, end_rack + 1):
    #         logger.info(f"Processing rack {rack_number}")
    #         data = self.fetch_rack_data(rack_number)
    #         if not data:
    #             continue
    #         count += 1
    #         rack_locations = data.get("data", {}).get("rack_locations", [])
    #         if not rack_locations:
    #             logger.error(f"No rack locations data found for rack {rack_number}.")
    #             continue
    #
    #         for location in rack_locations:
    #             pallets = location.get("pallets", [])
    #             if pallets is not None:
    #                 for pallet in pallets:
    #                     count += 1
    #                     inventory = pallet.get("inventory", {})
    #                     product_dict = {
    #                         "pallet_id": pallet.get("pallet_id", "unknown"),
    #                         "owner": inventory.get("Owner"),
    #                         "product": inventory.get("Product"),
    #                         "location": inventory.get("Location"),
    #                         "discription": inventory.get("Description1"),
    #                         "product_group": inventory.get("Product Group"),
    #                         "status_code": inventory.get("Stock Status Code"),
    #                         "product_shelf_life": inventory.get("Product Shelf Life"),
    #                         "pallet_domination": inventory.get("Pallet Denomination"),
    #                         "qty_available_in_loose": inventory.get("Qty Available in Loose"),
    #                         "balance_shelf_life_percentage": inventory.get("Balance Shelf Life Percentage"),
    #                         "balance_shelf_life_to_expiry": inventory.get("Balance Shelf Life to Expiry (days)")
    #                     }
    #                     self.spawn_pallet_at_location(rack_number, location, pallet.get("pallet_id", "unknown"), product_dict)
    #             else:
    #                 logger.error(f"No pallets found for location {location.get('location_id', 'unknown')} in rack {rack_number}.")

# Usage
# rack_handler = RackDataHandler()
# rack_handler.process_racks()
