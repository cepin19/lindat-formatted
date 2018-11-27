from math import ceil
import os
from flask import Blueprint, render_template, request, session, jsonify, current_app, g, url_for, \
    abort
import numpy as np
import tensorflow as tf
from tensor2tensor.serving import serving_utils
from tensor2tensor.utils import registry, usr_dir
from sentence_splitter import split_text_into_sentences

from .forms import TaskForm, FileForm
from ..logging_utils import logged

usr_dir.import_usr_dir('t2t_usr_dir')
hparams = tf.contrib.training.HParams(data_dir=os.path.expanduser('t2t_data_dir'))

en_cs_problem = registry.problem('translate_encs_wmt_czeng57m32k')
en_cs_problem.get_hparams(hparams)

en_fr_problem = registry.problem('translate_enfr_wmt32k')
en_fr_problem.get_hparams(hparams)


bp = Blueprint('main', __name__)
_choices = [('en-cs', 'English->Czech'), ('cs-en', 'Czech->English'),
            ('en-fr', 'English->French'), ('fr-en', 'French->English')]
_models = list(map(lambda pair: pair[0], _choices))


def model2problem(model):
    if model == 'en-cs' or model == 'cs-en':
        return en_cs_problem
    elif model == 'en-fr' or model == 'fr-en':
        return en_fr_problem
    else:
        return en_cs_problem  # keep en_cs_problem as default


def _translate(model, text):
    if not text or not text.strip():
        return []
    request_fn = serving_utils.make_grpc_request_fn(servable_name=model + '_model', timeout_secs=500,
                                                    # server='localhost:9000')
                                                    server='10.10.51.30:9000')
    lang = model.split('-')[0]
    sentences = []
    newlines_after = []
    for segment in text.split('\n'):
        if segment:
            sentences += split_to_sent_array(segment, lang=lang)
        newlines_after.append(len(sentences)-1)
    outputs = []
    for batch in np.array_split(sentences, ceil(len(sentences)/current_app.config['BATCH_SIZE'])):
        try:
            outputs += list(map(lambda sent_score: sent_score[0],
                        serving_utils.predict(batch.tolist(), model2problem(model), request_fn)))
        except:
            # When tensorflow serving restarts web clients seem to "remember" the channel where
            # the connection have failed. clearing up the session, seems to solve that
            session.clear()
            raise
    for i in newlines_after:
        if i >= 0:
            outputs[i] += '\n'
    return outputs


@bp.route('/', methods=['GET'])
def index():
    if _request_wants_json():
        return api_index()
    form = TaskForm()
    choices = url_for_choices()
    form.lang_pair.choices = choices
    form.lang_pair.default = choices[0][0]
    return render_template('index.html', form=form,
                           file_size_limit=current_app.config['MAX_CONTENT_LENGTH'])


@bp.route('/translate/upload', methods=['GET', 'POST'])
def upload():
    file_form = FileForm()
    choices = url_for_choices()
    file_form.lang_pair.choices = _choices
    file_form.lang_pair.default = _choices[0][0]
    if file_form.validate_on_submit():
        input_text = file_form.data_file.data.read().decode('utf-8')
        return str(_translate(file_form.lang_pair.data, input_text))
    return render_template('upload.html', file_form=file_form,
                           file_size_limit=current_app.config['MAX_CONTENT_LENGTH'])


@bp.route('/docs', methods=['GET'])
def docs():
    return render_template('docs.html', file_size_limit=current_app.config['MAX_CONTENT_LENGTH'])


def url_for_choices():
    return list(map(lambda choice: (url_for('main.run_task', model=choice[0]), choice[1]), _choices))


@logged()
def split_to_sent_array(text, lang):
    return split_text_into_sentences(text=text, language=lang)


def _request_wants_json():
    best = request.accept_mimetypes \
        .best_match(['application/json', 'text/html'])
    return best == 'application/json' and \
        request.accept_mimetypes[best] > \
        request.accept_mimetypes['text/html']


@bp.route('/api', methods=['GET'])
def api_index():
    return jsonify({
        '_links': {
            'self': {'href': url_for('main.api_index')},
            'versions': [{'href': url_for('main.api_index_v1'), 'title': 'Version 1'}],
            'latest': {'href': url_for('main.api_index_v1'), 'title': 'Version 1'}
        },
        '_embedded': {
            'latest': index_v1()
        }
    })


@bp.route('/api/v1')
def api_index_v1():
    return jsonify(index_v1())


def index_v1():
    return {
        '_links': {
            'self': {'href': url_for('main.api_index_v1')},
            'models': {'href': url_for('main.api_models_v1')}
        },
        '_embedded': {
            'models': models()
        }
    }


@bp.route('/api/v1/models', methods=['GET'])
def api_models_v1():
    return jsonify(models())


def models():
    return {
        '_links': {
            'self': url_for('main.api_models_v1'),
            'models': [{'href': choice[0], 'title': choice[1]} for choice in
                               url_for_choices()]
        }
    }


@bp.route('/api/v1/models/<any' + str(tuple(_models)) + ':model>', methods=['POST'])
def run_task(model):
    if request.files and 'input_text' in request.files:
        input_file = request.files.get('input_text')
        if input_file.content_type != 'text/plain':
            abort(415)
        text = input_file.read().decode('utf-8')
    else:
        text = request.form.get('input_text')
    outputs = _translate(model, text)
    if _request_wants_json():
        return jsonify(outputs)
    else:
        return str(outputs)


