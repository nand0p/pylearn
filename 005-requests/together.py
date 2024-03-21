from random import randrange
import requests
import hashlib
import base64
import os
import re

key = 'abstract world map in shiny metallic style'
#key = 'demonic children of hell praying in graveyard'
#key = 'hard rain inner city working girls'
#key = 'exploding star in abstract metallic style'
#key = 'metallic robots arguing in a bright abstract style'
#key = 'bright shiny metallic robots eating meat on a train'
#key = 'bright shiny metallic robots eating meat on top of a mountain trail'
#key = 'dinosaurs epic battle in abstract bright metallic style'
#key = 'robots eating humans in abstract bright metallic style'
#key = 'construction robots in abstract bright metallic sytle'
#key = 'desert landscape in abstract bright metallic style'
#key = 'inner-city landscape right at night in abstract bright metallic style'
#key = 'post-apocalyptic landscape in abstract bright metallic style'
#key = 'post-apocalyptic landscape'
#key = 'nuclear winter'
#key = 'climate change predictions'
#key = 'tell the truth'
#key = 'fight the law'
#key = 'speaking up'
#key = 'motorcycle wipeout flying sparks'
#key = 'city noise at night in hard rain'
#key = 'imagining despair in yellow'
#key = 'the moment of enlightenment'
#key = 'shimmering sunset over the gates of hell'
#key = 'blind ambition in red'  # XXX
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
file_ext = '.jpg'
file_out = re.sub('[^0-9a-zA-Z]+', '_', key)
dir_out = '/' + file_out + '/'
model_out = re.sub('[^0-9a-zA-Z]+', '_', model)
bearer_token = "Bearer " + token
debug = False

j_post = { "model": model,
           "prompt": key,
           "negative_prompt": "",
           "width": 1024,
           "height": 1024,
           "steps": 40,
           "n": 4, 
           "seed": randrange(1000) }

j_headers = { "Authorization": bearer_token }

r = requests.post(endpoint,
                  json=j_post,
                  headers=j_headers)

if r.status_code != 200:
  raise RuntimeError('API Response ' + str(r.status_code) + ' body: ' + r.text)
else:
  print('API Success: ', r.status_code)

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

print('id: ', j.get('id'))
print('object: ', j.get('object'))
print('created: ', j.get('created'))
print('model: ', j.get('model'))
print('prompt: ', j.get('prompt'))
print('logprobs: ', j.get('logprobs'))
print('index: ', j.get('index'))

print('--> processing: ' + file_out)
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
