# data_service.py
__all__ = ["DataService"]
import requests
import omni
import omni.usd
from pxr import UsdGeom
from pxr import UsdGeom, Gf
from typing import Optional, Tuple, Dict, Any
from datetime import datetime, timedelta
import time
# from paho.mqtt import client as mqtt_client
# from .custom_events import CustomEvents

class DataService:
    def __init__(self):
        self.base_url = "https://digital-twin.expangea.com/"
        self.headers = {
            'X-API-KEY': '2c38e689-8bac-4ec6-9e0e-70e98222dc2d'
        }

    def construct_api_url(self, endpoint: str) -> str:
        return f"{self.base_url}{endpoint}"

    def handle_api_request(self, api_url: str) -> Dict[str, Any]:
        try:
            response = requests.post(api_url, headers=self.headers)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            return response.json().get("data", {})
        except requests.RequestException as e:
            print(f"API request error: {e}")
            return {}

    def fetch_stock_info(self, endpoint: str) -> dict:
        api_url = self.construct_api_url(endpoint)
        return self.handle_api_request(api_url)
        # api_url = self.construct_api_url(endpoint)
        # stock_info = self.handle_api_request(api_url)
        # CustomEvents.emit_stock_info(stock_info)  # Emit the custom event with stock info
        # return stock_info

    def fetch_coordinates(self, endpoint: str) -> tuple:
        api_url = self.construct_api_url(endpoint)
        data = self.handle_api_request(api_url)

        coordinates = data.get("rack_location", {}).get("coordinates", {})
        # print(coordinates)
        return coordinates.get('x'), coordinates.get('y'), coordinates.get('z')

    def check_expiring_goods(self, stock_info, alert_days=7):
        today = datetime.today()
        expired_locations = []
        for location in stock_info.get("rack_locations", []):
            for pallet in location.get("pallets", []):
                inventory = pallet.get("inventory", {})
                exp_date_str = inventory.get("Expiry Date")
                if exp_date_str:
                    exp_date = datetime.strptime(exp_date_str, "%A, %B %d, %Y")
                    if 0 < (exp_date - today).days <= alert_days:
                        alert_message = f"ALERT: {inventory.get('Description1')} at Location ID {location.get('location_id')} is going to expire on {exp_date_str}"
                        print(alert_message)
                        self.send_omniverse_notification(alert_message)
                        expired_locations.append(location.get('location_id'))

        if not expired_locations:
            alert_message = "ALERT: No items found with expiry within the next {} days.".format(alert_days)
            print(alert_message)
            self.send_omniverse_notification(alert_message)

        return expired_locations


# Function to send a notification using Omniverse's notification system
def send_omniverse_notification(message):
    app = omni.kit.app.get_app()
    stage_notification = app.get_notification_manager()
    stage_notification.post_notification("Expiration Alert", message)


def move_camera(self, x: float, y: float, z: float):
    xform_path = "/Camera"
    view_camera_path = "/Camera/Camera_001/Camera_001_001"
    new_xyz_location =  Gf.Vec3d(x+220, y+50, z+70)
    new_rotation = Gf.Vec3f(75, 0.0, 0.0)
    focal_length = 20

    move_xform_and_set_view(xform_path, view_camera_path, new_xyz_location, new_rotation, focal_length=focal_length)
    print(f"Moved camera to location: {new_xyz_location}, with rotation: {new_rotation}, focal length: {focal_length}")

def move_xform_and_set_view(xform_path: str, view_camera_path: str, new_location: Optional[Gf.Vec3f] = None,
                            new_rotation: Optional[Gf.Vec3f] = None, focal_length: float = 20.0):
    xform_api = get_xform_by_path(xform_path)
    if not xform_api:
        print(f"Camera xform at '{xform_path}' not found or invalid!")
        return

    if new_location is not None:
        xform_api.SetTranslate(new_location)
    if new_rotation is not None:
        xform_api.SetRotate(new_rotation)
    stage = omni.usd.get_context().get_stage()
    view_camera_prim = stage.GetPrimAtPath(view_camera_path)
    if not view_camera_prim:
        print(f"View camera at '{view_camera_path}' not found!")
        return

    if not view_camera_prim.IsA(UsdGeom.Camera):
        print(f"Prim at '{view_camera_path}' is not a camera!")
        return


    view_camera = UsdGeom.Camera(view_camera_prim)
    view_camera.GetFocalLengthAttr().Set(focal_length)

    viewport_api = omni.kit.viewport.utility.get_active_viewport()
    viewport_api.camera_path = view_camera_prim.GetPath().pathString
    print(f"Moved xform of '{xform_api.GetPrim().GetName()}' and viewport is now viewing from '{view_camera_prim.GetName()}' with focal length {focal_length}")


def get_xform_by_path(prim_path: str) -> Optional[UsdGeom.XformCommonAPI]:
    stage = omni.usd.get_context().get_stage()
    prim = stage.GetPrimAtPath(prim_path)
    if prim.IsValid() and prim.IsA(UsdGeom.Xform):
        return UsdGeom.XformCommonAPI(prim)
    return None


def traverse(prim, name):
    if prim.GetName() == name:
        return prim
    for child in prim.GetAllChildren():
        result = traverse(child, name)
        if result:
            return result
    return None

def find_prim_by_name(stage, name):
    root_prim = stage.GetPseudoRoot()
    return traverse(root_prim, name)

def find_prim_then_select(name: str):
    # Get the stage from the Omniverse context
    stage = omni.usd.get_context().get_stage()

    # Find the prim by name
    prim = find_prim_by_name(stage, name)
    if not prim:
        print(f"Prim with name '{name}' not found!")
        return

    # Get the selection context
    selection = omni.usd.get_context().get_selection()

    # Select the item
    selection.clear_selected_prim_paths()
    selection.set_selected_prim_paths([prim.GetPath().pathString], True)

    print(f"Selected item with name '{name}' at path: '{prim.GetPath()}'")

def load_usd_file(file_path):
        context = omni.usd.get_context()
        if not context:
            print("Failed to get USD context.")
            return

        stage = context.get_stage()
        if not stage:
            print("Failed to get the USD stage. Ensure a stage is open or created.")
            return

        try:
            # Set the stage up axis and orientation
            UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
            UsdGeom.SetStageMetersPerUnit(stage, 1.0)  # Optional: set scale to meters

            ref_prim_path = '/root'
            # Ensure the root is an Xform
            stage.DefinePrim(ref_prim_path, 'Xform')
            ref_prim = stage.GetPrimAtPath(ref_prim_path)
            if not ref_prim.IsValid():
                print(f"Failed to define or get the reference prim at {ref_prim_path}.")
                return

            ref_prim.GetReferences().AddReference(file_path)
            print(f"Successfully referenced USD file at {file_path}")

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
            print(f"An error occurred while referencing the USD file: {str(e)}")
