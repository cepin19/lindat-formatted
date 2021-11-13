#!/bin/bash
set -ex
SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd ${SCRIPT_DIR}
moses=./moses-scripts/
fa=./fast_align/build/
fa_models=czeng20-train.sentence
src=cs
tgt=en

$moses/scripts/tokenizer/tokenizer.perl -l ${src} -no-escape < ${1}.txt > ${1}.tok
./tikal.sh -fc okf_openxml -xm -seg config/defaultSegmentation.srx ${1} -sl  ${src}  -to ${1}.mos.tok
perl -CSDA -plE 's/[^\S\t]/ /g' ${1}.mos.tok.${src}  > ${1}.mos.tok.${src}.spaces

$moses/scripts/tokenizer/tokenizer.perl -l ${tgt} -no-escape < ${1}.target > ${1}.target.tok

#paste ${1}.tok ${1}.target.tok | sed 's/\t/ ||| /g' | sed 's/^ ||| $/empt ||| empt/g'| python3 $fa/force_align.py $fa_models.fwd_params $fa_models.fwd_err $fa_models.rev_params $fa_models.rev_err > ${1}.align


