import sys

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node

from number_interfaces.action import Normalize


class NormalizeClient(Node):

    def __init__(self):
        super().__init__('normalize_client')
        self._action_client = ActionClient(self, Normalize, 'normalize')

    def send_goal(self, data):
        """Send the integer array to the action server."""
        goal_msg = Normalize.Goal()
        goal_msg.data = data

        self.get_logger().info('Waiting for action server...')
        self._action_client.wait_for_server()

        self.get_logger().info('Sending goal: %s' % data)
        send_goal_future = self._action_client.send_goal_async(
            goal_msg, feedback_callback=self.feedback_callback)
        send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        """Handle accept/reject of the goal."""
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected.')
            rclpy.shutdown()
            return
        self.get_logger().info('Goal accepted.')
        get_result_future = goal_handle.get_result_async()
        get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        """Print the final normalized array and shut down."""
        result = future.result().result
        self.get_logger().info('Result (normalized): %s'
                               % list(result.normalized_data))
        rclpy.shutdown()

    def feedback_callback(self, feedback_msg):
        """Print each normalized value as it arrives."""
        feedback = feedback_msg.feedback
        self.get_logger().info('Feedback [%d] = %.4f'
                               % (feedback.index, feedback.current_value))


def main(args=None):
    """Parse integer arguments and run the client."""
    rclpy.init(args=args)

    numbers = []
    for arg in sys.argv[1:]:
        try:
            numbers.append(int(arg))
        except ValueError:
            pass  
    if not numbers:
        numbers = [2, 4, 6, 8, 10]

    node = NormalizeClient()
    node.send_goal(numbers)
    rclpy.spin(node)
    node.destroy_node()


if __name__ == '__main__':
    main()
