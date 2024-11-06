__all__ = ["MyExtension"]

import asyncio
from functools import partial

import omni.ext
import omni.kit.app
import omni.kit.ui
import omni.ui as ui
import carb

from .window import Custom_Window
from .style import WIN_WIDTH, WIN_HEIGHT

class MyExtension(omni.ext.IExt):
    WINDOW_NAME = "Toll L3 Unilever"
    MENU_PATH = f"Window/{WINDOW_NAME}"

    def on_startup(self):
        self._window = None

        ui.Workspace.set_show_window_fn(self.WINDOW_NAME, partial(self.show_window, None))
        carb.log_info("[my_company.my_python_ui_extension] Extension startup")

        editor_menu = omni.kit.ui.get_editor_menu()
        if editor_menu:
            self._menu = editor_menu.add_item(self.MENU_PATH, self.show_window, toggle=True, value=False)

        ui.Workspace.show_window(self.WINDOW_NAME)

    def on_shutdown(self):
        if self._window:
            self._window.destroy()
            self._window = None
        carb.log_warn("Extension shutting down, window destroyed.")

        ui.Workspace.set_show_window_fn(self.WINDOW_NAME, None)
        carb.log_info("[my_company.my_python_ui_extension] Extension shutdown")

    def _set_menu(self, value):
        editor_menu = omni.kit.ui.get_editor_menu()
        if editor_menu:
            editor_menu.set_value(self.MENU_PATH, value)

    async def _destroy_window_async(self):
        await omni.kit.app.get_app().next_update_async()
        if self._window:
            self._window.destroy()
            self._window = None
            carb.log_info("Window successfully destroyed asynchronously.")

    def _visiblity_changed_fn(self, visible):
        self._set_menu(visible)
        if not visible:
            asyncio.ensure_future(self._destroy_window_async())

    def show_window(self, menu, value):
        carb.log_info(f"Attempting to {'show' if value else 'hide'} the window. Current window: {self._window}")

        if value:
            if not self._window:
                try:
                    carb.log_info("Creating a new window instance...")
                    self._window = Custom_Window(self.WINDOW_NAME, width=WIN_WIDTH, height=WIN_HEIGHT)
                    self._window.set_visibility_changed_fn(self._visiblity_changed_fn)
                    carb.log_warn("Window created successfully.")
                except Exception as e:
                    carb.log_error(f"Failed to create window: {e}")
            if self._window:
                self._window.visible = True
                carb.log_warn("Window set to visible.")
        elif self._window:
            self._window.visible = False
            carb.log_warn("Window hidden successfully.")
