import json
import os

DATASET_PATH = "evaluation_dataset.json"

def log_sample(sample):
    if os.path.exists(DATASET_PATH):
        with open(DATASET_PATH, "r") as f:
            data = json.load(f)
    else:
        data = []

    data.append(sample)

    with open(DATASET_PATH, "w") as f:
        json.dump(data, f, indent=4)