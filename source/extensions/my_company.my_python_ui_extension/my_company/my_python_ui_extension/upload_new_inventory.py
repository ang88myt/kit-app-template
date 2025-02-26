import omni.ui as ui
import carb
import omni.client
import requests
import json
import pathlib
from omni.kit.window.filepicker import FilePickerDialog
from .data_service import _show_notification

# API Endpoint and headers
UPLOAD_URL = "https://digital-twin-dev.expangea.com/warehouse/5BTG/"
HEADERS = {
    "X-API-KEY": "2c38e689-8bac-4ec6-9e0e-70e98222dc2d"  # Replace with your actual API key if required
}

class ExcelUploader:
    """Excel File Uploader for Omniverse"""

    def __init__(self):
        self._dialog = None
        self.selected_file = None
        self.upload_success_callback = None  # <-- Callback to be set externally

    def destroy(self):
        if self._dialog:
            self._dialog.destroy()
            self._dialog = None

    def __on_filter_item(self, item):
        """Filter to show only folders and Excel files."""
        if not item or item.is_folder:
            return True
        if item.path.endswith(".xls") or item.path.endswith(".xlsx"):
            return True
        return False

    def __on_apply_upload(self, filename: str, dir: str):
        """Called when the user presses the Upload button in the dialog."""
        self._dialog.hide()
        # Combine directory and filename into full path
        full_path = omni.client.combine_urls(dir if dir.endswith("/") else dir + "/", filename)
        self.upload_file(full_path, filename)

    def upload_file(self, file_path: str, filename: str):
        """Uploads the Excel file to the API endpoint."""
        try:
            carb.log_info(f"📤 Uploading file: {file_path}")
            with open(file_path, "rb") as file:
                files = {"file": (filename, file, "application/vnd.ms-excel")}
                response = requests.post(UPLOAD_URL, headers=HEADERS, files=files)
            if response.status_code == 200:
                carb.log_info(f"✔ Upload Successful: {filename}")
                _show_notification("Success!!", "New Inventory data Uploaded.", "INFO")
                # Invoke the success callback if defined
                if self.upload_success_callback:
                    self.upload_success_callback()
            else:
                carb.log_error(f"❌ Upload Failed ({response.status_code}): {response.text}")
        except Exception as e:
            carb.log_error(f"❌ Exception during file upload: {e}")

    def show_upload_dialog(self):
        """Shows the file picker dialog for selecting an Excel file."""
        self.destroy()  # Remove any previously opened dialog
        try:
            # Get a default directory (using omni.client.combine_urls if needed)
            # For example, using the ${data} token to get the data folder:
            token = carb.tokens.get_tokens_interface()
            current_directory = token.resolve("${data}")
            # Ensure a capital drive letter on Windows
            current_directory = current_directory[:1].upper() + current_directory[1:]

            self._dialog = FilePickerDialog(
                "Select Excel File to Upload",
                apply_button_label="Upload",
                current_directory=current_directory,
                click_apply_handler=self.__on_apply_upload,
                item_filter_options=["Excel Files (*.xls;*.xlsx)", "All Files (*)"],
                item_filter_fn=self.__on_filter_item,
            )
        except ImportError:
            carb.log_error("❌ Failed to import FilePickerDialog for file upload.")
