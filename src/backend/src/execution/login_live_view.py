import os
import subprocess
import threading

FRAME_RATE = 25
VIDEO_SIZE = "1920x1080"
JPEG_QUALITY = 5

_JPEG_START = b"\xff\xd8"
_JPEG_END = b"\xff\xd9"
_READ_CHUNK_SIZE = 64 * 1024


class LiveSession:
    """
    Live view of exactly one running login. Frames are only ever stored while the
    session is open, so a closed session can never hand out frames of another login.
    """

    def __init__(self, action_history_id: int):
        self.action_history_id = action_history_id
        self.closed = False
        self.capture_started = False
        self.process: subprocess.Popen | None = None
        self.reader_thread: threading.Thread | None = None
        self._frame: bytes | None = None
        self._sequence = 0
        self._lock = threading.Lock()

    def push_frame(self, frame: bytes):
        with self._lock:
            if self.closed:
                return
            self._frame = frame
            self._sequence += 1

    def get_frame(self) -> tuple[int, bytes | None]:
        with self._lock:
            return self._sequence, self._frame

    def close(self):
        with self._lock:
            self.closed = True
            self._frame = None


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
        with self._lock:
            session = self._active
            if (
                session is None
                or session.closed
                or session.action_history_id != action_history_id
            ):
                return None
            # Capture only while someone is watching, all viewers share one capture
            if not session.capture_started:
                session.capture_started = True
                LoginLiveView._start_capture(session)
            return session

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
            VIDEO_SIZE,
            "-framerate",
            str(FRAME_RATE),
            "-f",
            "x11grab",
            "-i",
            display,
            "-codec:v",
            "mjpeg",
            "-q:v",
            str(JPEG_QUALITY),
            "-f",
            "mjpeg",
            "pipe:1",
        ]

    @staticmethod
    def _start_capture(session: LiveSession):
        try:
            session.process = subprocess.Popen(
                LoginLiveView._ffmpeg_command(),
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
            )
        except OSError as exception:
            print(f"Could not start live view capture: {exception!r}")
            return
        session.reader_thread = threading.Thread(
            target=LoginLiveView._read_frames,
            args=(session, session.process.stdout),
            daemon=True,
        )
        session.reader_thread.start()

    @staticmethod
    def _read_frames(session: LiveSession, stdout):
        buffer = b""
        while not session.closed:
            chunk = stdout.read1(_READ_CHUNK_SIZE)
            if not chunk:
                return
            buffer += chunk
            while True:
                start = buffer.find(_JPEG_START)
                if start == -1:
                    # Keep the last byte, it could be the first half of a start marker
                    buffer = buffer[-1:]
                    break
                end = buffer.find(_JPEG_END, start + len(_JPEG_START))
                if end == -1:
                    buffer = buffer[start:]
                    break
                session.push_frame(buffer[start : end + len(_JPEG_END)])
                buffer = buffer[end + len(_JPEG_END) :]

    @staticmethod
    def _close_session(session: LiveSession):
        session.close()
        process = session.process
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        if session.reader_thread is not None:
            session.reader_thread.join(timeout=2)
