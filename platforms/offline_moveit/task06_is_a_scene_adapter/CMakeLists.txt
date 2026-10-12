cmake_minimum_required(VERSION 3.16)
project(task06_is_a_scene_adapter LANGUAGES CXX)
find_package(Eigen3 REQUIRED)
find_package(moveit_core REQUIRED)
find_package(srdfdom REQUIRED)
find_package(yaml-cpp REQUIRED)
find_package(nlohmann_json REQUIRED)
enable_testing()
# 原数学/搜索/FCL target 完整复用，无 ROS init/Node/服务/命令接口。
add_subdirectory("${CMAKE_CURRENT_SOURCE_DIR}/../task06_constrained_rrtconnect" task06_reuse)
add_executable(task06_is_a_native_audit native_audit.cpp
  "${CMAKE_CURRENT_SOURCE_DIR}/../../../baselines/p4_closed_chain/closure.cpp")
target_link_libraries(task06_is_a_native_audit PRIVATE
  task06_constrained_rrtconnect task05_collision_adapter)
target_compile_options(task06_is_a_native_audit PRIVATE -Wall -Wextra -Wpedantic)
