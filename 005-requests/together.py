from argparse import ArgumentParser
from random import randrange
import requests
import hashlib
import base64
import os
import re


#model = 'stabilityai/stable-diffusion-xl-base-1.0'
#model = 'codellama/CodeLlama-70b-Python-hf'

parser = ArgumentParser()
parser.add_argument('--debug', action='store_true', help='debug')
parser.add_argument('--verbose', action='store_true', help='debug verbose')
parser.add_argument('--keyin', type=str, default='art', nargs='+', help='key for image')
parser.add_argument('--data', type=str, default='art', help='data dir path')
parser.add_argument('--count', type=int, default=1, help='num images')
parser.add_argument('--seed', type=int, default=randrange(10000), help='num images')
parser.add_argument('--width', type=int, default=1024, help='num images')
parser.add_argument('--height', type=int, default=1024, help='num images')
parser.add_argument('--steps', type=int, default=40, help='num images')
parser.add_argument('--model',
                    type=str,
                    default='stabilityai/stable-diffusion-xl-base-1.0',
                    help='select ai model')
parser.add_argument('--endpoint',
                    type=str,
                    default='https://api.together.xyz/v1/completions',
                    help='key for image')
args = parser.parse_args()


token = os.environ.get('META_KEY')
if not token:
  raise RuntimeError('Set META_KEY environment variable to api bearer token.')


key = ' '.join(args.keyin)
file_ext = '.jpg'
file_out = re.sub('[^0-9a-zA-Z]+', '_', key)
dir_out = '/' + file_out + '/'
model_out = re.sub('[^0-9a-zA-Z]+', '_', args.model)
bearer_token = "Bearer " + token
data_dir = '../data/' + args.data + '/'
if not os.path.exists(data_dir):
  os.makedirs(data_dir)

j_post = { "prompt": key,
           "negative_prompt": "",
           "model": args.model,
           "width": args.width,
           "height": args.height,
           "steps": args.steps,
           "n": args.count,
           "seed": args.seed }

j_headers = { "Authorization": bearer_token }

if args.debug:
  print('------> model :', args.model)
  print('------> endpoint: ', args.endpoint)
  print('------> width: ', args.width)
  print('------> height: ', args.height)
  print('------> steps: ', args.steps)
  print('------> count: ', args.count)
  print('------> seed: ', args.seed)
  print('------> j_headers: ', j_headers)
  print('------> j_post: ', j_headers)
  print('------> debug: ', args.debug)
  print('------> verbose: ', args.verbose)
  print('------> keyin: ', args.keyin)
  print('------> key: ', key)

r = requests.post(args.endpoint,
                  json=j_post,
                  headers=j_headers)

if r.status_code != 200:
  raise RuntimeError('API Response ' + str(r.status_code) + ' body: ' + r.text)
else:
  print()
  print('------> API Success: ', r.status_code)
  print()

if not os.path.exists(data_dir):
  os.makedirs(data_dir)
if not os.path.exists(data_dir + dir_out):
  os.makedirs(data_dir + dir_out)

j = r.json()
images = j.get('choices')

if args.debug:
  print('------> object: ', j.get('object'))
  print('------> created: ', j.get('created'))
  print('------> id: ', j.get('id'))
  if args.verbose:
    print('--------> images: ', images)
    print('--------> r: ', r.text)
    print('--------> j: ', j)

print()
print('--------> processing file: ' + file_out)
print()

image_count = 0
for image_dict in images:
  image_count = image_count + 1
  print('--------> processing image: ', image_count)
  for image_b in image_dict.values():
    if isinstance(image_b, str):

      image_data = base64.b64decode(image_b)
      md5Hash = hashlib.md5(image_data)
      md5Hashed = md5Hash.hexdigest()

      if args.debug:
        print('----------> md5hash: ', md5Hash)
        print('----------> md5hashed: ', md5Hashed)
        if args.verbose:
          print('----------> image data: ', image_data)

      image_file = [ data_dir,
                     dir_out,
                     file_out,
                     '_',
                     md5Hashed,
                     file_ext ]

      print('----------> writing: %r ' % ''.join(image_file))
      with open(''.join(image_file), "wb") as fh:
        fh.write(image_data)

print('------------> current ', image_count, ' images processed')
