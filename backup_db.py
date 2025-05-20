import os
import subprocess
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in environment variables")

# Create backup directory if it doesn't exist
backup_dir = 'backups'
if not os.path.exists(backup_dir):
    os.makedirs(backup_dir)

# Generate backup filename with timestamp
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
backup_file = os.path.join(backup_dir, f'backup_{timestamp}.sql')

# Extract database credentials from URL
# Format: postgresql://username:password@host:port/database
parts = DATABASE_URL.split('://')[1].split('@')
credentials = parts[0].split(':')
host_db = parts[1].split('/')
host_port = host_db[0].split(':')

username = credentials[0]
password = credentials[1]
host = host_port[0]
port = host_port[1] if len(host_port) > 1 else '5432'
database = host_db[1]

# Create backup using pg_dump
try:
    # Set PGPASSWORD environment variable
    os.environ['PGPASSWORD'] = password
    
    # Run pg_dump command
    cmd = [
        'pg_dump',
        '-h', host,
        '-p', port,
        '-U', username,
        '-d', database,
        '-F', 'c',  # Custom format
        '-f', backup_file
    ]
    
    subprocess.run(cmd, check=True)
    print(f"Backup created successfully: {backup_file}")
    
    # Clean up old backups (keep last 7 days)
    for file in os.listdir(backup_dir):
        if file.startswith('backup_') and file.endswith('.sql'):
            file_path = os.path.join(backup_dir, file)
            file_time = datetime.fromtimestamp(os.path.getctime(file_path))
            if (datetime.now() - file_time).days > 7:
                os.remove(file_path)
                print(f"Removed old backup: {file}")
                
except subprocess.CalledProcessError as e:
    print(f"Error creating backup: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
finally:
    # Clear PGPASSWORD from environment
    if 'PGPASSWORD' in os.environ:
        del os.environ['PGPASSWORD'] 