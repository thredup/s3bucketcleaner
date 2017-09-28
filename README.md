# s3bucketcleaner

Container scans AWS s3 bucket for outdated files and deletes them.
The main purpose is to perform periodic cleanup to reduce costs.

## Configuration

Application implemented as a python script with boto3 client library
Environment variables must be set at container start:

* ***AWS_ACCESS_KEY_ID*** Amazon Access Key ID.
* ***AWS_SECRET_ACCESS_KEY*** Amazon Secret Key.
* ***S3_BUCKET_NAME***  A bucket name to look for a files  
* ***S3_OBJECT_PREFIX*** a subfolder inside bucket
* ***S3_OBJECT_NAME*** object prefix
* ***S3_PAGE_SIZE*** amount of objects to request for scan/delete, max value is 1000, set as default
* ***S3_OBJECT_AGE*** object age to keep, default 365

## Usage example

```
$ docker run -d --name s3cleaner -e "AWS_ACCESS_KEY_ID=MY_AWS_ACCESS_KEY_ID" \
                                 -e "AWS_SECRET_ACCESS_KEY=MY_AWS_SECRET_ACCESS_KEY" \
                                 -e "S3_BUCKET_NAME=my-shiny-archive" \
                                 -e "S3_OBJECT_PREFIX=photos" \
                                 -e "S3_OBJECT_AGE=100" \
                                 -e "S3_PAGE_SIZE=1000" \
                                 s3bucketcleaner:latest
```

It is also possible to mount inside container aws credentials file with corresponding access credentials.
(http://docs.aws.amazon.com/en_us/cli/latest/userguide/cli-config-files.html)

```
$ docker run -d --name s3cleaner -e "S3_BUCKET_NAME=my-shiny-archive" \
                                 -e "S3_OBJECT_PREFIX=photos" \
                                 -e "S3_OBJECT_AGE=100" \
                                 -e "S3_PAGE_SIZE=1000" \
                                 -v /aws_bucket/credentials:/root/.aws/credentials \
                                 s3bucketcleaner:latest
```

Please remember to create dedicated IAM role with List and Delete permissions for a your bucket and not use root account credentials.

## Logging

Use
```
docker logs -f s3cleaner
```

Application uses STDOUT to print boto3 response object when delete operation performed in json format:
```
{
    'Deleted': [
        {
            'Key': 'string',
            'VersionId': 'string',
            'DeleteMarker': True|False,
            'DeleteMarkerVersionId': 'string'
        },
    ],
    'RequestCharged': 'requester',
    'Errors': [
        {
            'Key': 'string',
            'VersionId': 'string',
            'Code': 'string',
            'Message': 'string'
        },
    ]
}
```
See http://boto3.readthedocs.io/en/latest/reference/services/s3.html#S3.Client.delete_object for details
