# import omni.ui as ui
# import omni.usd
# import omni.kit.commands
# import carb
# from pxr import Sdf, Usd
#
# # Import missing functions
# from omni.kit.viewport.utility import get_active_viewport
# from omni.kit.commands import execute as frame_viewport_selection
#
# # ----- Function to Print User Properties -----
# def print_user_properties(prim):
#     """Prints only user-defined properties of the selected prim."""
#     user_props = prim.GetAttributes()
#
#     print(f"📌 User Properties for: {prim.GetPath().pathString}")
#     found = False  # Flag to check if there are any user properties
#
#     for attr in user_props:
#         if attr.GetNamespace() == "userProperties":  # ✅ Only print user properties
#             try:
#                 value = attr.Get()
#                 print(f"  - {attr.GetName()}: {value}")
#                 found = True
#             except Exception:
#                 print(f"  - {attr.GetName()}: <Error retrieving value>")
#
#     if not found:
#         print("  ❌ No user properties found.")
#
#
# # ----- Function to Build UI for Hierarchy -----
# def update_ui():
#     """Updates the UI dynamically based on the selected prim."""
#     stage = omni.usd.get_context().get_stage()
#     selection = omni.usd.get_context().get_selection().get_selected_prim_paths()
#
#     if not selection:
#         print("No selection made.")
#         return
#
#     selected_prim = stage.GetPrimAtPath(selection[0])
#
#     if not selected_prim.IsValid():
#         print("Selected prim is not valid.")
#         return
#
#     # Print user properties for the selected prim
#     print_user_properties(selected_prim)
#
# # ----- Subscribe to Selection Change Event -----
# def on_selection_changed(event):
#     """Triggers update when selection changes."""
#     if event.type == int(omni.usd.StageEventType.SELECTION_CHANGED):
#         update_ui()
#
# # Subscribe to selection changes
# usd_context = omni.usd.get_context()
# stage_event_stream = usd_context.get_stage_event_stream()
# stage_event_sub = stage_event_stream.create_subscription_to_pop(on_selection_changed, name="Selection Update")
#
#
# class HierarchyViewer:
#     def __init__(self):
#         self.window = ui.Window("Hierarchy Viewer", width=400, height=500)
#         self.matches = []
#         self.hierarchy_items = []
#         self._build_ui()
#
#     def _build_ui(self):
#         with self.window.frame:
#             with ui.VStack():
#                 ui.Spacer(height=4)
#
#                 # Search Bar
#                 self.search_field = ui.StringField()
#                 self.search_field.model.add_value_changed_fn(
#                     lambda _: self._filter_by_text(self.search_field.model.get_value_as_string())
#                 )
#
#                 ui.Spacer(height=4)
#
#                 # Display search results as collapsible hierarchy
#                 self.results_container = ui.VStack()
#
#                 ui.Spacer(height=7)
#
#     def _traverse(self, prim, name):
#         """Recursively searches for a prim by name and returns it."""
#         if prim.GetName() == name:
#             return prim
#         for child in prim.GetAllChildren():
#             result = self._traverse(child, name)
#             if result:
#                 return result
#         return None
#
#     def _filter_by_text(self, search_text):
#         """Searches for attributes within /Root/WH_5BTG matching search_text and updates the UI."""
#         if not search_text:
#             print("Search text is empty.")
#             return
#
#         print(f"🔍 Searching for attributes containing: '{search_text}' in '/Root/WH_5BTG'...")
#         stage = omni.usd.get_context().get_stage()
#         if not stage:
#             print("USD Stage not found.")
#             return
#
#         root_prim = self._traverse(stage.GetPrimAtPath("/Root"), "WH_5BTG")
#         if not root_prim or not root_prim.IsValid():
#             print(f"❌ Root prim '/Root/WH_5BTG' not found.")
#             return
#
#         self.matches = []
#         self.hierarchy_items = []
#
#         def search_children(prim):
#             for child in prim.GetAllChildren():
#                 for attr in child.GetAttributes():
#                     try:
#                         value = attr.Get()
#                         if isinstance(value, str) and search_text.lower() in value.lower():
#                             hierarchy = child.GetPath().pathString.split('/')
#                             self.matches.append((hierarchy, attr.GetName(), value))
#                             self.hierarchy_items.append(hierarchy[-1])
#                     except Exception:
#                         continue
#                 search_children(child)
#
#         search_children(root_prim)
#         self._update_results_ui()
#
#     def _update_results_ui(self):
#         """Updates the UI with collapsible frames for search results, ensuring correct button count."""
#         self.results_container.clear()
#         button_count = 0
#
#         with self.results_container:
#             ui.Label(f"Found {len(self.matches)} matches:")
#             for match in self.matches:
#                 hierarchy = match[0]
#                 attr_name = match[1]
#                 attr_value = match[2]
#
#                 with ui.CollapsableFrame(hierarchy[-2] if len(hierarchy) > 1 else "Root", height=0):
#                     with ui.VStack():
#                         ui.Label(f"📂 {hierarchy[-1]} ({attr_name} = {attr_value})")
#
#                         unique_items = set(self.hierarchy_items)
#
#                         for item in unique_items:
#                             ui.Button(
#                                 item,
#                                 height=25,
#                                 clicked_fn=lambda h=item: self._select_and_frame_object(h)
#                             )
#                             button_count += 1
#
#                 print(f"✔ Found in {'/'.join(hierarchy)} -> {attr_name} = {attr_value}")
#
#               ui.Label(f"Total Buttons: {button_count}")
#
#     def _select_and_frame_object(self, prim_path):
#         """Selects the specified object and then zooms into it in Omniverse."""
#         self._find_prim_then_select(prim_path)
#         self._frame_selected_object()
#
#     def _frame_selected_object(self):
#         """Frames or zooms into the currently selected object in Omniverse."""
#         stage = omni.usd.get_context().get_stage()
#         selection = omni.usd.get_context().get_selection().get_selected_prim_paths()
#
#         if not selection:
#             print("No object selected. Please select an object to frame.")
#             return
#
#         prim_to_frame = Sdf.Path(selection[0])  # Frame the first selected object
#         active_viewport = get_active_viewport()
#
#         if active_viewport:
#             frame_viewport_selection(active_viewport)
#             print(f"Framing object: {prim_to_frame}")
#         else:
#             omni.kit.commands.execute(
#                 'FramePrimsCommand',
#                 prim_to_move=prim_to_frame,
#                 prims_to_frame=[prim_to_frame.pathString],
#                 time_code=Usd.TimeCode.Default(),
#                 aspect_ratio=1.0,
#                 zoom=0.6
#             )
#             print(f"Executed framing command for: {prim_to_frame}")
#
#     def _find_prim_then_select(self, name: str):
#         """Finds a prim by name, selects it, and logs the selection."""
#         stage = omni.usd.get_context().get_stage()
#         prim = self._traverse(stage.GetDefaultPrim(), name)
#         if not prim:
#             carb.log_error(f"Prim with name '{name}' not found!")
#             return
#
#         selection = omni.usd.get_context().get_selection()
#         selection.clear_selected_prim_paths()
#         selection.set_selected_prim_paths([prim.GetPath().pathString], True)
#
#         carb.log_warn(f"Selected item with name '{name}' at path: '{prim.GetPath()}'")
#
#
# # Instantiate and show the UI
# viewer = HierarchyViewer()


