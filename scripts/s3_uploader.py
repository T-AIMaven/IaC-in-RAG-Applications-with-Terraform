import boto3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# AWS credentials
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
region_name = os.getenv('AWS_REGION', 'eu-central-1')

# S3 bucket details
bucket_name = os.getenv('DOCUMENT_BUCKET')
local_directory = os.getenv('LOCAL_DOCUMENT_DIRECTORY', '../documents')
s3_subdirectory = 'documents/'  # Subdirectory in S3 where files will be uploaded

# Create an S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=region_name
)

# Load files to S3 Bucket
def upload_files(directory, bucket, subdirectory):
    for subdir, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(subdir, file)
            s3_path = os.path.join(subdirectory, os.path.relpath(file_path, directory))
            try:
                s3.upload_file(file_path, bucket, s3_path)
                print(f'Successfully uploaded {file_path} to s3://{bucket}/{s3_path}')
            except Exception as e:
                print(f'Failed to upload {file_path}: {e}')

if __name__ == "__main__":
    # Upload all files in the directory
    upload_files(local_directory, bucket_name, s3_subdirectory)