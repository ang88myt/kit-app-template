import omni.usd
from pxr import UsdGeom, Gf
import carb

def select_child_two_levels_below_at_xyz(target_x, target_y, target_z, threshold=0.001):
    """
    Finds a prim whose translation is near the target XYZ and then selects
    the child that is two levels below that prim.
    """
    usd_context = omni.usd.get_context()
    stage = usd_context.get_stage()
    if not stage:
        carb.log_error("❌ No valid USD stage loaded!")
        return

    target = Gf.Vec3d(target_x, target_y, target_z)

    def traverse_for_location(prim):
        if prim and prim.IsValid():
            xform = UsdGeom.Xform(prim)
            if xform:
                # Check if the prim has a translate op
                for op in xform.GetOrderedXformOps():
                    if op.GetOpType() == UsdGeom.XformOp.TypeTranslate:
                        trans = op.Get()
                        if trans and (Gf.Vec3d(trans) - target).GetLength() < threshold:
                            return prim
            # Continue to search in children if not found
            for child in prim.GetChildren():
                found = traverse_for_location(child)
                if found:
                    return found
        return None

    root = stage.GetPseudoRoot()
    found_prim = traverse_for_location(root)
    if not found_prim:
        carb.log_warn("⚠ No prim found near the target location!")
        return

    # Now, select the child two levels below found_prim
    children = found_prim.GetChildren()
    if not children:
        carb.log_warn(f"⚠ Prim {found_prim.GetPath()} has no children!")
        return

    first_child = children[0]
    second_children = first_child.GetChildren()
    if not second_children:
        carb.log_warn(f"⚠ Child {first_child.GetPath()} has no children (no second level)!")
        return

    target_child = second_children[0]
    prim_path = str(target_child.GetPath())
    usd_context.get_selection().set_selected_prim_paths([prim_path], True)
    carb.log_info(f"✅ Selected child two levels below prim at {found_prim.GetPath()}: {prim_path}")

# Example usage:
# Select the child two levels below a prim located near XYZ (1.0, 2.0, 3.0)
select_child_two_levels_below_at_xyz(-8821.76953, 7729.5498, 920.0)
