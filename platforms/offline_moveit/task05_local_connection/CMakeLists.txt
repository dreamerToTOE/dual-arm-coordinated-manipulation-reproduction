cmake_minimum_required(VERSION 3.16)
project(task05_offline_local_connection LANGUAGES CXX)
find_package(Eigen3 REQUIRED)
find_package(moveit_core REQUIRED)
find_package(srdfdom REQUIRED)
find_package(yaml-cpp REQUIRED)
find_package(nlohmann_json REQUIRED)
enable_testing()
# 原TASK03/04源码与回归完整复用，不启动ROS进程。
add_subdirectory("${CMAKE_CURRENT_SOURCE_DIR}/../task04_projection" task04_reuse)
add_library(task05_local_connection
  "${CMAKE_CURRENT_SOURCE_DIR}/../../../baselines/p4_closed_chain/local_connection.cpp")
target_link_libraries(task05_local_connection PUBLIC task04_projection)
target_compile_options(task05_local_connection PRIVATE -Wall -Wextra -Wpedantic)
add_executable(task05_connection_math
  "${CMAKE_CURRENT_SOURCE_DIR}/../../../tests/task05_local_connection_math.cpp")
target_link_libraries(task05_connection_math PRIVATE task05_local_connection)
target_compile_options(task05_connection_math PRIVATE -Wall -Wextra -Wpedantic)
add_test(NAME task05_connection_math COMMAND task05_connection_math)
add_library(task05_collision_adapter collision_adapter.cpp)
target_link_libraries(task05_collision_adapter PUBLIC task03_model_adapter
  moveit_core::moveit_planning_scene moveit_core::moveit_collision_detection_fcl
  yaml-cpp nlohmann_json::nlohmann_json)
target_compile_options(task05_collision_adapter PRIVATE -Wall -Wextra -Wpedantic)
add_executable(task05_model_test model_test.cpp
  "${CMAKE_CURRENT_SOURCE_DIR}/../../../baselines/p4_closed_chain/closure.cpp")
target_link_libraries(task05_model_test PRIVATE task05_local_connection task05_collision_adapter)
target_compile_options(task05_model_test PRIVATE -Wall -Wextra -Wpedantic)
