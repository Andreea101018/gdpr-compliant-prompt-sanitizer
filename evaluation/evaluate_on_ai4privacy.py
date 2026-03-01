# ============================================================
# EXACT REPRODUCTION OF TRAINING EVALUATION
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
from seqeval.metrics import accuracy_score, f1_score


# ------------------------------------------------------------
# 1️⃣ Load Dataset
# ------------------------------------------------------------

dataset = load_dataset("ai4privacy/pii-masking-400k")
val_data = dataset["validation"]

print("Validation size:", len(val_data))


# ------------------------------------------------------------
# 2️⃣ Load Trained Model
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = (BASE_DIR / "bert/ml-ner-model").resolve()

print("Loading model from:", MODEL_PATH)

model = BertForTokenClassification.from_pretrained(
    str(MODEL_PATH),
    local_files_only=True
)

import torch

print("Classifier weight mean:",
      model.classifier.weight.abs().mean().item())

tokenizer = BertTokenizerFast.from_pretrained(
    str(MODEL_PATH),
    local_files_only=True
)

id2label = model.config.id2label
label2id = model.config.label2id


# ------------------------------------------------------------
# 3️⃣ SAME ENCODING AS TRAINING (DO NOT MODIFY)
# ------------------------------------------------------------

def encode_example(example):
    encoding = tokenizer(
        example["mbert_tokens"],
        is_split_into_words=True,
        truncation=True,
        max_length=512,
        padding=False,
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

data_collator = DataCollatorForTokenClassification(tokenizer)


# ------------------------------------------------------------
# 4️⃣ DEFINE SAME METRICS AS TRAINING
# ------------------------------------------------------------

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)

    true_preds = []
    true_labels = []

    for pred_seq, label_seq in zip(preds, labels):
        p_seq, l_seq = [], []

        for p, l in zip(pred_seq, label_seq):
            if l != -100:
                p_seq.append(id2label[int(p)])
                l_seq.append(id2label[int(l)])

        true_preds.append(p_seq)
        true_labels.append(l_seq)

    return {
        "accuracy": accuracy_score(true_labels, true_preds),
        "f1": f1_score(true_labels, true_preds),
    }


# ------------------------------------------------------------
# 5️⃣ RUN EVALUATION (IDENTICAL TO TRAINING)
# ------------------------------------------------------------

trainer = Trainer(
    model=model,
    data_collator=data_collator,
    compute_metrics=compute_metrics,
)

metrics = trainer.evaluate(tokenized_val)

print("\nEvaluation metrics:", metrics)