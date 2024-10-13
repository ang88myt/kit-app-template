# noinspection PyInterpreter
__all__ = ["Window"]

import logging
import omni.kit.notification_manager as nm
import omni.ui as ui

from .style import julia_modeler_style, ATTR_LABEL_WIDTH

import requests
from .custom_date_search_widget import CustomDateSearchWidget
from .custom_button import CustomButtonWidget
from .custom_info_button import CustomInfoWidget
from .custom_bool_widget import CustomBoolWidget
from .custom_color_widget import CustomColorWidget
from .custom_combobox_widget import CustomComboboxWidget
from .custom_multifield_widget import CustomMultifieldWidget
from .custom_path_button import CustomPathButtonWidget
from .custom_radio_collection import CustomRadioCollection
from .custom_slider_widget import CustomSliderWidget
from .data_service import DataService
from .cube_mover_data import CubeMoverDataLayer
from .spawn_cube import SpawnObjects
# from .chat_assist import MyAssistantExtension
import omni.kit.commands

SPACING = 5


class Window(ui.Window):
    """The class that represents the window"""

    def __init__(self, title: str, delegate=None, **kwargs):
        self.__label_width = ATTR_LABEL_WIDTH
        self._data_service = DataService()
        # self._chat_assist = MyAssistantExtension()
        self._pallet_info = None
        self._pallet_info = None
        self._info_label = None
        self.used_percentage = 40
        self.free_percentage = 60

        super().__init__(title, **kwargs)

        # Apply the style to all the widgets of this window
        self.frame.style = julia_modeler_style

        # Set the function that is called to build widgets when the window is visible
        self.frame.set_build_fn(self._build_fn)
        # self._show_pallet_notification()
        pallets_about_to_expire = [
            "UINT0000082525", "UINT0000082525", "UINT0000082521", "0UINT0000082522",
            "SYS16242516", "SYS16242525", "SYS16242523", "SYS16242522", "SYS16154632",
            "SYS16154632", "SYS16154607", "SYS16242524A", "SYS16242515A"
        ]

        # Create a message for the notification
        message = "Pallets about to expire in 1 week time:\n" + "\n".join(pallets_about_to_expire)
        _show_notification(message=message, title="Pallets Expire",status="warning")
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
        with ui.CollapsableFrame("Warehouse", name="group", build_header_fn=self._build_collapsable_header):
            with ui.VStack(height=0, spacing=SPACING):
                ui.Spacer(height=6)
                # Custom widget for getting pallet info with button callback
                CustomInfoWidget(
                    label="Pallet Info",
                    placeholder="PID",
                    btn_callback=self._btn_pallet_info  # Pass the button callback function
                )
                ui.Spacer(height=6)

                CustomButtonWidget(
                    btn_label="Show Damaged Goods",
                    btn_callback=self._btn_damaged_goods
                )
                ui.Spacer(height=6)

                CustomButtonWidget(
                    btn_label="Chat Assistant",
                    btn_callback=self._btn_chat
                )

    def _build_expiry(self):
        with ui.CollapsableFrame("Expiry", name="group", build_header_fn=self._build_collapsable_header):
            with ui.VStack(height=0, spacing=SPACING):
                ui.Spacer(height=6)
                CustomInfoWidget(
                    label="Expired Date Before",
                    placeholder="yyyy-mm-dd",
                    btn_callback=self._btn_exipry_date  # Pass the button callback function
                )
                ui.Spacer(height=6)

                CustomDateSearchWidget(label="Expired Date Range",
                                       placeholder1="dd-mm-yyyy",
                                       placeholder2="dd-mm-yyyy",
                                       btn_callback=self._btn_search_date_range
                                       )
                ui.Spacer(height=6)
                CustomInfoWidget(
                    label="Expiring Within",
                    placeholder="yyyy-mm-dd",
                    btn_callback=self._btn_exipring_1week  # Pass the button callback function
                )
                # combobox_widget=CustomComboboxWidget(
                #     label="Expiring Within",
                #     options=["One Week", "Two Week", "Three Week","One Month"]
                # )
                # combobox_widget.add_value_changed_callback(self._cbx_expiring_items)

                ui.Spacer(height=6)
                # ui.Label("Expired Pallets")
                # ui.Label(str(self._info_label), word_wrap=1)

    def _build_tracking(self):
        """Build the widgets of tracking devices"""
        with ui.CollapsableFrame("DEVICE TRACKING", name="group", build_header_fn=self._build_collapsable_header):
            with ui.VStack(height=0, spacing=SPACING):
                ui.Spacer(height=6)
                # Custom widget for tracking devices

                widget = CustomBoolWidget(
                    label="Track UWB",
                    default_value=False ,
                    on_change_callback=self._cbx_on_value_change
                )



                # CustomBoolWidget(
                #     label="Track Personals",
                #     default_value=False
                # )
                # CustomBoolWidget(
                #     label="Device 01",
                #     default_value=False
                # )
                # CustomBoolWidget(
                #     label="Device 02",
                #     default_value=False
                # )
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
                CustomButtonWidget(
                    "Reset View",
                    btn_callback=self._btn_reset_view
                )

    def _build_storage_utilization(self):
        """Build the widgets of the 'Scene' group"""
        with ui.CollapsableFrame("STORAGE UTILIZATION", name="group", build_header_fn=self._build_collapsable_header):
            with ui.VStack(height=0, spacing=SPACING):
                ui.Spacer(height=6)
                # CustomButtonWidget(
                #     btn_label="Rack Storage Utilization",
                #     btn_callback=self._btn_space_utilization
                # )
                ui.Spacer(height=6)
                ui.Label(f"Used: {self.used_percentage}%")
                with ui.HStack():
                    progress_bar = ui.ProgressBar()
                    # progress_bar.model.
                    progress_bar.model.set_value(self.used_percentage / 100)

                     #style={"background_color": ui.color.red}
                    ui.Spacer(width=10)

                # Free percentage bar (green)
                ui.Label(f"Free: {self.free_percentage}%")
                with ui.HStack():
                    progress_bar = ui.ProgressBar()
                    progress_bar.model.set_value(self.free_percentage / 100)
                    progress_bar.set_mouse_pressed_fn(self._pgb_on_mouse_pressed)

                    ui.Spacer(width=10)

    def build_utility(self):
        pass

    def _cbx_on_value_change(self, is_checked):
        # API URL and headers
        api_url = "https://digital-twin.expangea.com/device/Cube/"
        headers = {
            'X-API-KEY': '2c38e689-8bac-4ec6-9e0e-70e98222dc2d'
        }

        # Define the prim path of the cube you want to move
        cube_prim_path = "/World/Xform/Cube"  # Adjust this to your actual cube's prim path in the USD scene

        # Create an instance of the CubeMoverWithAPI
        cube_mover = CubeMoverDataLayer(cube_prim_path=cube_prim_path, api_url=api_url, headers=headers)

        if is_checked:
            #Start moving
            logging.warning("Cube Start")
            cube_mover.start_moving()
        else:
            #Start moving
            logging.warning("Cube Stop")
            cube_mover.stop_moving()

    def _pgb_on_mouse_pressed(self, x, y, button, modifiers):
        # self.window.set_position(100, 0)
        # Create a new window

        self.window = ui.Window(
            " ",
            width=150,
            height=120,
            flags=ui.WINDOW_FLAGS_NO_COLLAPSE| ui.WINDOW_FLAGS_NO_CLOSE | ui.WINDOW_FLAGS_NO_RESIZE  #|  ui.WINDOW_FLAGS_NO_MOV

        )

        # self.window.dock_in("right")

        self.window.frame.set_style({"background_color": (0, 0, 0, 0)})
        with self.window.frame:
            with ui.VStack(height=0, spacing=SPACING):
                ui.Label(f"Storage Usage", alignment=ui.Alignment.CENTER, style={"font_size": 18})
                ui.Spacer(height=1)

                ui.Label(f"Used: {self.used_percentage}%",
                         alignment=ui.Alignment.CENTER,
                         style={"color": ui.color.pink, "font_size": 18},

                         )
                ui.Label(f"Free: {self.free_percentage}%",
                         alignment=ui.Alignment.CENTER,
                         style={"color": ui.color.lightblue,"font_size": 18},

                             )
        # _show_notification(title="Free Storage %", message="Free Storage Space: 60%",status="info")
        # _show_notification(title="Used Storage %", message="Used Storage Space: 40%",status="warning")
        # level = "3"
        # rack_number = "9"
        # x_start_1 = -2670.00
        # y_start_1 = 8308.57
        # z_base = 0.0
        # distance_between_columns = -140
        # cube_size = 100  # Adjust the cube size as needed
        # rack_depth = 2  # Starting rack depth (set to 2)
        # offset_y = 130  # Offset for the second rack depth, can be +130 or -130
        # col_start = 1  # Start column
        # col_end = 58  # End column
        #
        # # Instantiate the SpawnObjects class with the parameters
        # spawner = SpawnObjects(level=level, rack_number=rack_number, x_start=x_start_1, y_start=y_start_1,
        #                        z_base=z_base, distance_between_columns=distance_between_columns, cube_size=cube_size,
        #                        rack_depth=rack_depth, offset_y=offset_y, col_start=col_start, col_end=col_end)
        # # Create racks with depth and offset
        # spawner.create_racks_with_depth()

    def _btn_exipring_1week(self, date):
        date="2024-10-08"
        material_path = "/Environment/Looks/Light_1900K_Yellow"
        self._data_service.check_expiry_date(date=date, material_path=material_path)


    def _btn_damaged_goods(self):
        pass

    def _btn_chat(self):
        pass
        # self._chat_assist.launch_assistant()

    def _btn_space_utilization(self):
        pass

    def _btn_search_date_range(self, date, other_date):
        material_path = "/Environment/Looks/Light_1900K_Red"
        self._data_service.check_expiry_date(date=date, other_date=other_date,material_path=material_path)

    def _btn_reset_view(self):
        pass

    def _btn_pallet_info(self, pallet_id):
        self._data_service.show_pallet_info(pallet_id)


    def _btn_exipry_date(self, date):
        material_path = "/Environment/Looks/Light_1900K_Red"
        self._data_service.check_expiry_date(date=date, material_path=material_path)

    def _build_fn(self):
        """
        The method that is called to build all the UI once the window is visible.
        """
        with ui.ScrollingFrame(name="window_bg", horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF):
            with ui.VStack(height=0):
                # self._build_title()
                self._build_storage_utilization()
                self._build_scene()
                self._build_expiry()
                self._build_tracking()
                self._build_camera_option()


def _show_notification(title: str, message: str, status: str):
    if status == "info":
        status = omni.kit.notification_manager.NotificationStatus.INFO
    elif status == "warning":
        status = omni.kit.notification_manager.NotificationStatus.WARNING
    elif status == "error":
        status = omni.kit.notification_manager.NotificationStatus.ERROR
    else:
        status = omni.kit.notification_manager.NotificationStatus.INFO  # Default to INFO if status is unknown

    # Create the notification without the OK button (can be added later if needed)
    omni.kit.notification_manager.post_notification(  # Added the title to the notification
        text=message,
        hide_after_timeout=False,  # Ensures the notification stays on until manually closed
        duration=0,  # Keeps the notification indefinitely until dismissed
        status=status
    )


