cmake_minimum_required(VERSION 3.10)

project(tes-camera LANGUAGES CXX) # set project name to tes-camera,

set(CMAKE_CXX_STANDARD 23) # Utilize C++ 23
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_executable(tes-camera
    src/main.cpp
    # include future executables here ...
)

target_include_directories(tes-camera PRIVATE include) # Include future header files...

# target_link_libraries(tes-camera LIBRARYNAME) use later to add external libraries

set_target_properties(tes-camera PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin
)