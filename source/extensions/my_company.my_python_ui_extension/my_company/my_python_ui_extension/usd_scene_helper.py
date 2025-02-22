import asyncio
import carb
import omni.usd
from pxr import Usd, UsdGeom, Sdf, Gf
import omni.kit.notification_manager as nm
class USDSceneHelper:
    """Helper class for managing USD scenes in Omniverse."""

    def __init__(self, usd_file_path: str):
        self.usd_file_path = usd_file_path
        self.usd_context = omni.usd.get_context()

    async def load_stage(self):
        """Loads the specified USD file asynchronously."""
        if not self.usd_file_path:
            carb.log_error("❌ No USD file path provided!")
            return False

        try:
            carb.log_info(f"📂 Loading USD file: {self.usd_file_path}")
            await self.usd_context.open_stage_async(self.usd_file_path)
            carb.log_info(f"✅ Successfully loaded USD file: {self.usd_file_path}")
            return True
        except Exception as e:
            carb.log_error(f"❌ Failed to load USD file: {e}")
            return False

    async def ensure_stage_is_ready(self):
        """Waits until the USD stage is fully loaded before proceeding."""
        for _ in range(10):  # Retry for 10 frames
            stage = self.usd_context.get_stage()
            if stage and stage.GetRootLayer():
                return stage  # ✅ Return valid stage
            await asyncio.sleep(0.1)  # Wait before retrying

        carb.log_error("❌ USD Stage did not load in time!")
        return None

    def ensure_xform_exists(self, xform_path: str, translation: Gf.Vec3f = Gf.Vec3f(0, 0, 0)):
        """Ensures an Xform exists at the given path, creating it if needed."""
        stage = self.usd_context.get_stage()
        if not stage:
            carb.log_error("❌ USD Stage is not initialized.")
            return False

        xform_sdf_path = Sdf.Path(xform_path)
        prim = stage.GetPrimAtPath(xform_sdf_path)

        if prim.IsValid():
            carb.log_info(f"✔ Xform already exists at {xform_path}.")
            return prim

        # Create the Xform if it does not exist
        try:
            xform = UsdGeom.Xform.Define(stage, xform_sdf_path)
            xform.AddTranslateOp().Set(translation)
            carb.log_info(f"✔ Created Xform at {xform_path} with translation {translation}")
            return xform
        except Exception as e:
            carb.log_error(f"❌ Failed to create Xform at {xform_path}: {e}")
            return False

    def delete_prim(self, prim_path: str):
        """Deletes a prim at the specified path."""
        stage = self.usd_context.get_stage()
        if not stage:
            carb.log_error("❌ USD Stage is not initialized.")
            return False

        prim = stage.GetPrimAtPath(Sdf.Path(prim_path))
        if prim and prim.IsValid():
            omni.kit.commands.execute("DeletePrims", paths=[prim.GetPath()])
            carb.log_info(f"🗑 Deleted prim at {prim_path}")
            return True
        else:
            carb.log_warn(f"⚠ No valid prim found at {prim_path}.")
            return False

    def show_notification(self,title: str, message: str, status: str):
        status_map = {
            "info": nm.NotificationStatus.INFO,
            "warning": nm.NotificationStatus.WARNING,
            # "error": nm.NotificationStatus.ERROR
        }
        status_enum = status_map.get(status, nm.NotificationStatus.INFO)

        nm.post_notification(
            text=message,
            hide_after_timeout=False,
            duration=0,
            status=status_enum
        )
