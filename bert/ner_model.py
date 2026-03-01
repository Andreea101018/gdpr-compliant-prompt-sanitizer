import os
import torch
from transformers import BertTokenizerFast, BertForTokenClassification
import transformers
transformers.logging.set_verbosity_error()


class TransformerNER:
    def __init__(self, model_path=None):
        if model_path is None:
            base = os.path.dirname(__file__)
            model_path = os.path.join(base, "ml-ner-model")

        self.tokenizer = BertTokenizerFast.from_pretrained(
            model_path,
            local_files_only=True
        )
        self.model = BertForTokenClassification.from_pretrained(
            model_path,
            local_files_only=True
        )
        self.model.eval()

        self.id2label = self.model.config.id2label

    def predict(self, text):
        """
        Returns exact (entity_text, entity_label) pairs using offset mapping.
        """

        encoding = self.tokenizer(
            text,
            return_offsets_mapping=True,
            return_tensors="pt",
            truncation=True
        )

        # Extract offsets BEFORE removing them
        offsets = encoding["offset_mapping"][0].tolist()

        # REMOVE offset_mapping before passing to model ❗❗
        model_inputs = {k: v for k, v in encoding.items() if k != "offset_mapping"}

        with torch.no_grad():
            logits = self.model(**model_inputs).logits

        pred_ids = torch.argmax(logits, dim=-1)[0].tolist()

        input_ids = encoding["input_ids"][0]

        entities = []
        current_label = None
        current_start = None
        current_end = None

        for (token_id, pred_id, (start, end)) in zip(input_ids, pred_ids, offsets):

            token = self.tokenizer.convert_ids_to_tokens([token_id])[0]

            # Skip CLS/SEP
            if token in ("[CLS]", "[SEP]"):
                continue

            label = self.id2label[pred_id]

            # BIO decoding
            if "-" in label:
                prefix, label = label.split("-", 1)
            else:
                prefix, label = "O", "O"

            if prefix == "B":
                # Flush previous entity
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

        # Flush last entity
        if current_label:
            span = text[current_start:current_end]
            entities.append((span, current_label))

        return entities
