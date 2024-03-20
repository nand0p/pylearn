import requests
import hashlib
import base64
import os
import re


key = 'ants feeding on carcass'
#key = 'scorpion crawling out of a shoe'
#key = 'man pushing elephant on a swing'
#key = 'helicopter crashing landing into very large hot tub'
#key = 'cathedral scene spanish civil war shootout'
#key = 'railroad scene spanish civil war shootout'
#key = 'desert scene with camels and robotic vultures'



model = 'stabilityai/stable-diffusion-xl-base-1.0'
#model = 'codellama/CodeLlama-70b-Python-hf'


token = os.environ.get('META_KEY')
if not token:
  raise RuntimeError('Set META_KEY environment variable to api bearer token.')

endpoint = 'https://api.together.xyz/v1/completions'
data_dir = '../data/art/'
file_out = re.sub('[^0-9a-zA-Z]+', '_', key)
dir_out = '/' + file_out + '/'
model_out = re.sub('[^0-9a-zA-Z]+', '_', model)
bearer_token = "Bearer " + token
debug = False

if not os.path.exists(data_dir):
  os.makedirs(data_dir)
if not os.path.exists(data_dir + model_out):
  os.makedirs(data_dir + model_out)
if not os.path.exists(data_dir + model_out + dir_out):
  os.makedirs(data_dir + model_out + dir_out)

j_post = { "model": model,
           "prompt": key,
           "negative_prompt": "",
           "width": 1024,
           "height": 1024,
           "steps": 40,
           "n": 4, 
           "seed": 472 }

j_headers = { "Authorization": bearer_token }

r = requests.post(endpoint,
                  json=j_post,
                  headers=j_headers)

j = r.json()
images = j.get('choices')

if debug:
  print('r: ', r.text)
  print('j: ', j)
  print('images: ', images)

print(j.get('id'),
      j.get('object'),
      j.get('created'),
      j.get('model'),
      j.get('prompt'),
      j.get('logprobs'),
      j.get('index'))

print('--> processing: ' + file_out)
for image_dict in images:
  for image_b in image_dict.values():

    if debug:
      print(image_b)

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
                     '.png' ]

      print('----> writing: %r ' % ''.join(image_file))
      with open(''.join(image_file), "wb") as fh:
        fh.write(image_data)
