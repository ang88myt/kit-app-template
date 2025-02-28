# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["julia_modeler_style"]

from omni.ui import color as cl
from omni.ui import constant as fl
from omni.ui import url
import omni.kit.app
import omni.ui as ui
import pathlib

EXTENSION_FOLDER_PATH = pathlib.Path(
    omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
)

ATTR_LABEL_WIDTH = 150
BLOCK_HEIGHT = 22
TAIL_WIDTH = 35
WIN_WIDTH = 400
WIN_HEIGHT = 930

# Pre-defined constants. It's possible to change them at runtime.
cl.window_bg_color = cl(0.2, 0.2, 0.2, 1.0)
cl.window_title_text = cl(.9, .9, .9, .9)
cl.collapsible_header_text = cl(.8, .8, .8, .8)
cl.collapsible_header_text_hover = cl(.95, .95, .95, 1.0)
cl.main_attr_label_text = cl(.65, .65, .65, 1.0)
cl.main_attr_label_text_hover = cl(.9, .9, .9, 1.0)
cl.multifield_label_text = cl(.65, .65, .65, 1.0)
cl.combobox_label_text = cl(.65, .65, .65, 1.0)
cl.field_bg = cl(0.18, 0.18, 0.18, 1.0)
cl.field_border = cl(1.0, 1.0, 1.0, 0.2)
cl.btn_border = cl(1.0, 1.0, 1.0, 0.4)
cl.slider_fill = cl(1.0, 1.0, 1.0, 0.3)
cl.revert_arrow_enabled = cl(.25, .5, .75, 1.0)
cl.revert_arrow_disabled = cl(.35, .35, .35, 1.0)
cl.transparent = cl(0, 0, 0, 0)
cl.progress_fill_used = cl(1.0, 0.0, 0.0, 1.0)  # Red for used
cl.progress_fill_free = cl(0.0, 1.0, 0.0, 1.0)  # Green for free

fl.main_label_attr_hspacing = 10
fl.attr_label_v_spacing = 3
fl.collapsable_group_spacing = 2
fl.outer_frame_padding = 15
fl.tail_icon_width = 15
fl.border_radius = 3
fl.border_width = 1
fl.window_title_font_size = 18
fl.field_text_font_size = 14
fl.main_label_font_size = 14
fl.multi_attr_label_font_size = 14
fl.radio_group_font_size = 14
fl.collapsable_header_font_size = 16
fl.range_text_size = 10

url.damaged_icon = f"{EXTENSION_FOLDER_PATH}/icons/damaged_icon.svg"
url.expired_icon = f"{EXTENSION_FOLDER_PATH}/icons/expired_icon.svg"
url.near_expiry_icon = f"{EXTENSION_FOLDER_PATH}/icons/near_expiry_icon.svg"
url.qaf_icon = f"{EXTENSION_FOLDER_PATH}/icons/qaf_icon.svg"
url.violation_icon = f"{EXTENSION_FOLDER_PATH}/icons/violation_icon.svg"
url.closed_arrow_icon = f"{EXTENSION_FOLDER_PATH}/icons/closed.svg"
url.open_arrow_icon = f"{EXTENSION_FOLDER_PATH}/icons/opened.svg"
url.revert_arrow_icon = f"{EXTENSION_FOLDER_PATH}/icons/revert_arrow.svg"
url.checkbox_on_icon = f"{EXTENSION_FOLDER_PATH}/icons/checkbox_on.svg"
url.checkbox_off_icon = f"{EXTENSION_FOLDER_PATH}/icons/checkbox_off.svg"
url.radio_btn_on_icon = f"{EXTENSION_FOLDER_PATH}/icons/radio_btn_on.svg"
url.radio_btn_off_icon = f"{EXTENSION_FOLDER_PATH}/icons/radio_btn_off.svg"
url.diag_bg_lines_texture = f"{EXTENSION_FOLDER_PATH}/icons/diagonal_texture_screenshot.png"
url.locate_icon = f"{EXTENSION_FOLDER_PATH}/icons/locate_icon.svg"
url.search_icon = f"{EXTENSION_FOLDER_PATH}/icons/mynaui_search.svg"
url.location_icon = f"{EXTENSION_FOLDER_PATH}/icons/mdi_location.svg"
url.pallet_icon = f"{EXTENSION_FOLDER_PATH}/icons/material-symbols-light_pallet-outline.svg"
url.rack_icon = f"{EXTENSION_FOLDER_PATH}/icons/bi_hdd-rack.png"
url.sku_icon = f"{EXTENSION_FOLDER_PATH}/icons/fluent_tray-item-remove-24-filled.svg"

