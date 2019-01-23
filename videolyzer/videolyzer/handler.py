import urllib
import boto3


def start_label_detection(bucketname, key):
    reko = boto3.client('rekognition')

    response = reko.start_label_detection(
        Video={
            'S3Object': {
                'Bucket': bucketname,
                'Name': key
            }
        })

    print(response)
    return


def start_processing_video(event, context):
    for record in event['Records']:
        start_label_detection(
            record['s3']['bucket']['name'],
            urllib.parse.unquote_plus(record['s3']['object']['key'])
        )

    return