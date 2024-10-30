import omni.usd
import csv
import omni.kit.commands

class ItemRenamer:
    def __init__(self, file_path):
        """Initialize with the path to the CSV file containing area and item mappings."""
        self.file_path = file_path
        self.rename_data = {}  # Dictionary to hold areas as keys and lists of item names as values

    def load_names_from_csv(self):
        """Loads item names from the CSV file and organizes them under specified areas, removing duplicates."""
        try:
            with open(self.file_path, mode='r', newline='') as file:
                reader = csv.DictReader(file)  # Use DictReader to access columns by name
                for row in reader:
                    area = row['Area']
                    item_name = row['Item']
                    if area not in self.rename_data:
                        self.rename_data[area] = []
                    # Only add the item if it's not a duplicate within the same area
                    if item_name not in self.rename_data[area]:
                        self.rename_data[area].append(item_name)

            # Print summary of loaded data
            for area, names in self.rename_data.items():
                print(f"Loaded {len(names)} unique items under {area} from CSV.")
        except Exception as e:
            print(f"Error reading CSV file: {e}")

    def get_selected_items(self):
        """Retrieves the currently selected items in Omniverse."""
        stage = omni.usd.get_context().get_stage()
        selection = omni.usd.get_context().get_selection().get_selected_prim_paths()
        print(f"Found {len(selection)} selected items.")
        return selection

    def rename_and_organize_items(self):
        """Renames selected items in Omniverse based on loaded names and organizes them under Xform nodes."""
        # Step 1: Load names from the CSV file
        self.load_names_from_csv()

        # Step 2: Get selected items in Omniverse
        selection = self.get_selected_items()

        # Flatten all names from the dictionary and check count
        all_names = [name for names in self.rename_data.values() for name in names]
        if len(selection) > len(all_names):
            print("Warning: More selected items than names in CSV. Aborting renaming.")
            return
        elif len(selection) < len(all_names):
            print("Warning: More names in CSV than selected items. Extra names will be ignored.")
            all_names = all_names[:len(selection)]  # Trim to match selected items

        # Step 3: Rename each selected item and organize under Xforms
        stage = omni.usd.get_context().get_stage()
        index = 0  # Keep track of which name we're using
        for area, names in self.rename_data.items():
            # Check if an Xform for the area already exists; if not, create it
            area_path = f"/World/{area}"
            if not stage.GetPrimAtPath(area_path):
                omni.kit.commands.execute("CreatePrimWithDefaultXform", prim_type="Xform", prim_path=area_path)
                print(f"Created Xform: {area_path}")
            else:
                print(f"Xform {area_path} already exists.")

            # Rename and reparent each item under the corresponding Xform
            for name in names:
                if index >= len(selection):
                    break  # Stop if we've renamed all selected items

                prim_path = selection[index]
                new_name = name
                new_prim_path = f"{area_path}/{new_name}"

                # Check if a prim with the new name already exists under the same Xform
                if stage.GetPrimAtPath(new_prim_path):
                    print(f"Warning: A prim with the name '{new_name}' already exists under '{area_path}'. Skipping rename for {prim_path}.")
                    continue

                # Rename and reparent
                try:
                    omni.kit.commands.execute(
                        "MovePrim",
                        path_from=prim_path,
                        path_to=new_prim_path
                    )
                    print(f"Renamed and moved {prim_path} to {new_prim_path}")
                except Exception as e:
                    print(f"Failed to rename and move {prim_path}: {e}")

                index += 1

# Usage example:
# Replace 'path/to/your/file.csv' with the actual path to your CSV file
file_path = 'C:/_update_/file.csv'
renamer = ItemRenamer(file_path)
renamer.rename_and_organize_items()
