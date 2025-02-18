__all__ = ["Custom_Window"]

import logging
from collections import defaultdict
from pxr import UsdGeom
import omni.usd
import omni.kit
import omni.ui as ui
import omni.kit.notification_manager as nm
# from omni.ui import color as cl
from .style import julia_modeler_style, ATTR_LABEL_WIDTH, WIN_WIDTH, WIN_HEIGHT
# from .custom_button import CustomButtonWidget
# from .custom_info_button import CustomInfoWidget
# from .custom_radio_collection import CustomRadioCollection
from .data_service import DataService,_show_notification, _isolate_selected_parent,_traverse, _frame_selected_object
# from .cube_mover_data import CubeMoverDataLayer
from .proximity_checker import ProximityChecker
from .custom_path_button import CustomPathButtonWidget
# from .custom_radio_collection import CustomRadioCollection
# from .custom_bool_widget import CustomBoolWidget
from .custom_button import  CustomButtonWidget

SPACING = 5
WINDOW_TITLE = ""


class Custom_Window(ui.Window):
    """The class that represents the window"""

    def __init__(self, title: str = "Review Panel",**kwargs):
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
            ui.Spacer(height=5)
            with ui.HStack():
                ui.Label(title, name="collapsable_name")
                image_name = "collapsable_opened" if collapsed else "collapsable_closed"
                ui.Image(name=image_name, width=10, height=10)
            ui.Spacer(height=5)
            # ui.Line(style_type_name_override="HeaderLine")


    def _build_update_scene(self):
        with ui.CollapsableFrame("UPDATE WAREHOUSE", name="group", build_header_fn=self._build_collapsable_header,collapsed=True):
            with ui.VStack(height=0, spacing=SPACING):
                CustomPathButtonWidget(label="Upload File",path="C:/Users/admin/Downloads/",btn_label="Upload",
                                       btn_callback=_show_notification("Upload", "File uploaded successfully.", "INFO"),
                                       )
                ui.Spacer(height=5)
                CustomButtonWidget(btn_label="Update Scene",
                                   tooltip="Update Warehouse Data",
                                   clicked_fn=self._update_scene)
            ui.Spacer(height=5)
            ui.Line(style_type_name_override="HeaderLine")
            ui.Spacer(height=5)


    def _download_scene(self):
        _show_notification(title="download", message="Downloaded Inventory 12/02/2025", status="INFO")

    def _update_scene(self):
        success = self._data_service.spawn_all_pallets()
        if success:
            _show_notification("Update Complete", "All pallets have been spawned successfully.", "INFO")
        else:
            _show_notification("Update Failed", "Failed to fetch rack data or spawn pallets.", "WARNING")

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

            # Storage Capacity Section
            # ui.Label("Storage Capacity", style={"font_size": 14, "color": "white"})
            # ui.Spacer(height=10)
            # Rack Space Usage
            #
            # with ui.HStack(spacing=SPACING):
            #     ui.Label("Rack Space Usage", style={"font_size": 16, "color": "white"})
            #     ui.Label("35% Used", style={"font_size": 16, "color": "gray", "alignment": ui.Alignment.RIGHT_CENTER})
            # ui.Spacer(height=10)
            # with ui.HStack(spacing=SPACING):
            #     progress_bar = ui.ProgressBar(style={"color": "lightblue"})
            #     progress_bar.model.set_value(0.65)
            # ui.Spacer(height=10)
            # # Staging Area Usage
            # with ui.HStack(spacing=SPACING):
            #     ui.Label("Staging Area Usage", style={"font_size": 16, "color": "white"})
            #     ui.Label("75% used", style={"font_size": 16, "color": "gray","alignment": ui.Alignment.RIGHT_CENTER})
            # ui.Spacer(height=10)
            # with ui.HStack(spacing=SPACING):
            #     progress_bar = ui.ProgressBar(style={"color": "lightblue"})
            #     progress_bar.model.set_value(0.35)  # 60% used
            # ui.Spacer(height=10)
            # ui.Line(style_type_name_override="HeaderLine")
            # ui.Spacer(height=10)
            # # Proximity Violations Section
            # with ui.CollapsableFrame("Proximity Violations", name="group",
            #                          build_header_fn=self._build_collapsable_header):
            #     with ui.VStack(spacing=10):
            #         # Display total violations count
            #         with ui.HStack(spacing=8):
            #             # ui.Spacer(width=30)
            #             ui.Label("3",
            #                      style={"font_size": 18, "color": "white","alignment": ui.Alignment.LEFT_CENTER})
            #
            #         # List of pallets with "Locate" buttons
            #         for _ in range(3):  # Placeholder for 3 pallets
            #                 with ui.HStack():
            #                         ui.Label("Pallet name", style={"font_size": 14, "color": "white"})
            #                         # ui.Image(
            #                         #     name="locate_icon", width=14, height=16  # Replace with actual icon/image name
            #                         # )
            #                         CustomButtonWidget(btn_label="Locate",
            #                                            tooltip="Locate the pallet",
            #                                            image_url="D:\Git\kit-app-template\source\extensions\my_company.my_python_ui_extension\icons\locate_icon.svg",
            #                                            image_width=15,
            #                                            image_height=15,
            #                                            btn_callback=lambda p=0: self._navigate_to_pallet(p)
            #                                            )
            # ui.Line(style_type_ame_override="HeaderLine")
            # ui.Spacer(spacing=8)
            # '''Critical Items Tracking Section'''
            # ui.Label("Critical Items Tracking", style={"font_size": 16, "color": "white"})
            # ui.Spacer(spacing=8)
            # with ui.VStack(spacing=8):
            #     # Critical items with icons
            #     for label, color, icon in [
            #         ("Damaged Items", "blue", "damaged_icon"),
            #         ("Expired Items", "red", "expired_icon"),
            #         ("Near Expiry", "green", "near_expiry_icon"),
            #         ("QAF Items", "orange", "qaf_icon")
            #     ]:
            #         with ui.HStack(spacing=10):
            #             # Icon Image
            #             ui.Image(name=icon, width=41, height=41)  # Customize size as needed
            #             with ui.CollapsableFrame(label, name="group", collapsed=False):
            #                 with ui.HStack(spacing=8):
            #                     # Label and Count
            #                     with ui.VStack():
            #                         # ui.Label(label, style={"font_size": 14, "color": color})
            #                         ui.Label("0", style={"font_size": 14, "color": "white"})
            #         with ui.VStack(spacing=10):
            #             # ui.Spacer(height=5)
            #             ui.Line(style_type_name_override="HeaderLine")
            #             # ui.Spacer(height=5)


    def _build_stock_status(self):
        '''Critical Items Tracking Section'''
        critical_status_count, critical_pallets_by_rack = self._data_service.fetch_status_code_data()
        total_critical_count = sum(critical_status_count.values())
        pallets_by_status = defaultdict(list)
        for rack_no, pallets in critical_pallets_by_rack.items():
            for pallet in pallets:
                stock_status_code = pallet["stock_status_code"]
                pallets_by_status[stock_status_code].append(pallet)


        with ui.VStack(spacing=8):
            # Critical items with icons and labels
            with ui.VStack(spacing=SPACING):
                ui.Label("Critical Items Tracking", style={"font_size": 18, "color": "white"})
                ui.Spacer(height=6)

                # Create a collapsible section for each type of critical item
                for label, color, icon, status_code_key in [
                    ("Damaged Items", "blue", "damaged_icon", "DMG"),
                    ("Expired Items", "red", "expired_icon", "EX"),
                    ("Near Expiry", "green", "near_expiry_icon", "NE"),
                    ("QAF Items", "orange", "qaf_icon", "QAF")
                ]:
                    with ui.HStack(spacing=10):
                        ui.Image(name=icon, width=41, height=41)
                        count = critical_status_count.get(status_code_key, 0)
                        with ui.CollapsableFrame(f'{label} : {count}', name="group",build_header_fn=self._build_collapsable_header, collapsed=True,):
                            with ui.VStack(spacing=10):
                                # ui.Label(
                                #     f"{count} ",
                                #     style={"font_size": 16, "white": "gray", "font_weight": "bold"}
                                # )
                                ui.Spacer(height=5)

                                if status_code_key in pallets_by_status:
                                    for pallet in pallets_by_status[status_code_key]:
                                        pallet_id = pallet["pallet_id"]
                                        with ui.HStack(spacing=10):
                                            ui.Label(f"PID: {pallet_id}",
                                                     style={"font_size": 18, "color": "white"})

                                            # Add button for locating the pallet
                                            CustomButtonWidget(
                                                btn_label="Locate",
                                                tooltip=f"Locate Pallet {pallet_id}",
                                                image_url="D:/Git/kit-app-template/source/extensions/my_company.my_python_ui_extension/icons/locate_icon.svg",
                                                image_width=15,
                                                image_height=15,
                                                clicked_fn=lambda p=pallet_id: self._navigate_to_pallet(p)
                                            )
                                ui.Spacer(heigh=10)
                                ui.Line(style_type_name_override="HeaderLine")
                                ui.Spacer(heigh=10)


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


    def _build_violation_check(self):
        """Build the UI for proximity violations with clear explanations."""
        # Initialize the ProximityChecker
        pro_checker = ProximityChecker(racks_range=(21, 39), distance_threshold=200.0)
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
                                         build_header_fn=self._build_collapsable_header):

                    with ui.VStack(spacing=SPACING):


                        # Display individual violations
                        for food_pallet_id, hpc_pallets in food_pallets_with_hpc.items():
                            with ui.HStack(spacing=SPACING):
                                ui.Label(f"PID: {food_pallet_id}", style={"font_size": 18, "color": "white"})
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

        # Get staging area utilization
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
        with ui.ScrollingFrame(name="window_bg", horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF):
            with ui.VStack(height=0):

                # self._build_update_scene()
                self._build_scene()
                # self._build_storage_utilization()
                # self._build_violation_check()
                # self._build_stock_status()
                # self._build_download_scene()
                # self._build_tracking()

                # self._build_search_panel()


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

