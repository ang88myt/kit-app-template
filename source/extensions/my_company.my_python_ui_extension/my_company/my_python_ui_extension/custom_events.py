#events.py
__all__ = ["CustomEvents"]

import carb.events
import omni.kit.app

class CustomEvents:
    STOCK_INFO_FETCHED = carb.events.type_from_id(" my_company.my_python_ui_extension.data_service")

    @staticmethod
    def emit_stock_info(info):
        """Emit the stock info fetched event."""
        payload = {"stock_info": info}
        omni.kit.app.get_app().event_stream.post(CustomEvents.STOCK_INFO_FETCHED, payload)
