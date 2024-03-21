import boto3
import time
import json
import sys
import os

data_tree='../data'
s3_bucket='art.hex7.com'
s3_client = boto3.client('s3')
s3_file = 'tmp/s3_list.json'
debug = False
upload_images = True


with open(s3_file, "r") as infile:
  s3_list = json.load(infile)

print('make index html file')
html = '<html><body><h1>art.hex7.com</h1>'

print('html images')
for image in s3_list:
  html += '<img src=http://art.hex7.com.s3-website-us-east-1.amazonaws.com/' + image + '><br>'

print('html footer')
html += '</body></html>'

print('write index html file')
with open("tmp/index.html", "w") as outfile:
    outfile.write(html)

extra_args = {'ACL': 'public-read',
              'ContentType': 'text/html',
              'ContentLanguage': 'en-US'}

print('upload index html file')
rez_upload = s3_client.upload_file(Filename='tmp/index.html',
                                   Bucket=s3_bucket,
                                   Key='index.html',
                                   ExtraArgs=extra_args)

if debug:
  print(rez_upload)