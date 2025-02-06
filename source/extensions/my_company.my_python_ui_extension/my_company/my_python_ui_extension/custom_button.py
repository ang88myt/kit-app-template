__all__ = ["CustomButtonWidget"]

from typing import Callable
import omni.ui as ui
from omni.ui import color as cl
from .style import BLOCK_HEIGHT

class CustomButtonWidget:
    """A widget that displays a button and can trigger a callback function."""

    def __init__(self, btn_label: str, tooltip: str, btn_callback: Callable,
                 image_url: str = None,
                 spacing: int = 0,
                 image_width: int = 0,
                 image_height: int = 0,):
        self.__btn_label = btn_label
        self.__btn = None
        self.__spacing = spacing
        self.__image_url = image_url
        self.__image_width = image_width
        self.__image_height = image_height
        self.__callback = btn_callback
        self.__frame = ui.Frame()
        self.__tooltip = tooltip
        with self.__frame:
            self._build_fn()

    def destroy(self):
        """Clean up references to UI components to ensure proper garbage collection."""
        self.__btn = None
        self.__callback = None
        self.__frame.destroy()
        self.__frame = None

    def _build_fn(self):
        """Draw the widget parts and set up the callback."""


        # Create the button
        self.__btn = ui.Button(
            name="tool_button",
            text=self.__btn_label,
            tooltip=self.__tooltip,
            height=BLOCK_HEIGHT,
            width=ui.Fraction(2),
            image_url=self.__image_url,
            image_width=self.__image_width,
            image_height=self.__image_height,
            # visible=True,
            spacing=self.__spacing,
            style={"stack_direction": ui.Direction.LEFT_TO_RIGHT},
            alignment=ui.Alignment.CENTER,
            fill_policy=ui.FillPolicy.PRESERVE_ASPECT_FIT,
            clicked_fn=self.__callback,

        )
