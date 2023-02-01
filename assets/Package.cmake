set(CMAKE_INSTALL_DEFAULT_COMPONENT_NAME "DEFAULT")

# Modify this if you need
macro(enzyme_package binary application)
	add_custom_target(EnzymePackage ALL
		BYPRODUCTS ${CMAKE_BINARY_DIR}/${application}.ipa
		COMMAND rsync -av ${CMAKE_SOURCE_DIR}/assets/IPA/* ${BIN_FOLDER}/IPA
		COMMAND ${CMAKE_COMMAND} -E copy ${BIN_FOLDER}/${application} ${BIN_FOLDER}/IPA/Payload/${application}.app/${application}
		COMMAND ${CMAKE_COMMAND} -E copy ${binary} ${BIN_FOLDER}/IPA/Payload/${application}.app/hook.dylib
		COMMAND zip -ur "${CMAKE_BINARY_DIR}/Example.ipa" *
		WORKING_DIRECTORY ${BIN_FOLDER}/IPA
	)
endmacro()