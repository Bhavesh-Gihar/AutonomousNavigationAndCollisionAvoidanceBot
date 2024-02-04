import pickle
import rclpy
import time
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from rclpy.node import Node


class ScanToVelocityNode(Node):
    def __init__(self):
        super().__init__('scan_to_velocity_node')
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            0  # QoS profile depth
        )
        self.publisher = self.create_publisher(
            Twist,
            '/cmd_vel',
            0
        )
        self.model = self.load_model()

    def load_model(self):
        with open('/home/bhavesh/Documents/AutonomousNavigationAndCollisionAvoidanceBot/bag_files/dt_model.pkl', 'rb') as f:
            model = pickle.load(f)
        return model

    def scan_callback(self, msg):
        time.sleep(1) 

        ranges = msg.ranges

        velocity = self.compute_velocity(ranges)

        self.publish_velocity(velocity)

    def compute_velocity(self, ranges):
        velocity = Twist()

        pred_dir, pred_speed = self.model.predict([ranges])[0].split()

        if pred_dir == 'x' :
            velocity.linear.x = float(pred_speed)
        elif pred_dir == 'y':
            velocity.linear.y = float(pred_speed)
        elif pred_dir == 'z':
            velocity.linear.z = float(pred_speed)
        elif pred_dir == 'i':
            velocity.angular.x = float(pred_speed)
        elif pred_dir == 'j':
            velocity.angular.y = float(pred_speed)
        elif pred_dir == 'k':
            velocity.angular.z = float(pred_speed)

        return velocity

    def publish_velocity(self, velocity):
        self.publisher.publish(velocity)

def main(args=None):
    rclpy.init(args=args)
    node = ScanToVelocityNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
