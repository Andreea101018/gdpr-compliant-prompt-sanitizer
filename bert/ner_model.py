import os
import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification
import transformers

transformers.logging.set_verbosity_error()


class TransformerNER:
    def __init__(self, model_path=None):

        if model_path is None:
            base = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(base, "models", "pii_xlmr_final")

        model_path = os.path.abspath(model_path)

        self.tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            local_files_only=True
        )

        self.model = AutoModelForTokenClassification.from_pretrained(
            model_path,
            local_files_only=True
        )

        self.model.eval()

        if torch.cuda.is_available():
            self.model.to("cuda")

        self.id2label = self.model.config.id2label

    def predict(self, text):

        encoding = self.tokenizer(
            text,
            return_offsets_mapping=True,
            return_tensors="pt",
            truncation=True
        )

        offsets = encoding["offset_mapping"][0].tolist()
        model_inputs = {k: v for k, v in encoding.items() if k != "offset_mapping"}

        if torch.cuda.is_available():
            model_inputs = {k: v.to("cuda") for k, v in model_inputs.items()}

        with torch.no_grad():
            logits = self.model(**model_inputs).logits

        pred_ids = torch.argmax(logits, dim=-1)[0].tolist()
        input_ids = encoding["input_ids"][0]

        entities = []
        current_label = None
        current_start = None
        current_end = None

        for token_id, pred_id, (start, end) in zip(input_ids, pred_ids, offsets):

            label = self.id2label[pred_id]

            if "-" in label:
                prefix, label = label.split("-", 1)
            else:
                prefix, label = "O", "O"

            if prefix == "B":
                if current_label:
                    span = text[current_start:current_end]
                    entities.append((span, current_label))

                current_label = label
                current_start = start
                current_end = end

            elif prefix == "I" and label == current_label:
                current_end = end

            else:
                if current_label:
                    span = text[current_start:current_end]
                    entities.append((span, current_label))

                current_label = None
                current_start = None
                current_end = None

        if current_label:
            span = text[current_start:current_end]
            entities.append((span, current_label))

        return entities