import time
import unittest

import launch
import launch_ros.actions
import launch_testing.actions

import pytest

import rclpy
from rclpy.action import ActionClient

from std_msgs.msg import Float64MultiArray

from number_interfaces.action import Normalize
from number_interfaces.srv import GetCount


@pytest.mark.launch_test
def generate_test_description():
    """Launch the action server under test."""
    server_node = launch_ros.actions.Node(
        package='number_normalizer',
        executable='normalize_server',
        name='normalize_server',
        output='screen',
    )
    return (
        launch.LaunchDescription([
            server_node,
            launch_testing.actions.ReadyToTest(),
        ]),
        {'server_node': server_node},
    )


class TestNormalizeNodes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def setUp(self):
        self.node = rclpy.create_node('test_normalize_node')

    def tearDown(self):
        self.node.destroy_node()

    def _run_goal(self, data, collect_feedback=None):
        client = ActionClient(self.node, Normalize, 'normalize')
        self.assertTrue(
            client.wait_for_server(timeout_sec=15.0),
            'Action server "normalize" is not available')

        goal = Normalize.Goal()
        goal.data = data

        if collect_feedback is not None:
            def _fb(msg):
                collect_feedback.append(msg.feedback.current_value)
            send_future = client.send_goal_async(goal, feedback_callback=_fb)
        else:
            send_future = client.send_goal_async(goal)

        rclpy.spin_until_future_complete(self.node, send_future, timeout_sec=15.0)
        goal_handle = send_future.result()
        self.assertIsNotNone(goal_handle, 'No response from action server')
        self.assertTrue(goal_handle.accepted, 'Goal was not accepted')

        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self.node, result_future, timeout_sec=30.0)
        return result_future.result().result

    def _get_counts(self):
        client = self.node.create_client(GetCount, 'get_count')
        self.assertTrue(
            client.wait_for_service(timeout_sec=15.0),
            'Service "get_count" is not available')
        future = client.call_async(GetCount.Request())
        rclpy.spin_until_future_complete(self.node, future, timeout_sec=15.0)
        response = future.result()
        self.assertIsNotNone(response, 'No response from get_count service')
        return response

    def test_action(self):
        feedback = []
        result = self._run_goal([0, 5, 10], collect_feedback=feedback)
        self.assertEqual(list(result.normalized_data), [0.0, 0.5, 1.0])
        # feedback должен прийти на каждое число
        self.assertEqual(len(feedback), 3)
        self.assertAlmostEqual(feedback[0], 0.0)
        self.assertAlmostEqual(feedback[-1], 1.0)

    def test_service(self):
        before = self._get_counts()
        self._run_goal([3, 9])
        after = self._get_counts()
        self.assertEqual(after.total_requests, before.total_requests + 1)
        self.assertEqual(
            after.total_numbers_processed,
            before.total_numbers_processed + 2)

    def test_topic(self):
        received = []
        self.node.create_subscription(
            Float64MultiArray, 'normalized_numbers',
            lambda msg: received.append(list(msg.data)), 10)

        self._run_goal([1, 2, 3, 4])

        deadline = time.time() + 5.0
        while time.time() < deadline and not received:
            rclpy.spin_once(self.node, timeout_sec=0.5)

        self.assertTrue(received, 'No message received on /normalized_numbers')
        self.assertEqual(len(received[-1]), 4)
        self.assertAlmostEqual(received[-1][0], 0.0)
        self.assertAlmostEqual(received[-1][-1], 1.0)


@launch_testing.post_shutdown_test()
class TestServerShutdown(unittest.TestCase):

    def test_exit_code(self, proc_info, server_node):
        """Server should not crash during the tests."""
        launch_testing.asserts.assertExitCodes(
            proc_info,
            allowable_exit_codes=[0, -2, -15],  # 0, SIGINT, SIGTERM
            process=server_node,
        )
