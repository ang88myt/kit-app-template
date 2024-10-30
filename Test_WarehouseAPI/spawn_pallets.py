# import omni.usd
# from pxr import Usd, UsdGeom, Gf, Sdf, Kind
# import logging
# import requests
#
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
#
# # Retrieve the current stage
# stage = omni.usd.get_context().get_stage()
#
# # API details
# api_url = "https://digital-twin.expangea.com/rack/5BTG/3/23/"
# headers = {
#     "X-API-KEY": "2c38e689-8bac-4ec6-9e0e-70e98222dc2d"
# }
#
# # Path to the pallet USD file
# pallet_usd_path = "D:/Toll Innovation/TC Level 3 Demo/_Update/Pallet_Asm_A04_120x122x75cm_PR_V_NVD_01.usd"
#
# # Fetch the data from the API
# try:
#     response = requests.post(api_url, headers=headers)
#     response.raise_for_status()  # Check if the request was successful
#     data = response.json()
# except requests.exceptions.RequestException as e:
#     logger.error(f"Error fetching data from API: {e}")
#     exit()
#
# # Check if the response contains rack locations and pallets information
# rack_locations = data.get("data", {}).get("rack_locations", [])
# if not rack_locations:
#     logger.error("No rack locations data found in the response.")
#     exit()
#
# # Function to spawn a pallet at a specific location
# def spawn_pallet_at_location(location, pallet_id):
#     if location is None:
#         logger.error("Location is None, cannot spawn pallet.")
#         return
#
#     location_id = location.get('location_id', 'unknown')
#     xform_prim_path = f"/rack_location/_{location_id}"
#
#     try:
#         coordinates = location.get("coordinates", {})
#         logger.warning(f"{location_id}, {pallet_id}, "
#                        f"{coordinates.get('x', 'N/A')}, {coordinates.get('y', 'N/A')}, {coordinates.get('z', 'N/A')}")
#
#         if all(k in coordinates for k in ["x", "y", "z"]):
#             # Check if the Xform exists or create it
#             xform = UsdGeom.Xform.Define(stage, xform_prim_path)
#
#             # Check if the translate operation already exists and update it if needed
#             translate_op = None
#             for op in xform.GetOrderedXformOps():
#                 if op.GetOpType() == UsdGeom.XformOp.TypeTranslate:
#                     translate_op = op
#                     break
#
#             # If translate op exists, update it; otherwise, create a new one
#             if translate_op:
#                 translate_op.Set(Gf.Vec3d(coordinates["x"], coordinates["y"], coordinates["z"]))
#                 logger.warning(f"Updated existing translate op at {xform_prim_path}")
#             else:
#                 xform.AddTranslateOp().Set(Gf.Vec3d(coordinates["x"], coordinates["y"], coordinates["z"]))
#                 logger.warning(f"Created new translate op at {xform_prim_path}")
#
#             # Check if the rotate operation already exists and update it if needed
#             rotate_op = None
#             for op in xform.GetOrderedXformOps():
#                 if op.GetOpType() == UsdGeom.XformOp.TypeRotateXYZ:
#                     rotate_op = op
#                     break
#
#             # If rotate op exists, update it; otherwise, create a new one
#             if rotate_op:
#                 rotate_op.Set(Gf.Vec3f(0.0, 0.0, 90.0))
#                 logger.warning(f"Updated existing rotate op at {xform_prim_path}")
#             else:
#                 xform.AddRotateXYZOp().Set(Gf.Vec3f(0.0, 0.0, 90.0))
#                 logger.warning(f"Created new rotate op at {xform_prim_path}")
#
#         else:
#             logger.error(f"No valid coordinates found for location {location_id}")
#
#         # Spawn the pallet at this location
#         pallet_prim_path = f"{xform_prim_path}/{pallet_id}"
#         if not stage.GetPrimAtPath(pallet_prim_path).IsValid():
#             pallet_prim = stage.DefinePrim(pallet_prim_path, "Xform")
#             pallet_prim.GetReferences().AddReference(pallet_usd_path)
#
#             # Set the pallet as a component
#             Usd.ModelAPI(pallet_prim).SetKind(Kind.Tokens.assembly)
#
#             logger.warning(f"Spawned Pallet {pallet_id} at {pallet_prim_path}")
#         else:
#             logger.info(f"Pallet already exists at {pallet_prim_path}")
#
#     except AttributeError as e:
#         logger.error(f"AttributeError occurred: {e} - Likely due to missing or invalid data in location.")
#
#
# # Iterate over the rack locations and spawn pallets
# for location in rack_locations:
#     # Check if pallets exist in the location
#     pallets = location.get("pallets", [])
#     if pallets is not None:
#         for pallet in pallets:
#             spawn_pallet_at_location(location, pallet.get("pallet_id", "unknown"))
#     else:
#         logger.error(f"No pallets found for location {location.get('location_id', 'unknown')}")


