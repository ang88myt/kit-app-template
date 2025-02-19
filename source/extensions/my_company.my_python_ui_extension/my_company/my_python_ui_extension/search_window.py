__all__ = ["SearchWindowPanel"]

# import logging
# from collections import defaultdict
# from pxr import UsdGeom
import omni.usd
import omni.kit
import omni.ui as ui
# from omni.ui import color as cl
from .custom_button import CustomButtonWidget
# from .custom_info_button import CustomInfoWidget
from .data_service import (DataService,
                           _show_notification,
                           _isolate_selected_parent,
                           _get_selected_prim_hierarchy,
                           _traverse, _find_prim_then_select,
                           _frame_selected_object
                           )
from omni.kit.widget.searchfield import SearchField
from pxr import Usd, UsdGeom, Gf, Sdf, Kind, UsdShade
from omni.kit.viewport.utility import get_active_viewport, frame_viewport_selection
import omni.kit.commands
import carb
# import pathlib
from .style import julia_modeler_style, ATTR_LABEL_WIDTH, WIN_WIDTH, WIN_HEIGHT

SPACING = 5
WINDOW_TITLE = ""

class SearchWindowPanel(ui.Window):
    """The class that represents the window"""

    def __init__(self, title: str = "Search Panel", **kwargs):
        super().__init__(title, dock="left", **kwargs)

        self.__label_width = ATTR_LABEL_WIDTH

        self._data_service = DataService()
        self.frame.style = julia_modeler_style
        self.frame.set_build_fn(self._build_fn)

        self.matches = []
        self.previous_hierarchy = None
        self.hierarchy_items = []
        self.hierarchy_dict = {}

    @property
    def label_width(self):
        return self.__label_width

    @label_width.setter
    def label_width(self, value):
        self.__label_width = value
        self.frame.rebuild()

    def _build_collapsable_header(self, collapsed, title, icon_image="default_icon"):
        """Build a custom title of CollapsableFrame"""
        with ui.VStack():
            ui.Spacer(height=SPACING)
            with ui.HStack():
                ui.Image(name=icon_image, width=18, height=18)
                ui.Spacer(width=SPACING)
                ui.Label(title, name="collapsable_name", style={"font_size": 14, "color": "white", "font_weight": "bold"})
                ui.Spacer(width=SPACING)
                image_name = "collapsable_opened" if collapsed else "collapsable_closed"
                ui.Spacer(width=ui.Fraction(2))
                ui.Image(name=image_name, width=18, height=18)
            ui.Spacer(height=SPACING)
            # ui.Line(style_type_name_override="HeaderLine")

    def _build_scene(self):
        """Builds the content for the search panel."""
        with ui.VStack(spacing=10, height=5, style={"padding": 8, "background_color": "#1e1e1e", "border_radius": 5}):
            # Title Section
            ui.Label("Warehouse Search", style={"font_size": 18, "font_weight": "bold", "color": "white"})
            ui.Label("Track and manage your assets here", style={"font_size": 14, "color": "#cccccc"})
            # ui.Spacer(height=10)

            self.search_field = SearchField(
                on_search_fn=lambda filters: self._filter_by_text("".join(filters) if filters else ""),
                # on_search_fn=print("test"),
                show_tokens=False,
                separator=None,
                width=250,
                height=25
            )
            # with ui.ScrollingFrame(height=600,
            #                        style={"background_color": "#1e1e1e", "border_radius": 6, }
            #                        ):
            self.results_container = ui.VStack()


    def _build_fn(self):
        with ui.ScrollingFrame(name="window_bg", horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF):
            with ui.VStack(height=0):
                # self._build_update_scene()

                self._build_scene()

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
                        else:

                            if parent_key not in self.hierarchy_dict:
                                self.hierarchy_dict[parent_key] = []
                            self.hierarchy_dict[parent_key].append(hierarchy[-1])
                    except Exception:
                        continue
                search_children(child)

        search_children(root_prim)

        self.results_container.clear()
        with ui.VStack(height=15):

            with self.results_container:
                if self.matches:
                    ui.Label(f"{len(self.matches)} result")
                    for parent, children in self.hierarchy_dict.items():
                        parent = parent.split('/')
                        ui.Spacer(height=15)
                        ui.Line(style_type_name_override="HeaderLine")
                        ui.Spacer(height=15)
                        with ui.HStack(height=SPACING):
                            ui.Image(name="sku_icon", height=20, width=20)
                            ui.Label(parent[5], style={"font_size": 16, "color": "white", "font_weight": "bold"})
                        ui.Spacer(height=15)
                        ui.Line(style_type_name_override="HeaderLine")
                        with ui.CollapsableFrame(title=parent[4],
                                                 build_header_fn=lambda collapsed,
                                                                        title: self._build_collapsable_header(
                                                     collapsed, title, "location_icon"),
                                                 icon_image="location_icon",
                                                 collapsed=True,
                                                 ):
                            with ui.CollapsableFrame(title=parent[3],
                                                     build_header_fn=lambda collapsed,
                                                                            title: self._build_collapsable_header(
                                                         collapsed, title, "rack_icon"),
                                                     icon_image="rack_icon",
                                                     collapsed=False,
                                                     ):

                                for item in children:
                                    # ui.Button(
                                    #     item,
                                    #     tooltip=f"zoom in {item}",
                                    #     clicked_fn=lambda h=item: self._select_and_frame_object(h)
                                    # )
                                    CustomButtonWidget(btn_label=item,
                                                       tooltip=f"zoom in {item}",
                                                       #image_url=f"{EXTENSION_FOLDER_PATH}/icons/material-symbols-light_pallet-outline.svg",
                                                       image_url="D:\Git\kit-app-template\source\extensions\my_company.my_python_ui_extension\icons\material-symbols-light_pallet-outline.svg",
                                                       spacing=2,
                                                       image_width=16,
                                                       image_height=16,
                                                       clicked_fn=lambda h=item: self._select_and_frame_object(h),
                                                       )
                else:
                    ui.Label(f"{len(self.matches)} result")
                    _show_notification("Search Alert", "Search Item Not found!", "WARNING")

            ui.Line(style_type_name_override="HeaderLine")

        # self._update_results_ui()

    def _update_results_ui(self):
        print("test")
        # self.results_container.clear()
        # with ui.VStack(height=10):
        #     with self.results_container:
        #         ui.Label(f"Found {len(self.matches)} matches:")
        #         for parent, children in self.hierarchy_dict.items():
        #             parent = parent.split('/')
        #             with ui.CollapsableFrame(parent[4], height=0):
        #                 for item in children:
        #                     ui.Button(
        #                         item,
        #                         tooltip=f"zoomed {item}",
        #                         clicked_fn=lambda h=item: self._select_and_frame_object(h)
        #                     )
        # ui.Line(style_type_name_override="HeaderLine")

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

    def _find_prim_by_name(self, stage, name):
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

