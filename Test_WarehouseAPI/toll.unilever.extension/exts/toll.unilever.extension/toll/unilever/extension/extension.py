
# import omni.ext
# import omni.ui as ui
# from omni.ui import scene as s

# from pxr import Usd, UsdGeom, Gf
# import omni.usd
# # from omni.kit.viewport.utility import get_active_viewport, get_active_viewport_window, frame_viewport_selection
# from .data_service import DataService, move_xform_and_set_view, find_prim_then_select

# # Functions and vars are available to other extensions as usual in python: `my_company.my_python_ui_extension.some_public_function(x)`
# def some_public_function(x: int):
#     print(f"[my_company.my_python_ui_extension] some_public_function was called with {x}")
#     return x ** x


# # Any class derived from `omni.ext.IExt` in the top level module (defined in `python.modules` of `extension.toml`) will
# # be instantiated when the extension gets enabled, and `on_startup(ext_id)` will be called.
# # Later when the extension gets disabled on_shutdown() is called.
# class MyExtension(omni.ext.IExt):
#     # ext_id is the current extension id. It can be used with the extension manager to query additional information,
#     # like where this extension is located on the filesystem.

#     def on_startup(self, ext_id):
#         self._data_service = DataService()
#         print("[my_company.my_python_ui_extension] Extension startup")
#         self._create_ui()

#     def _create_ui(self):
#         self._window = ui.Window("Data Link", width=350, height=400)

#         with self._window.frame:
#             with ui.VStack():
#                 width = 200
#                 height = 10
#                 ui.Label("PalletID", height=height)
#                 ui.Spacer(height=height)
#                 self.endpoint_field = ui.StringField(width=width, height=height)
#                 ui.Spacer(height=height)
#                 ui.Label("LocationID", height=height)
#                 self.location_field = ui.StringField(width=width, height=height)
#                 self.info_label = ui.Label("")

#                 with ui.HStack():
#                     ui.Button("Submit", clicked_fn=self._on_update, height=20)
#                     ui.Button("Place", clicked_fn=self._on_place, height=20)
#                     ui.Button("Reset", clicked_fn=self._on_reset, height=20)
#                     ui.Button("Test", clicked_fn=self._on_test, height=20)


#     def _on_update(self):

#         endpoint = f"pallet/{self.endpoint_field.model.get_value_as_string()}/"
#         print(f"Fetching stock info from endpoint: {endpoint}")

#         find_prim_then_select(self.endpoint_field.model.get_value_as_string())

#         stock_info = self._data_service.fetch_stock_info(endpoint)

#         if stock_info:
#             limited_items = list(stock_info.items())[:11]
#             info_text = "\n".join([f"{key}: {value}" for key, value in limited_items])


#             print(info_text)
#             # self.info_label.text = info_text

#             location_id = stock_info.get("rack_location").get("location_id")
#             location_endpoint = f"rack-location/{location_id}/"
#             print(f"Fetching coordinates from endpoint: {location_endpoint}")

#             x, y, z = self._data_service.fetch_coordinates(endpoint)
#             print(x, y , z)
#             if x is not None and y is not None and z is not None:
#                 self._move_camera(x, y, z)
#             else:
#                 self.info_label.text = "Failed to fetch stock info"


#     def _move_camera(self, x: float, y: float, z: float):
#         xform_path = "/Camera"
#         view_camera_path = "/Camera/Camera_001/Camera_001_001"
#         new_xyz_location =  Gf.Vec3d(x+0.022, y+-5, z+2)
#         new_rotation = Gf.Vec3f(75, 0.0, 0.0)
#         focal_length = 0.2

#         move_xform_and_set_view(xform_path, view_camera_path, new_xyz_location, new_rotation, focal_length=focal_length)
#         print(f"Moved camera to location: {new_xyz_location}, with rotation: {new_rotation}, focal length: {focal_length}")

#     def _on_reset():
#         self.info_label.text = "Empty"
#         self.endpoint_field.model.set_value("")
#         self.location_field.model.set_value("")

#     def _on_place(self):
#         location_endpoint = "rack-location/3015021/"
#         x, y, z = self._data_service.fetch_coordinates(location_endpoint)
#         if x is None or y is None or z is None:
#             print(f"Failed to fetch coordinates from endpoint: {location_endpoint}")
#             return

#         stage = omni.usd.get_context().get_stage()
#         selection = omni.usd.get_context().get_selection().get_selected_prim_paths()
#         if not selection:
#             print("No items selected.")
#             return

#         for prim_path in selection:
#             prim = stage.GetPrimAtPath(prim_path)
#             if not prim.IsValid():
#                 print(f"Invalid prim path: {prim_path}")
#                 continue

#             omni.kit.commands.execute(
#                 'TransformPrimSRT',
#                 path=prim_path,
#                 new_translation=(x, y, z),
#                 new_rotation_euler=(0.0, 0.0, 0.0),
#                 new_scale=(1.0, 1.0, 1.0)
#             )
#             print(f"Moved {prim_path} to location ({x}, {y}, {z})")


#     def _on_test(self):
#         print("Test function executed.")

#     def on_shutdown(self):
#         print("[my_company.my_python_ui_extension] Extension shutdown")
__all__ = ["toll_unilever_extension"]
import asyncio
from functools import partial

import omni.ext
import omni.kit.ui
import omni.ui as ui


from .style import WIN_WIDTH, WIN_HEIGHT
from .window import JuliaModelerWindow
from .data_service import DataService


class toll_unilever_extension(omni.ext.IExt):

    WINDOW_NAME = "Toll L3 Unilever"
    MENU_PATH = f"Window/{WINDOW_NAME}"

    def on_startup(self):
        # The ability to show the window if the system requires it. We use it
        # in QuickLayout.

        self._data_service = DataService()
        ui.Workspace.set_show_window_fn(toll_unilever_extension.WINDOW_NAME, partial(self.show_window, None))

        # Add the new menu
        editor_menu = omni.kit.ui.get_editor_menu()
        if editor_menu:
            self._menu = editor_menu.add_item(
                toll_unilever_extension.MENU_PATH, self.show_window, toggle=True, value=True
            )

        # Show the window. It will call `self.show_window`
        ui.Workspace.show_window(toll_unilever_extension.WINDOW_NAME)


    def on_shutdown(self):
        self._menu = None
        # if self._window:
        #     self._window.destroy()
        #     self._window = None

        # Deregister the function that shows the window from omni.ui
        ui.Workspace.set_show_window_fn(toll_unilever_extension.WINDOW_NAME, None)

    def _set_menu(self, value):
        """Set the menu to create this window on and off"""
        editor_menu = omni.kit.ui.get_editor_menu()
        if editor_menu:
            editor_menu.set_value(toll_unilever_extension.MENU_PATH, value)

    async def _destroy_window_async(self):
        # wait one frame, this is due to the one frame defer
        # in Window::_moveToMainOSWindow()
        await omni.kit.app.get_app().next_update_async()
        if self._window:
            self._window.destroy()
            self._window = None

    def _visibility_changed_fn(self, visible):
        # Called when the user presses "X"
        self._set_menu(visible)
        if not visible:
            # Destroy the window, since we are creating a new window
            # in show_window
            asyncio.ensure_future(self._destroy_window_async())

    def show_window(self, menu, value):
        if value:
            self._window = JuliaModelerWindow(
                toll_unilever_extension.WINDOW_NAME, width=WIN_WIDTH, height=WIN_HEIGHT)
            self._window.set_visibility_changed_fn(self._visibility_changed_fn)
        elif self._window:
            self._window.visible = False
