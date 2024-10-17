import requests
import logging
import asyncio
import omni.usd
from pxr import UsdGeom, Gf

# Set up logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# API endpoint and headers
HTTP_ENDPOINT = "https://digital-twin.expangea.com/device/Cube3/"
API_HEADERS = {
    'X-API-KEY': '2c38e689-8bac-4ec6-9e0e-70e98222dc2d',
    'Content-Type': 'application/json'
}

# Retrieve the current USD stage in Omniverse
stage = omni.usd.get_context().get_stage()

# Internal flag to control cube movement
move_cube = True  # Set to False to stop the cube from moving


# Function to fetch data from the device-specific API endpoint
async def fetch_device_data():
    try:
        # Send a POST request to the device-specific API
        response = requests.post(url=HTTP_ENDPOINT, headers=API_HEADERS)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        logger.warning(f"API Data Received: {data}")
        return data  # Return the parsed JSON response
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data from API: {e}")
        return None


# Function to move the cube directly based on coordinates
def move_cube_to_position(new_pos):
    cube_prim_path = "/World/Cube"  # Path to the cube prim in the USD stage

    # Check if the cube exists in the scene
    cube_prim = stage.GetPrimAtPath(cube_prim_path)
    if cube_prim.IsValid():
        logger.warning(f"Cube3 found at {cube_prim_path}, attempting to move...")

        # Get the Xform of the cube to update its position
        xform = UsdGeom.Xform.Get(stage, cube_prim_path)
        translate_op = None

        # Check for existing translate op
        for op in xform.GetOrderedXformOps():
            if op.GetOpType() == UsdGeom.XformOp.TypeTranslate:
                translate_op = op
                break

        if translate_op:
            # Directly modify the existing translate op
            translate_op.Set(Gf.Vec3d(new_pos["x"], new_pos["y"], new_pos["z"]))
            logger.warning(f"Moved Cube3 to (x: {new_pos['x']}, y: {new_pos['y']}, z: {new_pos['z']})")
        else:
            # Add a new translate op if none exists
            xform.AddTranslateOp().Set(Gf.Vec3d(new_pos["x"], new_pos["y"], new_pos["z"]))
            logger.warning(
                f"Added translate operation and moved Cube3 to (x: {new_pos['x']}, y: {new_pos['y']}, z: {new_pos['z']})")
    else:
        logger.error(f"Cube3 prim not found at {cube_prim_path}")


# Main function to update the cube position asynchronously without blocking
async def update_cube_position_every_3_seconds():
    while True:
        # Only move the cube if the boolean is set to True
        if move_cube:
            # Fetch the device data from the API
            device_data = await fetch_device_data()

            if device_data:
                data = device_data.get("data", {})
                if "coordinates" in data:
                    # Log the exact coordinates received from the API
                    logger.warning(f"Coordinates Received: {data['coordinates']}")

                    # Get the new position from the API data
                    new_position = {
                        "x": data["coordinates"].get("x", 0.0),
                        "y": data["coordinates"].get("y", 0.0),
                        "z": data["coordinates"].get("z", 0.0)
                    }

                    # Move the cube to the new position
                    move_cube_to_position(new_position)
                else:
                    logger.warning("No coordinates found in the API response.")
            else:
                logger.warning("No data available from the device API.")

        # Wait for 3 seconds asynchronously
        await asyncio.sleep(3)


# Schedule the asynchronous update function in Omniverse Kit's event loop
async def main():
    # Start the cube update process
    await update_cube_position_every_3_seconds()


# Run the main function
omni.kit.app.get_app().get_update_event_stream().create_subscription_to_pop(lambda e: asyncio.ensure_future(main()))
