cmake_minimum_required(VERSION 3.16)
project(task03_offline_closure LANGUAGES CXX)

# [ENGINEERING] 只链接已安装的 MoveIt 运动学库，不启动 ROS/MoveIt 服务。
find_package(Eigen3 REQUIRED)
find_package(moveit_core REQUIRED)
find_package(urdfdom REQUIRED)
find_package(srdfdom REQUIRED)
find_package(yaml-cpp REQUIRED)
find_package(nlohmann_json REQUIRED)

add_library(task03_model_adapter model_adapter.cpp)
target_compile_features(task03_model_adapter PUBLIC cxx_std_17)
target_include_directories(task03_model_adapter PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}/../../..")
target_link_libraries(task03_model_adapter PUBLIC Eigen3::Eigen
  moveit_core::moveit_robot_model moveit_core::moveit_robot_state srdfdom::srdfdom)
target_compile_options(task03_model_adapter PRIVATE -Wall -Wextra -Wpedantic)

add_executable(task03_model_test model_test.cpp
  "${CMAKE_CURRENT_SOURCE_DIR}/../../../baselines/p4_closed_chain/closure.cpp")
target_link_libraries(task03_model_test PRIVATE task03_model_adapter yaml-cpp
  nlohmann_json::nlohmann_json)
target_compile_options(task03_model_test PRIVATE -Wall -Wextra -Wpedantic)

add_executable(task03_math_test
  "${CMAKE_CURRENT_SOURCE_DIR}/../../../tests/task03_closure_math.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/../../../baselines/p4_closed_chain/closure.cpp")
target_compile_features(task03_math_test PRIVATE cxx_std_17)
target_include_directories(task03_math_test PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../..")
target_link_libraries(task03_math_test PRIVATE Eigen3::Eigen)
target_compile_options(task03_math_test PRIVATE -Wall -Wextra -Wpedantic)
enable_testing()
add_test(NAME task03_synthetic_math COMMAND task03_math_test)
