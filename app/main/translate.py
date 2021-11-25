#from app.logging_utils import logged
from app.model_settings import models
import requests
import subprocess
import logging
log = logging.getLogger(__name__)


def translate_with_model(model, text, src=None, tgt=None):
    if not text or not text.strip():
        return []
    return model.translate(text, src, tgt)


def translate_from_to(source, target, text):
    models_on_path = models.get_model_list(source, target)
    if not models_on_path:
        raise ValueError('No models found for the given pair')
    translation = []
    for obj in models_on_path:
        translation = translate_with_model(obj['model'], text, obj['src'], obj['tgt'])
        text = ' '.join(translation).replace('\n ', '\n')
    return translation

def translate_document(src,tgt,filename):
    #run tikal and m4loc tools on the source document to convert to xliff and extract raw text
    result = subprocess.run(["/doc_translation//preprocess_tikal.sh", filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    with open(filename+".txt") as src_text_f,open(filename+".target","w") as tgt_text_f:
        src_text=src_text_f.read().rstrip('\n') #??? why do I have do rstrip?
        logging.error("src_text: {}".format(src_text))
        trans=translate_from_to(src.split("/")[-1],tgt,src_text)
        #restore leading newlines
        i=0
        restore_ws=""
        while src_text[i].isspace():restore_ws+=src_text[i]
        trans=restore_ws+''.join(trans)
        logging.error("trans: {}".format(trans))
        #tgt_text_f.write('\n'.join([t.strip() for t in trans if not t.isspace()]))
        tgt_text_f.write(trans)
    result = subprocess.run(["/doc_translation/preprocess_align.sh", filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    with open(filename+".tok") as tok_src_f, open(filename+".target.tok") as tok_tgt_f:
        tok_src=tok_src_f.read().splitlines()
        tok_tgt=tok_tgt_f.read().splitlines()
    logging.error("tok_src: {}".format(tok_src))
    assert len(tok_src)==len(tok_tgt), "Number of lines in source and translation does not match!"
    sentences=[]
    for line_src,line_tgt in zip(tok_src,tok_tgt):
        sentences.append({'src':{'text':line_src.strip()},'tgt':{'text':line_tgt.strip()}})
    json_data={"sentences":sentences}
    print(json_data)
    r=requests.post("http://{}:{}/".format("localhost","9010"),  json=json_data)
    with open(filename+".align","w") as align_file:
        for line in r.json()["sentences"]:
            align_file.write(line["alignment"]+'\n')

    result = subprocess.run(["/doc_translation/postprocess_tikal.sh", filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    #reinsert tags, detokenize, fix
    return filename.replace(".docx",".out.docx")