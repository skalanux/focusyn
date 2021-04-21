from gi.repository import Gtk

import focusyn.pomodoro.plugin as plugin
from focusyn.pomodoro import Events, on


class PluginA(plugin.Plugin):
    has_settings = True

    def __init__(self):
        super().__init__()
        self.parent = None

    @on(Events.WINDOW_SHOW)
    def listener(self, *_, **__) -> str:
        return "plugin_a"

    def settings_window(self, parent: Gtk.Widget) -> Gtk.Dialog:
        self.parent = parent
        dialog = Gtk.MessageDialog(
            message_type=Gtk.MessageType.INFO,
            transient_for=parent,
            buttons=Gtk.ButtonsType.OK,
            text="Plugin A Settings",
        )
        dialog.connect("response", lambda widget, _: widget.destroy())
        return dialog
