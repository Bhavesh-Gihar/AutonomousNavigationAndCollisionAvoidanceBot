#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/laser_scan.hpp>
#include <geometry_msgs/msg/twist.hpp>
#include "/home/bhavesh/Documents/AutonomousNavigationAndCollisionAvoidanceBot/bag_files/dt_model.h" 

class ScanSubscriber : public rclcpp::Node {
public:
  ScanSubscriber() : Node("scan_subscriber") {
    subscription_ = this->create_subscription<sensor_msgs::msg::LaserScan>("/scan", 0, std::bind(&ScanSubscriber::scanCallback, this, std::placeholders::_1));
    command_publisher_ = this->create_publisher<geometry_msgs::msg::Twist>("cmd_vel", 10);
  }

private:
  void scanCallback(const sensor_msgs::msg::LaserScan scan_msg) {

    // Run model prediction
    float* tempDataStore = (float*)malloc(360 * sizeof(float));
    for(int i = 0; i < 360; i++) {
        tempDataStore[i] = scan_msg.ranges[i];
    }
    int class_index = classifier.predict(tempDataStore);

    // Generate velocity commands based on class prediction
    geometry_msgs::msg::Twist cmd_vel;


    if (class_index == 0) {
      cmd_vel.angular.z = -1; 
    } else if(class_index == 2) {
      cmd_vel.linear.x = 0.5;
    } else if(class_index == 1) {
      cmd_vel.angular.z = 1; 
    }
    
    // Publish velocity commands
    command_publisher_->publish(cmd_vel);
  }

  rclcpp::Subscription<sensor_msgs::msg::LaserScan>::SharedPtr subscription_;
  rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr command_publisher_;
  Eloquent::ML::Port::RandomForest classifier;
};

int main(int argc, char *argv[]) {
  rclcpp::init(argc, argv);
  auto node = std::make_shared<ScanSubscriber>();
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}