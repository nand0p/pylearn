import botocore
import boto3
import time


key = 'tanks'


debug = False
s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3')
s3_bucket = key + '.hex7.com'
s3_zone = 'Z3AQBSTGFYJSTF'
s3_dns = 's3-website-us-east-1.amazonaws.com'
print('debug: ', debug)
if debug:
  print('s3_bucket: ', s3_bucket)
  print('s3_zone: ', s3_zone)
  print('s3_dns: ', s3_dns)


print('make bucket if not exists: ', s3_bucket)
try:
  rez = s3_resource.meta.client.head_bucket(Bucket=s3_bucket)
except botocore.exceptions.ClientError as e:
  error_code = int(e.response['Error']['Code'])
  if error_code == 404:
    rez = s3_client.create_bucket(Bucket=s3_bucket)
if debug:
  print(rez)


website_configuration = {
  'ErrorDocument': {'Key': 'error.html'},
  'IndexDocument': {'Suffix': 'index.html'},
}
if debug:
  print('website_configuration: ', website_configuration)


print('set bucket ownership controls')
rez = s3_client.put_bucket_ownership_controls(Bucket=s3_bucket,
        OwnershipControls={ 'Rules': [ { 'ObjectOwnership': 'BucketOwnerPreferred' }, ] })
time.sleep(1)
if debug:
  print(rez)


print('put public access block')
rez = s3_client.put_public_access_block(Bucket=s3_bucket,
        PublicAccessBlockConfiguration={'BlockPublicAcls': False,
                                       'IgnorePublicAcls': False,
                                       'BlockPublicPolicy': False,
                                       'RestrictPublicBuckets': False})
time.sleep(1)
if debug:
  print(rez)


print('put bucket acl')
rez = s3_client.put_bucket_acl(ACL='public-read',
                               Bucket=s3_bucket)
time.sleep(1)
if debug:
  print(rez)


print('put bucket website')
rez = s3_client.put_bucket_website(Bucket=s3_bucket,
        WebsiteConfiguration=website_configuration)
time.sleep(1)
if debug:
  print(rez)


print('get r53 zone id')
r53_client = boto3.client('route53')
r53_rez = r53_client.list_hosted_zones_by_name(DNSName='hex7.com')
zone_id = r53_rez['HostedZones'][0]['Id'].split('/')[-1]
time.sleep(1)
if debug:
  print(r53_rez)
print('zone id: ', zone_id)


print('create r53 alias to s3')
record = s3_bucket + '.'
change = { 'Changes': [ {
             'Action': 'CREATE',
             'ResourceRecordSet': {
               'Name': record,
               'Type': 'A',
               'AliasTarget': {
                 'HostedZoneId': s3_zone,
                 'DNSName': s3_dns,
                 'EvaluateTargetHealth': False } } } ] }

print('change: ', change)

rez = r53_client.change_resource_record_sets(
        HostedZoneId=zone_id.split('/')[-1],
        ChangeBatch=change)

if debug:
  print(rez)
