// README.md 
# Blackboard Database Handler

This project implements a C++ database handler that uses `std::string` keys for record identification. Each record consists of an integer ID and multiple rows of name-value pairs. The handler supports operations to add, remove, and modify records, while logging operation names and timestamps for audit purposes.

## High-Level Architecture
- **Data Structures**:
  - `Record`: Represents a single record with an ID and rows of name-value pairs.
  - `std::unordered_map<std::string, Record>`: Used to efficiently store and retrieve records by their string keys.

## Design Patterns Used
- **Command Pattern**: Encapsulates operations as objects, enabling logging and undo functionality.
- **Factory Method**: Used for creating `Record` instances, separating creation logic from handling logic.

## Implementation Details
- Use `std::vector<std::pair<std::string, std::string>>` for storing name-value pairs within `Record`.
- Implement basic operations in a way that avoids recursion and minimizes string copying.

## Basic Operations
- **Add Record**: Adds a new record with the given key and initializes it with an ID and rows.
- **Remove Record**: Deletes a record identified by the key.
- **Modify Record**: Updates an existing record's rows.
- **Log Operations**: Each operation should log its name and a Unix-like timestamp.

## Querying
- Implement a method to retrieve all rows where values start with '||'.

## Class Definitions and Method Signatures
The project consists of three main classes: `Record`, `DatabaseHandler`, and `LogManager`.

### Record Class
Represents a database record with the following properties:
- `int id`: a unique identifier for the record.
- `std::vector<std::pair<std::string, std::string>> rows`: a collection of name-value pairs to store the record's data.

### DatabaseHandler Class
Responsible for managing multiple `Record` objects. It provides the following methods:
- `void addRecord(const Record& record)`: adds a new record to the database.
- `bool removeRecord(int id)`: removes a record by its unique id, returning true if successful.
- `bool modifyRecord(int id, const std::vector<std::pair<std::string, std::string>>& newRows)`: modifies an existing record with new data.

### LogManager Class
Responsible for logging operations performed on the database. It provides the following methods:
- `void logOperation(const std::string& operation, const std::string& timestamp)`: logs the operation with a timestamp.

For data storage and manipulation, use the C++ Standard Library containers such as `std::vector` and `std::map` where necessary. The Observer design pattern is suitable for notifying `LogManager` when changes are made in `DatabaseHandler`.

// Record.h 
#ifndef RECORD_H
#define RECORD_H

#include <vector>
#include <string>
#include <utility>

class Record {
public:
    Record(int id);
    int getId() const;
    void addRow(const std::string& name, const std::string& value);
    void modifyRow(const std::string& name, const std::string& newValue);
    const std::vector<std::pair<std::string, std::string>>& getRows() const;
private:
    int id;
    std::vector<std::pair<std::string, std::string>> rows;
};

#endif // RECORD_H

// Record.cpp 
#include "Record.h"

Record::Record(int id) : id(id) {}

int Record::getId() const {
    return id;
}

void Record::addRow(const std::string& name, const std::string& value) {
    rows.emplace_back(name, value);
}

void Record::modifyRow(const std::string& name, const std::string& newValue) {
    for (auto& row : rows) {
        if (row.first == name) {
            row.second = newValue;
            break;
        }
    }
}

const std::vector<std::pair<std::string, std::string>>& Record::getRows() const {
    return rows;
}

// DatabaseHandler.h 
#ifndef DATABASEHANDLER_H
#define DATABASEHANDLER_H

#include <vector>
#include <memory>
#include "Record.h"

class DatabaseHandler {
public:
    void addRecord(const Record& record);
    bool removeRecord(int id);
    bool modifyRecord(int id, const std::vector<std::pair<std::string, std::string>>& newRows);
private:
    std::vector<std::shared_ptr<Record>> records;
};

#endif // DATABASEHANDLER_H

// DatabaseHandler.cpp 
#include "DatabaseHandler.h"

void DatabaseHandler::addRecord(const Record& record) {
    records.push_back(std::make_shared<Record>(record));
}

bool DatabaseHandler::removeRecord(int id) {
    auto it = std::remove_if(records.begin(), records.end(), [id](const std::shared_ptr<Record>& record) {
        return record->getId() == id;
    });
    if (it != records.end()) {
        records.erase(it, records.end());
        return true;
    }
    return false;
}

bool DatabaseHandler::modifyRecord(int id, const std::vector<std::pair<std::string, std::string>>& newRows) {
    for (auto& record : records) {
        if (record->getId() == id) {
            for (const auto& row : newRows) {
                record->modifyRow(row.first, row.second);
            }
            return true;
        }
    }
    return false;
}

// LogManager.h 
#ifndef LOGMANAGER_H
#define LOGMANAGER_H

#include <string>
#include <vector>

class LogManager {
public:
    void logOperation(const std::string& operation, const std::string& timestamp);
    const std::vector<std::string>& getLogs() const;
private:
    std::vector<std::string> logs;
};

#endif // LOGMANAGER_H

// LogManager.cpp 
#include "LogManager.h"

void LogManager::logOperation(const std::string& operation, const std::string& timestamp) {
    logs.push_back(timestamp + " - " + operation);
}

const std::vector<std::string>& LogManager::getLogs() const {
    return logs;
}