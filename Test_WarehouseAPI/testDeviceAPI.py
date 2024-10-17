import time
import requests
import threading
from pxr import UsdGeom, Gf, Sdf
import omni.usd

# Global variables
last_pos = Gf.Vec3d(0, 0, 0)
last_update_time = 0
cache_duration = 1.0  # Cache API response for 1 second
cached_data = None
stop_event = threading.Event()  # Event to control stopping the thread

HTTP_ENDPOINT = 'https://digital-twin.expangea.com/device/Cube/'
API_HEADERS = {
    'X-API-KEY': '2c38e689-8bac-4ec6-9e0e-70e98222dc2d',
    'Content-Type': 'application/json'
}

# Function to fetch data from the API with caching
def fetch_data():
    global cached_data, last_update_time
    current_time = time.time()

    if cached_data is None or (current_time - last_update_time) > cache_duration:
        try:
            response = requests.post(url=HTTP_ENDPOINT, headers=API_HEADERS)
            response.raise_for_status()  # Raise an exception for HTTP errors
            cached_data = response.json()
            last_update_time = current_time  # Update cache timestamp
            print(f"Fetched data: {cached_data}")  # Debug: Print the fetched data
        except Exception as e:
            print(f"Failed to fetch data from API: {e}")
            return None

    return cached_data

# Function to update the object's position based on cached data
def update_position():
    global last_pos
    data = fetch_data()

    if data is None:
        return  # Skip update if there's no valid data

    try:
        data = data.get("data", {})
        if data.get("name") == "Cube":
            new_pos = Gf.Vec3d(data['coordinates']['x'], data['coordinates']['y'], data['coordinates']['z'])
            print(f"New position from API: {new_pos}")  # Debug: Print new position

            # Define your smooth factor here
            smooth_factor = 0.1

            # Perform linear interpolation to smooth the movement
            interpolated_pos = last_pos + smooth_factor * (new_pos - last_pos)
            print(f"Interpolated position: {interpolated_pos}")  # Debug: Print interpolated position

            # Update the cube's position in Omniverse
            stage = omni.usd.get_context().get_stage()
            cube_prim = stage.GetPrimAtPath("/World/Cube")

            if not cube_prim.IsValid():
                print("Cube prim not found at /World/Cube")
                return

            xform = UsdGeom.Xformable(cube_prim)
            xform.SetXformOpOrder([])
            xform.AddTranslateOp().Set(interpolated_pos)

            # Store the current position as the last known position
            last_pos = interpolated_pos

    except Exception as e:
        print(f"Failed to update Cube position: {e}")

# Function to periodically call update_position in a separate thread
def periodic_update():
    while not stop_event.is_set():  # Continue running until stop_event is set
        try:
            update_position()
            time.sleep(0.5)  # Call this function every 0.5 seconds
        except Exception as e:
            print(f"Error in periodic_update: {e}")

# Start the periodic update in a separate thread
update_thread = threading.Thread(target=periodic_update, daemon=True)
update_thread.start()

# Function to stop the thread gracefully
def stop_update_thread():
    stop_event.set()  # Signal the thread to stop
    update_thread.join()  # Wait for the thread to finish
    print("Update thread has been stopped.")

# Example: Call stop_update_thread() when you want to stop the updates
