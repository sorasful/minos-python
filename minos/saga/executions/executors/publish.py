"""
Copyright (C) 2021 Clariteia SL

This file is part of minos framework.

Minos framework can not be copied and/or distributed without the express permission of Clariteia SL.
"""
from __future__ import (
    annotations,
)

from typing import (
    NoReturn,
)
from uuid import (
    UUID,
)

from dependency_injector.wiring import (
    Provide,
)

from minos.common import (
    MinosBroker,
    MinosModel,
)

from ... import (
    MinosSagaFailedExecutionStepException,
)
from ...definitions import (
    SagaStepOperation,
)
from ...exceptions import (
    MinosSagaExecutorException,
)
from ..context import (
    SagaContext,
)
from .local import (
    LocalExecutor,
)


class PublishExecutor(LocalExecutor):
    """Publish Executor class.

    This class has the responsibility to publish command on the corresponding broker's queue.
    """

    broker: MinosBroker = Provide["command_broker"]

    def __init__(self, *args, definition_name: str, execution_uuid: UUID, broker: MinosBroker = None, **kwargs):
        super().__init__(*args, **kwargs)
        if broker is not None:
            self.broker = broker

        self.definition_name = definition_name
        self.execution_uuid = execution_uuid

    async def exec(self, operation: SagaStepOperation, context: SagaContext, has_reply: bool = False) -> SagaContext:
        """Exec method, that perform the publishing logic run an pre-callback function to generate the command contents.

        :param operation: Operation to be executed.
        :param context: Execution context.
        :param has_reply: If `True` the command is published expecting (and waiting) a reply, otherwise a reply is not
            expected (and waited)
        :return: A saga context instance.
        """
        if operation is None:
            return context

        try:
            request = await self.exec_operation(operation, context)
            await self._publish(operation, request, has_reply)
        except MinosSagaExecutorException as exc:
            raise MinosSagaFailedExecutionStepException(exc.exception)
        return context

    async def _publish(self, operation: SagaStepOperation, request: MinosModel, has_reply: bool) -> NoReturn:
        await self.exec_function(
            self.broker.send_one,
            topic=operation.name,
            item=request,
            saga_uuid=str(self.execution_uuid),
            reply_topic=None if not has_reply else self.definition_name,
        )
