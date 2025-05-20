import os
import subprocess
from datetime import datetime
import boto3
from botocore.exceptions import ClientError

def backup_database():
    """Create a database backup and upload to S3"""
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")
    
    # Create backup directory if it doesn't exist
    backup_dir = 'backups'
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'{backup_dir}/backup_{timestamp}.sql'
    
    try:
        # Create database backup
        subprocess.run([
            'pg_dump',
            database_url,
            '-f', backup_file
        ], check=True)
        
        # Upload to S3 if configured
        if os.getenv('AWS_ACCESS_KEY_ID') and os.getenv('AWS_SECRET_ACCESS_KEY'):
            s3_client = boto3.client('s3')
            bucket_name = os.getenv('S3_BACKUP_BUCKET')
            
            if bucket_name:
                s3_client.upload_file(
                    backup_file,
                    bucket_name,
                    f'backups/{os.path.basename(backup_file)}'
                )
                print(f"Backup uploaded to S3: {backup_file}")
        
        # Clean up old backups (keep last 7 days)
        cleanup_old_backups(backup_dir)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error creating backup: {str(e)}")
        return False
    except ClientError as e:
        print(f"Error uploading to S3: {str(e)}")
        return False

def cleanup_old_backups(backup_dir, days_to_keep=7):
    """Remove backup files older than specified days"""
    import time
    
    current_time = time.time()
    for filename in os.listdir(backup_dir):
        filepath = os.path.join(backup_dir, filename)
        if os.path.isfile(filepath):
            file_age = current_time - os.path.getmtime(filepath)
            if file_age > (days_to_keep * 86400):  # Convert days to seconds
                os.remove(filepath)
                print(f"Removed old backup: {filepath}")

if __name__ == '__main__':
    backup_database() 