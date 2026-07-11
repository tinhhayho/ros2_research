// Demo 1 — minimal rclcpp publisher ("talker_cpp"), the C++ side for a firmware audience.
// Publishes on the SAME /chatter topic as the Python talker: one bus, two languages, no master.
#include <chrono>
#include <memory>
#include <string>

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

using namespace std::chrono_literals;

class TalkerCpp : public rclcpp::Node
{
public:
  TalkerCpp()
  : Node("talker_cpp"), count_(0)
  {
    pub_ = create_publisher<std_msgs::msg::String>("chatter", 10);
    timer_ = create_wall_timer(1s, [this]() {this->tick();});   // 1 Hz
    RCLCPP_INFO(get_logger(), "talker_cpp up: publishing on /chatter");
  }

private:
  void tick()
  {
    auto msg = std_msgs::msg::String();
    msg.data = "Hello from C++ (rclcpp): " + std::to_string(count_++);
    pub_->publish(msg);
    RCLCPP_INFO(get_logger(), "pub: \"%s\"", msg.data.c_str());
  }

  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr pub_;
  rclcpp::TimerBase::SharedPtr timer_;
  size_t count_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<TalkerCpp>());
  rclcpp::shutdown();
  return 0;
}
