import omni.usd
from pxr import UsdGeom, Gf
import logging
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Retrieve the current stage
stage = omni.usd.get_context().get_stage()

# API details
api_url = "https://digital-twin.expangea.com/expiry/5BTG/"
headers = {
    "X-API-KEY": "2c38e689-8bac-4ec6-9e0e-70e98222dc2d"
}

# Set to keep track of processed location IDs
processed_locations = set()

# Make a request to the API
response = requests.post(api_url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    data = response.json()
    expired_items = data.get('expired', [])

    for item in expired_items:
        pallet_id = item.get('pallet_id')
        location_id = item.get('location_id')
        rack_no = item.get('rack_no')
        floor_no = item.get('floor_no')
        balance_shelf_life_days = item['inventory'].get('Balance Shelf Life to Expiry (days)')

        # Extracting the coordinates from the data, using default values if None
        coordinates = item.get('coordinates', {})
        x = coordinates.get('x', 0.0) if coordinates is not None else 0.0
        y = coordinates.get('y', 0.0) if coordinates is not None else 0.0
        z = coordinates.get('z', 0.0) if coordinates is not None else 0.0

        # Check if location_id has already been processed
        if location_id not in processed_locations:
            # Add the location_id to the set
            processed_locations.add(location_id)

            # Log the information, including coordinates
            logger.info(f"Pallet ID: {pallet_id}, Location ID: {location_id}, Rack No: {rack_no}, "
                        f"Balance Shelf Life (days): {balance_shelf_life_days}, Floor No: {floor_no}, Coordinates: ({x}, {y}, {z})")

            # Spawn a cube at the given coordinates
            cube_prim_path = f"/root/ex[ired/{pallet_id}"
            if not stage.GetPrimAtPath(cube_prim_path).IsValid():
                cube_prim = UsdGeom.Cube.Define(stage, cube_prim_path)
                cube_prim.AddTranslateOp().Set(Gf.Vec3f(x, y, z))
                logger.warning(f"Spawned cube for Pallet {pallet_id} at coordinates ({x}, {y}, {z})")
            else:
                logger.info(f"Cube already exists at {cube_prim_path}")
        else:
            logger.info(f"Duplicate location_id {location_id} detected, skipping...")
else:
    logger.error(f"Failed to retrieve data: {response.status_code} - {response.text}")
