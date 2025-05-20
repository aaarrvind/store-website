import boto3
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_aws_connection():
    try:
        # Get credentials from environment variables
        aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        bucket_name = os.getenv('S3_BACKUP_BUCKET')

        # Verify credentials are loaded
        if not all([aws_access_key, aws_secret_key, bucket_name]):
            print("❌ Error: Missing AWS credentials in .env file")
            print("Please check that these variables are set in your .env file:")
            print("AWS_ACCESS_KEY_ID")
            print("AWS_SECRET_ACCESS_KEY")
            print("S3_BACKUP_BUCKET")
            return

        # Initialize S3 client
        s3 = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )
        
        print("Testing AWS S3 Connection...")
        
        # Test 1: List buckets
        print("\n1. Testing bucket listing...")
        response = s3.list_buckets()
        print("Available buckets:")
        for bucket in response['Buckets']:
            print(f"- {bucket['Name']}")
            
        # Test 2: Upload a test file
        print("\n2. Testing file upload...")
        test_content = f"Test backup file created at {datetime.now()}"
        test_file = "test_backup.txt"
        
        # Create test file
        with open(test_file, 'w') as f:
            f.write(test_content)
            
        # Upload to S3
        s3.upload_file(test_file, bucket_name, f"test/{test_file}")
        print(f"Successfully uploaded {test_file} to {bucket_name}")
        
        # Test 3: List objects in bucket
        print("\n3. Testing object listing...")
        response = s3.list_objects_v2(Bucket=bucket_name)
        print("Objects in bucket:")
        if 'Contents' in response:
            for obj in response['Contents']:
                print(f"- {obj['Key']} (Size: {obj['Size']} bytes)")
        else:
            print("No objects found in bucket")
            
        # Test 4: Download the test file
        print("\n4. Testing file download...")
        downloaded_file = "downloaded_test.txt"
        s3.download_file(bucket_name, f"test/{test_file}", downloaded_file)
        print(f"Successfully downloaded {test_file} to {downloaded_file}")
        
        # Test 5: Delete the test file
        print("\n5. Testing file deletion...")
        s3.delete_object(Bucket=bucket_name, Key=f"test/{test_file}")
        print(f"Successfully deleted {test_file} from {bucket_name}")
        
        # Clean up local files
        os.remove(test_file)
        os.remove(downloaded_file)
        
        print("\n✅ All AWS S3 tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during AWS S3 testing: {str(e)}")
        raise

if __name__ == "__main__":
    test_aws_connection() 