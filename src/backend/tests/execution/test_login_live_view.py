import io

import pytest

from execution.login_live_view import LoginLiveView

FRAME_1 = b"\xff\xd8first\xff\xd9"
FRAME_2 = b"\xff\xd8second\xff\xd9"


@pytest.fixture
def popen(mocker):
    """Fake ffmpeg process that outputs two frames surrounded by garbage"""
    process = mocker.Mock()
    process.stdout = io.BufferedReader(io.BytesIO(b"junk" + FRAME_1 + FRAME_2 + b"\xff"))
    process.poll.return_value = None
    return mocker.patch("execution.login_live_view.subprocess.Popen", return_value=process)


@pytest.fixture
def login_live_view():
    return LoginLiveView()


def test_subscribe_without_running_login_returns_none(login_live_view, popen):
    assert login_live_view.subscribe(1) is None
    popen.assert_not_called()


def test_subscribe_to_other_login_returns_none(login_live_view, popen):
    login_live_view.start(1)

    assert login_live_view.subscribe(2) is None
    popen.assert_not_called()


def test_subscribe_after_stop_returns_none(login_live_view, popen):
    login_live_view.start(1)
    login_live_view.stop(1)

    assert login_live_view.subscribe(1) is None
    popen.assert_not_called()


def test_capture_is_started_once_on_first_subscribe(login_live_view, popen, monkeypatch):
    monkeypatch.setenv("DISPLAY", ":42")
    login_live_view.start(1)
    popen.assert_not_called()

    first = login_live_view.subscribe(1)
    second = login_live_view.subscribe(1)

    assert first is second
    popen.assert_called_once()
    command = popen.call_args.args[0]
    assert command[0] == "ffmpeg"
    assert command[command.index("-i") + 1] == ":42"
    login_live_view.stop(1)


def test_frames_are_read_from_capture(login_live_view, popen):
    login_live_view.start(1)
    session = login_live_view.subscribe(1)
    session.reader_thread.join(timeout=2)

    sequence, frame = session.get_frame()

    assert sequence == 2
    assert frame == FRAME_2
    login_live_view.stop(1)


def test_stop_terminates_capture_and_drops_frames(login_live_view, popen):
    login_live_view.start(1)
    session = login_live_view.subscribe(1)
    process = popen.return_value

    login_live_view.stop(1)

    process.terminate.assert_called_once()
    process.wait.assert_called()
    assert session.closed
    assert session.get_frame()[1] is None
    session.push_frame(FRAME_1)
    assert session.get_frame()[1] is None


def test_stop_of_other_login_keeps_session(login_live_view, popen):
    login_live_view.start(1)

    login_live_view.stop(2)

    assert login_live_view.subscribe(1) is not None
    login_live_view.stop(1)


def test_start_closes_previous_session(login_live_view, popen):
    login_live_view.start(1)
    previous = login_live_view.subscribe(1)

    login_live_view.start(2)

    assert previous.closed
    assert login_live_view.subscribe(1) is None
    assert login_live_view.subscribe(2) is not None
    login_live_view.stop(2)


def test_missing_ffmpeg_does_not_break_subscribe(login_live_view, mocker):
    mocker.patch(
        "execution.login_live_view.subprocess.Popen", side_effect=FileNotFoundError("ffmpeg")
    )
    login_live_view.start(1)

    session = login_live_view.subscribe(1)

    assert session is not None
    assert session.get_frame() == (0, None)
    login_live_view.stop(1)
