import omni.usd
from pxr import Usd, UsdGeom, Gf, Kind
import logging
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Retrieve the current stage
stage = omni.usd.get_context().get_stage()

# API base URL (the rack number will be appended in the loop)
api_base_url = "https://digital-twin.expangea.com/rack/5BTG/3/{rack_number}/"
headers = {
    "X-API-KEY": "2c38e689-8bac-4ec6-9e0e-70e98222dc2d"
}


# Function to fetch data from the API for a specific rack number
def fetch_rack_data(rack_number):
    try:
        api_url = api_base_url.format(rack_number=rack_number)
        response = requests.post(api_url, headers=headers)
        response.raise_for_status()  # Check if the request was successful
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data for rack {rack_number} from API: {e}")
        return None


# Function to check if a location already exists in /rack_location
def location_exists_in_stage(location_id):
    prim_path = f"/rack_location/_{location_id}"
    return stage.GetPrimAtPath(prim_path).IsValid()


# Function to spawn a cube at a specific location
def spawn_cube_at_location(location_id, coordinates):
    xform_prim_path = f"/rack_location/_{location_id}/cube"

    # Create the cube geometry at the specified location
    cube = UsdGeom.Cube.Define(stage, xform_prim_path)
    cube.GetSizeAttr().Set(50)  # Set size for cube (adjust as needed)

    xform = UsdGeom.Xform.Define(stage, xform_prim_path)
    xform.AddTranslateOp().Set(Gf.Vec3d(coordinates["x"], coordinates["y"], coordinates["z"]))

    logger.info(f"Spawned a cube at location {location_id} with coordinates {coordinates}")


# Loop through rack numbers from 21 to 25
for rack_number in range(21, 25):
    logger.info(f"Processing rack {rack_number}")

    # Fetch data for the current rack
    data = fetch_rack_data(rack_number)
    if data is None:
        continue  # Skip this iteration if no data was fetched

    # Check if the response contains rack locations and pallets information
    rack_locations = data.get("data", {}).get("rack_locations", [])
    if not rack_locations:
        logger.error(f"No rack locations data found for rack {rack_number}.")
        continue

    # Iterate over the rack locations
    for location in rack_locations:
        location_id = location.get('location_id', 'unknown')
        coordinates = location.get("coordinates", {})

        # Ensure coordinates have x, y, z values
        if all(k in coordinates for k in ['x', 'y', 'z']):
            pallets = location.get("pallets", [])

            if pallets:
                logger.info(f"Pallets found at location {location_id}:")
                for pallet in pallets:
                    pallet_id = pallet.get("pallet_id", "unknown")
                    logger.info(f"  Pallet ID: {pallet_id}")
            else:
                logger.info(f"No pallets at location {location_id}, spawning a cube.")
                if not location_exists_in_stage(location_id):
                    spawn_cube_at_location(location_id, coordinates)
                else:
                    logger.info(f"Location {location_id} already exists in /rack_location")
        else:
            logger.error(f"Invalid coordinates for location {location_id}")

