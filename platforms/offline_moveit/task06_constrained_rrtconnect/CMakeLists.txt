cmake_minimum_required(VERSION 3.16)
project(task06_offline_constrained_rrtconnect LANGUAGES CXX)
find_package(Eigen3 REQUIRED)
find_package(moveit_core REQUIRED)
find_package(srdfdom REQUIRED)
find_package(yaml-cpp REQUIRED)
find_package(nlohmann_json REQUIRED)
enable_testing()
# 仅链接既有NR/RBS/FCL；不使用ROS context/服务/执行器。
add_subdirectory("${CMAKE_CURRENT_SOURCE_DIR}/../task05_local_connection" task05_reuse)
add_library(task06_constrained_rrtconnect
  "${CMAKE_CURRENT_SOURCE_DIR}/../../../baselines/p4_closed_chain/constrained_rrtconnect.cpp")
target_link_libraries(task06_constrained_rrtconnect PUBLIC task05_local_connection)
target_compile_options(task06_constrained_rrtconnect PRIVATE -Wall -Wextra -Wpedantic)
add_executable(task06_math
  "${CMAKE_CURRENT_SOURCE_DIR}/../../../tests/task06_constrained_rrtconnect_math.cpp")
target_link_libraries(task06_math PRIVATE task06_constrained_rrtconnect)
target_compile_options(task06_math PRIVATE -Wall -Wextra -Wpedantic)
add_test(NAME task06_math COMMAND task06_math)
add_executable(task06_model_test model_test.cpp
  "${CMAKE_CURRENT_SOURCE_DIR}/../../../baselines/p4_closed_chain/closure.cpp")
target_link_libraries(task06_model_test PRIVATE task06_constrained_rrtconnect task05_collision_adapter)
target_compile_options(task06_model_test PRIVATE -Wall -Wextra -Wpedantic)
