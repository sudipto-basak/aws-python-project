#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Classes for S3 bucket."""

import boto3
from botocore.exceptions import ClientError
import mimetypes
from pathlib import Path
from builtins import staticmethod
from hashlib import md5
from functools import reduce

from src import utils


class BucketManager:
    """Manage and S3 bucket."""

    CHUNK_SIZE = 8388608

    def __init__(self, session):
        """Create a BucketManager object."""
        self.session = session
        self.s3 = self.session.resource("s3")
        self.transfer_config = boto3.s3.transfer.TransferConfig(
            multipart_threshold=self.CHUNK_SIZE,
            multipart_chunksize=self.CHUNK_SIZE
        )

        self.manifest = {}
        self.local_set = set()

    @staticmethod
    def hash_data(data):
        """Get md5 hash of data."""
        hash = md5()
        hash.update(data)

        return hash

    def load_manifest(self, bucketname):
        """Load manifest for a bucket."""
        paginator = self.s3.meta.client.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=bucketname):
            for obj in page.get('Contents', []):
                self.manifest[obj['Key']] = obj['ETag']

    def gen_etag(self, path):
        """Generate ETag for local pathname."""
        hashes = []

        with open(path, 'rb') as f:
            while True:
                data = f.read(self.CHUNK_SIZE)

                if not data:
                    break

                hashes.append(self.hash_data(data))

        if not hashes:
            return
        elif len(hashes) == 1:
            return '"{}"'.format(hashes[0].hexdigest())
        else:
            digest = (h.digest() for h in hashes)
            hash = self.hash_data(reduce(lambda x, y: x + y, digest))
            return '"{}"'.format(hash.hexdigest(), len(hashes))

    def upload_file(self, bucket, path, key):
        """Upload content to S3."""
        content_type = mimetypes.guess_type(key)[0] or 'text/plain'

        etag = self.gen_etag(path)
        if self.manifest.get(key, '') == etag:
            # print("Skipping {}, no change detected".format(key))
            return

        return bucket.upload_file(
            path,
            key,
            ExtraArgs={
                'ContentType': content_type
                },
            Config=self.transfer_config
            )

    def get_bucket_location(self, bucketname):
        """Return the location of the bucket."""
        return self.s3.meta.client.get_bucket_location(Bucket=bucketname)['LocationConstraint'] or 'us-east-1'

    def get_bucket_url(self, bucketname):
        """Get URL for a bucket."""
        return "http://{}.{}".format(bucketname, utils.get_endpoint(self.get_bucket_location(bucketname)).host)

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

    def sync(self, bucket_name, pathname):
        """Sync s3 bucket with local filesystem path."""
        bucket = self.s3.Bucket(bucket_name)
        self.load_manifest(bucket_name)
        root = Path(pathname)

        def handle_directory(target):
            for p in target.iterdir():
                if p.is_dir():
                    handle_directory(p)
                if p.is_file():
                    self.local_set.add(p.relative_to(root).as_posix())
                    self.upload_file(
                        bucket,
                        str(p.as_posix()),
                        str(p.relative_to(root).as_posix())
                        )

        handle_directory(root)
        # print(self.local_set)
        # print(set(self.manifest))
        self.remove_extra_files_from_s3(
            bucket,
            set(self.manifest).difference(self.local_set)
        )

        print("Website URL: {}".format(self.get_bucket_url(bucket.name)))
        return

    def remove_extra_files_from_s3(self, bucket, keyset):
        """Remove files from s3 which is not present in local."""
        keylist = list([{'Key': key} for key in keyset])
        # print(keylist)
        if keylist:
            response = bucket.delete_objects(
                Delete={
                    'Objects': keylist
                }
            )

            # print(response)
