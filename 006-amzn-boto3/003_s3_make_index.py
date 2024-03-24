import boto3
import time
import json
import sys
import os

key = 'art'

data_tree = '../data/' + key
s3_bucket = key + '.hex7.com'
s3_client = boto3.client('s3')
s3_file = 'tmp/s3_list.json'
debug = False
upload_images = True
extra_args = {'ACL': 'public-read',
              'ContentType': 'text/html',
              'ContentLanguage': 'en-US'}


print()
print('--> verify variables')
print()
print('data_tree: ', data_tree)
print('s3_bucket: ', s3_bucket)
print('s3_file: ', s3_file)
print('debug: ', debug)
print('upload_images: ', upload_images)
print('extra_args: ', extra_args)
print()


print('----> load json data')
with open(s3_file, "r") as infile:
  s3_list = json.load(infile)


print('------> make index html file')
html = '<html><head>'
html += '<link rel="shortcut icon" href="favicon.ico">'
html += '<title>' + key + '.hex7.com</title>'
html += '</head><body><h1>' + key + '.hex7.com</h1>'


print('--------> generate image html')
for image in s3_list:
  image_name = image.split('/')[-1]
  image_keys = image_name.split('_')
  del image_keys[-1]
  html += '<img src=http://' + \
          key + \
          '.hex7.com/' + \
          image + \
          '><br>' + \
          ' '.join(image_keys) + \
          '<p>'


print('----------> generate footer html')
html += '</body></html>'


print('------------> write out index html file')
with open("tmp/index.html", "w") as outfile:
    outfile.write(html)


print('--------------> upload index html file')
rez_upload = s3_client.upload_file(Filename='tmp/index.html',
                                   Bucket=s3_bucket,
                                   Key='index.html',
                                   ExtraArgs=extra_args)
if debug:
  print(rez_upload)

print()
print('success')
print()
