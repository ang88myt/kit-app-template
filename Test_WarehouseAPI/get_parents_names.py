from pxr import Usd, Sdf
import omni.usd


def get_selected_prim_hierarchy():
    """Retrieve the selected prim name and its parent hierarchy."""

    # Get the stage
    stage = omni.usd.get_context().get_stage()

    # Get selected prim paths
    selection = omni.usd.get_context().get_selection().get_selected_prim_paths()

    if not selection:
        print("No object selected.")
        return

    # Get the first selected prim
    prim_path = selection[0]
    prim = stage.GetPrimAtPath(prim_path)

    if not prim.IsValid():
        print("Invalid prim selected.")
        return

    # Collect hierarchy names
    hierarchy = []
    while prim:
        hierarchy.append(prim.GetName())  # Store the name
        prim = stage.GetPrimAtPath(prim.GetPath().GetParentPath())  # Move up in hierarchy

    # Print the hierarchy from root to selected prim
    hierarchy.reverse()
    # Ensure the hierarchy has enough elements to extract Rack, Location, SKU, PID
    if len(hierarchy) < 6:
        print("Hierarchy does not contain enough elements for Rack, Location, SKU, PID.")
        return
    rack, location, sku, pid = hierarchy[2:6]

    return rack, location, sku, pid
    print(hierarchy[2:6])

    # print(" > ".join(hierarchy))


# Run the function
get_selected_prim_hierarchy()
