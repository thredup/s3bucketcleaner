#!/usr/local/bin/python
"""Cleanup S3 bucket from old image files."""

import boto3
import re
import datetime
import pytz
import os


s3_bucket_name = os.environ['S3_BUCKET_NAME']
s3_pbject_prefix = os.environ['S3_OBJECT_PREFIX']
s3_object_name = os.environ['S3_OBJECT_NAME']
s3_page_size = int(os.environ['S3_PAGE_SIZE'])
s3_object_age = int(os.environ['S3_OBJECT_AGE'])


client = boto3.client('s3')


def get_page(token, size):
    """Return portion of s3 backet objects."""
    if token:
        response = client.list_objects_v2(
            Bucket=s3_bucket_name,
            MaxKeys=size,
            Prefix=s3_pbject_prefix,
            ContinuationToken=token,
        )
    else:
        response = client.list_objects_v2(
            Bucket=s3_bucket_name,
            MaxKeys=size,
            Prefix=s3_pbject_prefix,
        )
    return response


def delete_objects(objects):
    """Delete objects from s3 bucket."""
    response = client.delete_objects(
        Bucket=s3_bucket_name,
        Delete={'Objects': objects, 'Quiet': True},
        )
    print(response)


content = True
token = ""
today = datetime.datetime.now(pytz.timezone('utc'))
objects_to_delete = []
# Request from AWS a list of s3_page_size objects
# iterate over objevts list, calculate age in days for s3_object_name
# s3_object_name ia an object name prefix
while content:
    s3objects = get_page(token, s3_page_size)
    if 'Contents' in s3objects:
        if 'NextContinuationToken' in s3objects:
            token = s3objects['NextContinuationToken']
        else:
            content = False
        for s3object in s3objects['Contents']:
            if re.search(s3_object_name, s3object['Key']):
                s3object_age = (today - s3object['LastModified']).days
                if s3object_age > s3_object_age:
                    # Compose page-sized array of object to delete
                    if len(objects_to_delete) < s3_page_size:
                        objects_to_delete.append({'Key': s3object['Key']})
                    else:
                        # Delete objects
                        delete_objects(objects_to_delete)
                        objects_to_delete = []
                        objects_to_delete.append({'Key': s3object['Key']})
        # Delete objects if not full request page composed asnd no content left
        if not content and len(objects_to_delete) != 0:
            delete_objects(objects_to_delete)
print("Cleanup done")
