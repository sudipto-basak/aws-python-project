#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Classes for S3 bucket."""

from botocore.exceptions import ClientError
import mimetypes
from pathlib import Path
from builtins import staticmethod

import utils


class BucketManager:
    """Manage and S3 bucket."""

    def __init__(self, session):
        """Create a BucketManager object."""
        self.session = session
        self.s3 = self.session.resource("s3")

    def get_bucket_location(self, bucketname):
        """Return the location of the bucket."""
        return self.s3.meta.client.get_bucket_location(Bucket=bucketname)['LocationConstraint'] or 'us-east-1'

    def get_bucket_url(self, bucketname):
        """Get URL for a bucket."""
        return "http://{}.{}".format(bucketname,utils.get_endpoint(self.get_bucket_location(bucketname)).host)

    def all_buckets(self):
        """Get Iterator of all S3 buckets."""
        return self.s3.buckets.all()

    def all_objects(self, bucket):
        """Get Iterator for all objects in a bucket."""
        return self.s3.Bucket(bucket).objects.all()

    def init_bucket(self, bucket_name):
        """Create or Find a bucket in S3."""
        s3_bucket = None

        try:
            if self.region_name == 'us-east-1':
                s3_bucket = self.s3.create_bucket(Bucket=bucket_name)
            else:
                s3_bucket = self.s3.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={
                        "LocationConstraint": self.session.region_name
                        })
            print("Bucket '{0}' is created successfully"
                  .format(s3_bucket.name))
            return s3_bucket
        except ClientError as error:
            if error.response['Error']['Code'] == "BucketAlreadyExists":
                print("Bucket name is not available. \
                Please chose another name!!")
                raise error

        return s3_bucket

    def set_bucket_policy(self, bucket):
        """Set bucket policy."""
        policy = """
        {
          "Version":"2012-10-17",
          "Statement":[
            {
              "Sid":"PublicReadGetObject",
              "Effect":"Allow",
              "Principal": "*",
              "Action":["s3:GetObject"],
              "Resource":["arn:aws:s3:::%s/*"]
            }
          ]
        }
        """ % bucket.name

        pol = bucket.Policy()
        pol.put(Policy=policy.strip())

        print(self.get_bucket_url(bucket.name))

    def configure_website(self, bucket):
        """Configure static website for a bucket."""
        bucket.Website().put(WebsiteConfiguration={
            'ErrorDocument': {
                'Key': 'error.html'
                },
            'IndexDocument': {
                'Suffix': 'index.html'
                }
            })

        return

    @staticmethod
    def upload_file(bucket, path, key):
        """Upload content to S3."""
        content_type = mimetypes.guess_type(key)[0] or 'text/plain'
        bucket.upload_file(
            path,
            key,
            ExtraArgs={
                'ContentType': content_type
                })

        return

    def sync(self, bucket_name, pathname):
        """Sync s3 bucket with local filesystem path."""
        bucket = self.s3.Bucket(bucket_name)
        root = Path(pathname)

        def handle_directory(target):
            for p in target.iterdir():
                if p.is_dir():
                    handle_directory(p)
                if p.is_file():
                    self.upload_file(
                        bucket,
                        str(p.as_posix()),
                        str(p.relative_to(root).as_posix())
                        )

        handle_directory(root)
        print(self.get_bucket_url(bucket.name))
        return
