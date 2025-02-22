# Copyright (c) 2024, NVIDIA CORPORATION. All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto. Any use, reproduction, disclosure, or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["PalletInfoUI"]

import omni.ui as ui
from omni.ui import color as cl
from omni.ui import constant as fl

# Window Constants
WIN_WIDTH = 320
WIN_HEIGHT = 450

# Colors & Styling
cl.window_bg_color = cl(0.2, 0.2, 0.2, 1.0)
cl.label_text = cl(0.9, 0.9, 0.9, 1.0)
cl.section_bg = cl(0.18, 0.18, 0.18, 1.0)
cl.section_border = cl(1.0, 1.0, 1.0, 0.2)

fl.section_padding = 6
fl.section_spacing = 4
fl.label_font_size = 12
fl.value_font_size = 14
fl.border_radius = 4

# Style Dictionary
pallet_info_style = {
    "Label::title": {
        "color": cl.label_text,
        "font_size": fl.value_font_size,
    },
    "Label::header": {
        "color": cl.label_text,
        "font_size": fl.label_font_size,
    },
    "VStack::section": {
        "background_color": cl.section_bg,
        "border_radius": fl.border_radius,
        "padding": fl.section_padding,
    },
}


class PalletInfoUI:
    """Pallet Information UI Panel"""

    def __init__(self):
        self.window = ui.Window("Pallet Information", width=WIN_WIDTH, height=WIN_HEIGHT)
        self._build_ui()

    def _build_ui(self):
        """Builds the main UI layout."""
        with self.window.frame:
            with ui.VStack(style={"margin": 6, "spacing": fl.section_spacing}):
                self._build_header()
                self._build_pallet_details()
                self._build_item_details()
                self._build_stock_information()

    def _build_header(self):
        """Creates the header section with Product Group information."""
        with ui.VStack(style=pallet_info_style["VStack::section"]):
            with ui.HStack(spacing=4):
                ui.Image(name="icons/product_group", width=20, height=20)
                ui.Label("Product Group", name="header", style=pallet_info_style["Label::header"])
            ui.Label("Consumables", name="title", style=pallet_info_style["Label::title"])

    def _build_pallet_details(self):
        """Creates the Pallet ID and SKU details section."""
        with ui.VStack(style=pallet_info_style["VStack::section"]):
            with ui.HStack(spacing=6):
                ui.Label("Pallet ID", name="header", style=pallet_info_style["Label::header"])
                ui.Spacer()
                ui.Label("Product/SKU", name="header", style=pallet_info_style["Label::header"])
            with ui.HStack(spacing=6):
                ui.Label("UINT00000000000", name="title", style=pallet_info_style["Label::title"])
                ui.Spacer()
                ui.Label("UINT00000000000", name="title", style=pallet_info_style["Label::title"])

    def _build_item_details(self):
        """Creates the Item Details section."""
        with ui.VStack(style=pallet_info_style["VStack::section"]):
            ui.Label("Item Details", name="header", style=pallet_info_style["Label::header"])
            ui.Label("Product Description", name="header", style=pallet_info_style["Label::header"])
            ui.Label(
                "Description goes here, Description goes here, Description goes here.",
                name="title",
                style=pallet_info_style["Label::title"],
                word_wrap=True
            )
            ui.Spacer(height=3)
            ui.Label("Owner", name="header", style=pallet_info_style["Label::header"])
            ui.Label("UI Unilever Asia Private Limited", name="title", style=pallet_info_style["Label::title"])

    def _build_stock_information(self):
        """Creates the stock status section."""
        with ui.VStack(style=pallet_info_style["VStack::section"]):
            with ui.HStack(spacing=6):
                ui.Label("Stock Status Code", name="header", style=pallet_info_style["Label::header"])
                ui.Spacer()
                ui.Label("Loose Item Quantity", name="header", style=pallet_info_style["Label::header"])
            with ui.HStack(spacing=6):
                ui.Label("00", name="title", style=pallet_info_style["Label::title"])
                ui.Spacer()
                ui.Label("000", name="title", style=pallet_info_style["Label::title"])

            ui.Spacer(height=3)
            with ui.HStack(spacing=6):
                ui.Label("Expiry Date", name="header", style=pallet_info_style["Label::header"])
                ui.Spacer()
                ui.Label("Days to Expiry", name="header", style=pallet_info_style["Label::header"])
            with ui.HStack(spacing=6):
                ui.Label("00-00-0000", name="title", style=pallet_info_style["Label::title"])
                ui.Spacer()
                ui.Label("000", name="title", style=pallet_info_style["Label::title"])


# Run the UI in Omniverse Script Editor
pallet_ui = PalletInfoUI()
