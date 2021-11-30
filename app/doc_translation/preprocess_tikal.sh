#!/bin/bash
set -ex
SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd ${SCRIPT_DIR}
moses=./moses-scripts/
fa=./fast_align/build/
fa_models=czeng20-train.sentence
src=cs
tgt=en


./tikal.sh -fc okf_openxml@img -xm -seg config/defaultSegmentation.srx ${1} -sl ${src} -to ${1}.mos
perl -CSDA -plE 's/[^\S\t]/ /g' ${1}.mos.${src}  > ${1}.mos.${src}.spaces
perl m4loc/xliff/remove_markup.pm < ${1}.mos.${src}.spaces > ${1}.txt

