#include <iostream>
#include <string>
#include <cstring>
#include <arpa/inet.h>
#include <unistd.h>

class SocketClient
{
private:
    int sock;                       // Socket descriptor
    struct sockaddr_in server_addr; // Server address

public:
    // Constructor
    SocketClient(const std::string &ip, int port)
    {
        // Step 1: Create a socket
        sock = socket(AF_INET, SOCK_STREAM, 0);
        if (sock < 0)
        {
            perror("Socket creation failed");
            exit(EXIT_FAILURE);
        }

        // Step 2: Setup the server address struct
        server_addr.sin_family = AF_INET;
        server_addr.sin_port = htons(port);
        if (inet_pton(AF_INET, ip.c_str(), &server_addr.sin_addr) <= 0)
        {
            perror("Invalid address / Address not supported");
            close(sock);
            exit(EXIT_FAILURE);
        }
    }

    // Connect to the server
    bool connect_to_server()
    {
        if (connect(sock, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0)
        {
            perror("Connection to server failed");
            return false;
        }
        std::cout << "Connected to server" << std::endl;
        return true;
    }

    // Send data to the server
    bool send_data(const std::string &data)
    {
        if (send(sock, data.c_str(), data.size(), 0) < 0)
        {
            perror("Failed to send data");
            return false;
        }
        return true;
    }

    // Receive data from the server
    std::string receive_data(size_t buffer_size = 1024)
    {
        char buffer[buffer_size];
        memset(buffer, 0, buffer_size);
        int bytes_received = recv(sock, buffer, buffer_size, 0);

        if (bytes_received < 0)
        {
            perror("Failed to receive data");
            return "";
        }
        else if (bytes_received == 0)
        {
            std::cout << "Server closed the connection" << std::endl;
            return "";
        }
        return std::string(buffer, bytes_received);
    }

    // Close the socket connection
    void close_connection()
    {
        close(sock);
        std::cout << "Connection closed" << std::endl;
    }

    // Destructor
    ~SocketClient()
    {
        close_connection();
    }
};