# import time
# import requests
# from pxr import Usd, UsdGeom, Gf
# import omni.usd
# import carb.events
#
#
# class CubeMoverDataLayer:
#     def __init__(self, cube_prim_path, api_url, headers, interpolation_speed=0.1):
#         self.cube_prim_path = cube_prim_path  # Path of the cube prim in the USD scene
#         self.api_url = api_url  # API endpoint to get coordinates
#         self.headers = headers  # API headers
#         self.moving = False  # Movement control flag
#         self.interval = 2.0  # Movement interval in seconds
#         self._last_time = time.time()
#
#         self.prev_x = None  # Set initial position to None to handle the first move correctly
#         self.prev_y = None
#         self.prev_z = None
#
#         self.target_x = 0.0  # Target x position from API
#         self.target_y = 0.0  # Target y position from API
#         self.target_z = 0.0  # Target z position from API
#
#         self.interpolation_speed = interpolation_speed  # Speed of interpolation (0 < t < 1)
#         self._subscription = None  # Initialize the subscription attribute
#
#     def fetch_xyz(self):
#         """
#         Fetch x, y, z coordinates from the API.
#         Convert units to centimeters by multiplying by 100.
#         Apply an offset of 1200 cm (12 meters) to x and y.
#         """
#         try:
#             response = requests.post(self.api_url, headers=self.headers)
#             response.raise_for_status()  # Raise an exception for HTTP errors
#             data = response.json()  # Parse JSON response
#             coordinates = data.get("data", {}).get("coordinates", {})
#             x = coordinates.get("x", 0.0)
#             y = coordinates.get("y", 0.0)
#             z = coordinates.get("z", 0.0)
#
#             # Print the original values from the API in meters
#             print(f"Original API data: X: {x} meters, Y: {y} meters, Z: {z} meters")
#
#             # Convert to centimeters and apply offsets
#             self.target_x = x * 100   # Convert to cm and apply 12m offset
#             self.target_y = y * 100   # Convert to cm and apply 12m offset
#             self.target_z = z * 100  # Convert to cm
#         except requests.exceptions.RequestException as e:
#             print(f"Error fetching data from API: {e}")
#
#     def lerp(self, start, end, t):
#         """
#         Perform linear interpolation between start and end values with factor t.
#         """
#         return (1 - t) * start + t * end
#
#     def move_cube(self):
#         """
#         Move the cube in Omniverse based on interpolated values to slow down the movement.
#         """
#         # Ensure we get the current stage
#         usd_context = omni.usd.get_context()
#         stage = usd_context.get_stage()
#
#         if not stage:
#             print("No active stage found.")
#             return
#
#         # Get the cube's USD prim from the stage
#         cube_prim = stage.GetPrimAtPath(self.cube_prim_path)
#         if not cube_prim.IsValid():
#             print(f"Prim not found at path: {self.cube_prim_path}")
#             return
#
#         # If this is the first move, set the previous position to the target position
#         if self.prev_x is None:
#             self.prev_x = self.target_x
#             self.prev_y = self.target_y
#             self.prev_z = self.target_z
#
#         # Interpolate between the current and target positions
#         x = self.lerp(self.prev_x, self.target_x, self.interpolation_speed)
#         y = self.lerp(self.prev_y, self.target_y, self.interpolation_speed)
#         z = self.lerp(self.prev_z, self.target_z, self.interpolation_speed)
#
#         # Update previous positions to the new interpolated values
#         self.prev_x = x
#         self.prev_y = y
#         self.prev_z = z
#
#         # Get the Xform of the cube and update the existing translate operation
#         xform = UsdGeom.Xformable(cube_prim)
#
#         if not xform:
#             print(f"Failed to retrieve Xformable for prim: {self.cube_prim_path}")
#             return
#
#         # Find the existing translate op and update it
#         translate_op = xform.GetOrderedXformOps()[0]  # Assuming translate is the first op in the order
#         translate_op.Set(Gf.Vec3f(x, y, z))
#
#         # Print the interpolated position of the cube in centimeters
#         print(f"Cube moved to (in cm): X: {x}, Y: {y}, Z: {z}")
#
#     def start_moving(self):
#         """
#         Start moving the cube every 2 seconds by fetching coordinates from the API.
#         """
#         self.moving = True
#
#         # Subscribe to the update stream for regular updates on the main thread
#         self._subscription = omni.kit.app.get_app().get_update_event_stream().create_subscription_to_pop(
#             self._on_update)
#
#     def stop_moving(self):
#         """
#         Stop moving the cube.
#         """
#         # Check if the subscription exists and unsubscribe if it's active
#         if self._subscription:
#             try:
#                 self._subscription.unsubscribe()  # Properly unsubscribe from the event stream
#                 self._subscription = None  # Clear the subscription reference to ensure no further calls
#                 print("Event stream unsubscribed successfully.")
#             except Exception as e:
#                 print(f"Failed to unsubscribe: {e}")
#         else:
#             print("No active subscription to unsubscribe.")
#
#         # Stop all activities and prevent further fetching or movement
#         self.moving = False  # Set the flag to False to stop any future movement
#         print("Fetching and movement forcefully stopped.")
#
#     def _on_update(self, event):
#         """
#         Callback function to handle updates from the event stream.
#         This is called every frame, so we check the interval to move the cube.
#         """
#         if not self.moving:  # If self.moving is False, don't move the cube
#             return
#
#         current_time = time.time()
#         if current_time - self._last_time >= self.interval:
#             self.fetch_xyz()  # Fetch new coordinates from the API every interval
#             self.move_cube()  # Move cube based on interpolated position
#             self._last_time = current_time

