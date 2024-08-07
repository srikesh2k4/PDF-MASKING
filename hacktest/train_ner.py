import spacy
from spacy.training import Example
from training_data import TRAIN_DATA
import random

def train_spacy(data, iterations):
    nlp = spacy.blank("en")  # Create a blank language class

    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner", last=True)
    else:
        ner = nlp.get_pipe("ner")

    for _, annotations in data:
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])

    optimizer = nlp.begin_training()
    for itn in range(iterations):
        print(f"Starting iteration {itn}")
        random.shuffle(data)
        losses = {}
        for text, annotations in data:
            example = Example.from_dict(nlp.make_doc(text), annotations)
            nlp.update([example], drop=0.5, losses=losses)
        print(losses)

    return nlp

# Train the model
nlp = train_spacy(TRAIN_DATA, 30)

# Save the model
nlp.to_disk("custom_ner_model")

# COPYRIGHTS Kotipalli Srikesh RA221003010979 SRMIST

