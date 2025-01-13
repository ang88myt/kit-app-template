def on_model_updated(self, _):
    """Handles updates to the model and fetches stock information."""
    if not self.model or not self.model.get_item("name"):
        self._root.visible = False
        return

    selected_object = self.model.get_item("name")

    if selected_object:
        selected_object = self._get_lowest_child_name_of_kind(selected_object, child_kind="assembly")
        if not selected_object:
            self._root.visible = False
            return

        # Safely process the selected object
        selected_object = selected_object.split('/')[-1] if '/' in selected_object else selected_object
        selected_object = selected_object.replace("hpc_", "").replace("food_", "").replace("_", "")

        if not selected_object:
            self._root.visible = False
            return

    # Handle stock info fetching
    current_time = time.time()
    if selected_object != self._current_pallet_id or (current_time - self._last_fetch_time) > self._fetch_delay:
        self._current_pallet_id = selected_object
        self._last_fetch_time = current_time
        self._fetch_and_cache_stock_info()

    stock_info = self._cached_stock_info
    if stock_info:
        inventory = stock_info.get("inventory", {})
        fields_to_display = {
            "  Product": inventory.get("Product"),
            "  Pallet Number": inventory.get("Pallet Number"),
            "  Location": inventory.get("Location"),
            "  Warehouse Code": inventory.get("Warehouse Code"),
            "  Owner": inventory.get("Owner"),
            "  Lot Number": inventory.get("Lot Number"),
            "  Quantity on Hand in Loose": inventory.get("Quantity on Hand in Loose"),
            "  Description1": inventory.get("Description1"),
            "  Expiry Date": inventory.get("Expiry Date"),
            "  MANUFACTURING DATE": inventory.get("MANUFACTURING DATE"),
            "  Product Shelf Life": inventory.get("Product Shelf Life"),
            "  Balance Shelf Life to Expiry (days)": inventory.get("Balance Shelf Life to Expiry (days)"),
            "  Pallet Denomination": inventory.get("Pallet Denomination"),
            "  Stock Status Code": inventory.get("Stock Status Code"),
            "  Product Group": inventory.get("Product Group"),
        }

        self.info_text = "\n".join(
            [f"{key}: {value}" for key, value in fields_to_display.items() if value is not None]
        )
        logger.info(self.info_text)
        if self._name_label:
            self._name_label.text = self.info_text

        position = self.model.get_as_floats(self.model.get_item("position"))
        if position:
            self._root.transform = sc.Matrix44.get_translation_matrix(*position)
            self._root.visible = True
        else:
            self._root.visible = False
    else:
        self._root.visible = False


def _get_lowest_child_name_of_kind(self, object_path, child_kind="assembly"):
    """Recursively fetches the name of the lowest child object of a specified kind."""
    from omni.usd import get_context
    stage = get_context().get_stage()

    # Ensure object_path is valid
    if not object_path:
        return None

    # Get the prim at the specified path
    prim = stage.GetPrimAtPath(object_path) if stage else None
    if not prim or not prim.IsValid():
        return None  # Return None if the prim is not valid

    # Check if the current prim matches the desired kind
    if prim.GetTypeName() == child_kind:
        # Check if it has any children
        children = list(prim.GetChildren())
        if not children:
            return prim.GetPath().pathString  # Return the full path if no children exist
        # Recursively process the first child
        return self._get_lowest_child_name_of_kind(children[0].GetPath().pathString, child_kind)

    # If the current prim does not match the desired kind, check its children
    children = list(prim.GetChildren())
    for child in children:
        result = self._get_lowest_child_name_of_kind(child.GetPath().pathString, child_kind)
        if result:
            return result

    return None  # Return None if no matching kind is found


def _get_lowest_child_name_of_kind(self, object_path, child_kind="assembly"):
    """Recursively fetches the name of the lowest child object of a specified kind."""
    from omni.usd import get_context
    stage = get_context().get_stage()

    # Ensure object_path is valid
    if not object_path:
        return None

    # Get the prim at the specified path
    prim = stage.GetPrimAtPath(object_path) if stage else None
    if not prim or not prim.IsValid():
        return None  # Return None if the prim is not valid

    # Check if the current prim matches the desired kind
    if prim.GetTypeName() == child_kind:
        # Check if it has any children
        children = list(prim.GetChildren())
        if not children:
            return prim.GetPath().pathString  # Return the full path if no children exist
        # Recursively process the first child
        return self._get_lowest_child_name_of_kind(children[0].GetPath().pathString, child_kind)

    # If the current prim does not match the desired kind, check its children
    children = list(prim.GetChildren())
    for child in children:
        result = self._get_lowest_child_name_of_kind(child.GetPath().pathString, child_kind)
        if result:
            return result

    return None  # Return None if no matching kind is found
