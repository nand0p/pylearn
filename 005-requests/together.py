from random import randrange
import requests
import hashlib
import base64
import os
import re


key = 'pierced tattooed jeweled gangster octopus'


model = 'stabilityai/stable-diffusion-xl-base-1.0'
#model = 'codellama/CodeLlama-70b-Python-hf'


token = os.environ.get('META_KEY')
if not token:
  raise RuntimeError('Set META_KEY environment variable to api bearer token.')

endpoint = 'https://api.together.xyz/v1/completions'
data_dir = '../data/art/'
file_ext = '.jpg'
file_out = re.sub('[^0-9a-zA-Z]+', '_', key)
dir_out = '/' + file_out + '/'
model_out = re.sub('[^0-9a-zA-Z]+', '_', model)
bearer_token = "Bearer " + token
seed = randrange(10000)
width = 1024
height = 1024
steps = 40
count = 3
debug = False

j_post = { "model": model,
           "prompt": key,
           "negative_prompt": "",
           "width": width,
           "height": height,
           "steps": steps,
           "n": count,
           "seed": seed }

j_headers = { "Authorization": bearer_token }

r = requests.post(endpoint,
                  json=j_post,
                  headers=j_headers)

if r.status_code != 200:
  raise RuntimeError('API Response ' + str(r.status_code) + ' body: ' + r.text)
else:
  print()
  print('API Success: ', r.status_code)
  print()

if not os.path.exists(data_dir):
  os.makedirs(data_dir)
if not os.path.exists(data_dir + model_out):
  os.makedirs(data_dir + model_out)
if not os.path.exists(data_dir + model_out + dir_out):
  os.makedirs(data_dir + model_out + dir_out)

j = r.json()
images = j.get('choices')

if debug:
  print('r: ', r.text)
  print('j: ', j)
  print('images: ', images)

print('endpoint: ', endpoint)
print('model: ', model)
print('id: ', j.get('id'))
print('object: ', j.get('object'))
print('created: ', j.get('created'))
print()
print('seed: ', seed)
print('count: ', count)
print('steps: ', steps)
print('width: ', width)
print('height: ', height)
print()
print('--> processing: ' + file_out)
print()

for image_dict in images:
  for image_b in image_dict.values():
    if isinstance(image_b, str):

      image_data = base64.b64decode(image_b)
      md5Hash = hashlib.md5(image_data)
      md5Hashed = md5Hash.hexdigest()

      image_file = [ data_dir,
                     model_out,
                     dir_out,
                     file_out,
                     '_',
                     md5Hashed,
                     file_ext ]

      print('----> writing: %r ' % ''.join(image_file))
      with open(''.join(image_file), "wb") as fh:
        fh.write(image_data)
