#include <iostream>
#include <cstring>
#include <sstream>
#include <vector>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <cstdlib>
#include "client_socket.cpp"
#include "database_handler.cpp"

std::vector<std::string> parse_command(const std::string &str)
{
    std::string delimiter = "|";
    std::vector<std::string> tokens;
    size_t start = 0;
    size_t end = str.find(delimiter);

    while (end != std::string::npos)
    {
        tokens.push_back(str.substr(start, end - start));
        start = end + delimiter.length();
        end = str.find(delimiter, start);
    }

    tokens.push_back(str.substr(start));
    return tokens;
}

int main(int argc, char *argv[])
{
    SocketClient client("127.0.0.1", 8080);
    DatabaseHandler metadata_db;
    // Connect and send a ready signal to main board
    if (client.connect_to_server())
    {
        client.send_data("CONNECT_SUCCESS");

        // Recieve command
        std::string response = client.receive_data();
        std::cout << "[SERV]: Parsing " << response << "..." << std::endl;

        // Parse commmand
        // TODO: Handle parameters
        // TODO: Handle invalid sent commands
        std::vector<std::string> parsed = parse_command(response);
        std::string command_type = parsed[0];

        // Handle received command
        if (command_type == "STD_CAPTURE") {
            int camera_select = stoi(parsed[1]);
            int request_epoch = stoi(parsed[2]);
            std::string path_to_capture_script = 
                "python3 /home/mendel/Arducam-CircuitPython/camera_controller.py STD_CAPTURE " 
                + std::to_string(camera_select) + " " 
                + std::to_string(request_epoch);
            
            int result = system(path_to_capture_script.c_str());
            if (result == 0) {
                std::cout << "[CAMERA] Python script executed successfully." << std::endl;
            } else {
                std::cout << "[CAMERA] Python script execution failed." << std::endl;
            }
        }
        
        if (command_type == "RETRIEVE") {
            std::string query_key = parsed[1];
            std::string query_val = parsed[2];
            std::vector<std::string> retrieve_args = {query_key, query_val};
            metadata_db.retrieve(retrieve_args);
        }
    }

    return 0;
}