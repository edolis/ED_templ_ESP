cmake_minimum_required(VERSION 3.16.0)

# Fallback logic if not passed via environment or CMAKE_EXTRA_ARGS
if(NOT DEFINED PROJECT_NAME OR PROJECT_NAME STREQUAL "")
    if(DEFINED ENV{PROJECT_NAME})
        set(PROJECT_NAME $ENV{PROJECT_NAME})
    else()
        set(PROJECT_NAME "default_app")
    endif()
endif()

if(NOT DEFINED PROJECT_VER OR PROJECT_VER STREQUAL "")
    if(DEFINED ENV{PROJECT_VER})
        set(PROJECT_VER $ENV{PROJECT_VER})
    else()
        set(PROJECT_VER "v0.0.0-0-unknown")
    endif()
endif()

message(STATUS "Resolved PROJECT_NAME=${PROJECT_NAME}")
message(STATUS "Resolved PROJECT_VER=${PROJECT_VER}")

include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(${PROJECT_NAME} VERSION ${PROJECT_VER})
