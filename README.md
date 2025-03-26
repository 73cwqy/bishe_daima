# Quantum-Enhanced Secure Offline Storage System

English | [中文](README_CN.md)

This project implements a secure offline data storage system based on quantum encryption technology, providing high-strength data protection and management functions.

## Features

- **Quantum-Enhanced Encryption**: Utilizes quantum random number generation technology to provide stronger encryption protection
- **Secure Offline Storage**: Data is stored locally, requiring no network connection, avoiding network attack risks
- **Integrity Verification**: Uses HMAC to ensure data integrity and prevent tampering
- **Metadata Management**: Supports adding custom metadata to stored data
- **Secure Deletion**: Provides secure deletion functionality, overwriting file content multiple times to ensure data cannot be recovered
- **Backup and Recovery**: Supports data backup and recovery functions

## Installation Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Initialize Storage System

```bash
python main.py init [--dir storage_directory] [--key-file key_file_path]
```

### Store Data

```bash
# Store a file
python main.py store --file file_path --key-file key_file_path [--meta metadata]

# Store text
python main.py store --text "text to store" --key-file key_file_path [--meta metadata]
```

Metadata format: `key1=value1,key2=value2`

### Retrieve Data

```bash
# Output to standard output
python main.py retrieve data_ID --key-file key_file_path

# Output to file
python main.py retrieve data_ID --output output_file_path --key-file key_file_path
```

### List All Data

```bash
python main.py list --key-file key_file_path
```

### Delete Data

```bash
# Secure deletion (default)
python main.py delete data_ID --key-file key_file_path [--secure]
```

### Backup Data

```bash
python main.py backup backup_directory --key-file key_file_path
```

### Restore Data

```bash
python main.py restore backup_directory --key-file key_file_path
```
