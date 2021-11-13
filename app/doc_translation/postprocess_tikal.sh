#!/bin/bash
set -ex
SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd ${SCRIPT_DIR}
moses=./moses-scripts/
fa=./fast_align/build/
m4loc=./m4loc/
fa_models=czeng20-train.sentence
src=cs
tgt=en



perl $m4loc/xliff/reinsert_wordalign.pm ${1}.mos.tok.${src}.spaces ${1}.align < ${1}.target.tok > ${1}.target.mos

#$moses/scripts/tokenizer/detokenizer.perl -l en < ${1}.target.mos > ${1}.target.mos.detok.1
#perl -pi -e 's| (<g.*?>) |\1|g' ${1}.target.mos # remove space after xliff tags added by previous script
#perl -pi -e 's| (<ex.*?>) |\1|g' ${1}.target.mos
#perl -pi -e 's| (<bx.*?>) |\1|g' ${1}.target.mos

#perl -pi -e 's| (</g.*?>) |\1|g' ${1}.target.mos 
#perl -pi -e 's| (</ex.*?>) |\1|g' ${1}.target.mos
#perl -pi -e 's| (</bx.*?>) |\1|g' ${1}.target.mos

#paste  ${1}.mos.en.spaces  ${1}.target.mos | python3 fix_spacing.py > ${1}.target.mos.fix
perl $m4loc/xliff/fix_markup_ws.pm  ${1}.mos.tok.${src}.spaces < ${1}.target.mos > ${1}.target.mos.fix


###TODO: we need to detok as if no xliff markup is there
#$moses/scripts/tokenizer/detokenizer.perl -l ${tgt} < ${1}.target.mos.fix > ${1}.target.mos.detok


#TODO
 paste ${1}.target ${1}.target.mos.fix | python3 fix_fix_markup.py > ${1}.target.mos.detok.fix  #- splits back tokens wrongly joined by fix_markup
sed -i 's/\s*$/ /g' ${1}.target.mos.detok.fix
./tikal.sh -lm ${1} -fc okf_openxml -sl ${src} -ie utf8 -oe utf8 -overtrg -from ${1}.target.mos.detok.fix -seg config/defaultSegmentation.srx

