from unittest import TestCase
import pybble


class TestAPI(TestCase):
    """
    Tests the process API module, pybble.process
    """

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

    def test_processes_listed(self):
        if len(self.processes) == 0:
            process_created = self.create_a_process()

        process_list = self.rubble.process.list()

        self.assertTrue(type(process_list) is dict)
        self.assertTrue('result' in process_list)

    def test_file_created(self):
        rubble_code = 'pybble_test;'
        rubble_filename = 'pybble-test.rubble'
        rubble_filename_path = '~system/private/{}'.format(rubble_filename)

        file_created_successfully = self.rubble.file.put(rubble_filename_path, rubble_code)

        self.assertTrue(file_created_successfully)

    def test_file_can_be_got(self):
        rubble_filename = 'fish'
        rubble_filename_path = '~system/examples/rubblebox/{}'.format(rubble_filename)

        file_data = self.rubble.file.get(rubble_filename_path)

        self.assertTrue(type(file_data) is str, "Getting file should return string contents of the file")

    def tearDown(self):
        # delete all left over processes
        for pid in self.processes:
            self.rubble.process.delete(pid)
