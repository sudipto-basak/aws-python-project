#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Webproject: Deploy website in AWS.

--------------------------------------------
Created on Jan 14, 2019
@author: ctrq970
--------------------------------------------

Webproject automates the deployment of static websites in S3
- Create S3 bucket
- Configure them
- Upload website code into the bucket
- Configure Cloudfront and SSL

"""

import boto3
import click
from bucket import BucketManager

session = None
bucket_manager = None


@click.group()
@click.option('--profile', default="eclipsedev",
              help="provide a aws profile name")
def cli(profile):
    """Create and deploy websites in AWS."""
    global session, bucket_manager
    session_config = {}
    if profile:
        session_config['profile_name'] = profile

    session = boto3.Session(**session_config)
    bucket_manager = BucketManager(session)


@cli.command('list-buckets')
def list_buckets():
    """List all s3 buckets."""
    for bucket in bucket_manager.all_buckets():
        print(bucket)


@cli.command('list-bucket-objects')
@click.argument('bucket')
def list_bucket_objects(bucket):
    """List objects in each bucket."""
    for obj in bucket_manager.all_objects(bucket):
        print(obj)


@cli.command('setup-bucket')
@click.argument('bucket')
def setup_bucket(bucket):
    """Create a new bucket and setup for Website hosting."""
    s3_bucket = bucket_manager.init_bucket(bucket)

    if s3_bucket is not None:
        bucket_manager.set_bucket_policy(s3_bucket)
        bucket_manager.configure_website(s3_bucket)

    return


@cli.command('sync')
@click.argument('bucket')
@click.argument('pathname', type=click.Path(exists=True))
def sync(pathname, bucket):
    """Sync contents of PATHNAME to BUCKET."""
    bucket_manager.sync(bucket, pathname)

    return


if __name__ == '__main__':
    cli()