import omni.usd
from pxr import Usd, UsdGeom, Gf, Sdf, Kind
import logging
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RackDataHandler:
    API_BASE_URL = "https://digital-twin.expangea.com/rack/5BTG/3/{rack_number}/"
    HEADERS = {
        "X-API-KEY": "2c38e689-8bac-4ec6-9e0e-70e98222dc2d"
    }
    PALLET_USD_PATH = "C:/_update_/Pallet_Asm_A04_120x122x75cm_PR_V_NVD_01.usd"

    def __init__(self):
        self.stage = omni.usd.get_context().get_stage()

    def fetch_rack_data(self, rack_number):
        """Fetch data from the API for a specific rack number."""
        try:
            api_url = self.API_BASE_URL.format(rack_number=rack_number)
            response = requests.post(api_url, headers=self.HEADERS)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data for rack {rack_number} from API: {e}")
            return None

    def spawn_pallet_at_location(self, rack_number, location, pallet_id):
        """Spawn a pallet at a specific location with translation and rotation applied."""
        if location is None:
            logger.error("Location is None, cannot spawn pallet.")
            return

        location_id = location.get('location_id', 'unknown')
        xform_prim_path = f"/All_Racks/Rack_{rack_number}/locID_{location_id}"

        try:
            coordinates = location.get("coordinates", {})
            logger.warning(f"{location_id}, {pallet_id}, "
                           f"{coordinates.get('x', 'N/A')}, {coordinates.get('y', 'N/A')}, {coordinates.get('z', 'N/A')}")

            if all(k in coordinates for k in ["x", "y", "z"]):
                xform = UsdGeom.Xform.Define(self.stage, xform_prim_path)
                translate_op = self._get_or_add_xform_op(xform, UsdGeom.XformOp.TypeTranslate, coordinates)
                rotate_op = self._get_or_add_xform_op(xform, UsdGeom.XformOp.TypeRotateXYZ, {"x": 0.0, "y": 0.0, "z": 90.0})

                # Spawn the pallet at this location
                pallet_prim_path = f"{xform_prim_path}/{pallet_id}"
                self._create_or_reference_pallet_prim(pallet_prim_path)

            else:
                logger.error(f"No valid coordinates found for location {location_id}")

        except AttributeError as e:
            logger.error(f"AttributeError occurred: {e} - Likely due to missing or invalid data in location.")

    def _get_or_add_xform_op(self, xform, op_type, coordinates):
        """Check for an existing transform operation; add one if it does not exist."""
        op = next((o for o in xform.GetOrderedXformOps() if o.GetOpType() == op_type), None)
        if op:
            op.Set(Gf.Vec3d(coordinates["x"], coordinates["y"], coordinates["z"]))
            logger.warning(f"Updated existing {op_type} op at {xform.GetPath()}")
        else:
            new_op = xform.AddTranslateOp() if op_type == UsdGeom.XformOp.TypeTranslate else xform.AddRotateXYZOp()
            new_op.Set(Gf.Vec3d(coordinates["x"], coordinates["y"], coordinates["z"]))
            logger.warning(f"Created new {op_type} op at {xform.GetPath()}")

        return op

    def _create_or_reference_pallet_prim(self, pallet_prim_path):
        """Create a pallet prim if it does not exist, or add a reference to it if it does."""
        if not self.stage.GetPrimAtPath(pallet_prim_path).IsValid():
            pallet_prim = self.stage.DefinePrim(pallet_prim_path, "Xform")
            pallet_prim.GetReferences().AddReference(self.PALLET_USD_PATH)
            Usd.ModelAPI(pallet_prim).SetKind(Kind.Tokens.assembly)
            logger.warning(f"Spawned Pallet at {pallet_prim_path}")
        else:
            logger.info(f"Pallet already exists at {pallet_prim_path}")

    def process_racks(self, start_rack=19, end_rack=40):
        """Process racks and spawn pallets based on API data."""
        for rack_number in range(start_rack, end_rack + 1):
            logger.info(f"Processing rack {rack_number}")
            data = self.fetch_rack_data(rack_number)
            if not data:
                continue

            rack_locations = data.get("data", {}).get("rack_locations", [])
            if not rack_locations:
                logger.error(f"No rack locations data found for rack {rack_number}.")
                continue

            for location in rack_locations:
                pallets = location.get("pallets", [])
                if pallets is not None:
                    for pallet in pallets:
                        self.spawn_pallet_at_location(rack_number, location, pallet.get("pallet_id", "unknown"))
                else:
                    logger.error(f"No pallets found for location {location.get('location_id', 'unknown')} in rack {rack_number}.")


# Usage
rack_handler = RackDataHandler()
rack_handler.process_racks()
