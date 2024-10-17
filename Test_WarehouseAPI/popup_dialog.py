from omni.kit.window.popup_dialog import MessageDialog

def show_notification():
    status=omni.kit.notification_manager.NotificationStatus.WARNING
    ok_button = omni.kit.notification_manager.NotificationButtonInfo("OK", on_complete=None)
    omni.kit.notification_manager.post_notification("notification 12313242534kpkgt[r]",
                                                    hide_after_timeout=False,
                                                    duration=0,
                                                    status=status,
                                                    button_infos=[ok_button])


# Call the function to show the notification dialog
show_notification()
