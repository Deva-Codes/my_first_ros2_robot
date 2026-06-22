cmake_minimum_required(VERSION 3.8)
project(my_package)

find_package(ament_cmake REQUIRED)

install(DIRECTORY
  urdf
  config
  worlds
  DESTINATION share/${PROJECT_NAME}
)

ament_package()