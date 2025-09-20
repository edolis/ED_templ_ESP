# This file was automatically generated for projects
# without default 'CMakeLists.txt' file.

FILE(GLOB_RECURSE app_sources ${CMAKE_SOURCE_DIR}/src/*.*)

if(CONFIG_BT_ENABLED)
    idf_component_register(
        SRCS ${app_sources}   $ENV{ESP_HEADERS}/x509_crt_bundle.S
        INCLUDE_DIRS "."
        REQUIRES bt
    )
else()
    idf_component_register(
        #EMBED_TXTFILES $ENV{ESP_HEADERS}/ca.crt # old loading in ram instead as a bundle
        SRCS ${app_sources}  $ENV{ESP_HEADERS}/x509_crt_bundle.S
        INCLUDE_DIRS "."
    )
endif()
