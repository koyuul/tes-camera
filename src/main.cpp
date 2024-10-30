#include <iostream>
#include <cstring>
#include <sstream>
#include <vector>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include "client_socket.cpp"

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

    // Connect and send a ready signal to main board
    if (client.connect_to_server())
    {
        client.send_data("CONNECT_SUCCESS");

        // Recieve command
        std::string response = client.receive_data();
        std::cout << "[SERV]: " << response << std::endl;

        // Parse commmand
        // TODO: Handle parameters
        // TODO: Handle invalid sent commands
        std::vector<std::string> parsed = parse_command(response);
        std::string command_type = parsed[0];
        std::string action = parsed[1];

        // Handle received command
    }

    return 0;
}