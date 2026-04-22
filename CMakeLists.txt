cmake_minimum_required(VERSION 3.8)
project(my_package)

find_package(ament_cmake REQUIRED)
find_package(gz-sim8 REQUIRED)
find_package(gz-plugin2 REQUIRED)
find_package(gz-transport13 REQUIRED)
find_package(gz-msgs10 REQUIRED)

add_library(custom_drive SHARED src/custom_drive.cpp)

target_link_libraries(custom_drive
gz-sim8::gz-sim8
  gz-plugin2::gz-plugin2
  gz-transport13::gz-transport13     
  gz-msgs10::gz-msgs10
)
install (TARGETS custom_drive DESTINATION lib/${PROJECT_NAME})
install(DIRECTORY 
       launch
       urdf
       worlds
       DESTINATION share/${PROJECT_NAME})
ament_package()