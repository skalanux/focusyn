import dbus
import pytest
from dbus.mainloop.glib import DBusGMainLoop
from dbusmock import DBusTestCase
from wiring.scanning import scan_to_graph

from focusyn.pomodoro import Application
from focusyn.pomodoro.app import State

DBusGMainLoop(set_as_default=True)


@pytest.fixture
def app(graph, window, plugin_engine, mocker) -> Application:
    graph.register_instance("focusyn.ui.view", window)
    graph.register_instance("focusyn.plugin", plugin_engine)
    graph.register_instance("dbus.session", mocker.Mock())

    scan_to_graph(["focusyn.pomodoro.app"], graph)

    return graph.get("focusyn.app")


def test_module(graph, app):
    instance = graph.get("focusyn.app")

    assert isinstance(instance, Application)
    assert instance is app


def test_collects_plugins_on_start(app, plugin_engine):
    assert plugin_engine.has_plugins() is True


class TestRun:
    def test_start_window_when_app_is_not_running(self, app, window):
        app.state = State.STOPPED

        app.Run()

        window.run.assert_called_once_with()

    def test_shows_window_when_app_is_running(self, app, window):
        app.state = State.STARTED

        app.Run()

        window.show.assert_called_once_with()


class TestFromGraph:
    def setup_method(self):
        DBusTestCase.start_session_bus()

    def teardown_method(self):
        DBusTestCase.tearDownClass()

    def test_create_app_instance_when_it_is_not_registered_in_dbus(self, graph, window, plugin_engine):
        graph.register_instance("focusyn.ui.view", window)
        graph.register_instance("focusyn.plugin", plugin_engine)
        scan_to_graph(["focusyn.pomodoro.app"], graph)

        instance = Application.from_graph(graph, DBusTestCase.get_dbus())

        assert isinstance(instance, Application)

    @pytest.fixture()
    def mock_dbus(self):
        mock = DBusTestCase.spawn_server(Application.BUS_NAME, Application.BUS_PATH, Application.BUS_INTERFACE)
        yield mock
        mock.terminate()
        mock.wait()

    def test_get_dbus_interface_when_is_registered_in_dbus(self, graph, mock_dbus):
        instance = Application.from_graph(graph, DBusTestCase.get_dbus())

        assert isinstance(instance, dbus.Interface)
        assert instance.dbus_interface == Application.BUS_INTERFACE
        assert instance.object_path == Application.BUS_PATH
        assert instance.requested_bus_name == Application.BUS_NAME
