from jinja2 import Environment, FileSystemLoader
from argparse import ArgumentParser
from flask import Flask, jsonify
from datetime import datetime
from zoneinfo import ZoneInfo
import subprocess
import json
import re


app = Flask(__name__)

parser = ArgumentParser()
parser.add_argument('--source', type=str, default='claude', help='select ai source')
parser.add_argument('--debug', action='store_true', help='debug')
parser.add_argument('--template', type=str, default='ai.html', help='jinja template')
parser.add_argument('--port', type=int, default=80, help='tcp port')
args = parser.parse_args()


filename = 'thinktanks.' + args.source + '.txt'
datemade = ' - '.join(datetime.now(ZoneInfo('US/Eastern')).isoformat().split('T'))
revision = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()

if args.debug:
  print('filename: ', filename)
  print('datemade: ', datemade)
  print('revision: ', revision)
  print('port: ', args.port)
  print('debug: ', args.debug)


def get_tank_raw(filename, debug=False):
  with open(filename) as file:
    tank_raw = [line.rstrip() for line in file]

  if args.debug:
    print()
    print('tank_raw: ', tank_raw)
    print()

  return tank_raw


def dd(name, score, location='none', desc1='none', desc2='none', x='none', p='none', q='none'):
  print()
  print('name: ', name)
  print('score: ', score)
  print('location: ', location)
  print('desq1: ', desc1)
  print('desq2: ', desc2)
  print('x: ', x)
  print('p: ', p)
  print('q: ', p)
  print()


def get_tank_data(tank_raw, source, debug=False):
  header = tank_raw[0] + '<br>' + tank_raw[1]
  tank_data = {}

  if source == 'claude':
    for item in tank_raw[2:]:
      x = item.rsplit('-', 1)
      p = x[0].split('(')
      location = ' '.join(p[1:]).replace(')', '')
      score = x[1]
      name = score + '_' + p[0]
      tank_data[name] = {}
      tank_data[name]['score'] = score
      tank_data[name]['location'] = location
      tank_data[name]['desc'] = 'none'
      dd(name=name, location=location, score=score, x=x, p=p)

  elif source == 'gemini':
    for item in tank_raw[2:]:
      x = item.rsplit('-', 1)
      if len(x) > 1:
        q = x[1].split(')')
        desc1 = q[0]
        p = x[0].split(':')
        location = p[0].replace('(', '<br>(')
        q = p[1].split(')')
        score = q[0].replace('(','<br>')
        if len(q) > 1:
          desc2 = q[1]
        else:
          desc2 = ' none '
        name = score + '_' + p[0]
        tank_data[name] = {}
        tank_data[name]['score'] = score
        tank_data[name]['location'] = location
        tank_data[name]['desc'] = desc1 + ' : ' + desc2
        dd(name=name, location=location, score=score, desc1=desc1, desc2=desc2, x=x, p=p)

  else:
    raise Exception('possible wrong source:  ', + source)

  if args.debug:
    print()
    print('header: ', header)
    print('tank_data: ', tank_data)
    print()

  return header, tank_data


tank_raw = get_tank_raw(filename=filename,
                        debug=args.debug)

header, tank_data = get_tank_data(tank_raw=tank_raw,
                                  source=args.source,
                                  debug=args.debug)

tank_list = sorted(tank_data)

if args.debug:
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
  j2_template = j2_env.get_template(args.template)
  j2_rendered = j2_template.render(header=header,
                                   tank_raw=tank_raw,
                                   tank_data=tank_data,
                                   tank_list=tank_list,
                                   revision=revision,
                                   datemade=datemade,
                                   source=args.source,
                                   port=args.port,
                                   debug=args.debug)

  with open(args.source + '.html', 'w') as f:
    f.write(j2_rendered)

  return j2_rendered


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=args.port)
