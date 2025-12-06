cmake_minimum_required(VERSION 3.12)
project(UTPScheduler)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Source files
set(SOURCES
    grafo.cpp
    restricciones.cpp
    planificador.cpp
)

# Create static library
add_library(scheduler_core STATIC ${SOURCES})

# Include directories
target_include_directories(scheduler_core PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

# Compiler flags
if(MSVC)
    target_compile_options(scheduler_core PRIVATE /W4 /O2)
else()
    target_compile_options(scheduler_core PRIVATE -Wall -Wextra -O3)
endif()

# Installation
install(TARGETS scheduler_core
        ARCHIVE DESTINATION lib
        LIBRARY DESTINATION lib)

install(FILES 
        grafo.hpp
        restricciones.hpp
        planificador.hpp
        DESTINATION include)
