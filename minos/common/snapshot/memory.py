from __future__ import (
    annotations,
)

from itertools import (
    chain,
)
from operator import (
    attrgetter,
)
from typing import (
    TYPE_CHECKING,
    AsyncIterator,
    Optional,
)
from uuid import (
    UUID,
)

from dependency_injector.wiring import (
    Provide,
    inject,
)

from ..exceptions import (
    MinosSnapshotAggregateNotFoundException,
    MinosSnapshotDeletedAggregateException,
)
from ..queries import (
    _Condition,
    _Ordering,
)
from ..repository import (
    MinosRepository,
)
from ..transactions import (
    TRANSACTION_CONTEXT_VAR,
)
from ..uuid import (
    NULL_UUID,
)
from .abc import (
    MinosSnapshot,
)

if TYPE_CHECKING:
    from ..model import (
        Aggregate,
    )


class InMemorySnapshot(MinosSnapshot):
    """InMemory Snapshot class.

    The snapshot provides a direct accessor to the aggregate instances stored as events by the event repository class.
    """

    @inject
    def __init__(self, repository: MinosRepository = Provide["repository"], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._repository = repository

    # noinspection PyMethodOverriding
    async def find(
        self,
        aggregate_name: str,
        condition: _Condition,
        ordering: Optional[_Ordering] = None,
        limit: Optional[int] = None,
        transaction_uuid: Optional[UUID] = None,
        **kwargs,
    ) -> AsyncIterator[Aggregate]:
        """Find a collection of ``Aggregate`` instances based on a ``Condition``.

        :param aggregate_name: Class name of the ``Aggregate``.
        :param condition: The condition that must be satisfied by the ``Aggregate`` instances.
        :param ordering: Optional argument to return the instance with specific ordering strategy. The default behaviour
            is to retrieve them without any order pattern.
        :param limit: Optional argument to return only a subset of instances. The default behaviour is to return all the
            instances that meet the given condition.
        :param transaction_uuid: Optional argument to return the snapshot view within a transaction..
        :param kwargs: Additional named arguments.
        :return: An asynchronous iterator that provides the requested ``Aggregate`` instances.
        """
        uuids = {v.aggregate_uuid async for v in self._repository.select(aggregate_name=aggregate_name)}

        aggregates = list()
        for uuid in uuids:
            try:
                aggregate = await self.get(aggregate_name, uuid, transaction_uuid, **kwargs)
            except MinosSnapshotDeletedAggregateException:
                continue

            if condition.evaluate(aggregate):
                aggregates.append(aggregate)

        if ordering is not None:
            aggregates.sort(key=attrgetter(ordering.by), reverse=ordering.reverse)

        if limit is not None:
            aggregates = aggregates[:limit]

        for aggregate in aggregates:
            yield aggregate

    # noinspection PyMethodOverriding
    async def get(
        self, aggregate_name: str, uuid: UUID, transaction_uuid: Optional[UUID] = None, **kwargs
    ) -> Aggregate:
        """Get an aggregate instance from its identifier.

        :param aggregate_name: Class name of the ``Aggregate``.
        :param uuid: Identifier of the ``Aggregate``.
        :param transaction_uuid: Optional argument to return the snapshot view within a transaction.
        :param kwargs: Additional named arguments.
        :return: The ``Aggregate`` instance.
        """

        if transaction_uuid is None:
            if (transaction := TRANSACTION_CONTEXT_VAR.get()) is not None:
                transaction_uuid = transaction.uuid
            else:
                transaction_uuid = NULL_UUID

        entries = [
            v
            async for v in self._repository.select(aggregate_name=aggregate_name, aggregate_uuid=uuid)
            if v.transaction_uuid in (transaction_uuid, NULL_UUID)
        ]
        if not len(entries):
            raise MinosSnapshotAggregateNotFoundException(f"Not found any entries for the {uuid!r} id.")

        entries.sort(key=attrgetter("version"))

        if len({e.transaction_uuid for e in entries}) > 1:
            minimal = next(e for e in entries if e.transaction_uuid == transaction_uuid)
            entries = list(
                chain(
                    (e for e in entries if e.version < minimal.version),
                    (e for e in entries if e.transaction_uuid == transaction_uuid),
                )
            )

        if entries[-1].action.is_delete:
            raise MinosSnapshotDeletedAggregateException(f"The {uuid!r} id points to an already deleted aggregate.")

        cls = entries[0].aggregate_cls
        instance: Aggregate = cls.from_diff(entries[0].aggregate_diff, **kwargs)
        for entry in entries[1:]:
            instance.apply_diff(entry.aggregate_diff)

        return instance

    # noinspection PyMethodOverriding
    async def synchronize(self, **kwargs) -> None:
        """Synchronize the snapshot to the latest available version.

        :param kwargs: Additional named arguments.
        :return: This method does not return anything.
        """
