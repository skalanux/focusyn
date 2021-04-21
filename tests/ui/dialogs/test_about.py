import pytest
from gi.repository import Gtk
from wiring.scanning import scan_to_graph

from focusyn import __version__
from focusyn.ui.testing import refresh_gui


@pytest.fixture
def about(graph, config):
    graph.register_instance("focusyn.config", config)
    scan_to_graph(["focusyn.ui.dialogs.about"], graph)

    return graph.get("focusyn.ui.about")


def test_module(graph, about):
    assert graph.get("focusyn.ui.about") is about


def test_dialog_info(about):
    assert about.get_comments() == "Focusyn Pomodoro Timer (GTK+ Interface)"
    assert about.get_copyright() == "2014, Elio Esteves Duarte"
    assert about.get_version() == __version__
    assert about.get_website() == "https://github.com/eliostvs/focusyn-gtk"
    assert about.get_website_label() == "Focusyn GTK on Github"
    assert about.get_license_type() == Gtk.License.GPL_3_0
    assert about.get_logo() is not None


def test_close_dialog(about, mocker):
    about.hide = mocker.Mock()

    about.emit("response", 0)
    refresh_gui()

    about.hide.assert_called_once()
