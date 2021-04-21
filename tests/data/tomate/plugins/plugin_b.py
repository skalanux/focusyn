import focusyn.pomodoro.plugin as plugin
from focusyn.pomodoro import Events, on


class PluginB(plugin.Plugin):
    has_settings = False

    @on(Events.WINDOW_SHOW)
    def listener(self, *_, **__) -> str:
        return "plugin_b"
