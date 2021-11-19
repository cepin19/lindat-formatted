from flask import Blueprint, render_template, request, current_app, url_for, redirect,flash
import  os
from .forms import TranslateForm
from app.model_settings import models as models_conf
from app.model_settings import languages
from werkzeug.utils import secure_filename
import subprocess
from app.main.translate import translate_document
from flask import send_from_directory

bp = Blueprint('main', __name__)
ALLOWED_EXTENSIONS=["docx"]
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/upload/<name>')
def download_file(name):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], name)

@bp.route('/upload', methods=['GET', 'POST'])
def translate_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            t=translate_document(request.form["source"],request.form["target"],os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            if t is None:
                return  ("error")

            return (os.path.join("/upload/",t))
            #return redirect(url_for('main.download_file', name=filename))

        else:
            print ("errror")



@bp.route('/', methods=['GET'])
def index():
    if _request_wants_json():
        return redirect(url_for('api.root_root_resource'))
    form = TranslateForm()
    form.models.choices = url_for_choices()
    form.models.default = form.models.choices[0][0]

    sources = list(sorted(filter(lambda l: l.targets, languages.languages.values()),
                          key=lambda l: l.title))

    default_src = sources[0]

    form.target.choices = sorted([(l.name, l.title) for l in default_src.targets],
                                 key=lambda x: x[1])

    form.source.choices = [(url_for('api.languages_language_item', language=l.name), l.title) for
                           l in sources]
    form.source.data = form.source.choices[0][0]
    return render_template('index.html', form=form,
                           file_size_limit=current_app.config['MAX_CONTENT_LENGTH'])


@bp.route('/docs', methods=['GET'])
def docs():
    return render_template('docs.html', file_size_limit=current_app.config['MAX_CONTENT_LENGTH'])


def url_for_choices():
    return list(map(lambda model:
                    (url_for('api.models_model_item', model=model.model), model.title),
                    models_conf.get_models()))


def _request_wants_json():
    best = request.accept_mimetypes \
        .best_match(['application/json', 'text/html'])
    return best == 'application/json' and \
           request.accept_mimetypes[best] > \
           request.accept_mimetypes['text/html']
