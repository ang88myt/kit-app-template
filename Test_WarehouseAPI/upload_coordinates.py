import omni
import omni.usd
import requests
from pxr import UsdGeom
import csv
import os

class RackLocationUploader:
    BASE_URL = "https://digital-twin-dev.expangea.com/"
    ENDPOINT = "upload-rack-location/"
    HEADERS = {
        'X-API-KEY': '2c38e689-8bac-4ec6-9e0e-70e98222dc2d',
        'Content-Type': 'application/json'
    }

    def __init__(self, warehouse, floor_no, rack_no):
        self.warehouse = warehouse
        self.floor_no = floor_no
        self.rack_no = rack_no

    def get_selected_prim_paths(self):
        """Retrieve the paths of the selected prims in the USD stage."""
        stage = omni.usd.get_context().get_stage()
        selection = omni.usd.get_context().get_selection()
        selected_paths = selection.get_selected_prim_paths()
        if not selected_paths:
            raise RuntimeError("No objects selected in the scene.")
        return selected_paths

    def get_transform_from_prim(self, prim_path):
        """Get the XYZ transform of a prim at the given path."""
        stage = omni.usd.get_context().get_stage()
        prim = stage.GetPrimAtPath(prim_path)

        if not prim.IsValid():
            raise RuntimeError(f"Prim at path {prim_path} is not valid.")

        xformable = UsdGeom.Xformable(prim)
        transform_matrix = xformable.ComputeLocalToWorldTransform(0)
        translation = transform_matrix.ExtractTranslation()

        return translation

    def parse_prim_name(self, prim_path):
        """Extract the prim name from the path and use it as location_id without leading underscore."""
        prim_name = prim_path.split('/')[-1]
        location_id = prim_name.lstrip('_')  # Remove the leading underscore if present
        return location_id

    def upload_data(self, transforms):
        """Upload the transformed data directly to the API endpoint."""
        try:
            url = self.BASE_URL + self.ENDPOINT
            response = requests.post(url, headers=self.HEADERS, json=transforms)

            if response.status_code == 200:
                print(f"Data uploaded successfully: {response.json()}")
            else:
                print(f"Failed to upload data: {response.status_code}, {response.text}")

        except Exception as e:
            print(f"Error occurred during upload: {e}")

    def save_transforms_to_csv(self, transforms, csv_file_path="upload_rack_location.csv"):
        """Save the warehouse, floor_no, rack_no, location_id, and translations (XYZ) to a CSV file."""
        with open(csv_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['warehouse', 'floor_no', 'rack_no', 'location_id', 'x', 'y', 'z'])

            for entry in transforms:
                writer.writerow([
                    entry['warehouse'], entry['floor_no'], entry['rack_no'],
                    entry['location_id'], entry['x'], entry['y'], entry['z']
                ])
        print(f"Transforms saved to {csv_file_path}")

    def execute(self):
        """Main execution method for retrieving, saving, and uploading prim transforms."""
        try:
            selected_prim_paths = self.get_selected_prim_paths()

            # Prepare the data for upload and CSV saving
            transforms = []
            for prim_path in selected_prim_paths:
                translation = self.get_transform_from_prim(prim_path)
                location_id = self.parse_prim_name(prim_path)

                # Format the translation values to 2 decimal places
                rounded_translation = [round(coord, 2) for coord in translation]

                # Create a dictionary for the current prim's transform
                transform_data = {
                    "warehouse": self.warehouse,
                    "floor_no": self.floor_no,
                    "rack_no": self.rack_no,
                    "location_id": location_id,
                    "x": rounded_translation[0],
                    "y": rounded_translation[1],
                    "z": rounded_translation[2]
                }
                transforms.append(transform_data)

            # Save data to CSV
            self.save_transforms_to_csv(transforms)

            # Upload the prepared data
            self.upload_data(transforms)

        except Exception as e:
            print(f"Error: {e}")

# Example usage
warehouse = "5BTG"
floor_no = "3"
rack_no = "26"

uploader = RackLocationUploader(warehouse=warehouse, floor_no=floor_no, rack_no=rack_no)
uploader.execute()
