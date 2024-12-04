import logging
from collections import defaultdict
from pxr import UsdGeom
import omni.usd
import omni.kit
import omni.ui as ui
import omni.kit.notification_manager as nm
from omni.ui import color as cl
from .style import julia_modeler_style, ATTR_LABEL_WIDTH
from .custom_button import CustomButtonWidget
from .custom_info_button import CustomInfoWidget
from .custom_bool_widget import CustomBoolWidget
from .custom_color_widget import CustomColorWidget
from .custom_multifield_widget import CustomMultifieldWidget
from .custom_slider_widget import CustomSliderWidget
from .custom_combobox_widget import CustomComboboxWidget
from .data_service import DataService
from .cube_mover_data import CubeMoverDataLayer
from .proximity_checker import ProximityChecker
from .custom_path_button import CustomPathButtonWidget
SPACING = 5
WINDOW_TITLE = "Unilever Extension"
COLORS = {
    "DMG": "blue",
    "NE": "yellow",
    "QAF": "purple",
    "EX": "red"
}

class Custom_Window(ui.Window):
    """The class that represents the window"""

    def __init__(self, title: str, delegate=None, **kwargs):
        super().__init__(title, **kwargs)
        self.__label_width = ATTR_LABEL_WIDTH
        self._data_service = DataService()
        self.used_percentage = 40
        self.free_percentage = 60
        self.top_level_parents = ['Show All', '/root', '/All_Racks', '/Critical_Items', '/World']
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
            ui.Spacer(height=8)
            with ui.HStack():
                ui.Label(title, name="collapsable_name")
                image_name = "collapsable_opened" if collapsed else "collapsable_closed"
                ui.Image(name=image_name, width=10, height=10)
            ui.Spacer(height=8)
            ui.Line(style_type_name_override="HeaderLine")

    def _build_scene(self):
        """Build the widgets of the 'Scene' group"""
        with ui.CollapsableFrame("WAREHOUSE", name="group", build_header_fn=self._build_collapsable_header):
            with ui.VStack(height=0, spacing=SPACING):
                ui.Spacer(height=6)
                CustomInfoWidget(label="Pallet ID", placeholder="PID", btn_callback=self._btn_pallet_info)
                ui.Spacer(height=6)
                CustomInfoWidget(label="Product ID", placeholder="PID", btn_callback=self._btn_product_info)
                ui.Spacer(height=6)
                CustomInfoWidget(label="Location ID", placeholder="LID", btn_callback=self._btn_location_info)
                ui.Spacer(height=6)
                # CustomButtonWidget(btn_label="Stock Status", tooltip="Critical Stock Status", btn_callback=self._build_stock_status)
                # ui.Spacer(height=6)
                CustomComboboxWidget(label="Isolate Selection",options=self.top_level_parents, _call_back=self._isolate_selected_parent)
                # CustomPathButtonWidget(lable="File Upload", )

    def _isolate_selected_parent(self, selected_parent):
        logging.warning("Isolation mode activated.")

        # Get the USD stage
        stage = omni.usd.get_context().get_stage()

        # If "Show All" is selected, make sure all top-level parents are visible
        if selected_parent == "Show All" or not selected_parent:
            print("Showing all parents.")
            for parent in self.top_level_parents:
                if parent == "Show All":
                    continue  # Skip the "Show All" entry
                prim = stage.GetPrimAtPath(parent)
                if prim.IsValid():
                    geom_prim = UsdGeom.Imageable(prim)
                    if geom_prim:
                        geom_prim.GetVisibilityAttr().Set(UsdGeom.Tokens.inherited)
            return

        # Show the selected parent and hide all others
        for parent in self.top_level_parents:
            if parent == "Show All":
                continue  # Skip the "Show All" entry
            prim = stage.GetPrimAtPath(parent)
            if prim.IsValid():
                geom_prim = UsdGeom.Imageable(prim)
                if geom_prim:
                    visibility = UsdGeom.Tokens.inherited if parent == selected_parent else UsdGeom.Tokens.invisible
                    geom_prim.GetVisibilityAttr().Set(visibility)

    def _btn_location_info(self,location_id):
        self._data_service.show_location_info(location_id)

    def _btn_product_info(self):
        pass

    def _build_stock_status(self):
        """Creates the Omniverse UI with CollapsableFrames for each rack, shows total critical status codes found at the top, and buttons for critical pallets."""
        critical_status_count, critical_pallets_by_rack = self._data_service.fetch_status_code_data()
        total_critical_count = sum(critical_status_count.values())

        with ui.CollapsableFrame("CRITICAL STOCK STATUS", name="group", build_header_fn=self._build_collapsable_header, collapsed=True):
            with ui.VStack(spacing=2):
                ui.Label(f"Grand Total Critical Items Found: {total_critical_count}", style={"font_size": 18, "color": "orange"})

                for status_code, count in critical_status_count.items():
                    color = COLORS.get(status_code, "white")
                    ui.Label(f"{status_code}| {count} items", style={"font_size": 14, "color": color, "alignment": ui.Alignment.LEFT_CENTER})

                ui.Spacer(height=2)

                pallets_by_status = defaultdict(list)
                for rack_no, pallets in critical_pallets_by_rack.items():
                    for pallet in pallets:
                        stock_status_code = pallet["stock_status_code"]
                        pallets_by_status[stock_status_code].append(pallet)

                for stock_status_code, pallets in pallets_by_status.items():
                    with ui.CollapsableFrame(f"Status Code: {stock_status_code}", name="group", build_header_fn=self._build_collapsable_header, collapsed=True):
                        with ui.ScrollingFrame(height=200):
                            with ui.VStack(spacing=6):
                                for pallet in pallets:
                                    pallet_id = pallet["pallet_id"]
                                    location_id = pallet["location_id"]
                                    CustomButtonWidget(f"Pallet ID: {pallet_id}", tooltip=f"Location ID: {location_id}", btn_callback=lambda p=pallet_id: self._navigate_to_pallet(p))

    def _build_violation_check(self):
        pro_checker = ProximityChecker(racks_range=(19, 41), distance_threshold=200.0)
        violations = pro_checker.proximity_check_all_racks()

        food_pallets_with_hpc = defaultdict(list)
        for violation in violations:
            food_pallets_with_hpc[violation['food_pallet_id']].append({
                "hpc_pallet_id": violation['hpc_pallet_id'],
                "hpc_location_id": violation['hpc_location_id'],
                "distance": violation['distance']
            })

            self._spawn_violation_cubes(violation)

        total_violations = pro_checker.get_total_violations()
        pro_checker.save_violations_to_csv()

        with ui.CollapsableFrame("PALLET VIOLATIONS", name="group", build_header_fn=self._build_collapsable_header, collapsed=True):
            with ui.ScrollingFrame(height=800):
                with ui.VStack(spacing=10):
                    ui.Label(f"Total Violations Found: {total_violations}", style={"font_size": 18, "color": "orange"})
                    ui.Spacer(height=10)

                    for food_pallet_id, hpc_pallets in food_pallets_with_hpc.items():
                        with ui.CollapsableFrame(f"Food Pallet ID: {food_pallet_id}", collapsed=True):
                            with ui.VStack(spacing=5):
                                for hpc_pallet in hpc_pallets:
                                    hpc_pallet_id = hpc_pallet['hpc_pallet_id']
                                    hpc_location_id = hpc_pallet['hpc_location_id']
                                    distance = hpc_pallet['distance']
                                    CustomButtonWidget(
                                        f"HPC Pallet ID: {hpc_pallet_id} | Distance: {distance} units",
                                        tooltip=f"Location ID: {hpc_location_id}",
                                        btn_callback=lambda p=hpc_pallet_id: self._navigate_to_pallet(p)
                                    )

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

    def _navigate_to_pallet(self, pallet_id):
        self._data_service.show_pallet_info(pallet_id)

    def _build_storage_utilization(self):
        # Get overall storage utilization
        used_percentage, free_percentage = self._data_service.calculate_storage_utilization()

        # Get staging area utilization
        staging_area = self._data_service.calculate_staging_space_utilization()

        with ui.CollapsableFrame("UNILEVER STORAGE UTILIZATION", name="group", build_header_fn=self._build_collapsable_header, collapsed=False):
            with ui.VStack(height=0, spacing=SPACING):
                ui.Spacer(height=6)
                ui.Label("Rack Space Usage")
                ui.Spacer(height=6)
                ui.Label(f"Occupied: {used_percentage}%     Free: {free_percentage}%")
                ui.Spacer(height=6)
                with ui.HStack():
                    progress_bar = ui.ProgressBar()
                    progress_bar.model.set_value(used_percentage / 100)
                    ui.Spacer(width=10)

                # Loop through each staging area and display its utilization
                for area, stats in staging_area.items():
                    ui.Spacer(height=6)
                    ui.Label(f"{area} Space Usage")
                    ui.Spacer(height=6)
                    area_used_percentage = stats['Used Space %']
                    area_free_percentage = stats['Free Space %']
                    ui.Label(f"Occupied: {area_used_percentage}%     Free: {area_free_percentage}%")
                    ui.Spacer(height=6)
                    with ui.HStack():
                        progress_bar = ui.ProgressBar()
                        progress_bar.model.set_value(area_used_percentage / 100)
                        ui.Spacer(width=10)

    def _cbx_on_value_change(self, is_checked):
        api_url = "https://digital-twin.expangea.com/device/Cube/"
        headers = {'X-API-KEY': '2c38e689-8bac-4ec6-9e0e-70e98222dc2d'}
        cube_prim_path = "/World/Xform/Cube"

        cube_mover = CubeMoverDataLayer(cube_prim_path=cube_prim_path, api_url=api_url, headers=headers)

        if is_checked:
            logging.warning("Cube Start")
            cube_mover.start_moving()
        else:
            logging.warning("Cube Stop")
            cube_mover.stop_moving()

    def _build_fn(self):
        with ui.ScrollingFrame(name="window_bg", horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF):
            with ui.VStack(height=0):
                self._build_storage_utilization()
                self._build_scene()
                self._build_stock_status()
                self._build_violation_check()
                # self._build_tracking()

    def _btn_pallet_info(self, pallet_id):
        self._data_service.show_pallet_info(pallet_id)

def _show_notification(title: str, message: str, status: str):
    status_map = {
        "info": nm.NotificationStatus.INFO,
        "warning": nm.NotificationStatus.WARNING,
        "error": nm.NotificationStatus.ERROR
    }
    status_enum = status_map.get(status, nm.NotificationStatus.INFO)

    nm.post_notification(
        text=message,
        hide_after_timeout=False,
        duration=0,
        status=status_enum
    )
