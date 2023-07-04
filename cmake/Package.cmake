set(CMAKE_INSTALL_DEFAULT_COMPONENT_NAME "DEFAULT")

# Modify this if you need
function(enzyme_package target)
	file(GLOB app_folder "${ENZYME_UNZIPPED_FOLDER}/Payload/*.app")
	get_filename_component(app_name ${app_folder} NAME)
	set(bin_folder ${CMAKE_BINARY_DIR}/enzyme_bin)

	add_custom_target(EnzymePackage ALL
		BYPRODUCTS ${CMAKE_BINARY_DIR}/${ENZYME_BINARY_NAME}.ipa
		MESSAGE "${bin_folder}"
		COMMAND rsync -av ${ENZYME_UNZIPPED_FOLDER}/* ${bin_folder}/IPA
		COMMAND ${CMAKE_COMMAND} -E copy ${bin_folder}/${ENZYME_BINARY_NAME} ${bin_folder}/IPA/Payload/${app_name}/${ENZYME_BINARY_NAME}
		COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:${target}> ${bin_folder}/IPA/Payload/${app_name}/hook.dylib
		COMMAND ${CMAKE_COMMAND} -E tar cfv "${CMAKE_BINARY_DIR}/${ENZYME_BINARY_NAME}.ipa" * --format=zip
		WORKING_DIRECTORY ${bin_folder}/IPA
	)
endfunction()
