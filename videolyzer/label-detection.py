# coding: utf-8
import boto3
from pathlib import Path

session = boto3.Session(profile_name='eclipsedev')
s3 = session.resource('s3')
bucket = s3.create_bucket(Bucket='python-reko-automation')
reko = session.client('rekognition')

pathname = 'C:\\Users\\ctrq970\\git\\aws-python-project\\videolyzer\\sample_video\\Pexels Videos 1746879.mp4'
path = Path(pathname)

bucket.upload_file(str(path.as_posix()),str(path.name))

response = reko.start_label_detection(Video={'S3Object': {'Bucket': bucket.name, 'Name': path.name}})
print(response)

result = reko.get_label_detection(JobId=response['JobId'])
result['JobStatus']
result['VideoMetadata']
result['Labels']

