# AWS S3 Automation System with GUI

Automated File Management and Backup System using AWS S3

## Table of Contents

- [Overview](#overview)
- [Technology Stack](#technology-stack)
- [Features](#features)
- [Setup & Installation](#setup--installation)
- [AWS Credentials](#aws-credentials)
- [Usage](#usage)
- [Summary of Achievements](#summary-of-achievements)
- [Author](#author)

## Overview

This project is a **complete file automation system** integrating seamless AWS S3 cloud interaction via a modern Python GUI. It enables file synchronization, automated backup, zip packaging, change detection, image management, and more, all protected by a login system and presented in a user-friendly interface.

## Technology Stack

- **Python 3**
- [Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) (AWS SDK for Python)
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) (Modern GUI Framework)
- [Watchdog](https://python-watchdog.readthedocs.io/en/latest/) (File System Monitoring)

## Features

### 1. Core AWS S3 Integration
- Create and validate S3 buckets.
- Upload, list, delete, and modify files.
- Hierarchical storage with folder-like S3 keys.

### 2. Enhanced File I/O Management
- **Supported extensions:** `.pdf`, `.jpeg`, `.jpg`, `.png`, `.mpeg`, `.doc`, `.txt`
- Extension-based filtering.
- Timestamp-based naming and organization.
- Errors managed with robust exception handling.
- Extensive logging to `s3_automation_master.log` and console.

### 3. Automated & Scheduled Backup
- Background thread backs up files from `backup_files/` every 60 seconds.
- Versioned file uploads to S3.

### 4. Real-Time File Change Detection
- `sync_folder/` monitored for real-time changes (create, modify, delete) with Watchdog.
- Instant upload/re-upload or removal from S3 as needed.

### 5. Zip & Versioned Bucket Uploads
- Zips contents of `zip_source/` as `backup.zip`.
- Uploads to `zips/` S3 folder.
- S3 bucket versioning enabled.

### 6. GUI with Modern Features
- Built in CustomTkinter for a clean, responsive experience.
- Login & Signup with "Remember Me."
- Dashboard: Action buttons, live log console, progress bar, theme toggle.

### 7. Image Handling
- Upload `.jpg`, `.jpeg`, `.png` files via file picker.
- Automatically organized into `pictures/` on S3.
- Auto-move utility prevents duplicates.

## Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/s3-automation-gui.git
   cd s3-automation-gui
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up AWS credentials** (see below).

## AWS Credentials

> **For testing only:**  
> You may temporarily embed AWS credentials in `s3_operations.py`:
```python
s3 = boto3.client(
    's3',
    aws_access_key_id='YOUR_AWS_ACCESS_KEY_ID',
    aws_secret_access_key='YOUR_AWS_SECRET_ACCESS_KEY'
)
```
- **Never** commit these credentials to any public repository.

**Recommended:**  
Add credentials to `~/.aws/credentials`:
```ini
[default]
aws_access_key_id = YOUR_AWS_ACCESS_KEY_ID
aws_secret_access_key = YOUR_AWS_SECRET_ACCESS_KEY
```

Then, in code:
```python
s3 = boto3.client('s3')  # Uses default AWS profile
```

## Usage

- **Run the application:**
  ```bash
  python main.py
  ```
- **Access the GUI** and use the dashboard to upload, backup, zip, and manage files.

**Additional Features:**
- Custom image upload tool
- Multi-threaded execution
- Clean, modern UI/UX with live feedback

## Author

**Ark Barua**  
Date Completed: July 18, 2025

*For questions, contact the author or submit an issue via the repository.*

Let me know if you'd like to have this tailored for code snippets, contribution guides, or more project-specific sections!
