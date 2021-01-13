#
# Copyright (c) 2021 Carsten Igel.
#
# This file is part of celery-client-stubs
# (see https://github.com/carstencodes/celery-client-stubs).
#
# License: 3-clause BSD, see https://opensource.org/licenses/BSD-3-Clause
#

"""
Definition of remote stub factory or proxy classes for Celery
"""

from typing import (
    Generic,
    Tuple,
    TypeVar,
    Optional,
    Dict,
    Any,
    Union,
)

# from typing import List
from datetime import datetime
from dataclasses import dataclass, asdict, field

from celery import Celery
from celery.result import AsyncResult, ResultBase

# from celery.app.routes import Router
# from celery.canvas import Signature
# from kombu import Producer, Connection


TResultType = TypeVar("TResultType", bound=ResultBase)


@dataclass
class CeleryOptions:
    """A small dataclass representing the most common options for a remote celery task."""

    countdown: Optional[float] = field(init=False, repr=True, default=None)
    eta: Optional[datetime] = field(init=False, repr=True, default=None)
    expires: Optional[Union[datetime, float]] = field(
        init=False, repr=True, default=None
    )


#    producer: Optional[Producer] = None
#    connection: Optional[Connection] = None
#    router: Optional[Router]=None
#    task_id: Optional[str] =None
#    link: Optional[Union[Signature, List[Signature]]]=None
#    link_error: Optional[Union[Signature, List[Signature]]]=None
#    add_to_parent:bool=True
#    group_id=None
#    group_index=None
#    retries: int=0
#    chord=None
#    reply_to=None
#    time_limit=None
#    soft_time_limit=None
#    root_id=None
#    parent_id=None
#    route_name=None
#    shadow=None
#    chain=None
#    task_type=None


class _CeleryDependent:
    """Definition of a celery dependent object."""

    def __init__(self, celery: Celery) -> None:
        self.__celery = celery

    @property
    def _celery(self) -> Celery:
        return self.__celery


class RemoteTask(Generic[TResultType], _CeleryDependent):
    """Basic definition of a remote executed task."""

    def __init__(self, name: str, celery: Celery, *args) -> None:
        super().__init__(celery)
        self.__name = name
        self.__args: Tuple = args

    @property
    def name(self) -> str:
        """Gets the name of the task.

        Returns:
            str: The name of the task.
        """
        return self.__name

    def _send(self, *, options: Optional[CeleryOptions] = None) -> TResultType:
        opts = options or CeleryOptions()
        d_opts: Dict[str, Any] = asdict(opts)
        return self._celery.send_task(
            self.name, *self.__args, result_cls=TResultType, **d_opts
        )

    def schedule_immediately(
        self, *, options: Optional[CeleryOptions] = None
    ) -> TResultType:
        """Schedules the remote task for immediate execution.

        Args:
            options (Optional[CeleryOptions], optional):
            The celery options to apply. Defaults to None.

        Returns:
            TResultType: The resulting celery result.
        """
        return self._send(options=options)

    def schedule_delayed(
        self,
        *,
        delay_in_seconds: float,
        options: Optional[CeleryOptions] = None,
    ) -> TResultType:
        """Schedules a task for delayed execution.

        Args:
            delay_in_seconds (float): The delay in
                seconds for the task to start.
            options (Optional[CeleryOptions], optional): The
                common options for a task. Defaults to None.

        Returns:
            TResultType: The resulting proxy for a task.
        """
        options = options or CeleryOptions()
        options.countdown = delay_in_seconds
        return self._send(options=options)

    def schedule_termination_before(
        self,
        *,
        dead_line: Union[float, datetime],
        options: Optional[CeleryOptions] = None,
    ) -> TResultType:
        """Schedules a task with an expiration time.

        Args:
            dead_line (Union[float, datetime]): The time
                after which the task has been expired.
            options (Optional[CeleryOptions], optional): The
                common options of a task. Defaults to None.

        Returns:
            TResultType: The resulting proxy type.
        """
        options = options or CeleryOptions()
        options.expires = dead_line
        return self._send(options=options)

    def schedule_until(
        self,
        *,
        execution_time: datetime,
        options: Optional[CeleryOptions] = None,
    ) -> TResultType:
        """Schedules a task to be executed until a specified time.

        Args:
            execution_time (datetime): The time to finish the task.
            options (Optional[CeleryOptions], optional): The common
                options for a task. Defaults to None.

        Returns:
            TResultType: The result type of the task.
        """
        options = options or CeleryOptions()
        options.eta = execution_time
        return self._send(options=options)


class AsyncRemoteTask(RemoteTask[AsyncResult]):
    """A celery remote task returning AsyncResult object."""


class RemoteTaskFactory(_CeleryDependent):
    """A factory class for remote tasks."""

    def _create_task(self, name: str, *args) -> RemoteTask:
        """Returns a generic remote task

        Args:
            name (str): The name of the task

        Returns:
            RemoteTask: The resulting task.
        """
        return RemoteTask(name, self._celery, *args)

    def _create_async_task(self, name: str, *args) -> AsyncRemoteTask:
        """Creates an async remote task.

        Args:
            name (str): The name of the task.

        Returns:
            AsyncRemoteTask: The resulting task.
        """
        return AsyncRemoteTask(name, self._celery, *args)
