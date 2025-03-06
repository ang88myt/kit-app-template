# import omni.usd
# from pxr import Usd, UsdGeom, Gf, UsdShade
# import logging
# import carb
#
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
# # Retrieve the current stage
# stage = omni.usd.get_context().get_stage()
#
# # Define the base parameters for the naming convention
# level = "3"
# rack_number = "40"
# rack_depth = "1"  # Assuming depth remains constant
# # Base coordinates for the first column
# x_start_1 = -4108
# y_start_1 = 1793
# z_base = 0.0
#
# # Distance between columns
# distance_between_columns = -140
#
# distance_half_between_columns = -70
#
# # Cube size-140
# cube_size = 100  # Adjust the cube size as needed
#
#
# # Function to create a rack column
# def create_rack_column(x_start, y_start, col_number):
#     # z_levels = [0, 220] + [220 + 175 * i for i in range(1, 5)]  # Z increments for 6 levels
#     z_levels = [0, 165] + [165 + 155 * i for i in range(1, 6)]  # Z increments for 6 levels
#     for rack_level, z in enumerate(z_levels, 1):
#         xform_name = f"{level}{rack_number}{rack_level}{col_number:02d}{rack_depth}"
#         xform_prim_path = f"/rack_location/_{xform_name}"
#
#         if not stage.GetPrimAtPath(xform_prim_path).IsValid():
#             xform = UsdGeom.Xform.Define(stage, xform_prim_path)
#             xform.AddTranslateOp().Set(Gf.Vec3d(x_start, y_start, z))
#             logger.warning(f"Created: {xform_prim_path} at ({x_start}, {y_start}, {z})")
#
#             # Spawn a cube as a child of this xform
#             spawn_cube_at_xform(xform_prim_path)
#
#
# # Function to spawn a cube at the location of each xform
# def spawn_cube_at_xform(xform_prim_path):
#     # Check if the xform exists
#     xform_prim = stage.GetPrimAtPath(xform_prim_path)
#     if not xform_prim.IsValid():
#         logger.error(f"Xform not found at {xform_prim_path}")
#         return
#
#     # Create a new cube as a child of the xform
#     cube_prim_path = f"{xform_prim_path}/Cube"
#     if not stage.GetPrimAtPath(cube_prim_path).IsValid():
#         cube = UsdGeom.Cube.Define(stage, cube_prim_path)
#         cube.GetSizeAttr().Set(cube_size)  # Set the cube size
#         cube.AddTranslateOp().Set(Gf.Vec3d(0, 0, cube_size / 2))  # Move the cube up by half its size
#         # material_path = "/Environment/Looks/Light_1900K_Green"
#         #
#         # _apply_material_to_prim(stage, prim_path=cube_prim_path, material_path=material_path)
#         logger.warning(f"Created Cube at {cube_prim_path}")
#     else:
#         logger.info(f"Cube already exists at {cube_prim_path}")
#
# def _apply_material_to_prim(stage, prim_path, material_path):
#     """Applies the specified material to the given prim."""
#     material_prim = stage.GetPrimAtPath(material_path)
#     if not material_prim:
#         carb.log_error(f"Material not found at path: {material_path}")
#         return
#
#     # Get the prim at the ref_prima_path and apply the material binding
#     prim = stage.GetPrimAtPath(prim_path)
#     if not prim:
#         carb.log_error(f"Prim not found at path: {prim_path}")
#         return
#
#     # Bind the material to the prim using UsdShade.MaterialBindingAPI
#     material_binding_api = UsdShade.MaterialBindingAPI(prim)
#     material_binding_api.Bind(UsdShade.Material(stage.GetPrimAtPath(material_path)))
#     carb.log_info(f"Material {material_path} applied to {prim_path}")
#
# # Create multiple rack columns and spawn cubes
# for col in range(58):
#     create_rack_column(x_start_1 + col * distance_between_columns, y_start_1, col + 1)

