# Import usd file from drive
from omni.isaac.kit import SimulationApp
from pxr import Usd, UsdGeom, Sdf, Gf

# Get the current stage from the Omniverse context
stage = omni.usd.get_context().get_stage()

# Assuming you want to load a USD file and reference it in the existing scene
file_path = 'C:/Users/admin/Downloads/testCube.usd'
try:
    # Load the USD file into a new layer and add a reference to it in the scene
    ref_prim_path = '/spawn'
    refPrim = stage.DefinePrim(ref_prim_path, 'Xform')
    refPrim.GetReferences().AddReference(file_path)
    print(f"Successfully referenced USD file at {file_path}")
except Exception as e:
    print(f"An error occurred while referencing the USD file: {str(e)}")

    # notification status: INFO, WARNING
