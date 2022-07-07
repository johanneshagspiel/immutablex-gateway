from datetime import datetime, timedelta
import unittest
from src.util.helpers import SafeDatetimeConverter


class To_Download_List_Creator_Tests(unittest.TestCase):

    def test_regular_start_timestamp_list_1(self):

        start_time_stamp = datetime.strptime("2021-06-01T00:00:00.00Z", "%Y-%m-%dT%H:%M:%S.%fZ")
        current_time_stamp = datetime.strptime("2021-06-01T00:30:00.00Z", "%Y-%m-%dT%H:%M:%S.%fZ")

        timestamp_list_str, next_start_time_stamp, not_caught_up_with_now_new = To_Download_List_Creator_Tests.create_timestamp_list(start_time_stamp, current_time_stamp)

        last_to_timestamp = SafeDatetimeConverter.string_to_datetime(timestamp_list_str[-1][1])

        timestamp_list_len = len(timestamp_list_str)


        self.assertEqual(current_time_stamp, last_to_timestamp)
        self.assertEqual(current_time_stamp + timedelta(microseconds=1), next_start_time_stamp)
        self.assertEqual(30, timestamp_list_len)
        self.assertTrue(not_caught_up_with_now_new)


    def test_regular_start_timestamp_list_2(self):

        start_time_stamp = datetime.strptime("2021-06-01T00:00:00.00Z", "%Y-%m-%dT%H:%M:%S.%fZ")
        current_time_stamp = datetime.strptime("2021-06-01T01:30:00.00Z", "%Y-%m-%dT%H:%M:%S.%fZ")

        timestamp_list_str, next_start_time_stamp, not_caught_up_with_now_new = To_Download_List_Creator_Tests.create_timestamp_list(start_time_stamp, current_time_stamp)

        last_to_timestamp = SafeDatetimeConverter.string_to_datetime(timestamp_list_str[-1][1])

        timestamp_list_len = len(timestamp_list_str)

        result_last_to_time_stamp = datetime.strptime("2021-06-01T00:30:00.00Z", "%Y-%m-%dT%H:%M:%S.%fZ")

        self.assertEqual(result_last_to_time_stamp, last_to_timestamp)
        self.assertEqual(result_last_to_time_stamp + timedelta(microseconds=1), next_start_time_stamp)
        self.assertEqual(30, timestamp_list_len)
        self.assertTrue(not_caught_up_with_now_new)


    def test_irregular_start_timestamp_list_1(self):

        start_time_stamp = datetime.strptime("2021-06-01T00:02:34.012Z", "%Y-%m-%dT%H:%M:%S.%fZ")
        current_time_stamp = datetime.strptime("2021-06-01T00:30:00.00Z", "%Y-%m-%dT%H:%M:%S.%fZ")

        timestamp_list_str, next_start_time_stamp, not_caught_up_with_now_new = To_Download_List_Creator_Tests.create_timestamp_list(start_time_stamp, current_time_stamp)

        last_to_timestamp = SafeDatetimeConverter.string_to_datetime(timestamp_list_str[-1][1])

        timestamp_list_len = len(timestamp_list_str)


        self.assertEqual(current_time_stamp, last_to_timestamp)
        self.assertEqual(current_time_stamp + timedelta(microseconds=1), next_start_time_stamp)
        self.assertEqual(28, timestamp_list_len)
        self.assertFalse(not_caught_up_with_now_new)


    def test_irregular_start_timestamp_list_2(self):

        start_time_stamp = datetime.strptime("2021-06-01T00:02:34.012Z", "%Y-%m-%dT%H:%M:%S.%fZ")
        current_time_stamp = datetime.strptime("2021-06-01T00:29:45.0840Z", "%Y-%m-%dT%H:%M:%S.%fZ")

        timestamp_list_str, next_start_time_stamp, not_caught_up_with_now_new = To_Download_List_Creator_Tests.create_timestamp_list(start_time_stamp, current_time_stamp)

        last_to_timestamp = SafeDatetimeConverter.string_to_datetime(timestamp_list_str[-1][1])

        timestamp_list_len = len(timestamp_list_str)


        self.assertEqual(current_time_stamp, last_to_timestamp)
        self.assertEqual(current_time_stamp + timedelta(microseconds=1), next_start_time_stamp)
        self.assertEqual(28, timestamp_list_len)
        self.assertFalse(not_caught_up_with_now_new)
