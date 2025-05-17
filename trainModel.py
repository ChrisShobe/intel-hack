from transformers import T5Tokenizer, T5ForConditionalGeneration, Trainer, TrainingArguments
from datasets import load_dataset
import pandas as pd

# === Load dataset using pandas to ensure proper parsing ===
df = pd.read_csv("train.csv", delimiter=",")  # Use the correct delimiter
print("Columns:", df.columns.tolist())  # Should print individual column names

from datasets import Dataset
dataset = Dataset.from_pandas(df)
dataset = dataset.shuffle(seed=42).select(range(1000))

# === Load tokenizer and model ===
tokenizer = T5Tokenizer.from_pretrained("t5-small")
model = T5ForConditionalGeneration.from_pretrained("t5-small")

# === Preprocessing function ===
def preprocess(example):
    # Create input text
    input_text = example["instruction"]
    
    # Handle responses
    responses = example["responses"]
    if pd.notna(responses) and responses != "[]":
        try:
            responses = eval(responses) if isinstance(responses, str) else responses
            if isinstance(responses, list) and responses:
                input_text += " Previous responses: " + " ".join(responses)
        except:
            pass
    
    # Tokenize
    model_input = tokenizer(
        input_text,
        padding="max_length",
        truncation=True,
        max_length=512
    )
    
    label_text = example.get("next_response", "")
    if label_text is None:
        label_text = ""
    label = tokenizer(
        text_target=label_text,
        padding="max_length",
        truncation=True,
        max_length=64
    )
    model_input["labels"] = label["input_ids"]
    return model_input

# === Tokenize ===
tokenized_dataset = dataset.map(
    preprocess,
    batched=True,                # Enable batching
    batch_size=32,               # You can adjust this (e.g., 32 or 64)
    remove_columns=dataset.column_names
)
# === Training ===
training_args = TrainingArguments(
    output_dir="models/slide2quiz-model",
    num_train_epochs=1,
    per_device_train_batch_size=8,
    logging_steps=2,
    save_strategy="epoch",
    report_to="none"
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    tokenizer=tokenizer
)

trainer.train()
trainer.save_model("models/slide2quiz-model")
tokenizer.save_pretrained("models/slide2quiz-model")

print("✅ Training complete")