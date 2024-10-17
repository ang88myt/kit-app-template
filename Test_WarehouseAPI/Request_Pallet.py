
import os
import requests
from pxr import Usd, UsdGeom, Gf
import omni.usd
# Function to fetch coordinates from API
def fetch_coordinates(api_url, headers):
    try:
        response = requests.post(api_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # Navigate through the JSON structure to get the coordinates
            coordinates = data.get('data', {}).get('coordinates', {})
            return coordinates.get('x'), coordinates.get('y'), coordinates.get('z')
        else:
            print(f"Failed to fetch coordinates: {response.status_code}")
            return None, None, None
    except Exception as e:
        print(f"Error fetching coordinates: {e}")
        return None, None, None
script_dir = "D:/Git/kit-app-toll-inno-unilever-l3/Test_WarehouseAPI"
file_path =  os.path.join(script_dir, 'testCube.usd')

# API details
api_url = "https://digital-twin.expangea.com/rack-location/3012011/"
headers = {
    'X-API-KEY': '2c38e689-8bac-4ec6-9e0e-70e98222dc2d'
}
x, y, z = fetch_coordinates(api_url, headers)
print(x, y, z)

if x is not None and y is not None and z is not None:
    # Get the current stage from the Omniverse context
    stage = omni.usd.get_context().get_stage()

    try:
        # Assuming there is a default root prim to which we can add the reference
        root_prim_path = '/test123'  # Replace this with the actual root prim path
        rootPrim = stage.GetPrimAtPath(root_prim_path)

        if not rootPrim.IsValid():
            raise Exception(f"No valid prim found at {root_prim_path}")
        rootPrim.GetReferences().AddReference(file_path)
        print(f"Successfully referenced USD file at {file_path}")

        # Apply the translation to the root prim
        xform = UsdGeom.Xformable(rootPrim)
        xform.AddTranslateOp().Set(Gf.Vec3f(x, y, z + 50))
        print(f"Placed at coordinates: ({x}, {y}, {z})")

    except Exception as e:
        print(f"An error occurred: {e}")
else:
    print("Failed to retrieve coordinates from API.")
