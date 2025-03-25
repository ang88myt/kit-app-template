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
    MAIN_WINDOW_NAME = "Review Panel"
    SEARCH_WINDOW_NAME = "Search Panel"
    MENU_PATH = f"Window/{MAIN_WINDOW_NAME}"
    MENU_PATH_SEARCH = f"Window/{SEARCH_WINDOW_NAME}"

    # ✅ USD File Path (Modify this path as needed)
    USD_FILE_PATH = "C:/Unilever_5BTG/Unilever_Templete_Stage.usd"

    def on_startup(self):
        """Called when the extension is starting."""
        self._main_window = None
        self._search_window = None

        # ✅ Load USD file asynchronously at startup
        asyncio.ensure_future(self._load_usd_stage())

        # Register window show functions
        ui.Workspace.set_show_window_fn(self.MAIN_WINDOW_NAME, partial(self.show_main_window, None))
        ui.Workspace.set_show_window_fn(self.SEARCH_WINDOW_NAME, partial(self.show_search_window, None))

        # Log startup message
        carb.log_info("[my_company.my_python_ui_extension] Extension startup")

        # Add the main window to the editor menu
        editor_menu = omni.kit.ui.get_editor_menu()
        if editor_menu:
            self._menu_main = editor_menu.add_item(self.MENU_PATH, self.show_main_window, toggle=True, value=False)
            self._menu_search = editor_menu.add_item(self.MENU_PATH_SEARCH, self.show_search_window, toggle=True, value=False)

        # Show both windows at startup
        ui.Workspace.show_window(self.MAIN_WINDOW_NAME)
        ui.Workspace.show_window(self.SEARCH_WINDOW_NAME)

    async def _load_usd_stage(self):
        """Loads the USD file at startup asynchronously only if it's not already loaded."""
        usd_context = omni.usd.get_context()
        existing_stage = usd_context.get_stage()

        # ✅ Check if the stage exists and has a valid layer
        if existing_stage:
            root_layer = existing_stage.GetRootLayer()
            if root_layer and root_layer.identifier == self.USD_FILE_PATH:
                carb.log_info(f"⚡ USD file {self.USD_FILE_PATH} is already loaded. No need to reload.")
                return  # ✅ Skip loading if the stage is already the same file

        # ✅ Otherwise, load the new stage
        try:
            carb.log_info(f"📂 Loading USD file: {self.USD_FILE_PATH}")
            await usd_context.open_stage_async(self.USD_FILE_PATH)
            carb.log_info(f"✅ Successfully loaded: {self.USD_FILE_PATH}")
        except Exception as e:
            carb.log_error(f"❌ Failed to load USD file: {e}")

    def on_shutdown(self):
        """Called when the extension is shutting down."""
        # Destroy the main and search windows if they exist
        if self._main_window:
            self._main_window.destroy()
            del self._main_window
            self._main_window = None

        if self._search_window:
            self._search_window.destroy()
            del self._search_window
            self._search_window = None

        # Unregister window functions and remove menu items
        ui.Workspace.set_show_window_fn(self.MAIN_WINDOW_NAME, None)
        ui.Workspace.set_show_window_fn(self.SEARCH_WINDOW_NAME, None)

        editor_menu = omni.kit.ui.get_editor_menu()
        if editor_menu:
            if self._menu_main:
                editor_menu.remove_item(self.MENU_PATH)
                self._menu_main = None
            if self._menu_search:
                editor_menu.remove_item(self.MENU_PATH_SEARCH)
                self._menu_search = None

        # Log shutdown message
        carb.log_info("[my_company.my_python_ui_extension] Extension shutdown")

    def _set_menu(self, value, menu_type):
        """Update the editor menu toggle value."""
        editor_menu = omni.kit.ui.get_editor_menu()
        if editor_menu:
            if menu_type == "main":
                editor_menu.set_value(self.MENU_PATH, value)
            elif menu_type == "search":
                editor_menu.set_value(self.MENU_PATH_SEARCH, value)

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
        self._set_menu(visible, window_type)
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
        """Show or hide the search window persistently."""
        if value:
            if not self._search_window:
                try:
                    self._search_window = SearchWindowPanel(title=self.SEARCH_WINDOW_NAME)

                    self._search_window.set_visibility_changed_fn(
                        lambda visible: self.show_search_window(menu, visible))
                    carb.log_warn("Search window created successfully.")
                    # self._search_window.set_visibility_changed_fn(partial(self._visibility_changed_fn, window_type="search"))

                except Exception as e:
                    carb.log_error(f"Failed to create Search Window: {e}")

            if self._search_window:
                self._search_window.visible = True
                carb.log_warn("Search window set to visible.")
        elif self._search_window:
            self._search_window.visible = False
            carb.log_warn("Search window hidden successfully.")
