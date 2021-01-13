#
# Copyright (c) 2021 Carsten Igel.
#
# This file is part of celery-client-stubs
# (see https://github.com/carstencodes/celery-client-stubs).
#
# License: 3-clause BSD, see https://opensource.org/licenses/BSD-3-Clause
#

from datetime import datetime, timedelta
import unittest

import celery_client_stubs


class MockAsyncResult:
    pass


class MockCelery:
    def send_task(
        self,
        name,
        *args,
        result_cls=None,
        countdown=None,
        eta=None,
        expires=None,
    ):
        setattr(self, "name", name)
        setattr(self, "args", args)
        setattr(self, "result_cls", result_cls)
        setattr(self, "countdown", countdown)
        setattr(self, "eta", eta)
        setattr(self, "expires", expires)

        return MockAsyncResult()


class MyTask(celery_client_stubs.AsyncRemoteTask):
    def __init__(self, celery, *args) -> None:
        super().__init__("my_task", celery, *args)


class BasicTest(unittest.TestCase):
    def test_name(self):
        celery = MockCelery()
        task = MyTask(celery, 1, 2, 3)
        task.schedule_immediately()
        self.assertEqual(celery.name, "my_task")
        self.assertIsNone(celery.countdown)
        self.assertIsNone(celery.eta)
        self.assertIsNone(celery.expires)

    def test_args(self):
        celery = MockCelery()
        task = MyTask(celery, 1, 2, 3)
        task.schedule_immediately()
        self.assertEqual(celery.args, (1, 2, 3))
        self.assertIsNone(celery.countdown)
        self.assertIsNone(celery.eta)
        self.assertIsNone(celery.expires)

    def test_delayed(self):
        celery = MockCelery()
        task = MyTask(celery, 1, 2, 3)
        task.schedule_delayed(delay_in_seconds=1.0)
        self.assertEqual(celery.countdown, 1.0)
        self.assertIsNone(celery.eta)
        self.assertIsNone(celery.expires)

    def test_immediately(self):
        celery = MockCelery()
        task = MyTask(celery, 1, 2, 3)
        task.schedule_immediately()
        self.assertIsNone(celery.countdown)
        self.assertIsNone(celery.eta)
        self.assertIsNone(celery.expires)

    def test_tomorrow(self):
        celery = MockCelery()
        task = MyTask(celery, 1, 2, 3)
        tomorrow = timedelta(days=1.0) + datetime.now()
        task.schedule_until(execution_time=tomorrow)
        self.assertIsNone(celery.countdown)
        self.assertEqual(celery.eta, tomorrow)
        self.assertIsNone(celery.expires)

    def test_before(self):
        celery = MockCelery()
        task = MyTask(celery, 1, 2, 3)
        tomorrow = timedelta(days=1.0) + datetime.now()
        task.schedule_termination_before(dead_line=tomorrow)
        self.assertIsNone(celery.countdown)
        self.assertIsNone(celery.eta)
        self.assertEqual(celery.expires, tomorrow)


if __name__ == "__main__":
    unittest.main
