cmake_minimum_required(VERSION 3.7.2)
project(proj)

set(CMAKE_CXX_COMPILER g++)
set(CMAKE_CXX_STANDARD 17)

find_package(Threads REQUIRED)

find_library(dimlib NAMES dim PATHS /usr/local/lib/dim)

if (${dimlib})
    message(FATAL_ERROR "no dim library")
else()
    message(STATUS "dim library found as ${dimlib}")
endif()

find_path(diminclude NAMES dic.hxx dis.hxx PATHS /usr/local/include/dim)

if (${diminclude})
    message(FATAL_ERROR "no dim include")
else()
    message(STATUS "dim include found as ${diminclude}")
endif()

include_directories(${diminclude})

add_subdirectory(server)
