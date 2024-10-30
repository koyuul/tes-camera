#include <iostream>
#include <cstring>
#include <string>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <fcntl.h>

int main(int argc, char *argv[])
{
    int server_fd, new_socket;
    struct sockaddr_in address;
    int opt = 1;
    int addrlen = sizeof(address);
    char buffer[1024] = {0};

    // initialize socket
    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd == 0)
    {
        perror("Socket failed");
        exit(EXIT_FAILURE);
    }
    std::cout << "Socket created successfully\n";

    // bind socket to port 8080
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY; // Listen on all interfaces
    address.sin_port = htons(8080);
    int bind_status = bind(server_fd, (struct sockaddr *)&address, sizeof(address));
    if (bind_status < 0)
    {
        perror("Bind failed");
        close(server_fd);
        exit(EXIT_FAILURE);
    }
    std::cout << "Socket binded successfully\n";

    // begin listening for connections
    bind_status = listen(server_fd, 3);
    if (bind_status < 0)
    {
        perror("Listen failed");
        close(server_fd);
        exit(EXIT_FAILURE);
    }
    std::cout << "Server listening on port 8080\n";

    // Set the server_fd to non-blocking mode
    fcntl(server_fd, F_SETFL, O_NONBLOCK);

    while (true)
    {
        // Accept new clients in a loop
        new_socket = accept(server_fd, (struct sockaddr *)&address, (socklen_t *)&addrlen);
        if (new_socket >= 0)
        {
            std::cout << "Accepted a client\n";
            // Handle client communication
            while (true)
            {
                // Read data from client
                int valread = read(new_socket, buffer, sizeof(buffer));
                if (valread > 0)
                {
                    std::cout << "[CLI]: " << buffer << std::endl;

                    // Respond to client
                    std::string success = "CONNECT_SUCCESS";
                    if (buffer == success)
                    {
                        const char *response = "IMAGE|STANDARD_CAPTURE";
                        send(new_socket, response, strlen(response), 0);
                    }
                }
                else if (valread == 0)
                {
                    // Client disconnected
                    std::cout << "Client disconnected\n";
                    close(new_socket);
                    break; // Exit inner loop to accept new clients
                }
                else
                {
                    perror("Read failed");
                    close(new_socket);
                    break; // Exit inner loop on error
                }
            }
        }

        // Optional: Add a short sleep or yield to avoid busy waiting
        usleep(100000); // Sleep for 100 milliseconds
    }

    close(server_fd);
    return 0;
}
