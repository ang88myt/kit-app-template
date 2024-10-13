__all__ = ["MyExtension"]
from functools import partial
import asyncio
import omni.kit.app
import omni.ext
import omni.kit.ui
import omni.ui as ui
import omni.kit.app
import omni.ext
from pxr import Usd, UsdGeom, Gf
import omni.usd
from omni.ui import scene as s
from .style import WIN_WIDTH, WIN_HEIGHT
from .window import Window
import carb
# from omni.kit.viewport.utility import get_active_viewport, get_active_viewport_and_window, frame_viewport_selection
# from .data_service import DataService, move_xform_and_set_view, find_prim_then_select

# Any class derived from `omni.ext.IExt` in the top level module (defined in `python.modules` of `extension.toml`) will
# be instantiated when the extension gets enabled, and `on_startup(ext_id)` will be called.
# Later when the extension gets disabled on_shutdown() is called.
class MyExtension(omni.ext.IExt):
    # ext_id is the current extension id. It can be used with the extension manager to query additional information,
    # like where this extension is located on the filesystem.
    WINDOW_NAME = "Toll L3 Unilever"
    MENU_PATH = f"Window/{WINDOW_NAME}"

    # def __init__(self):
    #     self._menu = None
    #     self._window = None

    def on_startup(self):

        self._window = None

        # Initialize window and data service
        # self._data_service = DataService()

        # Register the window display function in the workspace
        ui.Workspace.set_show_window_fn(MyExtension.WINDOW_NAME, partial(self.show_window, None))
        carb.log_info("[my_company.my_python_ui_extension] Extension startup")

        # Add menu item in the UI
        editor_menu = omni.kit.ui.get_editor_menu()
        if editor_menu:
            self._menu = editor_menu.add_item(
                MyExtension.MENU_PATH, self.show_window, toggle=True, value=False
            )

        # Automatically show the window
        ui.Workspace.show_window(MyExtension.WINDOW_NAME)

    def on_shutdown(self):
        # Clean up window and data service
        if self._window:
            self._window.destroy()
            self._window = None
        carb.log_warn("Extension shutting down, window destroyed.")

        # Deregister the function that shows the window
        ui.Workspace.set_show_window_fn(MyExtension.WINDOW_NAME, None)
        # self._data_service.close()
        carb.log_info("[my_company.my_python_ui_extension] Extension shutdown")

    # def _create_ui(self):
    #     self._window = ui.Window("Data Link", width=350, height=400)

    # with self._window.frame:
    #     with ui.VStack():
    #         width = 200
    #         height = 10
    #         ui.Label("PalletID", height=height)
    #         ui.Spacer(height=height)
    #         self.endpoint_field = ui.StringField(width=width, height=height)
    #         ui.Spacer(height=height)
    #         ui.Label("LocationID", height=height)
    #         self.location_field = ui.StringField(width=width, height=height)
    #         self.info_label = ui.Label("")
    #
    #         with ui.HStack():
    #             ui.Button("Submit", clicked_fn=self._on_update, height=20)
    #             ui.Button("Place", clicked_fn=self._on_place, height=20)
    #             ui.Button("Reset", clicked_fn=self._on_reset, height=20)
    #             ui.Button("Test", clicked_fn=self._on_test, height=20)

    # def _on_update(self):
    #
    #     endpoint = f"pallet/{self.endpoint_field.model.get_value_as_string()}/"
    #     print(f"Fetching stock info from endpoint: {endpoint}")
    #
    #     find_prim_then_select(self.endpoint_field.model.get_value_as_string())
    #
    #     stock_info = self._data_service.fetch_stock_info(endpoint)
    #
    #     if stock_info:
    #         limited_items = list(stock_info.items())[:11]
    #         info_text = "\n".join([f"{key}: {value}" for key, value in limited_items])
    #
    #
    #         print(info_text)
    #         # self.info_label.text = info_text
    #
    #         location_id = stock_info.get("rack_location").get("location_id")
    #         location_endpoint = f"rack-location/{location_id}/"
    #         print(f"Fetching coordinates from endpoint: {location_endpoint}")
    #
    #         x, y, z = self._data_service.fetch_coordinates(endpoint)
    #         print(x, y , z)
    #         if x is not None and y is not None and z is not None:
    #             self._move_camera(x, y, z)
    #         else:
    #             self.info_label.text = "Failed to fetch stock info"
    # def _cleanup_viewport_window(self):
    #     """Clean up the reference to the viewport window"""
    #     if self._viewport_window:
    #         # Perform any necessary disconnection or cleanup actions
    #         self._viewport_window = None
    #     print("Viewport window reference cleaned up.")

    def _set_menu(self, value):
        """Set the menu to create this window on and off"""
        editor_menu = omni.kit.ui.get_editor_menu()
        if editor_menu:
            editor_menu.set_value(MyExtension.MENU_PATH, value)

    async def _destroy_window_async(self):
        """Asynchronously destroy the window to avoid frame issues."""
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
        """Display or hide the window based on the value."""
        carb.log_info(f"Attempting to {'show' if value else 'hide'} the window. Current window: {self._window}")

        if value:
            if not self._window:
                try:
                    carb.log_info("Creating a new window instance...")
                    self._window = Window(
                        MyExtension.WINDOW_NAME, width=WIN_WIDTH, height=WIN_HEIGHT)
                    self._window.set_visibility_changed_fn(self._visiblity_changed_fn)
                    carb.log_warn("Window created successfully.")
                except Exception as e:
                    carb.log_error(f"Failed to create window: {e}")
            if self._window:
                self._window.visible = True  # Ensure the window is visible
                carb.log_warn("Window set to visible.")
        elif self._window:
            self._window.visible =  False
            carb.log_warn("Window hidden successfully.")


