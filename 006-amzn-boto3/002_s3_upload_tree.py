import botocore
import boto3
import time
import json
import sys
import os

key = 'art'

data_tree='../data/' + key
s3_bucket=key + '.hex7.com'
s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3')
s3_list = []
debug = False
upload_images = True


if upload_images:
  for path, dirs, files in os.walk(data_tree):
    for file in files:
      if file != '.DS_Store':
        print('processing: ', file)
        s3_file = os.path.normpath(path + '/' + file).replace('../', '')
        s3_list.append(s3_file)
        local_file = os.path.join(path, file)

        try:
          s3_resource.Object(s3_bucket, s3_file).load()
        except botocore.exceptions.ClientError as e:
          if e.response['Error']['Code'] == "404":
            print("Upload: ", local_file)
            print("Bucket: ", s3_bucket)
            print("Key: ", s3_file)
            rez_upload = s3_client.upload_file(Filename=local_file,
                                               Bucket=s3_bucket,
                                               Key=s3_file,
                                               ExtraArgs = {'ACL': 'public-read' })
            if debug:
              print('response: ', rez_upload)

if debug:
  print('s3_list: ', s3_list)

if not os.path.exists('tmp/'):
  os.makedirs('tmp/')

j_s3_list = json.dumps(s3_list, indent=4)
with open("tmp/s3_list.json", "w") as outfile:
    outfile.write(j_s3_list)

rez_upload = s3_client.upload_file(Filename='tmp/s3_list.json',
                                   Bucket=s3_bucket,
                                   Key='s3_list.json',
                                   ExtraArgs = {'ACL': 'public-read' })

if debug:
  print('upload json: ', rez_upload)
