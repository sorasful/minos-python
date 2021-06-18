"""
Copyright (C) 2021 Clariteia SL

This file is part of minos framework.

Minos framework can not be copied and/or distributed without the express permission of Clariteia SL.
"""
import unittest

from minos.common import (
    AggregateDiff,
    FieldsDiff,
    ModelField,
)
from tests.aggregate_classes import (
    Car,
)
from tests.utils import (
    FakeBroker,
    FakeRepository,
    FakeSnapshot,
)


class TestAggregateDiff(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        async with FakeBroker() as broker, FakeRepository() as repository, FakeSnapshot() as snapshot:
            self.initial = Car(3, "blue", id=1, version=1, _broker=broker, _repository=repository, _snapshot=snapshot)
            self.final = Car(5, "yellow", id=1, version=3, _broker=broker, _repository=repository, _snapshot=snapshot)
            self.another = Car(3, "blue", id=3, version=1, _broker=broker, _repository=repository, _snapshot=snapshot)

    def test_diff(self):
        expected = AggregateDiff(
            id=1,
            name=Car.classname,
            version=3,
            fields_diff=FieldsDiff({"doors": ModelField("doors", int, 5), "color": ModelField("color", str, "yellow")}),
        )
        observed = self.final.diff(self.initial)
        self.assertEqual(expected, observed)

    def test_apply_diff(self):
        diff = AggregateDiff(
            id=1,
            name=Car.classname,
            version=3,
            fields_diff=FieldsDiff({"doors": ModelField("doors", int, 5), "color": ModelField("color", str, "yellow")}),
        )
        self.initial.apply_diff(diff)
        self.assertEqual(self.final, self.initial)

    def test_apply_diff_raises(self):
        diff = AggregateDiff(
            id=2,
            name=Car.classname,
            version=3,
            fields_diff=FieldsDiff({"doors": ModelField("doors", int, 5), "color": ModelField("color", str, "yellow")}),
        )
        with self.assertRaises(ValueError):
            self.initial.apply_diff(diff)


if __name__ == "__main__":
    unittest.main()
