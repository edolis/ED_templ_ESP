# This file was automatically generated for projects
# without default 'CMakeLists.txt' file.

FILE(GLOB_RECURSE app_sources ${CMAKE_SOURCE_DIR}/src/*.*)

if(CONFIG_BT_ENABLED)
    idf_component_register(SRCS ${app_sources}
                           INCLUDE_DIRS "."
                           REQUIRES bt
                           EMBED_TXTFILES $ENV{ESP_HEADERS}/ca.crt #required by TLS
                           )
else()
    idf_component_register(SRCS ${app_sources}
                           INCLUDE_DIRS "."
                           EMBED_TXTFILES $ENV{ESP_HEADERS}/ca.crt #required by TLS
                           )

endif()

    #in local repository location:
    # idf_component_register(SRCS ${app_sources}
    #                         INCLUDE_DIRS "."
    #                         EMBED_TXTFILES certs/ca.crt #required by TLS
    #                         )