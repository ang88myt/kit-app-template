__all__ = ["CustomDateSearchWidget"]

from typing import Callable, Optional
import omni.ui as ui
from .style import ATTR_LABEL_WIDTH, BLOCK_HEIGHT
import re


class CustomDateSearchWidget:
    """A compound widget for gathering two date inputs (in dd-mm-yyyy format) and a search button to execute a callback"""

    def __init__(self, label: str, placeholder1: str, placeholder2: str, btn_callback: Optional[Callable] = None):
        self.__label = label
        self.__placeholder1 = placeholder1
        self.__placeholder2 = placeholder2
        self.__input_field1: Optional[ui.StringField] = None
        self.__input_field2: Optional[ui.StringField] = None
        self.__btn: Optional[ui.Button] = None
        self.__frame = ui.Frame()
        self.__btn_callback = btn_callback

        with self.__frame:
            self._build_fn()

    def destroy(self):
        """Destroys the widget's children components"""
        self.__input_field1 = None
        self.__input_field2 = None
        self.__btn = None
        self.__btn_callback = None
        self.__frame = None

    def _build_fn(self):
        """Builds the UI components"""
        with ui.HStack():
            ui.Label(
                self.__label,
                name="attribute_name",
                width=ATTR_LABEL_WIDTH
            )

            self.__input_field1 = ui.StringField(
                name="input_field1",
                placeholder_text=self.__placeholder1,
                width=ui.Fraction(2),
                height = BLOCK_HEIGHT
            )
            ui.Spacer(width=6)

            self.__input_field2 = ui.StringField(
                name="input_field2",
                placeholder_text=self.__placeholder2,
                width=ui.Fraction(2),
                height=BLOCK_HEIGHT
            )

            self.__btn = ui.Button(
                "Search",
                name="tool_button",
                width=ui.Fraction(2),
                height=BLOCK_HEIGHT,
                clicked_fn=self._on_button_click
            )

    def _on_button_click(self):
        """Handles the button click event"""
        date1 = self.__input_field1.model.get_value_as_string()
        date2 = self.__input_field2.model.get_value_as_string()

        if not (self._is_valid_date(date1) and self._is_valid_date(date2)):
            print("Invalid date format! Please enter dates in yyyy-mm-dd format.")
            return

        if self.__btn_callback:
            self.__btn_callback(date1, date2)

    def _is_valid_date(self, date_str: str) -> bool:
        """Validates the date format to be yyy-mm-dd"""
        pattern = r"^\d{4}-\d{2}-\d{2}$"
        return bool(re.match(pattern, date_str))

    @property
    def model(self) -> Optional[ui.AbstractItem]:
        """The widget's model"""
        return self.__input_field1.model if self.__input_field1 else None
