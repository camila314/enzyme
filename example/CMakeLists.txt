project(EnzymeTest LANGUAGES C CXX OBJC OBJCXX)
cmake_minimum_required(VERSION 3.0.0 FATAL_ERROR)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_BUILD_TYPE Release)

set(ENZYME_UNZIPPED_FOLDER "${CMAKE_CURRENT_LIST_DIR}/IPA")
set(ENZYME_BINARY_NAME "GeometryJump")

include(../Enzyme.cmake)

add_library(${PROJECT_NAME} SHARED 
    src/example.mm
    src/breakpoint_hooks.cpp
)

enzyme_setup(
    "${CMAKE_CURRENT_LIST_DIR}/IPA"
    "GeometryJump"
)

target_link_libraries(${PROJECT_NAME} PRIVATE 
    "-framework UIKit"
    "-framework Foundation"
)

enzyme_package(${PROJECT_NAME})