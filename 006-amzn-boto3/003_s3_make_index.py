from jinja2 import Environment, FileSystemLoader
from argparse import ArgumentParser
from datetime import datetime
from zoneinfo import ZoneInfo
import subprocess
import random
import boto3
import time
import json
import sys
import os

parser = ArgumentParser()
parser.add_argument('--debug', action='store_true', help='debug')
parser.add_argument('--key', type=str, default='art', help='directory')
parser.add_argument('--template', type=str, default='index.html', help='template file')
args = parser.parse_args()


data_tree = '../data/' + args.key
s3_bucket = args.key + '.hex7.com'
s3_client = boto3.client('s3')
s3_file = 'tmp/s3_list.json'
extra_args = {'ACL': 'public-read',
              'ContentType': 'text/html',
              'ContentLanguage': 'en-US'}
datemade = ' - '.join(datetime.now(ZoneInfo('US/Eastern')).isoformat().split('T'))
revision = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()


print()
print('--> verify variables')
print()
print('data_tree: ', data_tree)
print('s3_bucket: ', s3_bucket)
print('s3_file: ', s3_file)
print('debug: ', args.debug)
print('extra_args: ', extra_args)
print()


print('----> load json data')
with open(s3_file, "r") as infile:
  s3_list = json.load(infile)
random.shuffle(s3_list)


print('------> make index html file')
j2_file_loader = FileSystemLoader('templates')
j2_env = Environment(loader=j2_file_loader)
j2_template = j2_env.get_template(args.template)
html = j2_template.render(s3_list=s3_list,
                          key=args.key,
                          datemade=datemade,
                          revision=revision,
                          count=len(s3_list),
                          debug=args.debug)

with open('tmp/' + args.template, 'w') as f:
  f.write(html)

print('--------------> upload index html file')
rez_upload = s3_client.upload_file(Filename='tmp/index.html',
                                   Bucket=s3_bucket,
                                   Key='index.html',
                                   ExtraArgs=extra_args)

if args.debug:
  print(rez_upload)

print()
print('success')
print()
