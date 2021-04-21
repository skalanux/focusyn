import pytest
from wiring.scanning import scan_to_graph

from focusyn.pomodoro import Events, Session, SessionPayload, SessionType
from focusyn.pomodoro.session import State
from focusyn.ui.testing import create_session_end_payload, create_session_payload, run_loop_for


@pytest.fixture()
def session(graph, config, bus, mocker):
    graph.register_instance("focusyn.bus", bus)
    graph.register_instance("focusyn.config", config)
    mocker.patch("uuid.uuid4", return_value="1234")
    scan_to_graph(["focusyn.pomodoro.timer", "focusyn.pomodoro.session"], graph)
    return graph.get("focusyn.session")


def test_module(graph, session):
    instance = graph.get("focusyn.session")

    assert isinstance(instance, Session)
    assert instance is session


class TestSessionStart:
    def test_does_not_start_when_session_is_already_running(self, session):
        session.state = State.STARTED

        assert not session.start()

    @pytest.mark.parametrize("state", [State.ENDED, State.STOPPED])
    def test_starts_when_session_is_not_running(self, state, session, bus, mocker):
        session.state = state

        subscriber = mocker.Mock()
        bus.connect(Events.SESSION_START, subscriber, weak=False)

        result = session.start()

        assert result is True
        payload = SessionPayload(
            id="1234",
            type=SessionType.POMODORO,
            pomodoros=0,
            duration=25 * 60,
        )
        subscriber.assert_called_once_with(Events.SESSION_START, payload=payload)


class TestSessionStop:
    @pytest.mark.parametrize("state", [State.ENDED, State.STOPPED, State.STARTED])
    def test_does_not_stop_when_session_is_not_running(self, state, session):
        session.state = state

        assert not session.stop()

    def test_stops_when_session_is_running(self, session, bus, mocker):
        subscriber = mocker.Mock()
        bus.connect(Events.SESSION_INTERRUPT, subscriber, False)

        session.start()
        result = session.stop()

        assert result is True
        payload = SessionPayload(
            id="1234",
            type=SessionType.POMODORO,
            duration=25 * 60,
            pomodoros=0,
        )
        subscriber.assert_called_once_with(Events.SESSION_INTERRUPT, payload=payload)


class TestSessionReset:
    def test_does_not_reset_when_session_is_running(self, session):
        session.state = State.STARTED

        assert not session.reset()

    @pytest.mark.parametrize(
        "state,session_type,duration",
        [
            (State.ENDED, SessionType.SHORT_BREAK, 5 * 60),
            (State.STOPPED, SessionType.POMODORO, 25 * 60),
        ],
    )
    def test_resets_when_session_is_not_running(self, state, session_type, duration, session, bus, mocker):
        session.state = state
        session.current = session_type
        session.pomodoros = 1

        subscriber = mocker.Mock()
        bus.connect(Events.SESSION_RESET, subscriber, False)

        result = session.reset()

        assert result is True
        payload = SessionPayload(
            id="1234",
            type=session_type,
            pomodoros=0,
            duration=duration,
        )
        subscriber.assert_called_once_with(Events.SESSION_RESET, payload=payload)


class TestSessionEnd:
    @pytest.mark.parametrize("state", [State.ENDED, State.STOPPED])
    def test_does_end_when_session_is_not_running(self, state, session):
        session.state = state

        assert not session._end(None, None)

    def test_does_not_end_when_session_start_but_time_still_running(self, session):
        session.start()

        assert not session._end(None, None)

    @pytest.mark.parametrize(
        "old_session,old_pomodoros,new_session,new_pomodoros",
        [
            (SessionType.POMODORO, 0, SessionType.SHORT_BREAK, 1),
            (SessionType.LONG_BREAK, 0, SessionType.POMODORO, 0),
            (SessionType.SHORT_BREAK, 0, SessionType.POMODORO, 0),
            (SessionType.POMODORO, 3, SessionType.LONG_BREAK, 4),
        ],
    )
    def test_ends_when_session_is_running(
        self,
        old_session,
        old_pomodoros,
        new_session,
        new_pomodoros,
        session,
        config,
        bus,
        mocker,
    ):
        session.current = old_session
        session.pomodoros = old_pomodoros

        config.set("Timer", "pomodoro_duration", 0.02)
        config.set("Timer", "longbreak_duration", 0.02)
        config.set("Timer", "shortbreak_duration", 0.02)
        config.parser.getint = config.parser.getfloat

        subscriber = mocker.Mock()
        bus.connect(Events.SESSION_END, subscriber, False)

        session.start()
        run_loop_for(2)

        payload = create_session_end_payload(
            type=new_session,
            pomodoros=new_pomodoros,
            duration=1,
            previous=create_session_payload(type=old_session, pomodoros=old_pomodoros, duration=1),
        )
        subscriber.assert_called_once_with(Events.SESSION_END, payload=payload)


class TestSessionChange:
    def test_does_not_change_session_when_it_is_running(self, session):
        session.state = State.STARTED

        assert session.change(session=SessionType.LONG_BREAK) is False
        assert session.current is SessionType.POMODORO

    @pytest.mark.parametrize(
        "state,old,new",
        [
            (State.STOPPED, SessionType.SHORT_BREAK, SessionType.SHORT_BREAK),
            (State.ENDED, SessionType.LONG_BREAK, SessionType.LONG_BREAK),
        ],
    )
    def test_changes_session_when_it_is_not_running(self, state, old, new, bus, session, config, mocker):
        session.state = state
        subscriber = mocker.Mock()
        bus.connect(Events.SESSION_CHANGE, subscriber, False)

        assert session.change(session=new) is True
        assert session.current is new
        payload = create_session_payload(type=new, duration=config.get_int("Timer", new.option) * 60)
        subscriber.assert_called_once_with(Events.SESSION_CHANGE, payload=payload)

    @pytest.mark.parametrize("state", [State.STOPPED, State.ENDED])
    def test_listens_config_change_when_session_is_not_running(self, session, bus, mocker, state, config):
        session.state = state
        subscriber = mocker.Mock()
        bus.connect(Events.SESSION_CHANGE, subscriber, False)

        config.set("timer", SessionType.POMODORO.option, 20)

        payload = create_session_payload(duration=20 * 60)
        subscriber.assert_called_once_with(Events.SESSION_CHANGE, payload=payload)

    def test_not_listen_config_change_when_session_is_running(self, session, bus, config, mocker):
        session.state = State.STARTED
        subscriber = mocker.Mock()
        bus.connect(Events.SESSION_CHANGE, subscriber, False)

        config.set("timer", SessionType.POMODORO.option, 24)

        subscriber.assert_not_called()


def test_type_of():
    assert SessionType.POMODORO == SessionType.of(0)
    assert SessionType.SHORT_BREAK == SessionType.of(1)
    assert SessionType.LONG_BREAK == SessionType.of(2)


def test_type_option():
    assert SessionType.POMODORO.option == "pomodoro_duration"
    assert SessionType.SHORT_BREAK.option == "shortbreak_duration"
    assert SessionType.LONG_BREAK.option == "longbreak_duration"
