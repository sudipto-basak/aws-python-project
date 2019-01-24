import urllib
import boto3
import os
import json


def start_label_detection(bucketname, key):
    reko = boto3.client('rekognition')

    response = reko.start_label_detection(
        Video={
            'S3Object': {
                'Bucket': bucketname,
                'Name': key
            }
        },
        NotificationChannel={
            'SNSTopicArn': os.environ['REKOGNITION_SNS_TOPIC_ARN'],
            'RoleArn': os.environ['REKOGNITION_ROLE_ARN']
        })

    print(response)
    return


def get_video_labels(job_id):
    reko = boto3.client('rekognition')

    result = reko.get_label_detection(JobId=job_id)

    next_token = result.get('NextToken', None)

    while next_token:

        next_page = reko.get_label_detection(JobId=job_id, NextToken=next_token)

        result['Labels'].extend(next_page['Labels'])
        next_token = next_page.get('NextToken', None)

    return result


def put_labels_in_db(response, s3_object, s3_bucket, job_status):
    pass


# Lambda Events
def start_processing_video(event, context):
    for record in event['Records']:
        start_label_detection(
            record['s3']['bucket']['name'],
            urllib.parse.unquote_plus(record['s3']['object']['key'])
        )

    return

def handle_lable_detection(event, context):
    for record in event['Records']:
        message = json.loads(record['Sns']['Message'])
        job_id = message['JobId']
        job_status = message['JobId']
        s3_bucket = message['Video']['S3Bucket']
        s3_object = message['Video']['S3ObjectName']

        response = get_video_labels(job_id)
        print(response)
        put_labels_in_db(response, s3_object, s3_bucket, job_status)


    return
