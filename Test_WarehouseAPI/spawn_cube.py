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
# rack_number = "26"
# rack_depth = "2"  # Assuming depth remains constant
# # Base coordinates for the first column
# x_start_1 = -2661
# y_start_1 = 7130
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
#     z_levels = [0, 220] + [220 + 175 * i for i in range(1, 5)]  # Z increments for 6 levels
#     # z_levels = [0, 165] + [165 + 155 * i for i in range(1, 6)]  # Z increments for 6 levels
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
# for col in range(56):
#     create_rack_column(x_start_1 + col * distance_between_columns, y_start_1, col + 1)
#


import omni.usd
from pxr import Usd, UsdGeom, Gf, UsdShade
import logging
import carb

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Retrieve the current stage
stage = omni.usd.get_context().get_stage()

# List of columns where cube creation should be skipped if col_start is 3
COLUMNS_TO_SKIP = [9, 10, 17, 18, 19, 26, 27, 28, 35, 36, 44, 52, 53]

def should_skip_cube(col_number, col_start):
    """Check if the cube should be skipped for specific columns."""
    return col_start >= 3 and col_number in COLUMNS_TO_SKIP

class SpawnObjects:
    def __init__(self, level, rack_number, x_start, y_start, z_base, distance_between_columns, cube_size, rack_depth, offset_y, col_start, col_end):
        self.level = level
        self.rack_number = rack_number
        self.x_start = x_start
        self.y_start = y_start
        self.z_base = z_base
        self.distance_between_columns = distance_between_columns
        self.cube_size = cube_size
        self.rack_depth = rack_depth  # Rack depth provided as part of parameters
        self.offset_y = offset_y  # Offset y could be +130 or -130
        self.col_start = col_start  # Starting column
        self.col_end = col_end  # Ending column

    def create_rack_column(self, x_start, y_start, col_number, rack_depth):
        # Skip both xform and cube creation for specific columns
        if should_skip_cube(col_number, self.col_start):
            logger.info(f"Skipping xform and cube creation for column {col_number} as col_start is {self.col_start}")
            return  # Skip xform and cube creation

        # Define z levels for different rack levels
        z_levels = [0, 220] + [220 + 175 * i for i in range(1, 5)]  # Z increments for 6 levels
        for rack_level, z in enumerate(z_levels, 1):
            xform_name = f"{self.level}{self.rack_number}{rack_level}{col_number:02d}{rack_depth-1}"
            xform_prim_path = f"/rack_location/_{xform_name}"

            if not stage.GetPrimAtPath(xform_prim_path).IsValid():
                xform = UsdGeom.Xform.Define(stage, xform_prim_path)
                xform.AddTranslateOp().Set(Gf.Vec3d(x_start, y_start, z))
                logger.warning(f"Created: {xform_prim_path} at ({x_start}, {y_start}, {z})")

                # Spawn a cube as a child of this xform
                self.spawn_cube_at_xform(xform_prim_path, col_number)

    def spawn_cube_at_xform(self, xform_prim_path, col_number):
        """Spawn a cube unless the column is in the skip list and col_start is 3."""
        # Check if the xform exists
        xform_prim = stage.GetPrimAtPath(xform_prim_path)
        if not xform_prim.IsValid():
            logger.error(f"Xform not found at {xform_prim_path}")
            return

        # Create a new cube as a child of the xform
        cube_prim_path = f"{xform_prim_path}/Cube"
        if not stage.GetPrimAtPath(cube_prim_path).IsValid():
            cube = UsdGeom.Cube.Define(stage, cube_prim_path)
            cube.GetSizeAttr().Set(self.cube_size)  # Set the cube size
            cube.AddTranslateOp().Set(Gf.Vec3d(0, 0, self.cube_size / 2))  # Move the cube up by half its size

            material_path = f"/Environment/Looks/Light_1900K_Green"

            self._apply_material_to_prim(stage, prim_path=cube_prim_path, material_path=material_path)
            logger.warning(f"Created Cube at {cube_prim_path}")

        else:
            logger.info(f"Cube already exists at {cube_prim_path}")

    def create_racks_with_depth(self):
        """Create rack columns with multiple depths and configurable offsets"""
        # Iterate through the columns from col_start to col_end
        for col in range(self.col_start, self.col_end + 1):  # Adjust based on col_start and col_end
            # First depth level (rack_depth)
            x_pos = self.x_start + (col - self.col_start) * self.distance_between_columns
            self.create_rack_column(x_pos, self.y_start, col, rack_depth=self.rack_depth)

            # Only spawn the second depth if rack_depth is greater than 1
            if self.rack_depth > 1:
                x_pos = self.x_start + (col - self.col_start) * self.distance_between_columns
                self.create_rack_column(x_pos, self.y_start + self.offset_y, col, rack_depth=self.rack_depth+1)

    def _apply_material_to_prim(stage, prim_path, material_path):
        """Applies the specified material to the given prim."""
        material_prim = stage.GetPrimAtPath(material_path)
        if not material_prim:
            carb.log_error(f"Material not found at path: {material_path}")
            return

        # Get the prim at the ref_prim_path and apply the material binding
        prim = stage.GetPrimAtPath(prim_path)
        if not prim:
            carb.log_error(f"Prim not found at path: {prim_path}")
            return

        # Bind the material to the prim using UsdShade.MaterialBindingAPI
        material_binding_api = UsdShade.MaterialBindingAPI(prim)
        material_binding_api.Bind(UsdShade.Material(stage.GetPrimAtPath(material_path)))
        carb.log_info(f"Material {material_path} applied to {prim_path}")
# Parameters





