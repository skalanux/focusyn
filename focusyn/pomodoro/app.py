import enum

import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from wiring import SingletonScope, inject
from wiring.scanning import register

from .plugin import PluginEngine


class State(enum.Enum):
    STOPPED = 1
    STARTED = 2


@register.factory("focusyn.app", scope=SingletonScope)
class Application(dbus.service.Object):
    BUS_NAME = "com.github.Focusyn"
    BUS_PATH = "/com/github/Focusyn"
    BUS_INTERFACE = "com.github.Focusyn"
    SPEC = "focusyn.app"

    @inject(bus="dbus.session", window="focusyn.ui.view", plugins="focusyn.plugin")
    def __init__(self, bus, window, plugins: PluginEngine):
        dbus.service.Object.__init__(self, bus, self.BUS_PATH)
        self.state = State.STOPPED
        self._window = window
        plugins.collect()

    @dbus.service.method(BUS_INTERFACE, out_signature="b")
    def IsRunning(self):
        return self.state == State.STARTED

    @dbus.service.method(BUS_INTERFACE, out_signature="b")
    def Run(self):
        if self.IsRunning():
            self._window.show()
        else:
            self.state = State.STARTED
            self._window.run()

        return True

    @classmethod
    def from_graph(cls, graph, bus=dbus.SessionBus(mainloop=DBusGMainLoop())):
        request = bus.request_name(cls.BUS_NAME, dbus.bus.NAME_FLAG_DO_NOT_QUEUE)

        if request != dbus.bus.REQUEST_NAME_REPLY_EXISTS:
            graph.register_instance("dbus.session", bus)
            instance = graph.get(cls.SPEC)
        else:
            bus_object = bus.get_object(cls.BUS_NAME, cls.BUS_PATH)
            instance = dbus.Interface(bus_object, cls.BUS_INTERFACE)

        return instance
