from jinja2 import Environment, FileSystemLoader
from flask import Flask, jsonify
from datetime import datetime
from zoneinfo import ZoneInfo
import subprocess
import json
import re


filename = 'thinktanks.txt'
debug = False
port = 80
app = Flask(__name__)
datemade = ' - '.join(datetime.now(ZoneInfo('US/Eastern')).isoformat().split('T'))
revision = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()


def get_tank_raw(filename, debug=False):
  with open(filename) as file:
    tank_raw = [line.rstrip() for line in file]

  if debug:
    print()
    print('tank_raw: ', tank_raw)
    print()

  return tank_raw


def get_tank_data(tank_raw, debug=False):
  header = tank_raw[0] + '<br>' + tank_raw[1]
  tank_data = {}
  for item in tank_raw[2:]:
    x = item.rsplit('-', 1)
    p = x[0].split('(')
    country = ' '.join(p[1:]).replace(')', '')
    score = x[1]
    name = score + '_' + p[0]
    tank_data[name] = {}
    tank_data[name]['score'] = score
    tank_data[name]['country'] = country

    if debug:
      print()
      print('x: ', x)
      print('p: ', p)
      print('name: ', name)
      print('country: ', country)
      print('score: ', score)
      print('header: ', header)
      print('tank_data: ', tank_data)
      print()

  return header, tank_data


tank_raw = get_tank_raw(filename=filename, debug=debug)
header, tank_data = get_tank_data(tank_raw=tank_raw, debug=debug)
tank_list = sorted(tank_data)

if debug:
  print('tank_raw: ', tank_raw)
  print('tank_data: ', tank_data)
  print('tank_list: ', tank_list)


@app.route('/tank_raw', methods=['GET'])
def route_tank_raw():
  return jsonify(tank_raw)


@app.route('/tank_list', methods=['GET'])
def route_tank_list():
  return jsonify(tank_list)


@app.route('/tank_data', methods=['GET'])
def route_tank_data():
  return jsonify(tank_data)


@app.route('/t/<tank_name>', methods=['GET'])
def route_get_tank():
  return jsonify(tank_data[tank_name])


@app.route('/', methods=['GET'])
def route_root():
  j2_file_loader = FileSystemLoader('templates')
  j2_env = Environment(loader=j2_file_loader)
  j2_template = j2_env.get_template('index.html')
  j2_rendered = j2_template.render(header=header,
                                   tank_raw=tank_raw,
                                   tank_data=tank_data,
                                   tank_list=tank_list,
                                   revision=revision,
                                   datemade=datemade)

  with open("index.html", "w") as f:
    f.write(j2_rendered)

  return j2_rendered


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
