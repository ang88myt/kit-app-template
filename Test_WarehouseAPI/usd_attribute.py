import omni.usd
from pxr import Usd, Sdf


def add_category_with_attributes(prim_path, category_name, attributes):
    """
    Add a new category with multiple attributes to a prim.

    :param prim_path: Path to the prim in the USD stage.
    :param category_name: Name of the category (namespace).
    :param attributes: A dictionary of attribute names and their values.
    """
    # Get the stage
    stage = omni.usd.get_context().get_stage()

    # Get the prim
    prim = stage.GetPrimAtPath(prim_path)

    if not prim:
        print(f"Prim not found at path: {prim_path}")
        return

    # Add attributes in the category
    for attr_name, (value, value_type) in attributes.items():
        full_attr_name = f"{category_name}:{attr_name}"  # Use namespace
        if prim.HasAttribute(full_attr_name):
            print(f"Attribute '{full_attr_name}' already exists on prim '{prim_path}'.")
            continue
        # Create the attribute
        attribute = prim.CreateAttribute(full_attr_name, value_type)
        attribute.Set(value)
        print(f"Attribute '{full_attr_name}' created on prim '{prim_path}' with value: {value}")


# Example usage
prim_path = "/World/MyPrim"  # Replace with your prim path
category_name = "details"  # Name of the category (namespace)

# Define attributes: name -> (value, value_type)
attributes = {
    "color": ("red", Sdf.ValueTypeNames.String),
    "size": (10.5, Sdf.ValueTypeNames.Float),
    "weight": (25, Sdf.ValueTypeNames.Int),
    "material": ("steel", Sdf.ValueTypeNames.String),
    "isActive": (True, Sdf.ValueTypeNames.Bool),
}

add_category_with_attributes(prim_path, category_name, attributes)
