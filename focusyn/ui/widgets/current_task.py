import logging

from gi.repository import Gtk
from wiring import SingletonScope, inject
from wiring.scanning import register

from focusyn.pomodoro import Bus, Events, SessionPayload, Subscriber, TimerPayload, format_time_left, on

logger = logging.getLogger(__name__)


@register.factory("focusyn.ui.current_task", scope=SingletonScope)
class CurrentTask(Subscriber):
    @inject(bus="focusyn.bus")
    def __init__(self, bus: Bus):
        self.widget = Gtk.Entry(margin_top=30, margin_bottom=10, margin_right=10, margin_left=10)
        self.connect(bus)

    @on(Events.TIMER_UPDATE)
    def _on_timer_update(self, _, payload: TimerPayload) -> None:
        #self._update(payload.time_left)
        pass

    @on(Events.SESSION_START)
    def _on_session_start(self, _, payload: SessionPayload) -> None:
        self.widget.set_editable(False)
        #self._update(payload.duration)

    @on(Events.SESSION_INTERRUPT)
    def _on_session_interrupt(self, _, payload: SessionPayload) -> None:
        self.widget.set_editable(True)
        self.widget.grab_focus_without_selecting()


    def _update(self, duration: int) -> None:
        formatted_duration = format_time_left(duration)
        self.widget.set_text(self.timer_markup(formatted_duration))
        logger.debug("action=update value=%s", formatted_duration)

    @staticmethod
    def timer_markup(time_left: str) -> str:
        return '<span face="sans-serif" font="45">{}</span>'.format(time_left)
