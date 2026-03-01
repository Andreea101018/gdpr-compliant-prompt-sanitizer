# ============================================================
# FULL PROTOTYPE EVALUATION (sanitize pipeline)
# ============================================================

from datasets import load_dataset
from evaluation.span_eval import bio_to_spans
from your_pipeline_module import sanitize  # <-- adjust import


dataset = load_dataset("ai4privacy/pii-masking-400k")
val_data = dataset["validation"].select(range(2000))


def extract_gold_spans(example):
    return bio_to_spans(example["mbert_token_classes"])


def extract_predicted_spans(text):
    masked = sanitize(text)
    # Implement span extraction from masked output
    # Depends on your masking format
    return []


TP = FP = FN = 0

for example in val_data:
    text = " ".join(example["mbert_tokens"])

    gold_spans = set(extract_gold_spans(example))
    pred_spans = set(extract_predicted_spans(text))

    TP += len(gold_spans & pred_spans)
    FP += len(pred_spans - gold_spans)
    FN += len(gold_spans - pred_spans)

precision = TP / (TP + FP + 1e-8)
recall = TP / (TP + FN + 1e-8)
f1 = 2 * precision * recall / (precision + recall + 1e-8)

print("\nPROTOTYPE EVALUATION")
print("Precision:", precision)
print("Recall:", recall)
print("F1:", f1)