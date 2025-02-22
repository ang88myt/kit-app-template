__all__ = ["Custom_Window"]

import logging
from collections import defaultdict
import omni.usd
import omni.kit
import omni.ui as ui

# from omni.ui import color as cl
from .style import julia_modeler_style, ATTR_LABEL_WIDTH, WIN_WIDTH, WIN_HEIGHT
from .spawn_pallets import RackDataHandler
from .data_service import DataService,_show_notification, _isolate_selected_parent,_traverse, _frame_selected_object
# from .cube_mover_data import CubeMoverDataLayer
from .proximity_checker import ProximityChecker

from .custom_button import  CustomButtonWidget
import carb
import omni.kit.commands
from pxr import Sdf

SPACING = 5
WINDOW_TITLE = ""


class Custom_Window(ui.Window):
    """The class that represents the window"""

    def __init__(self, title: str = "Review Panel",**kwargs):
        super().__init__(title,dock="left", **kwargs)
        self.__label_width = ATTR_LABEL_WIDTH
        self.additional_ui_visible = False
        self._build_fn()
        self._data_service = DataService()
        # self._rack_data_handler = RackDataHandler()
# rack_handler.process_racks()
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
            ui.Spacer(height=5)
            with ui.HStack():
                ui.Label(title, name="collapsable_name")
                image_name = "collapsable_opened" if collapsed else "collapsable_closed"
                ui.Image(name=image_name, width=10, height=10)
            ui.Spacer(height=5)
            # ui.Line(style_type_name_override="HeaderLine")


    def _build_update_scene(self):
        pass


    def _download_scene(self):
        _show_notification(title="download", message="Downloaded Inventory 12/02/2025", status="INFO")

    def _build_download_scene(self):
        with ui.VStack(height=0, spacing=SPACING):
            ui.Spacer(height=5)
            CustomButtonWidget(btn_label="Download report file",
                               tooltip="Download Warehouse Data",
                               clicked_fn=self._download_scene)
            ui.Spacer(height=5)
            ui.Line(style_type_name_override="HeaderLine")
            ui.Spacer(height=5)

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


    def _build_scene(self):
        """Build the widgets for the 'Overview' scene."""
        with ui.VStack(spacing=SPACING):
            ui.Spacer(height=10)
            # Overview Header
            ui.Label("Overview", style={"font_size": 22, "color": "white", "font_weight": "bold"})
            ui.Line(style_type_name_override="HeaderLine")
            ui.Spacer(height=10)

    def _build_stock_status(self):
        """Critical Items Tracking Section."""

        # # ✅ Ensure _data_service exists before calling methods
        # if not hasattr(self, "_data_service") or self._data_service is None:
        #     carb.log_error("❌ _data_service is missing! Cannot fetch stock status data.")
        #     return False

        # ✅ Fetch status code data
        critical_status_count, critical_pallets_by_rack = self._data_service.fetch_status_code_data()
        total_critical_count = sum(critical_status_count.values())

        # ✅ Organize pallets by status codes
        pallets_by_status = defaultdict(list)
        for rack_no, pallets in critical_pallets_by_rack.items():
            for pallet in pallets:
                stock_status_code = pallet["stock_status_code"]
                pallets_by_status[stock_status_code].append(pallet)

        # ✅ Ensure SPACING is defined
        SPACING = 5

        # ✅ Build UI
        with ui.VStack(spacing=8):
            with ui.VStack(spacing=SPACING):
                ui.Label("Critical Items Tracking", style={"font_size": 18, "color": "white"})
                ui.Spacer(height=6)

                # ✅ Create collapsible sections for each type of critical item
                for label, color, icon, status_code_key in [
                    ("Damaged Items", "blue", "damaged_icon", "DMG"),
                    ("Expired Items", "red", "expired_icon", "EX"),
                    ("Near Expiry", "green", "near_expiry_icon", "NE"),
                    ("QAF Items", "orange", "qaf_icon", "QAF")
                ]:
                    count = critical_status_count.get(status_code_key, 0)

                    with ui.HStack(spacing=10):
                        ui.Image(name=icon, width=41, height=41)

                        with ui.CollapsableFrame(
                            f'{label} : {count}',
                            name="group",
                            build_header_fn=self._build_collapsable_header,
                            collapsed=True
                        ):
                            with ui.VStack(spacing=10):
                                ui.Spacer(height=5)

                                # ✅ Display pallets if available
                                if status_code_key in pallets_by_status:
                                    for pallet in pallets_by_status[status_code_key]:
                                        pallet_id = pallet["pallet_id"]

                                        with ui.HStack(spacing=10):
                                            ui.Label(f"{pallet_id}", style={"font_size": 16, "color": "white"})

                                            # ✅ Button to locate the pallet
                                            CustomButtonWidget(
                                                btn_label="Locate",
                                                tooltip=f"Locate Pallet {pallet_id}",
                                                image_url="D:/Git/kit-app-template/source/extensions/my_company.my_python_ui_extension/icons/locate_icon.svg",
                                                image_width=15,
                                                image_height=15,
                                                clicked_fn=lambda
                                                    pallet_id=pallet["pallet_id"]: self._navigate_to_pallet(pallet_id)
                                            )

                                # ✅ Add a separator after each section
                                ui.Spacer(height=10)
                                ui.Line(style_type_name_override="HeaderLine")
                                ui.Spacer(height=10)

        return True  # ✅ Ensure function returns a valid result

    def _build_violation_check(self):
        """Build the UI for proximity violations with clear explanations."""
        # Initialize the ProximityChecker
        # # ✅ Ensure data service exists before calling methods
        # if not hasattr(self, "_data_service") or self._data_service is None:
        #     carb.log_error("❌ _data_service is missing! Cannot calculate storage utilization.")
        #     return False

        pro_checker = ProximityChecker(racks_range=(21, 41), distance_threshold=200.0)
        violations = pro_checker.proximity_check_all_racks()

        # Organize violations by food pallet
        food_pallets_with_hpc = defaultdict(list)
        for violation in violations:
            food_pallets_with_hpc[violation['food_pallet_id']].append({
                "hpc_pallet_id": violation['hpc_pallet_id'],
                "hpc_location_id": violation['hpc_location_id'],
                "distance": violation['distance']
            })
            # Spawn cubes for visualization (optional)
            self._spawn_violation_cubes(violation)

        # Save violations to a CSV file
        pro_checker.save_violations_to_csv()
        total_violations = len(food_pallets_with_hpc)
        # Build the UI for violations
        with ui.VStack(spacing=SPACING):
            with ui.HStack(spacing=SPACING):
                ui.Image(name="violation_icon", width=41, height=41)  # Add a meaningful icon for violations
                with ui.CollapsableFrame(f'Proximity Violations : {total_violations}', name="group",
                                         build_header_fn=self._build_collapsable_header,collapsed=True):

                    with ui.VStack(spacing=SPACING):


                        # Display individual violations
                        for food_pallet_id, hpc_pallets in food_pallets_with_hpc.items():
                            with ui.HStack(spacing=SPACING):
                                ui.Label(f"{food_pallet_id}", style={"font_size": 16, "color": "white"})
                                ui.Spacer(width=10)
                                # ui.Image(name="locate_icon", width=14, height=14)

                                CustomButtonWidget(
                                    btn_label="Locate",
                                    tooltip=f"Locate Pallet {food_pallet_id}",
                                    image_url="D:/Git/kit-app-template/source/extensions/my_company.my_python_ui_extension/icons/locate_icon.svg",
                                    image_width=15,
                                    image_height=15,
                                    clicked_fn=lambda p=food_pallet_id: self._navigate_to_pallet(p)
                                )
            # Add a dividing line at the bottom
            ui.Spacer(heigh=10)
            ui.Line(style_type_name_override="HeaderLine")
            ui.Spacer(height=10)


    def _spawn_violation_cubes(self, violation):
        food_coordinates = self._data_service.fetch_coordinates(f"pallet/{violation['food_pallet_id']}/")
        self._data_service.spawn_cube(
            prim_name="ProximityViolations",
            pallet_id=f'food_{violation["food_pallet_id"]}',
            coordinates=food_coordinates,
            material_path="/Environment/Looks/Light_1900K_Yellow",
            location_id=violation['food_location_id'],
            group=f"Rack_{violation.get('rack_no')}"
        )

        hpc_coordinates = self._data_service.fetch_coordinates(f"pallet/{violation['hpc_pallet_id']}/")
        self._data_service.spawn_cube(
            prim_name="ProximityViolations",
            pallet_id=f'hpc_{violation["hpc_pallet_id"]}',
            coordinates=hpc_coordinates,
            material_path="/Environment/Looks/Light_1900K_Red",
            location_id=violation['hpc_location_id'],
            group=f"Rack_{violation.get('rack_no')}"
        )

    def _navigate_to_pallet(self, search_text):
        self._data_service.show_pallet_info(search_text)

    def _build_storage_utilization(self):
        # Get overall storage utilization
        used_percentage, free_percentage = self._data_service.calculate_storage_utilization()

        # ✅ Get staging area utilization
        staging_area = self._data_service.calculate_staging_space_utilization()
        ui.Label("Storage Capacity", style={"font_size": 14, "color": "white"})
        ui.Spacer(height=10)
        # Rack Space Usage

        with ui.HStack(spacing=SPACING):
            ui.Label("Racks Space Usage",
                     style={"font_size": 18, "color": "white","alignment": ui.Alignment.LEFT})
            ui.Label(f'{used_percentage}% used',
                     style={"font_size": 18, "color": "gray", "alignment": ui.Alignment.RIGHT})
        ui.Spacer(height=10)
        with ui.HStack(spacing=SPACING):
            progress_bar = ui.ProgressBar(style={"color": "lightblue"})
            progress_bar.model.set_value(round(free_percentage) / 100)
        ui.Spacer(height=10)
        # # Staging Area Usage
        for area, stats in staging_area.items():
            with ui.HStack(spacing=SPACING):
                area_used_percentage = stats['Used Space %']
                area_free_percentage = stats['Free Space %']
                ui.Label(f"Staging Area Usage", style={"font_size": 18, "color": "whiye","alignment": ui.Alignment.LEFT})
                ui.Label(f'{area_used_percentage}% used',
                         style={"font_size": 18, "color": "gray", "alignment": ui.Alignment.RIGHT})
            ui.Spacer(height=10)
            with ui.VStack():
                progress_bar = ui.ProgressBar(style={"color": "lightblue"})
                progress_bar.model.set_value(area_free_percentage / 100)
                ui.Spacer(width=10)

        with ui.VStack(spacing=SPACING):
            ui.Spacer(heigh=10)
            ui.Line(style_type_name_override="HeaderLine")
            ui.Spacer(height=10)
        # # Staging Area Usage
        # with ui.HStack(spacing=SPACING):
        #     ui.Label("Staging Area Usage", style={"font_size": 16, "color": "white"})
        #     ui.Label("60% used", style={"font_size": 16, "color": "white", "alignment": ui.Alignment.RIGHT_CENTER})
        # with ui.HStack(spacing=SPACING):
        #     progress_bar = ui.ProgressBar(style={"color": "lightblue"})
        #
        #     progress_bar.model.set_value(0.6)  # 60% used
        # ui.Spacer(height=10)
        # ui.Line(style_type_name_override="HeaderLine")
        # ui.Spacer(height=10)



        # with ui.VStack(height=0, spacing=SPACING):
        #     ui.Spacer(height=6)
        #     ui.Label("Rack Space Usage")
        #     ui.Spacer(height=6)
        #     # ui.Label(f"Occupied: {used_percentage}%     Free: {free_percentage}%")
        #     # ui.Spacer(height=6)
        #     with ui.HStack():
        #         progress_bar = ui.ProgressBar()
        #         progress_bar.model.set_value(used_percentage / 100)
        #         ui.Spacer(width=10)

            # Loop through each staging area and display its utilization
            # for area, stats in staging_area.items():
            #     ui.Spacer(height=6)
            #     ui.Label(f"{area} Space Usage")
            #     ui.Spacer(height=6)
            #     area_used_percentage = stats['Used Space %']
            #     area_free_percentage = stats['Free Space %']
            #     # ui.Label(f"Occupied: {area_used_percentage}%     Free: {area_free_percentage}%")
            #     # ui.Spacer(height=6)
            #     with ui.HStack():
            #         progress_bar = ui.ProgressBar()
            #         progress_bar.model.set_value(area_used_percentage / 100)
            #         ui.Spacer(width=10)

    # def _cbx_on_value_change(self, is_checked):
    #     api_url = "https://digital-twin.expangea.com/device/Cube/"
    #     headers = {'X-API-KEY': '2c38e689-8bac-4ec6-9e0e-70e98222dc2d'}
    #     cube_prim_path = "/World/Xform/Cube"
    #
    #     cube_mover = CubeMoverDataLayer(cube_prim_path=cube_prim_path, api_url=api_url, headers=headers)
    #
    #     if is_checked:
    #         logging.warning("Cube Start")
    #         cube_mover.start_moving()
    #     else:
    #         logging.warning("Cube Stop")
    #         cube_mover.stop_moving()

    def _build_fn(self):
        # self.additional_ui_visible = False  # Track visibility state

        # with ui.ScrollingFrame(name="window_bg", horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF):
        #     with ui.VStack(height=0) as self.main_container:
        #         self._build_scene()
        #         self._build_update_scene()
        #
        #         # Button to toggle additional UI
        #         self.toggle_button = ui.Button(
        #             "Update Review",
        #             clicked_fn=self._toggle_additional_ui,
        #             height=30
        #         )
        #
        #         # Placeholder for additional UI sections
        #         self.additional_ui_container = ui.VStack(visible=False)  # Initially hidden
        with ui.ScrollingFrame(name="window_bg", horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF):
            with ui.VStack(height=0):
                self._build_storage_utilization()
                self._build_violation_check()
                self._build_stock_status()
                # self._build_download_scene()
                # self._build_tracking()

    def _toggle_additional_ui(self):
        """Toggles visibility of additional UI sections after ensuring a valid USD stage exists."""

        # ✅ Ensure the USD stage is loaded before proceeding
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()

        if stage is None:
            carb.log_warn("⚠ No valid USD stage loaded. Cannot update UI.")
            return  # Exit function safely

        self.additional_ui_visible = not self.additional_ui_visible
        self.additional_ui_container.visible = self.additional_ui_visible

        # Change button text based on visibility state
        self.toggle_button.text = "Hide Additional UI" if self.additional_ui_visible else "Show Additional UI"

        if self.additional_ui_visible:
            self.additional_ui_container.clear()
            with self.additional_ui_container:
                self._build_storage_utilization()
                self._build_violation_check()
                self._build_stock_status()


# def show_notification(title: str, message: str, status: str):
#     status_map = {
#         "info": nm.NotificationStatus.INFO,
#         "warning": nm.NotificationStatus.WARNING,
#         # "error": nm.NotificationStatus.ERROR
#     }
#     status_enum = status_map.get(status, nm.NotificationStatus.INFO)
#
#     nm.post_notification(
#         text=message,
#         hide_after_timeout=False,
#         duration=0,
#         status=status_enum
#     )

