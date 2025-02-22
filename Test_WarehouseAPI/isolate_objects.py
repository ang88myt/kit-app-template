def _isolate(self, is_check: bool, status_code: str):
    """Toggle isolation mode for Xform parent objects of a specific status code."""
    logging.info(f"Isolation mode {'activated' if is_check else 'deactivated'} for status: {status_code}.")

    stage = omni.usd.get_context().get_stage()

    if not stage:
        logging.error("USD stage could not be retrieved.")
        return

    # Use a more targeted approach to find relevant Xform parents
    def find_xform_by_status(stage, status_code):
        """Find Xform prims by status code."""
        for prim in stage.TraverseAll():
            if prim.IsA(UsdGeom.Xform) and status_code in prim.GetName():
                yield prim

    if is_check:
        # Isolate the specified status code
        self._isolated_status = status_code
        for prim in find_xform_by_status(stage, status_code):
            geom_prim = UsdGeom.Imageable(prim)
            geom_prim.GetVisibilityAttr().Set(UsdGeom.Tokens.inherited)

        # Hide all other Xforms
        for prim in stage.TraverseAll():
            if prim.IsA(UsdGeom.Xform) and status_code not in prim.GetName():
                geom_prim = UsdGeom.Imageable(prim)
                geom_prim.GetVisibilityAttr().Set(UsdGeom.Tokens.invisible)
    else:
        # Remove isolation and show all Xforms
        if self._isolated_status == status_code:
            self._isolated_status = None
            for prim in stage.TraverseAll():
                if prim.IsA(UsdGeom.Xform):
                    geom_prim = UsdGeom.Imageable(prim)
                    geom_prim.GetVisibilityAttr().Set(UsdGeom.Tokens.inherited)

    logging.info(f"Isolation {'applied' if is_check else 'removed'} for status: {status_code}.")
