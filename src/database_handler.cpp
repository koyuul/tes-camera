#include <iostream>
#include <vector>
#include <set>
#include <sqlite3.h>

class DatabaseHandler {
private:
    sqlite3* db;
    std::set<std::string> acceptedArguments { "image_id", "request_epoch", "capture_epoch", "look_before_epoch" };
    
public:
    DatabaseHandler(){
        // Open database
        int exit = sqlite3_open("/home/mendel/tes-camera/image_info.db", &db);
        char* errorOutput;
        if (exit != SQLITE_OK) { std::cerr << sqlite3_errmsg(db) << std::endl; }
    }

    void retrieve(std::vector<std::string> arguments) {
        int image_id = -1;
        int request_epoch = -1;
        int capture_epoch = -1;
        int look_before_epoch = 0; // Set to 0 instead of -1 because it's default value is 0 (aka False)

        // Parse arguments vector into their respective arguments
        for (size_t i = 0; i < arguments.size(); i+=2) { // Iterate by 2 since we process each argument and the value immediately after
            std::string argument = arguments[i];
            if (acceptedArguments.find(argument) != acceptedArguments.end()) {
                if (argument == "image_id") image_id = std::stoi(arguments[i+1]);
                if (argument == "request_epoch") request_epoch = std::stoi(arguments[i+1]);
                if (argument == "capture_epoch") capture_epoch = std::stoi(arguments[i+1]);
                if (argument == "look_before_epoch") look_before_epoch = std::stoi(arguments[i+1]);
            }
        }
        query(image_id, request_epoch, capture_epoch, look_before_epoch);
    }


    // TODO: handle sorting by coords, write tests?
    // TODO: else if (predicted_location) { ... }
    void query(int image_id, int request_epoch, int capture_epoch, int look_before_epoch) {
        try {
            const char* query;
            sqlite3_stmt* stmt;
            if (image_id != -1) {
                query = "SELECT * FROM metadata WHERE image_id = ?";

                int rc = sqlite3_prepare_v2(db, query, -1, &stmt, nullptr);
                if (rc != SQLITE_OK) { std::cerr << "failed to prep stmt: " << sqlite3_errmsg(db) << std::endl; }
                sqlite3_bind_int(stmt, 1, image_id);
                if (rc != SQLITE_OK) { std::cerr << "Failed to bind parameter: " << sqlite3_errmsg(db) << std::endl; }
            } 
            else if (request_epoch != -1) {
                query = (look_before_epoch == 1)
                    ? "SELECT * FROM metadata ORDER BY ABS(request_epoch - ?) ASC LIMIT 1"
                    : "SELECT * FROM metadata WHERE request_epoch >= ? ORDER BY request_epoch ASC LIMIT 1";
                int rc = sqlite3_prepare_v2(db, query, -1, &stmt, nullptr);
                if (rc != SQLITE_OK) { std::cerr << "failed to prep stmt: " << sqlite3_errmsg(db) << std::endl; }
                sqlite3_bind_int(stmt, 1, request_epoch);
                if (rc != SQLITE_OK) { std::cerr << "Failed to bind parameter: " << sqlite3_errmsg(db) << std::endl; }
            } 
            else if (capture_epoch != -1) {
                query = (look_before_epoch == 1)
                    ? "SELECT * FROM metadata ORDER BY ABS(capture_epoch - ?) ASC LIMIT 1"
                    : "SELECT * FROM metadata WHERE capture_epoch >= ? ORDER BY capture_epoch ASC LIMIT 1";
                int rc = sqlite3_prepare_v2(db, query, -1, &stmt, nullptr);
                if (rc != SQLITE_OK) { std::cerr << "failed to prep stmt: " << sqlite3_errmsg(db) << std::endl; }
                sqlite3_bind_int(stmt, 1, capture_epoch);
                if (rc != SQLITE_OK) { std::cerr << "Failed to bind parameter: " << sqlite3_errmsg(db) << std::endl; }
            } 
            else {
                throw std::runtime_error("No valid filter for recieve query");
            }

            // Now that cursor is in right place, iterate through results
            while (sqlite3_step(stmt) == SQLITE_ROW) {
                int image_id = sqlite3_column_int(stmt, 0 );
                const char* image_path_ptr = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 1));
                std::string image_path = image_path_ptr ? std::string(image_path_ptr) : "NULL"; // Handle NULL case
                int request_epoch = sqlite3_column_int(stmt, 2);
                int capture_epoch = sqlite3_column_int(stmt, 3); 
                int camera_source = sqlite3_column_int(stmt, 4); 
                
                std::cout << "image_id: " << image_id << ", "
                << "image_path: " << image_path << ", "
                << "request_epoch: " << request_epoch << ", "
                << "capture_epoch: " << capture_epoch << ", "
                << "camera_source: " << camera_source << std::endl;
            }
        } catch (std::exception& err) {
            std::cout << "Query failed: " << err.what() <<  std::endl; 
        }
    }
};
