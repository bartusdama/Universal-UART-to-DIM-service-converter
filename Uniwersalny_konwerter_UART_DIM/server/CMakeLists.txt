add_executable(server src/server.cpp src/main.cpp)

target_include_directories(server PUBLIC include)

target_link_libraries(server PUBLIC ${dimlib})
target_link_libraries(server PUBLIC Threads::Threads)
