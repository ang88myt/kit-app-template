__all__ = ["CustomButtonWidget"]

from typing import Callable
import omni.ui as ui
from .style import BLOCK_HEIGHT

class CustomButtonWidget:
    """A widget that displays a button and can trigger a callback function."""

    def __init__(self, btn_label: str, tooltip: str, btn_callback: Callable):
        self.__btn_label = btn_label
        self.__btn = None
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
        with ui.HStack():
            # Create the button
            self.__btn = ui.Button(
                name="tool_button",
                text=self.__btn_label,
                tooltip=self.__tooltip,
                height=BLOCK_HEIGHT,
                width=ui.Fraction(1),
                clicked_fn=self.__callback
            )
