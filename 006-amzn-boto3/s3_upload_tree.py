import boto3
import time
import json
import sys
import os

data_tree='../data'
s3_bucket='art.hex7.com'
s3_client = boto3.client('s3')
s3_list = []
local_list = []
debug = False

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
for path, dirs, files in os.walk(data_tree):
  for file in files:

    s3_file = os.path.normpath(path + '/' + file).replace('../', '')
    s3_list.append(s3_file)
    local_file = os.path.join(path, file)
    local_list.append(local_file)

    print("Upload: ", local_file)
    print("Bucket: ", s3_bucket)
    print("Key: ", s3_file)

    rez_upload = s3_client.upload_file(Filename=local_file,
                                       Bucket=s3_bucket,
                                       Key=s3_file)

    rez_acl = s3_client.put_object_acl(ACL='public-read',
                                       Bucket=s3_bucket,
                                       Key=s3_file)

    if debug:
      print('response upload file: ', rez_upload)
      print('response put acl: ', rez_acl)

    print("upload ", s3_file, " success")

if not os.path.exists('tmp/'):
  os.makedirs('tmp/')

if debug:
  print('local_list', local_list)
  print('s3_list: ', s3_list)

j_s3_list = json.dumps(s3_list, indent=4)
with open("tmp/s3_list.json", "w") as outfile:
    outfile.write(j_s3_list)

rez_upload = s3_client.upload_file(Filename='tmp/s3_list.json',
                                   Bucket=s3_bucket,
                                   Key='s3_list.json')

rez_acl = s3_client.put_object_acl(ACL='public-read',
                                   Bucket=s3_bucket,
                                   Key='s3_list.json')

if debug:
  print('upload json: ', rez_upload)
  print('put acl: ', rez_acl)

j_local_list = json.dumps(local_list, indent=4)
with open("tmp/local_list.json", "w") as outfile:
    outfile.write(j_local_list)
