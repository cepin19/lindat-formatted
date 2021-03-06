#!/bin/bash
SRCLANG=${1:-"en"}
TGTLANG=${2:-"cs"}
url="https://lindat.mff.cuni.cz//services/translation/api/v2/models/${SRCLANG}-${TGTLANG}"
url="localhost:5000/api/v2/languages/"
cat /dev/stdin | while read -r line; do
    
    line=`echo $line | sed "s/'/\\\\\'/g"`
    
   if [ -z "$line" ]; then
	echo "$line"
   else 
    curl \
        -X POST "${url}?src=${SRCLANG}&tgt=${TGTLANG}" \
        -H "accept: text/plain" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "input_text=${line}"
    fi
done


