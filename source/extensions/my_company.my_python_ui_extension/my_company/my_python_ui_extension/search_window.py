__all__ = ["SearchWindowPanel"]

import logging
from collections import defaultdict
from pxr import UsdGeom
import omni.usd
import omni.kit
import omni.ui as ui
import omni.kit.notification_manager as nm
from omni.ui import color as cl
from .style import julia_modeler_style, ATTR_LABEL_WIDTH, WIN_WIDTH, WIN_HEIGHT
from .custom_button import CustomButtonWidget
from .custom_info_button import CustomInfoWidget
from .custom_radio_collection import CustomRadioCollection
from .data_service import DataService,_show_notification, _isolate_selected_parent,_traverse, _get_selected_prim_hierarchy


SPACING = 5
WINDOW_TITLE = ""


class SearchWindowPanel(ui.Window):
    """The class that represents the window"""

    def __init__(self, title: str = "Search Panel",**kwargs):
        super().__init__(title,dock="left", **kwargs)
        self.__label_width = ATTR_LABEL_WIDTH

        self._data_service = DataService()

        # self.top_level_parents = ['Show All', '/root', '/All_Racks', '/Critical_Items', '/World']
        self.frame.style = julia_modeler_style
        self.frame.set_build_fn(self._build_fn)

    @property
    def label_width(self):
        return self.__label_width

    @label_width.setter
    def label_width(self, value):
        self.__label_width = value
        self.frame.rebuild()

    def _build_collapsable_header(self, collapsed, title):
        """Build a custom title of CollapsableFrame"""
        with ui.VStack():
            ui.Spacer(height=6)
            with ui.HStack():
                ui.Label(title, name="collapsable_name")
                image_name = "collapsable_opened" if collapsed else "collapsable_closed"
                ui.Image(name=image_name, width=10, height=10)
            ui.Spacer(height=6)
            # ui.Line(style_type_name_override="HeaderLine")

    def _build_scene(self):
        """Builds the content for the search panel."""
        with ui.VStack(spacing=10, style={"padding": 8, "background_color": "#1e1e1e", "border_radius": 8}):
            # Title Section
            ui.Label("Warehouse Search", style={"font_size": 18, "font_weight": "bold", "color": "white"})
            ui.Label("Search for pallets, locations, or SKUs", style={"font_size": 14, "color": "#cccccc"})
            ui.Spacer(height=10)

            # with ui.ZStack():
            with ui.HStack(spacing=5):
                self.search_input = ui.StringField(
                    placeholder_text="Location or Pallet ID, or SKU",
                    height=24,
                    style={
                        "background_color": "transparent",
                        "border_radius": 4,
                        "color": "white",
                        "font_size": 14
                    }
                )
                # self.search_input.model.set_value("Search here")

                # ui.Image(name="search_icon", width=25, height=25, style={"opacity": 0.5})
                ui.Button(
                    image_url="D:\Git\kit-app-template\source\extensions\my_company.my_python_ui_extension\icons\mynaui_search.svg",  # Uses Omniverse built-in icons
                    width=45,
                    height=45,
                    image_width=15,
                    image_height=15,
                    alignment=ui.Alignment.CENTER,
                    fill_policy=ui.FillPolicy.PRESERVE_ASPECT_FIT,
                    click_fn=self._on_search_clicked
                )
                # CustomButtonWidget(
                #     btn_label="",
                #     tooltip=f"Search Item",
                #     image_url="D:/Git/kit-app-template/source/extensions/my_company.my_python_ui_extension/icons/mynaui_search.svg",
                #     image_width=15,
                #     image_height=15,
                #     btn_callback=self._on_search_clicked
                # )

            # Set the key press function to capture the Enter key
            # self.search_input.set_key_pressed_fn(self._handle_key_press)
            # ui.Spacer(height=10)
        rack, location, sku, pids = _get_selected_prim_hierarchy()
        total_pids = len(pids)  # Count the total number of PIDs

        ui.Spacer(height=10)
        ui.Line(style_type_name_override="HeaderLine")

        with ui.VStack(height=150):
            # Display the total count of PIDs
            ui.Label(
                "Total Search Result",
                style={"font_size": 14, "color": "#888888"},
            )
            # Display the location with an image and label in a horizontal stack
            with ui.HStack(spacing=5, width=10):
                ui.Image(name="location_icon", width=20, height=20, style={"opacity": 0.5})
                ui.Label(location, style={"font_size": 18, "color": "#888888"})

            ui.Line(style_type_name_override="HeaderLine")

            # Main collapsable frame for the warehouse
            with ui.CollapsableFrame(
                "Warehouse 5BTG",
                name="warehouse",
                build_header_fn=self._build_collapsable_header,
                collapsed=False,
                style={"font_size": 18, "color": "#888888"},
            ):
                with ui.VStack(spacing=5, height=0, name="warehouse_content", align_items=ui.Alignment.CENTER):
                    # Indent the Rack frame to the right
                    with ui.HStack():
                        ui.Spacer(width=35)  # Adjust width for proper indentation
                        with ui.CollapsableFrame(
                            rack,
                            name="rack",
                            build_header_fn=self._build_collapsable_header,
                            collapsed=False,
                            style={"font_size": 18, "color": "#888888"},
                        ):
                            # Ensure buttons are visible
                            with ui.VStack(spacing=15, align_items=ui.Alignment.CENTER):

                                ui.Label(f"Total Found: {total_pids} PIDs", style={"font_size": 14, "color": "#888888"})
                                # Render a button for each PID in the list
                                for pid in pids:
                                    ui.Button(
                                        pid,
                                        name=f"PID_{pid}",
                                        alignment=ui.Alignment.CENTER,
                                        style={"font_size": 18, "color": "#888888"},
                                    )

                    # Ensure vertical space is managed properly
                    ui.Line(style_type_name_override="HeaderLine")

    def _on_search_clicked(self):
        search_text = self.search_input.model.get_value_as_string()
        if search_text:
            print(f"Searching for: {search_text}")
            pallet_data = self._data_service.fetch_pallet_data(search_text)
            if pallet_data:
                _show_notification("Search Result", f"Found data for: {search_text}", "info")
            else:
                _show_notification("Search Failed", f"No data found for: {search_text}", "warning")
        else:
            _show_notification("Search Error", "Search input is empty.", "warning")

    def _handle_key_press(self, key, *args):
        """
        Trigger action only if the Enter key is pressed.
        The `key` argument is an integer representing the key code of the pressed key.
        """
        ENTER_KEY_CODE = 13  # Key code for Enter
        if key == ENTER_KEY_CODE:
            # Call a function that prints the user input
            self._print_user_input()

    def _print_user_input(self):
        """
        Fetch the current text in the input field and print it out.
        """
        user_text = self.search_input.model.get_value_as_string()
        if user_text.strip():
            # You can use print or logging, depending on your preference/environment.
            print(f"User typed: {user_text}")
            # Or logging:
            logging.warning(f"User typed: {user_text}")
        else:
            # For an empty string, you might want to show a message or log it
            print("No input provided.")


    def _build_fn(self):
        with ui.ScrollingFrame(name="window_bg", horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF):
            with ui.VStack(height=0):

                # self._build_update_scene()

                self._build_scene()


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
    print(" > ".join(hierarchy))


def show_notification(title: str, message: str, status: str):
    status_map = {
        "info": nm.NotificationStatus.INFO,
        "warning": nm.NotificationStatus.WARNING,
        # "error": nm.NotificationStatus.ERROR
    }
    status_enum = status_map.get(status, nm.NotificationStatus.INFO)

    nm.post_notification(
        text=message,
        hide_after_timeout=False,
        duration=0,
        status=status_enum
    )

