# import omni.usd
# from pxr import UsdGeom, Gf
#
#
# # Function to get the world-space position of a mesh object by its path
# def get_object_position(prim_path):
#     # Get the stage
#     stage = omni.usd.get_context().get_stage()
#
#     # Get the prim (object) at the specified path
#     prim = stage.GetPrimAtPath(prim_path)
#
#     if not prim.IsValid():
#         return None
#
#     # Get the object's transform and extract the translation (position)
#     xformable = UsdGeom.Xformable(prim)
#     transform_matrix = xformable.ComputeLocalToWorldTransform(0)
#     return transform_matrix.ExtractTranslation()
#
#
# # Function to check proximity between all mesh objects in the scene
# def check_proximity_for_all_mesh_objects(proximity_threshold):
#     # Get the stage (scene)
#     stage = omni.usd.get_context().get_stage()
#
#     # Get all the prims that are of type UsdGeom.Mesh
#     all_mesh_prims = [prim for prim in stage.Traverse() if prim.IsA(UsdGeom.Mesh)]
#
#     # Iterate through all pairs of mesh objects and check proximity
#     for i in range(len(all_mesh_prims)):
#         for j in range(i + 1, len(all_mesh_prims)):  # Avoid redundant comparisons
#             object1 = all_mesh_prims[i]
#             object2 = all_mesh_prims[j]
#
#             # Get positions of both mesh objects
#             position1 = get_object_position(object1.GetPath())
#             position2 = get_object_position(object2.GetPath())
#
#             # If either position is None (object not found), skip this pair
#             if position1 is None or position2 is None:
#                 continue
#
#             # Calculate the distance between the two objects
#             distance = (position1 - position2).GetLength()
#
#             # Check if the distance is within the proximity threshold
#             if distance < proximity_threshold:
#                 print(f"The mesh objects '{object1.GetName()}' and '{object2.GetName()}' are within proximity!")
#                 print(f"Distance: {distance}")
#
#
# # Example usage: Set the proximity threshold
# proximity_threshold = 300.0  # Set the proximity threshold (e.g., 10 units)
#
# # Call the function to check proximity for all mesh objects
# check_proximity_for_all_mesh_objects(proximity_threshold)

import omni.usd
import omni.kit.notification_manager as nm
from pxr import UsdGeom, Gf

class ProximityCheckScript:
    def __init__(self):
        # Initialize the stage (USD scene)
        self.stage = omni.usd.get_context().get_stage()

        # Set proximity threshold
        self.proximity_threshold = 10.0

    def on_play(self):
        # Called when the script starts playing
        print(f'{self.__class__.__name__}.on_play() -> Script started')
        self.check_proximity_for_all_mesh_objects()

    def on_stop(self):
        # Called when the script stops
        print(f'{self.__class__.__name__}.on_stop() -> Script stopped')

    def on_destroy(self):
        # Called when the script is destroyed
        print(f'{self.__class__.__name__}.on_destroy() -> Script destroyed')

    def on_update(self, current_time: float, delta_time: float):
        # Called on every frame update
        print(f'{self.__class__.__name__}.on_update(current_time={current_time}, delta_time={delta_time})')
        self.check_proximity_for_all_mesh_objects()

    # Function to get the world-space position of a mesh object by its path
    def get_object_position(self, prim_path):
        prim = self.stage.GetPrimAtPath(prim_path)
        if not prim.IsValid():
            return None
        xformable = UsdGeom.Xformable(prim)
        transform_matrix = xformable.ComputeLocalToWorldTransform(0)
        return transform_matrix.ExtractTranslation()

    # Function to show an error notification when objects are close
    def show_error_notification(self, message):
        nm.post_notification(
            text=message,
            hide_after_timeout=False,
            duration=0,
            status="error"
        )

    # Function to check proximity between all mesh objects
    def check_proximity_for_all_mesh_objects(self):
        # Get all the prims that are of type UsdGeom.Mesh
        all_mesh_prims = [prim for prim in self.stage.Traverse() if prim.IsA(UsdGeom.Mesh)]

        # Iterate through all pairs of mesh objects and check proximity
        for i in range(len(all_mesh_prims)):
            for j in range(i + 1, len(all_mesh_prims)):  # Avoid redundant comparisons
                object1 = all_mesh_prims[i]
                object2 = all_mesh_prims[j]

                # Get positions of both mesh objects
                position1 = self.get_object_position(object1.GetPath())
                position2 = self.get_object_position(object2.GetPath())

                if position1 is None or position2 is None:
                    continue

                # Calculate the distance between the two objects
                distance = (position1 - position2).GetLength()

                # Check if the distance is within the proximity threshold
                if distance < self.proximity_threshold:
                    message = f"Warning! The mesh objects '{object1.GetName()}' and '{object2.GetName()}' are within proximity! Distance: {distance}"
                    self.show_error_notification(message)

