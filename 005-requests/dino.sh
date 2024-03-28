#!/bin/bash -ex

COUNT_KEY=50
COUNT_GENERATION=2
SOURCE_FILE=dino2.txt
TOTAL=0

echo running with ${SOURCE_FILE} count: ${COUNT_KEY} gen: ${COUNT_GENERATION}

cat ${SOURCE_FILE} | while read KEY; do
  echo "---> iterating ${KEY}"

  for COUNT in $(seq ${COUNT_KEY}); do
    echo "----> iterating ${COUNT}"
    python together.py --debug --data dino --count ${COUNT_GENERATION} --key ${KEY}
    TOTAL=$((${TOTAL}+${COUNT_GENERATION}))
    echo "------------> current subtotal ${TOTAL}"
  done

  echo "--> current total ${TOTAL}"

done
echo
echo
echo "success. ${TOTAL} images created."
echo
