import json
import pandas as pd
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()

# ==========================
# Load Dataset
# ==========================
with open("evaluation_dataset.json") as f:
    raw_data = json.load(f)

formatted = {
    "question": [],
    "contexts": []
}

for sample in raw_data:
    formatted["question"].append(sample["question"])
    formatted["contexts"].append(sample["contexts"])

df = pd.DataFrame(formatted)

# ==========================
# Setup LLM (Groq)
# ==========================
llm = ChatGroq(
    model="llama3-70b-8192",
    temperature=0
)

# ==========================
# Simple Faithfulness Function
# ==========================
def compute_faithfulness(answer, context):
    """
    Computes a simple faithfulness score using cosine similarity
    between the answer and the context text using TF-IDF vectors.
    Returns a score between 0 and 1.
    """
    vectorizer = TfidfVectorizer().fit([answer, context])
    vectors = vectorizer.transform([answer, context])
    sim = cosine_similarity(vectors[0], vectors[1])[0][0]
    return sim

# ==========================
# Generate answers & evaluate faithfulness
# ==========================
generated_answers = []
faithfulness_scores = []

for idx, row in df.iterrows():
    question = row["question"]
    contexts = row["contexts"]
    context_text = " ".join(contexts) if isinstance(contexts, list) else str(contexts)

    prompt = f"Question: {question}\nAnswer using the context: {context_text}"

    # ChatGroq expects a list of messages
    messages = [HumanMessage(content=prompt)]
    generation = llm.generate(messages)  # returns GenerationResult

    # Extract generated answer
    generated_answer = generation.generations[0][0].text.strip()

    # Compute faithfulness score
    faith_score = compute_faithfulness(generated_answer, context_text)

    generated_answers.append(generated_answer)
    faithfulness_scores.append(faith_score)

# ==========================
# Save Results
# ==========================
df["generated_answer"] = generated_answers
df["faithfulness_score"] = faithfulness_scores

df.to_csv("evaluation_results.csv", index=False)

print("\nEvaluation Completed. Sample Results:")
print(df.head())