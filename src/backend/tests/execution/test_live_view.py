import io

import pytest

from execution.live_view import LiveView

FRAME_1 = b"\xff\xd8first\xff\xd9"
FRAME_2 = b"\xff\xd8second\xff\xd9"


@pytest.fixture
def popen(mocker):
    """Fake ffmpeg process that outputs two frames surrounded by garbage"""
    process = mocker.Mock()
    process.stdout = io.BufferedReader(io.BytesIO(b"junk" + FRAME_1 + FRAME_2 + b"\xff"))
    process.poll.return_value = None
    return mocker.patch("execution.live_view.subprocess.Popen", return_value=process)


@pytest.fixture
def live_view():
    return LiveView()


def test_subscribe_without_running_login_returns_none(live_view, popen):
    assert live_view.subscribe(1) is None
    popen.assert_not_called()


def test_subscribe_to_other_login_returns_none(live_view, popen):
    live_view.start(1)

    assert live_view.subscribe(2) is None
    popen.assert_not_called()


def test_subscribe_after_stop_returns_none(live_view, popen):
    live_view.start(1)
    live_view.stop(1)

    assert live_view.subscribe(1) is None
    popen.assert_not_called()


def test_capture_is_started_once_on_first_subscribe(live_view, popen, monkeypatch):
    monkeypatch.setenv("DISPLAY", ":42")
    live_view.start(1)
    popen.assert_not_called()

    first = live_view.subscribe(1)
    second = live_view.subscribe(1)

    assert first is second
    popen.assert_called_once()
    command = popen.call_args.args[0]
    assert command[0] == "ffmpeg"
    assert command[command.index("-i") + 1] == ":42"
    live_view.stop(1)


def test_frames_are_read_from_capture(live_view, popen):
    live_view.start(1)
    session = live_view.subscribe(1)
    session.reader_thread.join(timeout=2)

    sequence, frame = session.get_frame()

    assert sequence == 2
    assert frame == FRAME_2
    live_view.stop(1)


def test_stop_terminates_capture_and_drops_frames(live_view, popen):
    live_view.start(1)
    session = live_view.subscribe(1)
    process = popen.return_value

    live_view.stop(1)

    process.terminate.assert_called_once()
    process.wait.assert_called()
    assert session.closed
    assert session.get_frame()[1] is None
    session.push_frame(FRAME_1)
    assert session.get_frame()[1] is None


def test_stop_of_other_login_keeps_session(live_view, popen):
    live_view.start(1)

    live_view.stop(2)

    assert live_view.subscribe(1) is not None
    live_view.stop(1)


def test_start_closes_previous_session(live_view, popen):
    live_view.start(1)
    previous = live_view.subscribe(1)

    live_view.start(2)

    assert previous.closed
    assert live_view.subscribe(1) is None
    assert live_view.subscribe(2) is not None
    live_view.stop(2)


def test_missing_ffmpeg_does_not_break_subscribe(live_view, mocker):
    mocker.patch(
        "execution.live_view.subprocess.Popen", side_effect=FileNotFoundError("ffmpeg")
    )
    live_view.start(1)

    session = live_view.subscribe(1)

    assert session is not None
    assert session.get_frame() == (0, None)
    live_view.stop(1)
