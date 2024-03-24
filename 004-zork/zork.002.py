import json


j_file = 'map.json'
j_out = True
d_out = True
x = 20
y = 20


with open(j_file) as user_file:
  content = user_file.read()
  
map = json.loads(content)

if d_out:
  print(map)

if j_out:
  print(json.dumps(map))
