import unittest
from uuid import (
    UUID,
    uuid4,
)

from minos.aggregate import (
    Ref,
    RefInjector,
)
from minos.common import (
    ModelType,
)
from tests.utils import (
    Car,
    MinosTestCase,
)


class TestRefInjector(MinosTestCase):
    async def test_simple(self):
        model = await Car.create(3, "test")
        mapper = {model.uuid: model}

        expected = model
        observed = RefInjector(model.uuid, mapper).build()

        self.assertEqual(expected, observed)

    async def test_list(self):
        model = await Car.create(3, "test")
        mapper = {model.uuid: model}

        expected = [model, model, model]
        observed = RefInjector([model.uuid, model.uuid, model.uuid], mapper).build()

        self.assertEqual(expected, observed)

    async def test_dict(self):
        model = await Car.create(3, "test")
        mapper = {model.uuid: model}

        expected = {model: model}
        observed = RefInjector({model.uuid: model.uuid}, mapper).build()

        self.assertEqual(expected, observed)

    def test_model(self):
        mt_bar = ModelType.build("Bar", {"uuid": UUID, "version": int})
        mt_foo = ModelType.build("Foo", {"uuid": UUID, "version": int, "another": Ref[mt_bar]})

        model = mt_bar(uuid=uuid4(), version=1)
        mapper = {model.uuid: model}
        value = mt_foo(uuid=uuid4(), version=1, another=model.uuid)

        expected = mt_foo(uuid=value.uuid, version=1, another=model)
        observed = RefInjector(value, mapper).build()

        self.assertEqual(expected, observed)


if __name__ == "__main__":
    unittest.main()
