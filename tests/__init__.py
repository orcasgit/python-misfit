import threading
import unittest

from contextlib import contextmanager
from mock import patch


class TestMisfitBase(unittest.TestCase):
    @contextmanager
    def wait_for_thread(self, mock_obj):
        event = threading.Event()
        mock_obj.side_effect = lambda *args, **kwargs: event.set()
        with patch.object(event, 'wait'):
            yield
        event.wait()