import omni.ui as ui
import omni.usd
from omni.kit.widget.searchfield import SearchField
from pxr import Usd, UsdGeom, Gf, Sdf, Kind, UsdShade
from omni.kit.viewport.utility import get_active_viewport, frame_viewport_selection
import omni.kit.commands
# from .custom_button import CustomButtonWidget
import carb


class HierarchyViewer:
    def __init__(self):
        self.window = ui.Window("Search Viewer", width=400, height=500)
        self.matches = []
        self.previous_hierarchy = None
        self.hierarchy_items = []
        self.hierarchy_dict = {}
        self._build_ui()

    def _build_ui(self):
        with self.window.frame:
            with ui.VStack(height=5, style={"padding": 8, "background_color": "#1e1e1e", "border_radius": 6}):

                # ui.Spacer(height=4)
                self.search_field = SearchField(
                    on_search_fn=lambda filters: self._filter_by_text("".join(filters) if filters else ""),
                    show_tokens=False,
                    separator=None,
                    width=250,
                    height=25
                )
                # ui.Spacer(height=800)
                with ui.ScrollingFrame(height=600,
                                       style={"background_color": "#1e1e1e", "border_radius": 6,}
                                       ):
                    self.results_container = ui.VStack()
                ui.Spacer(height=7)

    def _traverse(self, prim, name):
        if prim.GetName() == name:
            return prim
        for child in prim.GetAllChildren():
            result = self._traverse(child, name)
            if result:
                return result
        return None

    def _filter_by_text(self, search_text):
        if not search_text:
            print("Search text is empty.")
            return

        print(f"🔍 Searching for attributes containing: '{search_text}' in '/Root/WH_5BTG'...")
        stage = omni.usd.get_context().get_stage()
        if not stage:
            print("USD Stage not found.")
            return

        root_prim = self._traverse(stage.GetPrimAtPath("/Root"), "WH_5BTG")
        if not root_prim or not root_prim.IsValid():
            print(f"❌ Root prim '/Root/WH_5BTG' not found.")
            return

        self.matches = []
        self.hierarchy_items = []
        self.hierarchy_dict = {}

        def search_children(prim):
            for child in prim.GetAllChildren():
                for attr in child.GetAttributes():
                    try:
                        value = attr.Get()
                        if isinstance(value, str) and search_text.lower() in value.lower():
                            hierarchy = child.GetPath().pathString.split('/')
                            self.matches.append((hierarchy, attr.GetName(), value))
                            parent_key = '/'.join(hierarchy[:-1])
                            if parent_key not in self.hierarchy_dict:
                                self.hierarchy_dict[parent_key] = []
                            self.hierarchy_dict[parent_key].append(hierarchy[-1])
                    except Exception:
                        continue
                search_children(child)

        search_children(root_prim)
        self._update_results_ui()

    def _update_results_ui(self):
        self.results_container.clear()
        with ui.VStack(height=10):
            with self.results_container:
                ui.Label(f"Found {len(self.matches)} matches:")
                for parent, children in self.hierarchy_dict.items():
                    parent = parent.split('/')
                    with ui.CollapsableFrame(parent[4], height=0):
                        for item in children:
                            ui.Button(
                                item,
                                tooltip=f"zoomed {item}",
                                clicked_fn=lambda h=item: self._select_and_frame_object(h)
                            )

    def _select_and_frame_object(self, prim_path):
        self._find_prim_then_select(prim_path)
        self._frame_selected_object()

    def _frame_selected_object(self):
        stage = omni.usd.get_context().get_stage()
        selection = omni.usd.get_context().get_selection().get_selected_prim_paths()

        if not selection:
            print("No object selected. Please select an object to frame.")
            return

        prim_to_frame = Sdf.Path(selection[0])
        active_viewport = get_active_viewport()

        if active_viewport:
            frame_viewport_selection(active_viewport)
            print(f"Framing object: {prim_to_frame}")
        else:
            omni.kit.commands.execute(
                'FramePrimsCommand',
                prim_to_move=prim_to_frame,
                prims_to_frame=[prim_to_frame.pathString],
                time_code=Usd.TimeCode.Default(),
                aspect_ratio=1.0,
                zoom=0.6
            )
            print(f"Executed framing command for: {prim_to_frame}")


    def _find_prim_by_name(self,stage, name):
        root_prim = stage.GetPseudoRoot()
        return self._traverse(root_prim, name)

    def _find_prim_then_select(self, name: str):
        # Get the stage from the Omniverse context
        stage = omni.usd.get_context().get_stage()

        # Find the prim by name
        prim = self._find_prim_by_name(stage, name)
        if not prim:
            carb.log_error(f"Prim with name '{name}' not found!")
            return

        # Get the selection context
        selection = omni.usd.get_context().get_selection()

        # Select the item
        selection.clear_selected_prim_paths()
        selection.set_selected_prim_paths([prim.GetPath().pathString], True)

        carb.log_warn(f"Selected item with name '{name}' at path: '{prim.GetPath()}'")



viewer = HierarchyViewer()

