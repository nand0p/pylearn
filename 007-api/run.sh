#!/bin/bash -ex

python api.py --source gemini  # --debug
python api.py --source claude  # --debug
python publish.py --debug
