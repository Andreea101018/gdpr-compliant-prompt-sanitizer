# ============================================================
# STRICT SPAN-LEVEL EVALUATION (ML Only)
# ============================================================

import numpy as np
from pathlib import Path
from datasets import load_dataset
from transformers import (
    BertTokenizerFast,
    BertForTokenClassification,
    DataCollatorForTokenClassification,
    Trainer,
)


# ------------------------------------------------------------
# Helper: Convert BIO sequence to spans
# ------------------------------------------------------------

def bio_to_spans(labels):
    spans = []
    start = None
    entity = None

    for i, label in enumerate(labels):
        if label.startswith("B-"):
            if start is not None:
                spans.append((entity, start, i))
            entity = label[2:]
            start = i

        elif label.startswith("I-"):
            continue

        else:  # O
            if start is not None:
                spans.append((entity, start, i))
                start = None
                entity = None

    if start is not None:
        spans.append((entity, start, len(labels)))

    return spans


# ------------------------------------------------------------
# Load Model
# ------------------------------------------------------------

dataset = load_dataset("ai4privacy/pii-masking-400k")
val_data = dataset["validation"]

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "bert/ml-ner-model-v1/checkpoint-61035"

model = BertForTokenClassification.from_pretrained(str(MODEL_PATH))
tokenizer = BertTokenizerFast.from_pretrained(str(MODEL_PATH))

id2label = model.config.id2label
label2id = model.config.label2id


def encode_example(example):
    encoding = tokenizer(
        example["mbert_tokens"],
        is_split_into_words=True,
        truncation=True,
        max_length=512,
    )

    word_ids = encoding.word_ids()
    labels = []
    previous_word_idx = None

    for word_idx in word_ids:
        if word_idx is None:
            labels.append(-100)
        elif word_idx != previous_word_idx:
            label = example["mbert_token_classes"][word_idx]
            labels.append(label2id[label])
        else:
            labels.append(-100)

        previous_word_idx = word_idx

    encoding["labels"] = labels
    return encoding


tokenized_val = val_data.map(
    encode_example,
    remove_columns=val_data.column_names
)

trainer = Trainer(model=model)
predictions = trainer.predict(tokenized_val)

logits, labels, _ = predictions
preds = np.argmax(logits, axis=-1)

TP = FP = FN = 0

for pred_seq, label_seq in zip(preds, labels):

    pred_labels = []
    true_labels = []

    for p, l in zip(pred_seq, label_seq):
        if l != -100:
            pred_labels.append(id2label[int(p)])
            true_labels.append(id2label[int(l)])

    pred_spans = set(bio_to_spans(pred_labels))
    true_spans = set(bio_to_spans(true_labels))

    TP += len(pred_spans & true_spans)
    FP += len(pred_spans - true_spans)
    FN += len(true_spans - pred_spans)

precision = TP / (TP + FP + 1e-8)
recall = TP / (TP + FN + 1e-8)
f1 = 2 * precision * recall / (precision + recall + 1e-8)

print("\nSTRICT SPAN EVALUATION")
print("Precision:", precision)
print("Recall:", recall)
print("F1:", f1)