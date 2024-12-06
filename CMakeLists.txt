cmake_minimum_required(VERSION 3.10)

project(tes-camera LANGUAGES CXX) # set project name to tes-camera,

set(CMAKE_CXX_STANDARD 20) # Utilize C++ 20
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Find SQLite3 library and headers
find_library(SQLITE3_LIB sqlite3)
find_path(SQLITE3_INCLUDE_DIR sqlite3.h)

add_executable(tes-camera
    src/main.cpp
    # include future executables here ...
    src/client_socket.cpp
    src/database_handler.cpp
)

# Include future header files...
# target_include_directories(tes-camera PRIVATE include) 

# Link external librarys here
target_link_libraries(tes-camera PRIVATE ${SQLITE3_LIB})

set_target_properties(tes-camera PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin
)