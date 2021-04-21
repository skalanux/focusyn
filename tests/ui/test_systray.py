import pytest
from gi.repository import Gtk
from wiring.scanning import scan_to_graph

from focusyn.pomodoro import Events
from focusyn.ui import SystrayMenu
from focusyn.ui.testing import refresh_gui


@pytest.fixture
def window():
    return Gtk.Label()


@pytest.fixture
def subject(graph, bus, window):
    graph.register_instance("focusyn.bus", bus)
    graph.register_instance("focusyn.ui.view", window)
    scan_to_graph(["focusyn.ui.systray"], graph)
    return graph.get("focusyn.ui.systray.menu")


def test_module(graph, subject):
    instance = graph.get("focusyn.ui.systray.menu")

    assert isinstance(instance, SystrayMenu)
    assert instance is subject


def test_hide_view_when_hide_menu_is_clicked(window, subject):
    window.props.visible = False

    subject.hide_item.emit("activate")

    refresh_gui()

    assert window.props.visible is False


def test_show_window_when_hide_item_is_clicked(window, subject):
    window.props.visible = False

    subject.show_item.emit("activate")

    refresh_gui()

    assert window.props.visible is True


@pytest.mark.parametrize("event,hide,show", [(Events.WINDOW_HIDE, False, True), (Events.WINDOW_SHOW, True, False)])
def test_change_items_visibility(event, hide, show, bus, subject):
    bus.send(event)

    assert subject.hide_item.props.visible is hide
    assert subject.show_item.props.visible is show