# The main style dict
julia_modeler_style = {
    "Image::sku_icon": {
        "image_url": url.sku_icon,
        "width": 16,
        "height": 16,
    },

    "Image::rack_icon": {
        "image_url": url.rack_icon,
        "width": 16,
        "height": 16,
    },

    "Image::pallet_icon": {
        "image_url": url.pallet_icon,
        "width": 16,
        "height": 16
    },

    "Image::location_icon": {
        "image_url": url.location_icon,
        "width": 16,
        "height": 16,
    },
    "Image::search_icon": {
        "image_url": url.search_icon,
        "width": 16,
        "height": 16,
    },

    "Image::locate_icon": {
        "image_url": url.locate_icon,
        "width": 41,
        "height": 41,
        # "alignment":ui.Fillpolicy.PRESERVE_ASPECT_FIT,
    },
    "Image::damaged_icon": {
        "image_url": url.damaged_icon,
        "width": 41,
        "height": 41
    },
    "Image::expired_icon": {
        "image_url": url.expired_icon,
        "width": 41,
        "height": 41
    },
    "Image::near_expiry_icon": {
        "image_url": url.near_expiry_icon,
        "width": 41,
        "height": 41
    },
    "Image::qaf_icon": {
        "image_url": url.qaf_icon,
        "width": 41,
        "height": 41
    },
    "Image::violation_icon": {
        "image_url": url.violation_icon,
        "width": 41,
        "height": 41
    },
    "Button::upload_new_button": {
        "background_color": cl(0, 0.65, 0.95, 1.0),  # Light blue background
        "color": cl(1.0, 1.0, 1.0, 1.0), # Sets the font color to red
        "margin_height": 0,  # No extra vertical margin
        "margin_width": 6,  # Adds spacing between buttons
        "border_width": 2,  # Thicker border for better contrast
        "border_radius": 4,  # Rounded corners
        "font_size": 20,  # Standard font size
        "width": ui.Fraction(2),
        "height": 50,
        "font_weight": "bold"  # Makes text stand outt
    },
    "Button::tool_button": {
        "background_color": cl.field_bg,
        "margin_height": 0,
        "margin_width": 6,
        "border_color": cl.btn_border,
        "border_width": fl.border_width,
        "font_size": fl.field_text_font_size,
    },
    "CollapsableFrame::group": {
        "margin_height": fl.collapsable_group_spacing,
        "background_color": cl.transparent,
    },
    # TODO: For some reason this ColorWidget style doesn't respond much, if at all (ie, border_radius, corner_flag)
    "ColorWidget": {
        "border_radius": fl.border_radius,
        "border_color": cl(0.0, 0.0, 0.0, 0.0),
    },
    "Field": {
        "background_color": cl.field_bg,
        "border_radius": fl.border_radius,
        "border_color": cl.field_border,
        "border_width": fl.border_width,
    },
    "Field::attr_field": {
        "corner_flag": ui.CornerFlag.RIGHT,
        "font_size": 2,
        # fl.field_text_font_size,  # Hack to allow for a smaller field border until field padding works
    },
    "Field::attribute_color": {
        "font_size": fl.field_text_font_size,
    },
    "Field::multi_attr_field": {
        "padding": 4,  # TODO: Hacky until we get padding fix
        "font_size": fl.field_text_font_size,
    },
    "Field::path_field": {
        "corner_flag": ui.CornerFlag.RIGHT,
        "font_size": fl.field_text_font_size,
    },
    "HeaderLine": {"color": cl(.5, .5, .5, .5)},
    "Image::collapsable_opened": {
        "color": cl.collapsible_header_text,
        "image_url": url.open_arrow_icon,
    },
    "Image::collapsable_opened:hovered": {
        "color": cl.collapsible_header_text_hover,
        "image_url": url.open_arrow_icon,
    },
    "Image::collapsable_closed": {
        "color": cl.collapsible_header_text,
        "image_url": url.closed_arrow_icon,
    },
    "Image::collapsable_closed:hovered": {
        "color": cl.collapsible_header_text_hover,
        "image_url": url.closed_arrow_icon,
    },
    "Image::radio_on": {"image_url": url.radio_btn_on_icon},
    "Image::radio_off": {"image_url": url.radio_btn_off_icon},
    "Image::revert_arrow": {
        "image_url": url.revert_arrow_icon,
        "color": cl.revert_arrow_enabled,
    },
    "Image::revert_arrow:disabled": {"color": cl.revert_arrow_disabled},
    "Image::checked": {"image_url": url.checkbox_on_icon},
    "Image::unchecked": {"image_url": url.checkbox_off_icon},
    "Image::slider_bg_texture": {
        "image_url": url.diag_bg_lines_texture,
        "border_radius": fl.border_radius,
        "corner_flag": ui.CornerFlag.LEFT,
    },
    "Label::attribute_name": {
        "alignment": ui.Alignment.RIGHT_TOP,
        "margin_height": fl.attr_label_v_spacing,
        "margin_width": fl.main_label_attr_hspacing,
        "color": cl.main_attr_label_text,
        "font_size": fl.main_label_font_size,
    },
    "Label::attribute_name:hovered": {"color": cl.main_attr_label_text_hover},
    "Label::collapsable_name": {"font_size": fl.collapsable_header_font_size},
    "Label::multi_attr_label": {
        "color": cl.multifield_label_text,
        "font_size": fl.multi_attr_label_font_size,
    },
    "Label::radio_group_name": {
        "font_size": fl.radio_group_font_size,
        "alignment": ui.Alignment.CENTER,
        "color": cl.main_attr_label_text,
    },
    "Label::range_text": {
        "font_size": fl.range_text_size,
    },
    "Label::window_title": {
        "font_size": fl.window_title_font_size,
        "color": cl.window_title_text,
    },
    "ScrollingFrame::window_bg": {
        "background_color": cl.window_bg_color,
        "padding": fl.outer_frame_padding,
        # "border_radius": 10  # Not obvious in a window, but more visible with only a frame
    },
    "Slider::attr_slider": {
        "draw_mode": ui.SliderDrawMode.FILLED,
        "padding": 0,
        "color": cl.transparent,
        # Meant to be transparent, but completely transparent shows opaque black instead.
        "background_color": cl(0.28, 0.28, 0.28, 0.01),
        "secondary_color": cl.slider_fill,
        "border_radius": fl.border_radius,
        "corner_flag": ui.CornerFlag.LEFT,  # TODO: Not actually working yet OM-53727
    },

    # Combobox workarounds
    "Rectangle::combobox": {  # TODO: remove when ComboBox can have a border
        "background_color": cl.field_bg,
        "border_radius": fl.border_radius,
        "border_color": cl.btn_border,
        "border_width": fl.border_width,
    },
    "ComboBox::dropdown_menu": {
        "color": cl.combobox_label_text,  # label color
        "padding_height": 1.25,
        "margin": 2,
        "background_color": cl.field_bg,
        "border_radius": fl.border_radius,
        "font_size": fl.field_text_font_size,
        "secondary_color": cl.transparent,  # button background color
    },
    "Rectangle::combobox_icon_cover": {"background_color": cl.field_bg},

    # Style for the used storage progress bar
    "ProgressBar::used_storage": {
        "fill_color": cl.progress_fill_used,
    },

    # Style for the free storage progress bar
    "ProgressBar::free_storage": {
        "fill_color": cl.progress_fill_free,
    }

}