# Example usage of the CubeMoverWithAPI class:
#
#
#
# Create an instance of the CubeMoverWithAPI
# cube_mover = CubeMoverWithAPI(cube_prim_path=cube_prim_path, api_url=api_url, headers=headers, interpolation_speed=0.1)
#
# Start the cube movement with coordinates fetched from the API
# cube_mover.start_moving()
#
# To stop the movement, you can call:
# cube_mover.stop_moving()


import time
import requests
from pxr import Usd, UsdGeom, Gf
import omni.usd
import carb.events
import omni.kit.app

class CubeMoverDataLayer:
    def __init__(self, cube_prim_path, api_url, headers, interpolation_speed=0.1):
        self.cube_prim_path = cube_prim_path  # Path of the cube prim in the USD scene
        self.api_url = api_url  # API endpoint to get coordinates
        self.headers = headers  # API headers
        self.moving = False  # Movement control flag
        self.interval = 2.0  # Movement interval in seconds
        self._last_time = time.time()

        self.prev_x = None  # Set initial position to None to handle the first move correctly
        self.prev_y = None
        self.prev_z = None

        self.target_x = 0.0  # Target x position from API
        self.target_y = 0.0  # Target y position from API
        self.target_z = 0.0  # Target z position from API

        self.interpolation_speed = interpolation_speed  # Speed of interpolation (0 < t < 1)
        self._subscription = None  # Initialize the subscription attribute

        # Subscribe to the app's shutdown event stream
        self.shutdown_stream = omni.kit.app.get_app().get_shutdown_event_stream()
        self.shutdown_sub = self.shutdown_stream.create_subscription_to_pop(self.on_shutdown_event,
                                                                            name="CubeMover_Shutdown_Subscription",
                                                                            order=0)

    def on_shutdown_event(self, e: carb.events.IEvent):
        """
        Handle the shutdown event, stopping all movement and subscriptions.
        """
        if e.type == omni.kit.app.POST_QUIT_EVENT_TYPE:
            print("Shutdown event received, stopping cube movement.")
            self.force_stop_moving()

    def fetch_xyz(self):
        """
        Fetch x, y, z coordinates from the API.
        Convert units to centimeters by multiplying by 100.
        Apply an offset of 1200 cm (12 meters) to x and y.
        """
        try:
            response = requests.post(self.api_url, headers=self.headers)
            response.raise_for_status()  # Raise an exception for HTTP errors
            data = response.json()  # Parse JSON response
            coordinates = data.get("data", {}).get("coordinates", {})
            x = coordinates.get("x", 0.0)
            y = coordinates.get("y", 0.0)
            z = coordinates.get("z", 0.0)

            # Print the original values from the API in meters
            print(f"Original API data: X: {x} meters, Y: {y} meters, Z: {z} meters")

            # Convert to centimeters and apply offsets
            # self.target_x = x * 100 + 1200  # Convert to cm and apply 12m offset
            # self.target_y = y * 100 + 1200  # Convert to cm and apply 12m offset
            # self.target_z = z * 100 +1200
            self.target_x = x * 100
            self.target_y = y * 100
            self.target_z = z * 100  # Convert to cm
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from API: {e}")

    def lerp(self, start, end, t):
        """
        Perform linear interpolation between start and end values with factor t.
        """
        return (1 - t) * start + t * end

    def move_cube(self):
        """
        Move the cube in Omniverse based on interpolated values to slow down the movement.
        """
        # Ensure we get the current stage
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()

        if not stage:
            print("No active stage found.")
            return

        # Get the cube's USD prim from the stage
        cube_prim = stage.GetPrimAtPath(self.cube_prim_path)
        if not cube_prim.IsValid():
            print(f"Prim not found at path: {self.cube_prim_path}")
            return

        # If this is the first move, set the previous position to the target position
        if self.prev_x is None:
            self.prev_x = self.target_x
            self.prev_y = self.target_y
            self.prev_z = self.target_z

        # Interpolate between the current and target positions
        x = self.lerp(self.prev_x, self.target_x, self.interpolation_speed)
        y = self.lerp(self.prev_y, self.target_y, self.interpolation_speed)
        z = self.lerp(self.prev_z, self.target_z, self.interpolation_speed)

        # Update previous positions to the new interpolated values
        self.prev_x = x
        self.prev_y = y
        self.prev_z = z

        # Get the Xform of the cube and update the existing translate operation
        xform = UsdGeom.Xformable(cube_prim)

        if not xform:
            print(f"Failed to retrieve Xformable for prim: {self.cube_prim_path}")
            return

        # Find the existing translate op and update it
        translate_op = xform.GetOrderedXformOps()[0]  # Assuming translate is the first op in the order
        translate_op.Set(Gf.Vec3f(x, y, z))

        # Print the interpolated position of the cube in centimeters
        print(f"Cube moved to (in cm): X: {x}, Y: {y}, Z: {z}")

    def start_moving(self):
        """
        Start moving the cube every 2 seconds by fetching coordinates from the API.
        """
        self.moving = True

        # Subscribe to the update stream for regular updates on the main thread
        self._subscription = omni.kit.app.get_app().get_update_event_stream().create_subscription_to_pop(self._on_update)

    def stop_moving(self):
        """
        Stop moving the cube.
        """
        self.moving = False  # Set the flag to False to stop moving
        if self._subscription:
            self._subscription.unsubscribe()  # Properly unsubscribe from the event stream
            self._subscription = None  # Clear the subscription reference to ensure no further calls
        print("Movement stopped successfully.")

    def force_stop_moving(self):
        """
        Forcefully stop all activities, including event subscriptions, data fetching, and cube movement.
        This will halt all operations and disable future actions.
        """
        # Check if the subscription exists and unsubscribe if it's active
        if self._subscription:
            try:
                self._subscription.unsubscribe()  # Properly unsubscribe from the event stream
                self._subscription = None  # Clear the subscription reference to ensure no further calls
                print("Event stream unsubscribed successfully.")
            except Exception as e:
                print(f"Failed to unsubscribe: {e}")
        else:
            print("No active subscription to unsubscribe.")

        # Stop all activities and prevent further fetching or movement
        self.moving = False  # Set the flag to False to stop any future movement
        print("Fetching and movement forcefully stopped.")

    def _on_update(self, event):
        """
        Callback function to handle updates from the event stream.
        This is called every frame, so we check the interval to move the cube.
        """
        if not self.moving:  # If self.moving is False, don't move the cube
            return

        current_time = time.time()
        if current_time - self._last_time >= self.interval:
            self.fetch_xyz()  # Fetch new coordinates from the API every interval
            self.move_cube()  # Move cube based on interpolated position
            self._last_time = current_time


# Example usage of the CubeMoverWithAPI class:

# API URL and headers
# api_url = "https://digital-twin.expangea.com/device/Cube/"
# headers = {
#     'X-API-KEY': '2c38e689-8bac-4ec6-9e0e-70e98222dc2d'
# }
#
# # Define the prim path of the cube you want to move
# cube_prim_path = "/World/Cube"  # Adjust this to your actual cube's prim path in the USD scene
#
# # Create an instance of the CubeMoverWithAPI
# cube_mover = CubeMoverWithAPI(cube_prim_path=cube_prim_path, api_url=api_url, headers=headers, interpolation_speed=0.1)
#
# # Start the cube movement with coordinates fetched from the API
# cube_mover.start_moving()

