"""
Copyright (C) 2021 Clariteia SL

This file is part of minos framework.

Minos framework can not be copied and/or distributed without the express permission of Clariteia SL.
"""
import unittest

from minos.common import (
    CommandReply,
)
from tests.aggregate_classes import (
    Car,
)


class TestCommandReply(unittest.TestCase):
    def test_constructor(self):
        command_reply = CommandReply("CarCreated", [Car(1, 1, 3, "blue"), Car(2, 1, 5, "red")], "saga_id8972348237")
        self.assertEqual("CarCreated", command_reply.topic)
        self.assertEqual([Car(1, 1, 3, "blue"), Car(2, 1, 5, "red")], command_reply.items)
        self.assertEqual("saga_id8972348237", command_reply.saga_uuid)

    def test_avro_serialization(self):
        command_reply = CommandReply("CarCreated", [Car(1, 1, 3, "blue"), Car(2, 1, 5, "red")], "saga_id8972348237")
        decoded_command = CommandReply.from_avro_bytes(command_reply.avro_bytes)
        self.assertEqual(command_reply, decoded_command)


if __name__ == "__main__":
    unittest.main()
