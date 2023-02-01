project(EnzymeTest LANGUAGES C CXX OBJC OBJCXX)
cmake_minimum_required(VERSION 3.0.0 FATAL_ERROR)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_BUILD_TYPE Release)

# Find SDK Path
execute_process(COMMAND xcrun --show-sdk-path --sdk iphoneos
	OUTPUT_VARIABLE IOS_SDK
	OUTPUT_STRIP_TRAILING_WHITESPACE
)

set(CMAKE_OSX_ARCHITECTURES "arm64")
set(CMAKE_OSX_SYSROOT ${IOS_SDK})

# Set output folder
set(BIN_FOLDER ${CMAKE_CURRENT_BINARY_DIR}/assets)
if (NOT EXISTS ${BIN_FOLDER})
	make_directory(${BIN_FOLDER})
endif()

# Using Geometry Dash as our example
add_custom_target(EnzymeCodegen ALL
	COMMAND mkdir -p ${BIN_FOLDER}//IPA
	COMMAND python3 patcher/main.py assets/IPA/Payload/GeometryJump.app/GeometryJump ${BIN_FOLDER}
	WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
	COMMENT "Creating Patch"
	BYPRODUCTS ${BIN_FOLDER}/bootloader.hpp
)

add_library(${PROJECT_NAME} SHARED src/example.mm)

# Our codegen creates a header file for us
target_include_directories(${PROJECT_NAME} PRIVATE
	${CMAKE_CURRENT_BINARY_DIR}/assets
)

target_link_libraries(${PROJECT_NAME} PRIVATE 
	"-framework UIKit"
	"-framework Foundation"
)
target_link_options(${PROJECT_NAME} PRIVATE "-L${IOS_SDK}/usr/lib")

include(${CMAKE_CURRENT_SOURCE_DIR}/assets/Package.cmake)

# We use Geometry Dash in this example
enzyme_package($<TARGET_FILE:${PROJECT_NAME}> GeometryJump)
