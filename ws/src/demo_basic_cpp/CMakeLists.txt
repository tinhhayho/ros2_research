cmake_minimum_required(VERSION 3.8)
project(demo_basic_cpp)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)

add_executable(talker_cpp src/talker.cpp)
ament_target_dependencies(talker_cpp rclcpp std_msgs)

install(TARGETS talker_cpp DESTINATION lib/${PROJECT_NAME})

ament_package()
