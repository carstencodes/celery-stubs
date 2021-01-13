#
# Copyright (c) 2021 Carsten Igel.
#
# This file is part of celery-stubs
# (see https://github.com/carstencodes/celery-stubs).
#
# License: 3-clause BSD, see https://opensource.org/licenses/BSD-3-Clause
#

from typing import (
    Generic, OrderedDict,
    Tuple,
    TypeVar,
    NamedTuple,
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
class CeleryOptions():
    countdown: Optional[float] = field(init=False, repr=True, default=None)
    eta: Optional[datetime] = field(init=False, repr=True, default=None)
    expires: Optional[Union[datetime, float]] = field(init=False, repr=True, default=None)

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
    def __init__(self, celery: Celery) -> None:
        self.__celery = celery

    @property
    def _celery(self) -> Celery:
        return self.__celery


class RemoteTask(Generic[TResultType], _CeleryDependent):
    def __init__(self, name: str, celery: Celery, *args) -> None:
        super().__init__(celery)
        self.__name = name
        self.__args: Tuple = args

    @property
    def name(self) -> str:
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
        return self._send(options=options)

    def schedule_delayed(
        self,
        *,
        delay_in_seconds: float,
        options: Optional[CeleryOptions] = None,
    ) -> TResultType:
        options = options or CeleryOptions()
        options.countdown = delay_in_seconds
        return self._send(options=options)

    def schedule_termination_before(
        self,
        *,
        dead_line: Union[float, datetime],
        options: Optional[CeleryOptions] = None,
    ) -> TResultType:
        options = options or CeleryOptions()
        options.expires = dead_line
        return self._send(options=options)

    def schedule_until(
        self,
        *,
        execution_time: datetime,
        options: Optional[CeleryOptions] = None,
    ) -> TResultType:
        options = options or CeleryOptions()
        options.eta = execution_time
        return self._send(options=options)


class AsyncRemoteTask(RemoteTask[AsyncResult]):
    pass


class RemoteTaskFactory(_CeleryDependent):
    def _create_task(self, name: str, *args) -> RemoteTask:
        return RemoteTask(name, self._celery, *args)

    def _create_async_task(self, name: str, *args) -> AsyncRemoteTask:
        return AsyncRemoteTask(name, self._celery, *args)