import omni.usd
from pxr import Usd, UsdGeom, Gf, UsdShade
import logging
import carb

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RackGenerator:
    # Mapping for rack depths based on rack numbers
    rack_depth_mapping = {
        21: "D2", 22: "D2", 23: "D2", 24: "D1", 25: "D1",
        26: "D2", 27: "D2", 28: "D2", 29: "D2", 30: "D2",
        31: "D1", 32: "D2", 33: "D2", 34: "D2", 35: "D2",
        36: "D1", 37: "D1", 38: "D2", 39: "D1", 40: "D1"
    }

    def __init__(self, level, rack_number, x_start, y_start, z_base, distance_between_columns, depth_offset=-140):
        self.stage = omni.usd.get_context().get_stage()
        self.level = level
        self.rack_number = rack_number
        self.rack_depth = self.rack_depth_mapping.get(int(rack_number), "D1")  # Default to D1 if rack number is not mapped
        self.x_start = x_start
        self.y_start = y_start
        self.z_base = z_base
        self.distance_between_columns = distance_between_columns
        self.depth_offset = depth_offset
        self.cube_size = 100  # Adjust the cube size as needed

    def create_rack_column(self, x_start, y_start, col_number, depth):
        z_levels = [0, 220] + [220 + 175 * i for i in range(1, 6)]  # Z increments for 6 levels  # Z increments for 6 levels
        for rack_level, z in enumerate(z_levels, 1):
            xform_name = f"{self.level}{self.rack_number}{rack_level}{col_number:02d}{depth}"
            xform_prim_path = f"/rack_location/_{xform_name}"

            if not self.stage.GetPrimAtPath(xform_prim_path).IsValid():
                xform = UsdGeom.Xform.Define(self.stage, xform_prim_path)
                xform.AddTranslateOp().Set(Gf.Vec3d(x_start, y_start, z))
                logger.warning(f"Created: {xform_prim_path} at ({x_start}, {y_start}, {z})")

                # Spawn a cube as a child of this xform
                self.spawn_cube_at_xform(xform_prim_path)

    def spawn_cube_at_xform(self, xform_prim_path):
        # Check if the xform exists
        xform_prim = self.stage.GetPrimAtPath(xform_prim_path)
        if not xform_prim.IsValid():
            logger.error(f"Xform not found at {xform_prim_path}")
            return

        # Create a new cube as a child of the xform
        cube_prim_path = f"{xform_prim_path}/Cube"
        if not self.stage.GetPrimAtPath(cube_prim_path).IsValid():
            cube = UsdGeom.Cube.Define(self.stage, cube_prim_path)
            cube.GetSizeAttr().Set(self.cube_size)  # Set the cube size
            cube.AddTranslateOp().Set(Gf.Vec3d(0, 0, self.cube_size / 2))  # Move the cube up by half its size
            logger.warning(f"Created Cube at {cube_prim_path}")
        else:
            logger.info(f"Cube already exists at {cube_prim_path}")

    def create_racks(self):
        start_col = 3 if int(self.rack_number) in {23, 26, 29, 32, 35} else 1
        for col in range(start_col, 59):  # Adjusted to start from column 3 for specific rack numbers
            if col == start_col:
                # No offset for the first column if starting from column 3
                x_start = self.x_start
            else:
                # Apply offset for subsequent columns
                x_start = self.x_start + (col - start_col) * self.distance_between_columns

            # Spawn cubes for both depths, with an offset for depth 2
            self.create_rack_column(x_start, self.y_start, col, depth="1")  # Depth 1 at initial position
            self.create_rack_column(x_start, self.y_start + self.depth_offset, col, depth="2")  # Depth 2 with offset

# Usage example with starting coordinates and depth offsets
rack_generator = RackGenerator(
    level="3",
    rack_number="26",
    x_start=-2649.99345,    # Starting x-coordinate for depth 1
    y_start=7263.4277,    # Starting y-coordinate
    z_base=0.0,
    distance_between_columns=-140,   # Column offset
    depth_offset=-135                # Depth 2 offset in x-direction
)
rack_generator.create_racks()
