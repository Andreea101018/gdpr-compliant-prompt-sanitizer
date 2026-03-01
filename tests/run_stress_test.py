import sys
import os
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from bert.integrated_sanitizer import sanitize

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(BASE_DIR, "sanitizer_stress_test.json")

with open(json_path, "r", encoding="utf-8") as f:
    tests = json.load(f)

for item in tests:
    result = sanitize(item["text"])
    print("="*60)
    print("INPUT :", item["text"])
    print("OUTPUT:", result["sanitized"])
    print("NOTICES:", result["notices"])