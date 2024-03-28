from argparse import ArgumentParser
import botocore
import boto3
import time
import json
import sys
import os


parser = ArgumentParser()
parser.add_argument('--debug', action='store_true', help='debug')
parser.add_argument('--upload', action='store_true', help='upload images')
parser.add_argument('--key', type=str, default='art', help='directory')
args = parser.parse_args()

s3_resource = boto3.resource('s3')
s3_client = boto3.client('s3')
s3_bucket = args.key + '.hex7.com'
data_tree = '../data/' + args.key
s3_list = []
if args.debug:
  print('data_tree: ', data_tree)
  print('s3_bucket: ', s3_bucket)
  print('args: ', args)


if args.upload:
  for path, dirs, files in os.walk(data_tree):
    for file in files:
      if file != '.DS_Store':
        print('processing: ', file)
        s3_file = os.path.normpath(path + '/' + file).replace('../', '')
        s3_list.append(s3_file)
        local_file = os.path.join(path, file)
        if args.debug:
          print('s3_file: ', s3_file)
          print('local_file: ', local_file)

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
            if args.debug:
              print('response: ', rez_upload)
        else:
          print('EXISTS. skipping.')
        finally:
          print()

if not os.path.exists('tmp/'):
  os.makedirs('tmp/')

j_s3_list = json.dumps(s3_list, indent=4)

if args.debug:
  print('s3_list: ', s3_list)
  print('j_s3_list: ', j_s3_list)

with open("tmp/s3_list.json", "w") as outfile:
    outfile.write(j_s3_list)

rez_upload = s3_client.upload_file(Filename='tmp/s3_list.json',
                                   Bucket=s3_bucket,
                                   Key='s3_list.json',
                                   ExtraArgs = {'ACL': 'public-read' })

if args.debug:
  print('upload json: ', rez_upload)
