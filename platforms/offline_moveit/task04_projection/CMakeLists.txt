cmake_minimum_required(VERSION 3.16)
project(task04_offline_projection LANGUAGES CXX)

find_package(Eigen3 REQUIRED)
find_package(moveit_core REQUIRED)
find_package(srdfdom REQUIRED)
find_package(yaml-cpp REQUIRED)
find_package(nlohmann_json REQUIRED)

# 直接复用TASK03构建和模型适配器，不修改已审源码/测试；不启动ROS服务。
enable_testing()
add_subdirectory("${CMAKE_CURRENT_SOURCE_DIR}/../task03_closure" task03_reuse)

add_library(task04_projection
  "${CMAKE_CURRENT_SOURCE_DIR}/../../../baselines/p4_closed_chain/projection.cpp")
target_compile_features(task04_projection PUBLIC cxx_std_17)
target_include_directories(task04_projection PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}/../../..")
target_link_libraries(task04_projection PUBLIC Eigen3::Eigen)
target_compile_options(task04_projection PRIVATE -Wall -Wextra -Wpedantic)

add_executable(task04_projection_math
  "${CMAKE_CURRENT_SOURCE_DIR}/../../../tests/task04_projection_math.cpp")
target_link_libraries(task04_projection_math PRIVATE task04_projection)
target_compile_options(task04_projection_math PRIVATE -Wall -Wextra -Wpedantic)
add_test(NAME task04_projection_math COMMAND task04_projection_math)

add_executable(task04_model_test model_test.cpp
  "${CMAKE_CURRENT_SOURCE_DIR}/../../../baselines/p4_closed_chain/closure.cpp")
target_link_libraries(task04_model_test PRIVATE task04_projection task03_model_adapter
  yaml-cpp nlohmann_json::nlohmann_json)
target_compile_options(task04_model_test PRIVATE -Wall -Wextra -Wpedantic)
