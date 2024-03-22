import boto3
import time

s3_bucket='art.hex7.com'
s3_client = boto3.client('s3')
website_configuration = {
  'ErrorDocument': {'Key': 'error.html'},
  'IndexDocument': {'Suffix': 'index.html'},
}

s3_client.put_bucket_ownership_controls(
  Bucket=s3_bucket,
  OwnershipControls={ 'Rules': [ { 'ObjectOwnership': 'BucketOwnerPreferred' }, ] })
time.sleep(2)

s3_client.put_public_access_block(
  Bucket=s3_bucket,
  PublicAccessBlockConfiguration={'BlockPublicAcls': False,
                                  'IgnorePublicAcls': False,
                                  'BlockPublicPolicy': False,
                                  'RestrictPublicBuckets': False})
time.sleep(2)
s3_client.put_bucket_acl(ACL='public-read',
                         Bucket=s3_bucket)

time.sleep(2)
s3_client.put_bucket_website(Bucket=s3_bucket,
                             WebsiteConfiguration=website_configuration)
