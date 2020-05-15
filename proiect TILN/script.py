from flask import Flask, render_template, url_for, request, flash, redirect
import os
import spacy
from spacy import displacy
from pathlib import Path
import json
import random
from tqdm import tqdm
from werkzeug.utils import secure_filename
from tika import parser

n_iter = 1000
nlp = spacy.load('en_core_web_sm')
output_dir = Path(os.path.join(os.path.dirname(__file__), 'model'))

from flaskext.markdown import Markdown

TEMPLATE_DIR = os.path.abspath('C:/Users/Andreea/Desktop/proiect TILN/templates')
STATIC_DIR = os.path.abspath('C:/Users/Andreea/Desktop/proiect TILN/static')
UPLOAD_FOLDER = 'C:/Users/Andreea/Desktop/proiect TILN/static/pdf'
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
Markdown(app)

HTML_WRAPPER = """<div style="overflow-x: auto; border:1px solid #e6e9ef; border-radius:0.25rem; padding: 1rem">{}</div>"""

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_training_data():
    with open('train_data_texts.txt', encoding='utf-8') as file:
        data = file.readlines()

    with open('train_data_entities.json') as file:
        entities = json.load(file)

    train_data = []
    for i in range(len(data)):
        train_data.append((data[i], entities[str(i)]))
    return train_data


def train_model(train_data):
    global output_dir

    if output_dir.exists():
        ner_model = spacy.load(output_dir)
        print("Loaded model '%s'" % output_dir)
    else:
        ner_model = spacy.blank('en')
        print("Created blank 'en' model")

    if 'ner' not in ner_model.pipe_names:
        ner = ner_model.create_pipe('ner')
        ner_model.add_pipe(ner, last=True)
    else:
        ner = ner_model.get_pipe('ner')

    for _, annotations in train_data:
        for ent in annotations.get('entities'):
            ner.add_label(ent[2])

    other_pipes = [pipe for pipe in ner_model.pipe_names if pipe != 'ner']
    with ner_model.disable_pipes(*other_pipes):  # only train NER
        optimizer = ner_model.begin_training()
        for itn in range(n_iter):
            print(f'Iteration nr: {itn + 1}/{n_iter}')
            random.shuffle(train_data)
            losses = {}
            for text, annotations in tqdm(train_data):
                ner_model.update(
                    [text],  # batch of texts
                    [annotations],  # batch of annotations
                    drop=0.5,  # dropout
                    sgd=optimizer,  # callable to update weights
                    losses=losses)
            print(losses)

    if not output_dir.exists():
        output_dir.mkdir()
    ner_model.to_disk(output_dir)
    print("Saved model to", output_dir)

def pdftotext(filename):
    #FILE_DIR = os.path.abspath('C:/Users/Andreea/Desktop/byte/uploads')
    path = UPLOAD_FOLDER
    #lista = os.listdir(path)
    #text = lista[0]
    file = os.path.join(UPLOAD_FOLDER, filename)
    raw = parser.from_file(file)
    # print(raw['content'])
    file1 = open('C:/Users/Andreea/Desktop/proiect TILN/static/pdf/out.txt', "w", encoding='utf-8')
    str(raw).replace('x', '')
    file1.write(str(raw).replace('\\n', '\n'))
    file1.close()

def extractParticipants(s):
    # START: Participants; END: Instruments || Measurement || Measures || Procedure || Results || Targets and informants
    start = s.find("Participants")
    end1 = s.find("Instruments")
    end2 = s.find("Measurement")
    end3 = s.find("Measures")
    end4 = s.find("Procedure")
    end5 = s.find("Results")
    end6 = s.find("Targets and informants")

    end = 0
    ok = 0

    l = list()
    if end1 != -1:
        l.append(end1)
        ok = 1
    if end2 != -1:
        l.append(end2)
        ok = 1
    if end3 != -1:
        l.append(end3)
        ok = 1
    if end4 != -1:
        l.append(end4)
        ok = 1
    if end5 != -1:
        l.append(end5)
        ok = 1
    if end6 != -1:
        l.append(end6)
        ok = 1

    if ok == 1:
        end = min(l)

    if start == -1 or ok == 0:
        return "Paragraph not found"
    else:
        return s[start:end]


@app.route('/')
def index():
    return render_template('templ.html')

@app.route("/upload", methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            pdftotext(filename)
            return redirect(url_for('index',filename=filename))

    return

@app.route('/extract', methods=["GET", "POST"])
def extract():
    if request.method == 'POST':
        rawtext = request.form['rawtext']
        ner_model = spacy.load(output_dir)
        doc = ner_model(rawtext)
        html = displacy.render(doc, style='ent')
        html = html.replace("\n\n", "\n")
        result = HTML_WRAPPER.format(html)

    return render_template('results.html', rawtext=rawtext, result=result)


@app.route('/extracting', methods=["GET", "POST"])
def extracting():
    if request.method == 'POST':
        with open('static/pdf/out.txt', 'r', encoding="utf8") as file:
            data = file.read()  # .replace('\n', '')
        rawtext=extractParticipants(data)
        #rawtext = request.form['rawtext']
        ner_model = spacy.load(output_dir)
        doc = ner_model(rawtext)
        html = displacy.render(doc, style='ent')
        html = html.replace("\n\n", "\n")
        result = HTML_WRAPPER.format(html)

    return render_template('results.html', rawtext=rawtext, result=result)

if __name__ == '__main__':
    app.run(debug=True)
