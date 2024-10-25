import omni.ui as ui
import logging
from .proximity_checker import ProximityChecker

class ViolationUI:
    def __init__(self):
        self.proximity_checker = ProximityChecker
        self.window = None

    def create_ui(self):
        # Perform proximity check first
        violations = self.proximity_checker.proximity_check_all_racks()

        # Collect unique food and HPC pallets
        unique_food_pallets = {v['food_pallet_id'] for v in violations}
        unique_hpc_pallets = {v['hpc_pallet_id'] for v in violations}

        # Get the total number of violations
        total_violations = self.proximity_checker.get_total_violations()

        # Create the UI window
        self.window = ui.Window("Pallet Violations", width=400, height=600)

        with self.window.frame:
            with ui.ScrollingFrame(height=800):  # Ensure the content is scrollable
                with ui.VStack(spacing=10):
                    # Display total violations at the top
                    ui.Label(f"Total Violations Found: {total_violations}", style={"font_size": 18, "color": "orange"})

                    # Add a spacer for UI layout
                    ui.Spacer(height=10)

                    # Display unique Food pallets with buttons
                    if unique_food_pallets:
                        ui.Label(f"Food Pallets", style={"font_size": 16, "color": "red"})
                        for pallet_id in unique_food_pallets:
                            CustomButtonWidget(f"Food Pallet ID: {pallet_id}",
                                               tooltip=f"Pallet ID: {pallet_id}",
                                               btn_callback=lambda p=pallet_id: self.on_pallet_click(p))

                    ui.Spacer(height=10)  # Add space between Food and HPC sections

                    # Display unique HPC pallets with buttons
                    if unique_hpc_pallets:
                        ui.Label(f"HPC Pallets", style={"font_size": 16, "color": "blue"})
                        for pallet_id in unique_hpc_pallets:
                            CustomButtonWidget(f"HPC Pallet ID: {pallet_id}",
                                               tooltip=f"Pallet ID: {pallet_id}",
                                               btn_callback=lambda p=pallet_id: self.on_pallet_click(p))

    def on_pallet_click(self, pallet_id):
        logging.info(f"Pallet clicked: {pallet_id}")
        # Here you can add logic to highlight the pallet in 3D scene or handle the click event


class CustomButtonWidget:
    """ Custom button widget to handle button creation with a callback """

    def __init__(self, label, tooltip="", btn_callback=None):
        with ui.HStack(height=20):
            ui.Button(label, clicked_fn=btn_callback, tooltip=tooltip)
