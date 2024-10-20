# import omni
# import omni.usd
# import csv
# from pxr import UsdGeom
# import os
# import requests
#
#
# def get_selected_prim_paths():
#     """Retrieve the paths of the selected prims in the USD stage."""
#     stage = omni.usd.get_context().get_stage()
#     selection = omni.usd.get_context().get_selection()
#     selected_paths = selection.get_selected_prim_paths()
#     if not selected_paths:
#         raise RuntimeError("No objects selected in the scene.")
#     return selected_paths
#
#
# def get_transform_from_prim(prim_path):
#     """Get the XYZ transform of a prim at the given path."""
#     stage = omni.usd.get_context().get_stage()
#     prim = stage.GetPrimAtPath(prim_path)
#
#     if not prim.IsValid():
#         raise RuntimeError(f"Prim at path {prim_path} is not valid.")
#
#     xformable = UsdGeom.Xformable(prim)
#     transform_matrix = xformable.ComputeLocalToWorldTransform(0)
#     translation = transform_matrix.ExtractTranslation()
#
#     return translation
#
#
# def parse_prim_name(prim_path):
#     """Extract the prim name from the path and use it as location_id without leading underscore."""
#     # Example prim_path: /rack_location/_3221011/Pallet_SYS16187572
#     prim_name = prim_path.split('/')[-1]
#     location_id = prim_name.lstrip('_')  # Remove the leading underscore if present
#     return location_id
#
#
# def save_transforms_to_csv(transforms, csv_file_path):
#     """Save the warehouse, rack_no, location_id, and translations (XYZ) to a CSV file."""
#     with open(csv_file_path, mode='w', newline='') as file:
#         writer = csv.writer(file)
#         writer.writerow(['warehouse', 'floor_no', 'rack_no', 'location_id', 'x', 'y', 'z'])
#
#         for entry in transforms:
#             writer.writerow(entry)
#
#
# # Execute immediately when the script is run
# try:
#     selected_prim_paths = get_selected_prim_paths()
#
#     transforms = []
#     for prim_path in selected_prim_paths:
#         translation = get_transform_from_prim(prim_path)
#         location_id = parse_prim_name(prim_path)
#         # Assuming warehouse is fixed, and rack_no is 22 as per your example
#         warehouse = "5BTG"
#         floor_no = "3"
#         rack_no = "32"
#         # Format the translation values to 2 decimal places
#         rounded_translation = [round(coord, 2) for coord in translation]
#         transforms.append(
#             [warehouse, floor_no, rack_no, location_id, rounded_translation[0], rounded_translation[1], rounded_translation[2]])
#
#     csv_file_path = os.path.join('D:\\Toll Innovation\\TC Level 3 Demo\\_Update', 'upload_rack_location.csv')
#     # csv_file_path = os.path.join('C:\\Users\\aungt\\Downloads\\TC Level 3 Demo', 'upload_rack_location.csv')
#     save_transforms_to_csv(transforms, csv_file_path)
#
#     print(f"Transforms of selected objects saved to {csv_file_path}")
# except Exception as e:
#     print(f"Error: {e}")

import omni
import omni.usd
import requests
from pxr import UsdGeom
import csv
import os

# Define constants
BASE_URL = "https://digital-twin.expangea.com/"
API_ENDPOINT = "upload-rack-location/"
HEADERS = {
    'X-API-KEY': '2c38e689-8bac-4ec6-9e0e-70e98222dc2d',
    'Content-Type': 'application/json'
}


def get_selected_prim_paths():
    """Retrieve the paths of the selected prims in the USD stage."""
    stage = omni.usd.get_context().get_stage()
    selection = omni.usd.get_context().get_selection()
    selected_paths = selection.get_selected_prim_paths()
    if not selected_paths:
        raise RuntimeError("No objects selected in the scene.")
    return selected_paths


def get_transform_from_prim(prim_path):
    """Get the XYZ transform of a prim at the given path."""
    stage = omni.usd.get_context().get_stage()
    prim = stage.GetPrimAtPath(prim_path)

    if not prim.IsValid():
        raise RuntimeError(f"Prim at path {prim_path} is not valid.")

    xformable = UsdGeom.Xformable(prim)
    transform_matrix = xformable.ComputeLocalToWorldTransform(0)
    translation = transform_matrix.ExtractTranslation()

    return translation


def parse_prim_name(prim_path):
    """Extract the prim name from the path and use it as location_id without leading underscore."""
    # Example prim_path: /rack_location/_3221011/Pallet_SYS16187572
    prim_name = prim_path.split('/')[-1]
    location_id = prim_name.lstrip('_')  # Remove the leading underscore if present
    return location_id


def upload_data(transforms):
    """Upload the transformed data directly to the API endpoint."""
    try:
        url = BASE_URL + API_ENDPOINT
        response = requests.post(url, headers=HEADERS, json=transforms)

        if response.status_code == 200:
            print(f"Data uploaded successfully: {response.json()}")
        else:
            print(f"Failed to upload data: {response.status_code}, {response.text}")

    except Exception as e:
        print(f"Error occurred during upload: {e}")
def save_transforms_to_csv(transforms, csv_file_path):
    """Save the warehouse, floor_no, rack_no, location_id, and translations (XYZ) to a CSV file."""
    with open(csv_file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['warehouse', 'floor_no', 'rack_no', 'location_id', 'x', 'y', 'z'])

        for entry in transforms:
            writer.writerow([entry['warehouse'], entry['floor_no'], entry['rack_no'],
                             entry['location_id'], entry['x'], entry['y'], entry['z']])

# Execute immediately when the script is run
try:
    selected_prim_paths = get_selected_prim_paths()

    # Prepare the data for upload and CSV saving
    transforms = []
    for prim_path in selected_prim_paths:
        translation = get_transform_from_prim(prim_path)
        location_id = parse_prim_name(prim_path)

        # Assuming warehouse and rack number are predefined
        warehouse = "5BTG"
        floor_no = "3"
        rack_no = "26"

        # Format the translation values to 2 decimal places
        rounded_translation = [round(coord, 2) for coord in translation]

        # Create a dictionary for the current prim's transform
        transform_data = {
            "warehouse": warehouse,
            "floor_no": floor_no,
            "rack_no": rack_no,
            "location_id": location_id,
            "x": rounded_translation[0],
            "y": rounded_translation[1],
            "z": rounded_translation[2]

        }

        transforms.append(transform_data)

    # Define the path for saving the CSV file
    # csv_file_path = os.path.join('D:\\Toll Innovation\\TC Level 3 Demo\\_Update', 'upload_rack_location.csv')
    csv_file_path = os.path.join('C:\\_Update_', 'upload_rack_location.csv')
    # Save data to CSV
    save_transforms_to_csv(transforms, csv_file_path)
    print(f"Transforms saved to {csv_file_path}")

    # Upload the prepared data
    upload_data(transforms)

except Exception as e:
    print(f"Error: {e}")

