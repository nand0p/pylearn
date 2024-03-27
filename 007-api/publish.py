from jinja2 import Environment, FileSystemLoader
from argparse import ArgumentParser
from flask import Flask, jsonify
from datetime import datetime
from zoneinfo import ZoneInfo
import subprocess
import boto3

parser = ArgumentParser()
parser.add_argument('--bucket', type=str, default='tanks.hex7.com', help='s3 bucket')
parser.add_argument('--template', type=str, default='index.html', help='s3 bucket')
parser.add_argument('--debug', action='store_true', help='debug')
args = parser.parse_args()
datemade = ' - '.join(datetime.now(ZoneInfo('US/Eastern')).isoformat().split('T'))
revision = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()
filenames = [ 'index.html', 'gemini.html', 'claude.html' ]

j2_file_loader = FileSystemLoader('templates')
j2_env = Environment(loader=j2_file_loader)
j2_template = j2_env.get_template(args.template)
j2_rendered = j2_template.render(revision=revision,
                                 datemade=datemade,
                                 debug=args.debug)

with open(args.template, 'w') as f:
  f.write(j2_rendered)

if args.debug:
  print('index: ', j2_rendered)

print('uploading: ', args.bucket, filenames)

extra_args = {'ACL': 'public-read',
              'ContentType': 'text/html',
              'ContentLanguage': 'en-US'}

s3_client = boto3.client('s3')
for f in filenames:
  try:
    s3_client.upload_file(Filename=f,
                          Key=f,
                          Bucket=args.bucket,
                          ExtraArgs=extra_args)
  except:
    raise Exception('cannot write file to s3: ' + f)

print('SUCCESS: ', args.bucket, filenames)
