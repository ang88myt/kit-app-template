__all__ = ["JuliaModelerWindow"]

import omni.ext
import omni.ui as ui
from omni.kit.window.popup_dialog import MessageDialog
from .style import julia_modeler_style, ATTR_LABEL_WIDTH
from pxr import Usd, UsdGeom, Gf
import omni.usd
from omni.kit.viewport.utility import get_active_viewport, get_active_viewport_window, frame_viewport_selection

from .custom_pallet_info_button import CustomPalletInfoWidget
from .custom_bool_widget import CustomBoolWidget
from .custom_color_widget import CustomColorWidget
from .custom_combobox_widget import CustomComboboxWidget
from .custom_multifield_widget import CustomMultifieldWidget
from .custom_path_button import CustomPathButtonWidget
from .custom_radio_collection import CustomRadioCollection
from .custom_slider_widget import CustomSliderWidget
from .data_service import DataService, find_prim_then_select, move_camera
SPACING = 5

class JuliaModelerWindow(ui.Window):
    """The class that represents the window"""

    def __init__(self, title: str, delegate=None, **kwargs):
        self.__label_width = ATTR_LABEL_WIDTH
        self._data_service = DataService()
        super().__init__(title, **kwargs)

        # Apply the style to all the widgets of this window
        self.frame.style = julia_modeler_style

        # Set the function that is called to build widgets when the window is visible
        self.frame.set_build_fn(self._build_fn)

    def destroy(self):
        # Destroys all the children
        super().destroy()

    @property
    def label_width(self):
        """The width of the attribute label"""
        return self.__label_width

    @label_width.setter
    def label_width(self, value):
        """The width of the attribute label"""
        self.__label_width = value
        self.frame.rebuild()

    def _build_title(self):
        with ui.VStack():
            ui.Spacer(height=10)
            ui.Label("Unilever Extension", name="window_title")
            ui.Spacer(height=10)

    def _build_collapsable_header(self, collapsed, title):
        """Build a custom title of CollapsableFrame"""
        with ui.VStack():
            ui.Spacer(height=8)
            with ui.HStack():
                ui.Label(title, name="collapsable_name")

                image_name = "collapsable_opened" if collapsed else "collapsable_closed"
                ui.Image(name=image_name, width=10, height=10)

            ui.Spacer(height=8)
            ui.Line(style_type_name_override="HeaderLine")

    def _build_scene(self):
        """Build the widgets of the 'Scene' group"""
        with ui.CollapsableFrame("SCENE", name="group", build_header_fn=self._build_collapsable_header):
            with ui.VStack(height=0, spacing=SPACING):
                ui.Spacer(height=6)
                # Custom widget for getting pallet info with button callback
                self._pallet_info_widget = CustomPalletInfoWidget(
                    label="Pallet Info",
                    btn_callback=self._btn_callback  # Pass the button callback function
                )
                self._expiry_date = CustomPalletInfoWidget(
                    label="Expiry Date",
                    btn_callback=self._btn_callback  # Pass the button callback function
                )
                ui.Spacer(height=6)

    def _build_tracking(self):
        """Build the widgets of tracking devices"""
        with ui.CollapsableFrame("DEVICE TRACKING", name="group", build_header_fn=self._build_collapsable_header):
            with ui.VStack(height=0, spacing=SPACING):
                ui.Spacer(height=6)
                # Custom widget for tracking devices

                CustomBoolWidget(label="Track Equipments", default_value=False)
                CustomBoolWidget(label="Track Personals", default_value=False)
                CustomBoolWidget(label="Device 01", default_value=False)
                CustomBoolWidget(label="Device 02", default_value=False)
                ui.Spacer(height=6)

    def _build_camera_option(self):
        """Build the widgets of the 'Camera' group"""
        with ui.CollapsableFrame("CAMERA OPTION", name="group", build_header_fn=self._build_collapsable_header):
            with ui.VStack(height=0, spacing=SPACING):
                ui.Spacer(height=6)
                CustomMultifieldWidget(
                    label="Orientation",
                    default_vals=[0.0, 0.0, 0.0]
                )
                CustomSliderWidget(min=10, max=50, label="FOV", default_val=20)
                CustomColorWidget(1.0, 0.875, 0.5, label="Color")
                ui.Spacer(height=6)
                # CustomBoolWidget(label="Shadow", default_value=True)
                # CustomSliderWidget(min=0, max=2, label="Shadow Softness", default_val=.1)

    def _btn_callback(self):
        """Callback for the button press in CustomPalletInfoWidget"""
        self._fetch_and_move_camera()

    def _build_fn(self):
        """
        The method that is called to build all the UI once the window is visible.
        """
        with ui.ScrollingFrame(name="window_bg", horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF):
            with ui.VStack(height=0):
                self._build_title()
                self._build_scene()
                self._build_tracking()
                self._build_camera_option()


    def _fetch_and_move_camera(self):
        """Fetch stock info from endpoint and move the camera"""
        pallet_id = self._pallet_info_widget.get_input_value()
        endpoint = f"pallet/{pallet_id}/"
        print(f"Fetching stock info from endpoint: {endpoint}")

        find_prim_then_select(pallet_id)

        stock_info = self._data_service.fetch_stock_info(endpoint)
        if stock_info:
            limited_items = list(stock_info.items())[:11]
            info_text = "\n".join([f"{key}: {value}" for key, value in limited_items])
            print(info_text)

            if "rack_location" in stock_info and stock_info["rack_location"]:
                location_id = stock_info["rack_location"].get("location_id")
                location_endpoint = f"rack-location/{location_id}/"
                print(f"Fetching coordinates from endpoint: {location_endpoint}")

                x, y, z = self._data_service.fetch_coordinates(location_endpoint)
                print(x, y , z)
                if x is not None and y is not None and z is not None:
                    move_camera(x, y, z)
                else:
                    print("Failed to fetch coordinates")
            else:
                print("Failed to fetch stock info")
