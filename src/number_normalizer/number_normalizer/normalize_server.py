import time

import rclpy
from rclpy.action import ActionServer
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node

from std_msgs.msg import Float64MultiArray

from number_interfaces.action import Normalize
from number_interfaces.srv import GetCount


class NormalizeServer(Node):

    def __init__(self):
        super().__init__('normalize_server')
        self._total_numbers = 0
        self._total_requests = 0

        cb_group = ReentrantCallbackGroup()

        self._action_server = ActionServer(
            self,
            Normalize,
            'normalize',
            execute_callback=self.execute_callback,
            callback_group=cb_group,
        )

        self._publisher = self.create_publisher(
            Float64MultiArray, 'normalized_numbers', 10)

        self._service = self.create_service(
            GetCount, 'get_count', self.get_count_callback,
            callback_group=cb_group)

        self.get_logger().info('Normalize action server is ready.')

    def get_count_callback(self, request, response):
        """Return how many numbers and requests have been processed."""
        response.total_numbers_processed = self._total_numbers
        response.total_requests = self._total_requests
        return response

    def execute_callback(self, goal_handle):
        """Normalize the incoming array with MinMaxScaler."""
        data = list(goal_handle.request.data)
        self.get_logger().info('Received goal with %d numbers: %s'
                               % (len(data), data))
        self._total_requests += 1

        result = Normalize.Result()

        if not data:
            goal_handle.succeed()
            result.normalized_data = []
            return result

        min_value = min(data)
        max_value = max(data)
        value_range = max_value - min_value

        normalized = []
        feedback_msg = Normalize.Feedback()

        for index, x in enumerate(data):
            if value_range == 0:
                scaled = 0.0
            else:
                scaled = (x - min_value) / value_range
            scaled = float(scaled)
            normalized.append(scaled)

            feedback_msg.index = index
            feedback_msg.current_value = scaled
            goal_handle.publish_feedback(feedback_msg)
            self.get_logger().info('Feedback [%d] = %.4f' % (index, scaled))

            self._total_numbers += 1
            time.sleep(0.5)

        goal_handle.succeed()
        result.normalized_data = normalized

        topic_msg = Float64MultiArray()
        topic_msg.data = normalized
        self._publisher.publish(topic_msg)

        self.get_logger().info('Result: %s' % normalized)
        return result


def main(args=None):
    """Spin the server with a multi-threaded executor."""
    rclpy.init(args=args)
    node = NormalizeServer()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