# import logging
# from collections import defaultdict
# from pxr import UsdGeom
# import omni.usd
# import omni.kit
# import omni.ui as ui
# import omni.kit.notification_manager as nm
# from omni.ui import color as cl
# from .style import julia_modeler_style, ATTR_LABEL_WIDTH, WIN_WIDTH, WIN_HEIGHT
# from .custom_button import CustomButtonWidget
# from .custom_info_button import CustomInfoWidget
# from .custom_radio_collection import CustomRadioCollection
# from .data_service import DataService, _show_notification, _get_selected_prim_hierarchy
# from omni.kit.widget.searchfield import SearchField
#
# SPACING = 5
# WINDOW_TITLE = ""
#
#
# class SearchWindowPanel(ui.Window):
#     """Represents the search panel window."""
#
#     def __init__(self, title: str = "Search Panel",width=300, height=500, **kwargs):
#         super().__init__(title, dock="left", **kwargs)
#         self.__label_width = ATTR_LABEL_WIDTH
#         self._data_service = DataService()
#         self.frame.style = julia_modeler_style
#         self.frame.set_build_fn(self._build_fn)
#
#         # Subscribe to selection changes inside the class
#         usd_context = omni.usd.get_context()
#         self.stage_event_stream = usd_context.get_stage_event_stream()
#         self.stage_event_sub = self.stage_event_stream.create_subscription_to_pop(
#             self.on_selection_changed, name="Selection Update"
#         )
#
#     def destroy(self):
#         """Cleanup when window is closed."""
#         self.stage_event_sub = None  # Unsubscribe from event stream
#         super().destroy()
#
#     @property
#     def label_width(self):
#         return self.__label_width
#
#     @label_width.setter
#     def label_width(self, value):
#         self.__label_width = value
#         self.frame.rebuild()
#
#     def on_selection_changed(self, event):
#         """Triggers update when selection changes."""
#         if event.type == int(omni.usd.StageEventType.SELECTION_CHANGED):
#             self.update_ui()
#
#     def _build_scene(self):
#         """Builds the content for the search panel UI."""
#         with ui.VStack(spacing=10, style={"padding": 8, "background_color": "#1e1e1e", "border_radius": 8}):
#             # Title Section
#             ui.Label("Warehouse Search", style={"font_size": 18, "font_weight": "bold", "color": "white"})
#             ui.Label("Search for pallets, locations, or SKUs", style={"font_size": 14, "color": "#cccccc"})
#             ui.Spacer(height=10)
#
#             # Search Field UI
#             with ui.VStack():
#                 ui.Spacer(height=4)
#                 self.search_field = SearchField(
#                     on_search_fn=lambda filters: self._on_search_text_changed(self.search_field.get_search_text()),
#                     show_tokens=False,
#                     separator=None,
#                     width=250,
#                     height=25
#                 )
#
#     def on_search_fn(self, search_text: str):
#         """Performs a recursive search for matching prims under '/World/SamplePalletForTest'."""
#         stage = omni.usd.get_context().get_stage()
#         parent_path = "/Root/WH_5BTG"
#         parent_prim = stage.GetPrimAtPath(parent_path)
#
#         if not parent_prim.IsValid():
#             print(f"Parent prim {parent_path} not found.")
#             return []
#
#         def traverse_descendants(prim):
#             """Recursively traverses all children of a prim."""
#             for child in prim.GetChildren():
#                 yield child
#                 yield from traverse_descendants(child)
#
#         results = []
#         for prim in traverse_descendants(parent_prim):
#             for attr in prim.GetAttributes():
#                 try:
#                     value = attr.Get()
#                 except Exception:
#                     continue
#                 if isinstance(value, str) and search_text.lower() in value.lower():
#                     results.append(prim.GetPath().pathString)
#                     break
#
#         return results
#
#
#     def _on_result_clicked(self, prim_path: str):
#         """Handles when a search result is clicked."""
#         self._data_service.show_pallet_info(prim_path)
#         show_notification("Search", f"Zoomed into: {prim_path}", "info")
#
#     def _build_fn(self):
#         """Builds the main UI layout."""
#         with ui.ScrollingFrame(name="window_bg",
#                                # horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF
#                                ):
#             with ui.VStack(height=0):
#                 self._build_scene()
#
#
# # Utility Functions
# def get_selected_prim_hierarchy():
#     """Retrieves the selected prim name and its parent hierarchy."""
#     stage = omni.usd.get_context().get_stage()
#     selection = omni.usd.get_context().get_selection().get_selected_prim_paths()
#     if not selection:
#         print("No object selected.")
#         return None
#
#     prim_path = selection[0]
#     prim = stage.GetPrimAtPath(prim_path)
#     if not prim.IsValid():
#         print("Invalid prim selected.")
#         return None
#
#     hierarchy = []
#     while prim:
#         hierarchy.append(prim.GetName())
#         prim = stage.GetPrimAtPath(prim.GetPath().GetParentPath())
#
#     hierarchy.reverse()
#     print(" > ".join(hierarchy))
#     return hierarchy
#
#
# def show_notification(title: str, message: str, status: str):
#     """Displays notifications with different statuses."""
#     status_map = {
#         "info": nm.NotificationStatus.INFO,
#         "warning": nm.NotificationStatus.WARNING,
#     }
#     status_enum = status_map.get(status, nm.NotificationStatus.INFO)
#
#     nm.post_notification(
#         text=message,
#         hide_after_timeout=False,
#         duration=0,
#         status=status_enum
#     )
#
# def print_user_properties(selected_prim):
#     """Prints all attributes that start with 'userProperties:' for the selected prim."""
#     if not selected_prim.IsValid():
#         print("Selected prim is not valid.")
#         return
#
#     print(f"\nSelected Prim: {selected_prim.GetPath()}")
#
#     for attr in selected_prim.GetAttributes():
#         if attr.GetName().startswith("userProperties:"):
#             print(f"{attr.GetName()} = {attr.Get()}")
