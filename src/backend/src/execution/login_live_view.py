import os
import subprocess
import threading
from collections.abc import Callable

FRAME_RATE = 25
CAPTURE_SIZE = "1920x1080"
# Scaled down to save bandwidth, the frame rate is kept for a smooth live view
OUTPUT_SIZE = "1280:720"
JPEG_QUALITY = 5
# Seconds a new viewer waits for the first frame before the live view counts as failed
FIRST_FRAME_TIMEOUT = 5

_JPEG_START = b"\xff\xd8"
_JPEG_END = b"\xff\xd9"
_READ_CHUNK_SIZE = 64 * 1024
_PROCESS_EXIT_TIMEOUT = 2


class _Capture:
    """One ffmpeg process that captures the virtual display"""

    def __init__(self, process: subprocess.Popen):
        self.process = process
        self.reader_thread: threading.Thread | None = None
        # Set when nobody needs the capture anymore, its frames are ignored from then on
        self.stopped = False
        # Set when ffmpeg stopped sending frames
        self.ended = False


class LiveSession:
    """
    Live view of exactly one running login. Frames are only ever stored while the
    session is open, so a closed session can never hand out frames of another login.
    """

    def __init__(self, action_history_id: int):
        self.action_history_id = action_history_id
        self.closed = False
        self.viewers = 0
        self.capture: _Capture | None = None
        self._frame: bytes | None = None
        self._sequence = 0
        self._condition = threading.Condition()
        self._listeners: set[Callable[[], None]] = set()

    def add_listener(self, listener: Callable[[], None]):
        """The listener is called on every new frame and when the session closes"""
        with self._condition:
            self._listeners.add(listener)

    def remove_listener(self, listener: Callable[[], None]):
        with self._condition:
            self._listeners.discard(listener)

    def push_frame(self, frame: bytes, capture: _Capture):
        with self._condition:
            if self.closed or capture.stopped:
                return
            self._frame = frame
            self._sequence += 1
            self._condition.notify_all()
            listeners = list(self._listeners)
        for listener in listeners:
            listener()

    def get_frame(self) -> tuple[int, bytes | None]:
        with self._condition:
            return self._sequence, self._frame

    def wait_for_first_frame(self, timeout: float) -> bool:
        with self._condition:
            self._condition.wait_for(
                lambda: self._frame is not None
                or self.closed
                or self.capture is None
                or self.capture.ended,
                timeout,
            )
            return self._frame is not None and not self.closed

    def add_viewer(
        self, start_capture: Callable[["LiveSession"], _Capture | None]
    ) -> bool:
        """Starts the capture if needed. Returns False if the session is closed."""
        with self._condition:
            if self.closed:
                return False
            self.viewers += 1
            if self.capture is None or self.capture.ended:
                self.capture = start_capture(self)
            return True

    def remove_viewer(self) -> _Capture | None:
        """Returns the capture that has to be stopped because nobody watches anymore"""
        with self._condition:
            self.viewers = max(self.viewers - 1, 0)
            if self.viewers > 0 or self.capture is None:
                return None
            capture = self.capture
            capture.stopped = True
            self.capture = None
            # A new viewer must not get a frame of a stopped capture
            self._frame = None
            return capture

    def capture_ended(self, capture: _Capture):
        with self._condition:
            capture.ended = True
            self._condition.notify_all()

    def close(self) -> _Capture | None:
        """Returns the capture that has to be stopped"""
        with self._condition:
            self.closed = True
            self._frame = None
            capture = self.capture
            self.capture = None
            if capture is not None:
                capture.stopped = True
            self._condition.notify_all()
            listeners = list(self._listeners)
        for listener in listeners:
            listener()
        return capture


class LoginLiveView:
    """
    Captures the virtual display while a login is running and hands the frames to
    the viewers of that login. The scheduler runs one login at a time and calls
    stop() before the next login starts, so a session only ever contains frames of
    its own login.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._active: LiveSession | None = None

    def start(self, action_history_id: int):
        with self._lock:
            previous = self._active
            self._active = LiveSession(action_history_id)
        if previous is not None:
            LoginLiveView._close_session(previous)

    def stop(self, action_history_id: int):
        with self._lock:
            session = self._active
            if session is None or session.action_history_id != action_history_id:
                return
            self._active = None
        LoginLiveView._close_session(session)

    def subscribe(self, action_history_id: int) -> LiveSession | None:
        """
        Blocks until the first frame is available. Every successful subscribe must be
        followed by unsubscribe(), so the capture stops once nobody is watching.
        """
        with self._lock:
            session = self._active
            if session is None or session.action_history_id != action_history_id:
                return None
        # Capture only while someone is watching, all viewers share one capture
        if not session.add_viewer(LoginLiveView._start_capture):
            return None
        # No frames arrive if ffmpeg or the display is missing
        if not session.wait_for_first_frame(FIRST_FRAME_TIMEOUT):
            self.unsubscribe(session)
            return None
        return session

    @staticmethod
    def unsubscribe(session: LiveSession):
        # Must not block, it is called from the event loop
        capture = session.remove_viewer()
        if capture is not None and capture.process.poll() is None:
            capture.process.terminate()

    @staticmethod
    def _ffmpeg_command() -> list[str]:
        # The display is never taken from user input
        display = os.getenv("DISPLAY", ":99")
        return [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-video_size",
            CAPTURE_SIZE,
            "-framerate",
            str(FRAME_RATE),
            "-f",
            "x11grab",
            "-i",
            display,
            "-vf",
            f"scale={OUTPUT_SIZE}",
            "-codec:v",
            "mjpeg",
            "-q:v",
            str(JPEG_QUALITY),
            "-f",
            "mjpeg",
            "pipe:1",
        ]

    @staticmethod
    def _start_capture(session: LiveSession) -> _Capture | None:
        try:
            process = subprocess.Popen(
                LoginLiveView._ffmpeg_command(),
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
            )
        except OSError as exception:
            print(f"Could not start live view capture: {exception!r}")
            return None
        capture = _Capture(process)
        capture.reader_thread = threading.Thread(
            target=LoginLiveView._read_frames,
            args=(session, capture),
            daemon=True,
        )
        capture.reader_thread.start()
        return capture

    @staticmethod
    def _read_frames(session: LiveSession, capture: _Capture):
        buffer = bytearray()
        try:
            while not capture.stopped:
                chunk = capture.process.stdout.read1(_READ_CHUNK_SIZE)
                if not chunk:
                    return
                buffer += chunk
                while True:
                    start = buffer.find(_JPEG_START)
                    if start == -1:
                        # Keep the last byte, it could be half of a start marker
                        del buffer[:-1]
                        break
                    end = buffer.find(_JPEG_END, start + len(_JPEG_START))
                    if end == -1:
                        del buffer[:start]
                        break
                    end += len(_JPEG_END)
                    session.push_frame(bytes(buffer[start:end]), capture)
                    del buffer[:end]
        finally:
            session.capture_ended(capture)
            LoginLiveView._stop_process(capture.process)

    @staticmethod
    def _stop_process(process: subprocess.Popen):
        if process.poll() is None:
            process.terminate()
        try:
            process.wait(timeout=_PROCESS_EXIT_TIMEOUT)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()

    @staticmethod
    def _close_session(session: LiveSession):
        capture = session.close()
        if capture is None:
            return
        LoginLiveView._stop_process(capture.process)
        if capture.reader_thread is not None:
            capture.reader_thread.join(timeout=_PROCESS_EXIT_TIMEOUT)
