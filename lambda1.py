import json
import boto3

# Read the mocked file
with open('erp_data.json', 'r') as file:
    data = json.load(file)

# Modify the data if needed
# For example, let's change the status of the last entry to "finished"
data[-1]['status'] = 'finished'

# Convert the modified data back to JSON string
modified_data = json.dumps(data)

# Initialize Boto3 S3 client
s3 = boto3.client('s3')

# Specify bucket name and object key
bucket_name = 'test-lambda-api-project'
object_key = 'modified_data.json'

# Upload the modified data to S3 bucket
s3.put_object(Bucket=bucket_name, Key=object_key, Body=modified_data)

print("Modified data has been uploaded to S3 bucket.")
