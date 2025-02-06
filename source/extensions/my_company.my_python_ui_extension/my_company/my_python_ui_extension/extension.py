# __all__ = ["MyExtension"]
#
# import asyncio
# from functools import partial
#
# import omni.ext
# import omni.kit.app
# import omni.kit.ui
# import omni.ui as ui
# import carb
#
# from .window import Custom_Window
# from .style import WIN_WIDTH, WIN_HEIGHT
#
# class MyExtension(omni.ext.IExt):
#     WINDOW_NAME = "Toll L3 Unilever"
#     MENU_PATH = f"Window/{WINDOW_NAME}"
#
#     def on_startup(self):
#         self._window = None
#
#         ui.Workspace.set_show_window_fn(self.WINDOW_NAME, partial(self.show_window, None))
#         carb.log_info("[my_company.my_python_ui_extension] Extension startup")
#
#         editor_menu = omni.kit.ui.get_editor_menu()
#         if editor_menu:
#             self._menu = editor_menu.add_item(self.MENU_PATH, self.show_window, toggle=True, value=False)
#
#         ui.Workspace.show_window(self.WINDOW_NAME)
#
#     def on_shutdown(self):
#         if self._window:
#             self._window.destroy()
#             self._window = None
#         carb.log_warn("Extension shutting down, window destroyed.")
#
#         ui.Workspace.set_show_window_fn(self.WINDOW_NAME, None)
#         carb.log_info("[my_company.my_python_ui_extension] Extension shutdown")
#
#     def _set_menu(self, value):
#         editor_menu = omni.kit.ui.get_editor_menu()
#         if editor_menu:
#             editor_menu.set_value(self.MENU_PATH, value)
#
#     async def _destroy_window_async(self):
#         await omni.kit.app.get_app().next_update_async()
#         if self._window:
#             self._window.destroy()
#             self._window = None
#             carb.log_info("Window successfully destroyed asynchronously.")
#
#     def _visiblity_changed_fn(self, visible):
#         self._set_menu(visible)
#         if not visible:
#             asyncio.ensure_future(self._destroy_window_async())
#
#     def show_window(self, menu, value):
#         carb.log_info(f"Attempting to {'show' if value else 'hide'} the window. Current window: {self._window}")
#
#         if value:
#             if not self._window:
#                 try:
#                     carb.log_info("Creating a new window instance...")
#                     self._window = Custom_Window(self.WINDOW_NAME, width=WIN_WIDTH, height=WIN_HEIGHT)
#                     self._window.set_visibility_changed_fn(self._visiblity_changed_fn)
#                     carb.log_warn("Window created successfully.")
#                 except Exception as e:
#                     carb.log_error(f"Failed to create window: {e}")
#             if self._window:
#                 self._window.visible = True
#                 carb.log_warn("Window set to visible.")
#         elif self._window:
#             self._window.visible = False
#             carb.log_warn("Window hidden successfully.")

__all__ = ["MyExtension"]

import asyncio
from functools import partial
import omni.ext
import omni.kit.ui
import omni.ui as ui
import carb

from .window import Custom_Window  # Import the main custom window
from .search_window import SearchWindowPanel  # Import the new search window panel
from .style import WIN_WIDTH, WIN_HEIGHT  # Constants for window dimensions


