from __future__ import unicode_literals, print_function
from spacy import displacy
from pathlib import Path
from tqdm import tqdm
import random
import spacy
import json
import os
from tika import parser

n_iter = 1000
nlp = spacy.load('en_core_web_sm')
output_dir = Path(os.path.join(os.path.dirname(__file__), 'model'))


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


def test_model(txt):
    print("Loading from", output_dir)
    ner_model = spacy.load(output_dir)
    doc = ner_model(txt)
    print('Entities', [(ent.text, ent.label_) for ent in doc.ents])
    spacy.displacy.serve(doc, style='ent', host='127.0.0.1', port=5000)

def pdftotext():
    #FILE_DIR = os.path.abspath('C:/Users/Andreea/Desktop/byte/uploads')
    raw = parser.from_file('C:/Users/Andreea/Desktop/byte/uploads/')
    # print(raw['content'])
    file1 = open('C:/Users/Andreea/Desktop/byte/uploads/out.txt', "w", encoding='utf-8')
    str(raw).replace('x', '')
    file1.write(str(raw).replace('\\n', '\n'))
    file1.close()


if __name__ == '__main__':
    #TRAIN_DATA = load_training_data()
    #x = random.randint(0, len(TRAIN_DATA) - 1)
    #test_model(TRAIN_DATA[x][0])
    test_model("""The study was conducted with the support of the Human Resources /
    (HR) department of a large German insurance company. HR sent email
    messages to the insurance agents. The message included the study's invitation,
    link to an online test, personal login code, and consent to use
    nine-month-later sales performance. 389 agents were contacted, 165
    followed the link, and 114 finished the online test. One year later, HR
    provided sales performance data (29% participation rate). Of the 114
    participants, 15 were female. Participant mean age was 44.6 (SD =
    9.3) years, having a job tenure of 12.5 years (SD= 8.2 years).""")