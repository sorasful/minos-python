"""
Copyright (C) 2021 Clariteia SL

This file is part of minos framework.

Minos framework can not be copied and/or distributed without the express permission of Clariteia SL.
"""
import unittest

from minos.common.testing import (
    PostgresAsyncTestCase,
)
from minos.networks import (
    CommandConsumer,
)
from tests.utils import (
    BASE_PATH,
)


class TestCommandConsumer(PostgresAsyncTestCase):
    CONFIG_FILE_PATH = BASE_PATH / "test_config.yml"

    def test_from_config(self):
        consumer = CommandConsumer.from_config(config=self.config)
        self.assertIsInstance(consumer, CommandConsumer)
        self.assertEqual(["AddOrder", "DeleteOrder", "UpdateOrder", "GetOrder"], consumer.topics)
        self.assertEqual(self.config.commands.broker, consumer._broker)
        self.assertEqual(self.config.commands.queue.host, consumer.host)
        self.assertEqual(self.config.commands.queue.port, consumer.port)
        self.assertEqual(self.config.commands.queue.database, consumer.database)
        self.assertEqual(self.config.commands.queue.user, consumer.user)
        self.assertEqual(self.config.commands.queue.password, consumer.password)

    def test_table_name(self):
        self.assertEqual("command_queue", CommandConsumer.TABLE_NAME)


if __name__ == "__main__":
    unittest.main()