class MyExtension(omni.ext.IExt):
    # Window names
    MAIN_WINDOW_NAME = "Toll L3 Unilever"
    SEARCH_WINDOW_NAME = "Search Panel"
    MENU_PATH = f"Window/{MAIN_WINDOW_NAME}"

    def on_startup(self):
        """Called when the extension is starting."""
        self._main_window = None
        self._search_window = None

        # Register the window show functions
        ui.Workspace.set_show_window_fn(self.MAIN_WINDOW_NAME, partial(self.show_main_window, None))
        ui.Workspace.set_show_window_fn(self.SEARCH_WINDOW_NAME, partial(self.show_search_window, None))

        # Log startup message
        carb.log_info("[my_company.my_python_ui_extension] Extension startup")

        # Add the main window to the editor menu
        editor_menu = omni.kit.ui.get_editor_menu()
        if editor_menu:
            self._menu = editor_menu.add_item(self.MENU_PATH, self.show_main_window, toggle=True, value=False)

        # Show both windows at startup
        ui.Workspace.show_window(self.MAIN_WINDOW_NAME)
        ui.Workspace.show_window(self.SEARCH_WINDOW_NAME)

    def on_shutdown(self):
        """Called when the extension is shutting down."""
        # Destroy the main and search windows if they exist
        if self._main_window:
            self._main_window.destroy()
            self._main_window = None
        if self._search_window:
            self._search_window.destroy()
            self._search_window = None

        # Unregister window functions and remove menu
        ui.Workspace.set_show_window_fn(self.MAIN_WINDOW_NAME, None)
        ui.Workspace.set_show_window_fn(self.SEARCH_WINDOW_NAME, None)

        editor_menu = omni.kit.ui.get_editor_menu()
        if editor_menu and self._menu:
            editor_menu.remove_item(self.MENU_PATH)

        # Log shutdown message
        carb.log_info("[my_company.my_python_ui_extension] Extension shutdown")

    def _set_menu(self, value):
        """Update the editor menu toggle value."""
        editor_menu = omni.kit.ui.get_editor_menu()
        if editor_menu:
            editor_menu.set_value(self.MENU_PATH, value)

    async def _destroy_window_async(self, window_type):
        """Destroys a specific window asynchronously."""
        await omni.kit.app.get_app().next_update_async()
        if window_type == "main" and self._main_window:
            self._main_window.destroy()
            self._main_window = None
            carb.log_info("Main window successfully destroyed asynchronously.")
        elif window_type == "search" and self._search_window:
            self._search_window.destroy()
            self._search_window = None
            carb.log_info("Search window successfully destroyed asynchronously.")

    def _visibility_changed_fn(self, visible, window_type):
        """Callback for when a window's visibility changes."""
        self._set_menu(visible)
        if not visible:
            asyncio.ensure_future(self._destroy_window_async(window_type))

    def show_main_window(self, menu, value):
        """Show or hide the main window."""
        carb.log_info(f"Attempting to {'show' if value else 'hide'} the main window. Current window: {self._main_window}")

        if value:
            if not self._main_window:
                try:
                    carb.log_info("Creating a new main window instance...")
                    self._main_window = Custom_Window(self.MAIN_WINDOW_NAME, width=WIN_WIDTH, height=WIN_HEIGHT)
                    self._main_window.set_visibility_changed_fn(partial(self._visibility_changed_fn, window_type="main"))
                    carb.log_warn("Main window created successfully.")
                except Exception as e:
                    carb.log_error(f"Failed to create main window: {e}")
            if self._main_window:
                self._main_window.visible = True
                carb.log_warn("Main window set to visible.")
        elif self._main_window:
            self._main_window.visible = False
            carb.log_warn("Main window hidden successfully.")

    def show_search_window(self, menu, value):
        """Show or hide the search window."""
        carb.log_info(f"Attempting to {'show' if value else 'hide'} the search window. Current window: {self._search_window}")

        if value:
            if not self._search_window:
                try:
                    carb.log_info("Creating a new search window instance...")
                    self._search_window = SearchWindowPanel(title=self.SEARCH_WINDOW_NAME)
                    self._search_window.set_visibility_changed_fn(partial(self._visibility_changed_fn, window_type="search"))
                    carb.log_warn("Search window created successfully.")
                except Exception as e:
                    carb.log_error(f"Failed to create search window: {e}")
            if self._search_window:
                self._search_window.visible = True
                carb.log_warn("Search window set to visible.")
        elif self._search_window:
            self._search_window.visible = False
            carb.log_warn("Search window hidden successfully.")

