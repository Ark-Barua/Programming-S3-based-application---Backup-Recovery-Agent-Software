# s3_operations.py

import boto3
import os
import time
import logging
import threading
import zipfile
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ---------- CONFIG ----------
bucket_name = '24030142004'
sync_folder = 'sync_folder/'
backup_folder = 'backups/'
backup_local_folder = 'backup_files/'
source_zip_folder = 'zip_source/'
zip_filename = 'backup.zip'
local_modify_file = "cloud.txt"
validated_upload_file = 'cloud.pdf'
simple_upload_file = 'cloud.txt'
jpg_upload_file = 'cloud.jpg'
allowed_extensions = ['.pdf', '.jpeg', '.jpg', '.png', '.mpeg', '.doc', '.txt']  # Added .png

# ---------- SETUP ----------
os.makedirs(sync_folder, exist_ok=True)
os.makedirs(backup_local_folder, exist_ok=True)
os.makedirs(source_zip_folder, exist_ok=True)

logging.basicConfig(
    filename='s3_automation_master.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ---------- AWS S3 Client ----------
s3 = boto3.client(
    's3',
    aws_access_key_id='XXXXX',
    aws_secret_access_key='XXXXX'
)

# ---------- UTILITIES ----------
def is_valid_file(filename):
    _, ext = os.path.splitext(filename)
    return ext.lower() in allowed_extensions

# ---------- FUNCTIONS ----------
def create_bucket_if_not_exists():
    try:
        s3.head_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' already exists.")
    except:
        try:
            s3.create_bucket(Bucket=bucket_name)
            print(f"Bucket '{bucket_name}' created.")
        except Exception as e:
            print(f"Bucket creation error: {e}")

def enable_versioning():
    try:
        s3.put_bucket_versioning(
            Bucket=bucket_name,
            VersioningConfiguration={'Status': 'Enabled'}
        )
        print("Versioning enabled.")
    except Exception as e:
        print(f"Versioning error: {e}")

def upload_file_to_s3(filepath):
    filename = os.path.basename(filepath)
    if not is_valid_file(filename):
        return
    try:
        s3.upload_file(Filename=filepath, Bucket=bucket_name, Key=f'synced/{filename}')
        print(f"Synced: {filename}")
    except Exception as e:
        print(f"Sync upload error: {e}")

def delete_file_from_s3(filename):
    try:
        s3.delete_object(Bucket=bucket_name, Key=f'synced/{filename}')
        print(f"Deleted from S3: {filename}")
    except Exception as e:
        print(f"Deletion error: {e}")

class S3SyncHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            upload_file_to_s3(event.src_path)
    def on_modified(self, event):
        if not event.is_directory:
            upload_file_to_s3(event.src_path)
    def on_deleted(self, event):
        if not event.is_directory:
            delete_file_from_s3(os.path.basename(event.src_path))

def start_sync():
    observer = Observer()
    observer.schedule(S3SyncHandler(), path=sync_folder, recursive=False)
    observer.start()
    print("Watching sync folder...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def backup_files():
    for file in os.listdir(backup_local_folder):
        local_path = os.path.join(backup_local_folder, file)
        if os.path.isfile(local_path) and is_valid_file(file):
            try:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                key = f"{backup_folder}{timestamp}_{file}"
                s3.upload_file(Filename=local_path, Bucket=bucket_name, Key=key)
                print(f"Backup: {file} ➜ {key}")
            except Exception as e:
                print(f"Backup failed: {e}")

def start_backup():
    while True:
        backup_files()
        time.sleep(60)

def move_jpg_files():
    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
        for obj in response.get('Contents', []):
            key = obj['Key']
            if key.lower().endswith(('.jpg', '.jpeg', '.png')) and not key.startswith("pictures/"):
                new_key = f"pictures/{os.path.basename(key)}"
                s3.copy_object(CopySource={'Bucket': bucket_name, 'Key': key}, Bucket=bucket_name, Key=new_key)
                s3.delete_object(Bucket=bucket_name, Key=key)
                print(f"Moved: {key} ➜ {new_key}")
            elif key.startswith("pictures/"):
                print(f"Skipped (already in pictures/): {key}")
    except Exception as e:
        print(f"Move image error: {e}")

def list_bucket_files():
    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
        print("Files in bucket:")
        for obj in response.get('Contents', []):
            print("-", obj['Key'])
    except Exception as e:
        print(f"List error: {e}")

def modify_and_upload():
    try:
        with open(local_modify_file, 'a') as f:
            f.write("\nThis is additional content.")
        s3.upload_file(Filename=local_modify_file, Bucket=bucket_name, Key=local_modify_file)
        print(f"Modified and uploaded: {local_modify_file}")
    except Exception as e:
        print(f"Modify/upload error: {e}")

def simple_upload():
    try:
        s3.upload_file(Filename=simple_upload_file, Bucket=bucket_name, Key=simple_upload_file)
        print(f"Uploaded '{simple_upload_file}'")
    except Exception as e:
        print(f"Upload error: {e}")

def validated_upload():
    if not os.path.exists(validated_upload_file):
        print("File not found.")
        return
    if not is_valid_file(validated_upload_file):
        print("Invalid file type.")
        return
    try:
        s3.upload_file(Filename=validated_upload_file, Bucket=bucket_name, Key=validated_upload_file)
        print(f"Validated upload: {validated_upload_file}")
    except Exception as e:
        print(f"Upload error: {e}")

def create_zip():
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for root, dirs, files in os.walk(source_zip_folder):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, source_zip_folder)
                zipf.write(file_path, arcname)
    print(f"🗜️ Created ZIP: {zip_filename}")

def upload_zip():
    try:
        s3.upload_file(zip_filename, bucket_name, f'zips/{zip_filename}')
        print(f"Uploaded ZIP: zips/{zip_filename}")
    except Exception as e:
        print(f"ZIP upload error: {e}")

def upload_jpg_file():
    if not os.path.exists(jpg_upload_file):
        print(f"JPG file '{jpg_upload_file}' not found.")
        return
    try:
        s3.upload_file(Filename=jpg_upload_file, Bucket=bucket_name, Key='image.jpg')
        print(f"Uploaded '{jpg_upload_file}' as 'image.jpg'")
    except Exception as e:
        print(f"JPG upload error: {e}")

# ---------- Upload Any Image ----------
def upload_custom_image():
    import tkinter.filedialog as fd
    filepath = fd.askopenfilename(
        title="Select an image",
        filetypes=[("Image Files", "*.jpg *.jpeg *.png")]
    )
    if not filepath:
        print("No file selected.")
        return

    filename = os.path.basename(filepath)
    if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        print("Unsupported image format.")
        return

    try:
        key = f"pictures/{filename}"
        s3.upload_file(Filename=filepath, Bucket=bucket_name, Key=key)
        print(f"Uploaded image: {filename} ➜ {key}")
    except Exception as e:
        print(f"Image upload error: {e}")
