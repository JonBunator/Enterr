import io
import os
import threading

import pytest

from execution import login_live_view as login_live_view_module
from execution.login_live_view import LoginLiveView

FRAME_1 = b"\xff\xd8first\xff\xd9"
FRAME_2 = b"\xff\xd8second\xff\xd9"


class FakeProcess:
    """Fake ffmpeg process whose output stays open until it is terminated"""

    def __init__(self, output: bytes):
        read_fd, self._write_fd = os.pipe()
        self.stdout = os.fdopen(read_fd, "rb")
        os.write(self._write_fd, output)
        self._lock = threading.Lock()
        self.returncode = None
        self.terminate_calls = 0

    def _exit(self):
        with self._lock:
            if self.returncode is None:
                self.returncode = 0
                os.close(self._write_fd)

    def poll(self):
        return self.returncode

    def terminate(self):
        self.terminate_calls += 1
        self._exit()

    def kill(self):
        self._exit()

    def wait(self, timeout=None):
        return self.returncode


@pytest.fixture
def processes():
    processes = []
    yield processes
    for process in processes:
        process.kill()
        process.stdout.close()


@pytest.fixture
def popen(mocker, processes):
    """Every started ffmpeg outputs two frames surrounded by garbage"""

    def start(*_args, **_kwargs):
        process = FakeProcess(b"junk" + FRAME_1 + FRAME_2 + b"\xff")
        processes.append(process)
        return process

    return mocker.patch(
        "execution.login_live_view.subprocess.Popen", side_effect=start
    )


@pytest.fixture
def login_live_view():
    login_live_view = LoginLiveView()
    yield login_live_view
    active = login_live_view._active
    if active is not None:
        login_live_view.stop(active.action_history_id)


def _wait_for_frame(session, frame):
    for _ in range(100):
        if session.get_frame()[1] == frame:
            return
        threading.Event().wait(0.01)
    raise AssertionError(f"Frame {frame!r} never arrived")


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


def test_capture_is_shared_by_all_viewers(login_live_view, popen, monkeypatch):
    monkeypatch.setenv("DISPLAY", ":42")
    login_live_view.start(1)
    popen.assert_not_called()

    first = login_live_view.subscribe(1)
    second = login_live_view.subscribe(1)

    assert first is second
    assert first.viewers == 2
    popen.assert_called_once()
    command = popen.call_args.args[0]
    assert command[0] == "ffmpeg"
    assert command[command.index("-i") + 1] == ":42"
    assert command[command.index("-vf") + 1] == "scale=1280:720"
    assert command[command.index("-framerate") + 1] == "25"


def test_frames_are_read_from_capture(login_live_view, popen):
    login_live_view.start(1)
    session = login_live_view.subscribe(1)

    _wait_for_frame(session, FRAME_2)

    assert session.get_frame() == (2, FRAME_2)


def test_capture_runs_until_last_viewer_unsubscribes(
    login_live_view, popen, processes
):
    login_live_view.start(1)
    session = login_live_view.subscribe(1)
    login_live_view.subscribe(1)
    process = processes[0]

    login_live_view.unsubscribe(session)

    assert process.terminate_calls == 0
    assert session.capture is not None

    login_live_view.unsubscribe(session)

    assert process.terminate_calls == 1
    assert session.viewers == 0
    assert session.capture is None
    assert session.get_frame()[1] is None


def test_subscribe_after_all_viewers_left_restarts_capture(
    login_live_view, popen, processes
):
    login_live_view.start(1)
    session = login_live_view.subscribe(1)
    login_live_view.unsubscribe(session)

    assert login_live_view.subscribe(1) is session

    assert popen.call_count == 2
    assert processes[1].poll() is None


def test_stop_terminates_capture_and_drops_frames(login_live_view, popen, processes):
    login_live_view.start(1)
    session = login_live_view.subscribe(1)
    capture = session.capture

    login_live_view.stop(1)

    assert processes[0].poll() is not None
    assert not capture.reader_thread.is_alive()
    assert session.closed
    assert session.get_frame()[1] is None
    session.push_frame(FRAME_1, capture)
    assert session.get_frame()[1] is None


def test_stop_of_other_login_keeps_session(login_live_view, popen):
    login_live_view.start(1)

    login_live_view.stop(2)

    assert login_live_view.subscribe(1) is not None


def test_start_closes_previous_session(login_live_view, popen):
    login_live_view.start(1)
    previous = login_live_view.subscribe(1)

    login_live_view.start(2)

    assert previous.closed
    assert login_live_view.subscribe(1) is None
    assert login_live_view.subscribe(2) is not None


def test_listeners_are_notified_about_frames_and_close(login_live_view, mocker):
    mocker.patch.object(LoginLiveView, "_start_capture", return_value=None)
    login_live_view.start(1)
    session = login_live_view._active
    listener = mocker.Mock()
    session.add_listener(listener)
    capture = login_live_view_module._Capture(mocker.Mock())

    session.push_frame(FRAME_1, capture)
    login_live_view.stop(1)

    assert listener.call_count == 2
    session.remove_listener(listener)


def test_missing_ffmpeg_returns_none(login_live_view, mocker):
    mocker.patch(
        "execution.login_live_view.subprocess.Popen",
        side_effect=FileNotFoundError("ffmpeg"),
    )
    login_live_view.start(1)

    assert login_live_view.subscribe(1) is None
    assert login_live_view._active.viewers == 0


def test_ffmpeg_without_frames_returns_none(login_live_view, mocker, processes):
    def start(*_args, **_kwargs):
        # ffmpeg exits right away, e.g. because the display is missing
        process = FakeProcess(b"")
        process.terminate()
        processes.append(process)
        return process

    mocker.patch("execution.login_live_view.subprocess.Popen", side_effect=start)
    login_live_view.start(1)

    assert login_live_view.subscribe(1) is None
    assert login_live_view._active.viewers == 0
    assert login_live_view._active.capture is None


def test_frames_are_split_across_reads(login_live_view, mocker):
    session = login_live_view_module.LiveSession(1)
    process = mocker.Mock()
    process.poll.return_value = 0
    process.stdout = io.BufferedReader(io.BytesIO(FRAME_1 + FRAME_2), buffer_size=4)
    capture = login_live_view_module._Capture(process)

    LoginLiveView._read_frames(session, capture)

    assert session.get_frame() == (2, FRAME_2)
    assert capture.ended
