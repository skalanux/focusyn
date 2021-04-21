import pytest
from gi.repository import Gdk, Gtk
from wiring.scanning import scan_to_graph

from focusyn.pomodoro import Events
from focusyn.ui import Systray, Window
from focusyn.ui.testing import active_shortcut, create_session_end_payload, create_session_payload


@pytest.fixture
def window(bus, config, graph, session) -> Window:
    graph.register_instance("focusyn.bus", bus)
    graph.register_instance("focusyn.config", config)
    graph.register_instance("focusyn.session", session)

    namespaces = [
        "focusyn.ui",
        "focusyn.pomodoro.plugin",
    ]
    scan_to_graph(namespaces, graph)
    return graph.get("focusyn.ui.view")


def test_module(graph, window):
    instance = graph.get("focusyn.ui.view")

    assert isinstance(instance, Window)
    assert instance is window


def test_shortcuts(shortcut_engine, window):
    from focusyn.ui.widgets import HeaderBar

    assert active_shortcut(shortcut_engine, HeaderBar.START_SHORTCUT, window=window.widget) is True


def test_start(mocker, window):
    gtk_main = mocker.patch("focusyn.ui.window.Gtk.main")
    show_all = mocker.patch("focusyn.ui.window.Gtk.Window.show_all")

    window.run()

    gtk_main.assert_called_once_with()
    show_all.assert_called_once_with()


class TestWindowHide:
    def test_iconify_when_tray_icon_plugin_is_not_registered(self, window, bus, mocker):
        subscriber = mocker.Mock()
        bus.connect(Events.WINDOW_HIDE, subscriber, weak=False)

        result = window.hide()

        assert result is Gtk.true
        subscriber.assert_called_once_with(Events.WINDOW_HIDE, payload=None)

    def test_deletes_when_tray_icon_plugin_is_registered(self, bus, graph, mocker, window):
        graph.register_factory(Systray, mocker.Mock)
        subscriber = mocker.Mock()
        bus.connect(Events.WINDOW_HIDE, subscriber, weak=False)
        window.widget.set_visible(True)

        result = window.hide()

        assert result
        assert window.widget.get_visible() is False
        subscriber.assert_called_once_with(Events.WINDOW_HIDE, payload=None)


class TestWindowQuit:
    def test_quits_when_timer_is_not_running(self, mocker, session, window):
        main_quit = mocker.patch("focusyn.ui.window.Gtk.main_quit")
        session.is_running.return_value = False

        window.widget.emit("delete-event", Gdk.Event.new(Gdk.EventType.DELETE))

        main_quit.assert_called_once_with()

    def test_hides_when_timer_is_running(self, bus, mocker, session, window):
        session.is_running.return_value = True
        subscriber = mocker.Mock()
        bus.connect(Events.WINDOW_HIDE, subscriber, weak=False)

        window.widget.emit("delete-event", Gdk.Event.new(Gdk.EventType.DELETE))

        subscriber.assert_called_once_with(Events.WINDOW_HIDE, payload=None)


def test_shows_window_when_session_end(bus, mocker, window):
    window.widget.set_visible(False)
    subscriber = mocker.Mock()
    bus.connect(Events.WINDOW_SHOW, subscriber, weak=False)
    payload = create_session_end_payload(previous=create_session_payload())

    bus.send(Events.SESSION_END, payload=payload)

    assert window.widget.get_visible()
    subscriber.assert_called_once_with(Events.WINDOW_SHOW, payload=None)
