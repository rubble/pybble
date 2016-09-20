from unittest import TestCase
import pybble


class TestProcess(TestCase):

    def setUp(self):
        self.rubble = pybble.client.Client()
        self.processes = []

    def create_a_process(self):
        process_created = self.rubble.process.create("")
        self.processes.append(process_created['pid'])

        # Check the pid was created
        self.assertTrue('pid' in process_created,
                        "Can't update a process, process can be created")

        return process_created

    def test_process_created(self):
        response = self.rubble.process.create("")
        self.processes.append(response['pid'])
        self.assertTrue('pid' in response)
        self.assertTrue('pid' in response)

    def test_process_can_be_got(self):
        process_created = self.create_a_process()

        # Check the the process can be got
        process_info = self.rubble.process.get(process_created['pid'])

        self.assertTrue(type(process_info) is dict)
        self.assertFalse('error' in process_info)

    def test_process_updated(self):
        process_created = self.create_a_process()

        # Test the process can be updated
        process_updated = self.rubble.process.update("", process_created['pid'])
        self.assertTrue(type(process_updated) is dict)
        self.assertFalse('error' in process_updated)

    def test_process_deleted(self):
        process_created = self.create_a_process()

        # Delete the process can be updated
        process_updated = self.rubble.process.delete(process_created['pid'])
        self.assertTrue(type(process_updated) is dict)
        self.assertFalse('error' in process_updated)

    def tearDown(self):
        for pid in self.processes:
            self.rubble.process.delete(pid)