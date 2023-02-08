cmake_minimum_required(VERSION 3.2.0 FATAL_ERROR)

# iOS Development requires clang
if (NOT CMAKE_CXX_COMPILER_ID STREQUAL "Clang")
	message(FATAL_ERROR "Enzyme requires the use of clang.")
endif()

# Check iOS SDK Path
if (${CMAKE_SYSTEM_NAME} MATCHES "Darwin")
	# Find SDK Path
	execute_process(COMMAND xcrun --show-sdk-path --sdk iphoneos
		OUTPUT_VARIABLE ENZYME_IOS_SDK
		OUTPUT_STRIP_TRAILING_WHITESPACE
	)
else()
	# Check for environment variable
	if (EXISTS $ENV{ENZYME_IOS_SDK})
		set(ENZYME_IOS_SDK $ENV{ENZYME_IOS_SDK})
	else()
		message(FATAL_ERROR "Cannot find iOS SDK! Set the ENZYME_IOS_SDK environment variable")
	endif()
endif()

# Configuration stuff
set(CMAKE_OSX_ARCHITECTURES "arm64")
set(CMAKE_OSX_SYSROOT ${ENZYME_IOS_SDK})

# Set output folder
set(ENZYME_BIN_FOLDER ${CMAKE_BINARY_DIR}/enzyme_bin)
if (NOT EXISTS ${ENZYME_BIN_FOLDER})
	make_directory(${ENZYME_BIN_FOLDER})
endif()

set(ENZYME_ROOT ${CMAKE_CURRENT_LIST_DIR})

macro(enzyme_setup unzipped_folder binary_name)
	# Perform checks on the IPA
	if (NOT DEFINED ENZYME_UNZIPPED_FOLDER)
		message(FATAL_ERROR "Define ENZYME_UNZIPPED_FOLDER where the unzipped IPA is located.")
	endif()

	if (NOT EXISTS "${ENZYME_UNZIPPED_FOLDER}/Payload")
		message(FATAL_ERROR "Cannot find Payload folder. Place your unzipped IPA file into the folder defined in ENZYME_UNZIPPED_FOLDER.")
	endif()

	file(GLOB ENZYME_APP_FOLDER "${ENZYME_UNZIPPED_FOLDER}/Payload/*.app")

	if(ENZYME_APP_FOLDER STREQUAL "")
		message(FATAL_ERROR "Unable to find application inside Payload folder.")
	endif()

	if (NOT DEFINED ENZYME_BINARY_NAME)
		message(FATAL_ERROR "Unable to determine binary name. Define ENZYME_BINARY_NAME.")
	endif()

	if (NOT EXISTS "${ENZYME_APP_FOLDER}/${ENZYME_BINARY_NAME}")
		message(FATAL_ERROR "Unable to find binary name ${ENZYME_BINARY_NAME} in application folder")
	endif()

	# Codegen target
	add_custom_target(EnzymeCodegen ALL
		COMMAND mkdir -p ${ENZYME_BIN_FOLDER}//IPA
		COMMAND python3 enzyme.py
			${ENZYME_APP_FOLDER}/${ENZYME_BINARY_NAME}
			${ENZYME_BIN_FOLDER}
			${ENZYME_BINARY_NAME}
			${CMAKE_CURRENT_SOURCE_DIR}
		WORKING_DIRECTORY ${ENZYME_ROOT}/patcher
		COMMENT "Creating Patch"
		BYPRODUCTS ${ENZYME_BIN_FOLDER}/bootloader.hpp
	)
	add_dependencies(${PROJECT_NAME} EnzymeCodegen)

	# Our codegen creates a header file for us
	target_include_directories(${PROJECT_NAME} PRIVATE ${ENZYME_BIN_FOLDER})
	target_link_options(${PROJECT_NAME} PRIVATE "-L${ENZYME_IOS_SDK}/usr/lib")
endmacro()

include(${CMAKE_CURRENT_LIST_DIR}/cmake/Package.cmake)
