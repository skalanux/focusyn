from gi.repository import GdkPixbuf, Gtk
from wiring import SingletonScope, inject
from wiring.scanning import register


@register.factory("focusyn.ui.about", scope=SingletonScope)
class AboutDialog(Gtk.AboutDialog):
    @inject(config="focusyn.config")
    def __init__(self, config):
        Gtk.AboutDialog.__init__(
            self,
            comments="Focusyn Pomodoro Timer (GTK+ Interface)",
            copyright="2014, Elio Esteves Duarte",
            license="GPL-3",
            license_type=Gtk.License.GPL_3_0,
            logo=GdkPixbuf.Pixbuf.new_from_file(config.icon_path("focusyn", 48)),
            modal=True,
            program_name="Focusyn Gtk",
            title="Focusyn Gtk",
            version="0.12.0",
            website="https://github.com/eliostvs/focusyn-gtk",
            website_label="Focusyn GTK on Github",
        )

        self.props.authors = ["Elio Esteves Duarte"]
        self.connect("response", lambda widget, _: widget.hide())

    @property
    def widget(self):
        return self
