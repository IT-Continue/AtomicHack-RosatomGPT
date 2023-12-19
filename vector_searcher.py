from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

STOP_WORDS = []


def send_question(question: str, path: str) -> str:
    # Content list
    answers = []

    # Answers writing
    for filename in os.listdir(path):
        file_path = os.path.join(f"./{path}", filename)

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                answers.append(file.read())
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")

    # Create TF-IDF vectorizer
    tfidf_vectorizer = TfidfVectorizer(ngram_range=(1, 3))

    # Convert text to TF-IDF vectors
    tfidf_matrix = tfidf_vectorizer.fit_transform(answers)

    # Query processing
    query = question

    # Convert query to TF-IDF vector
    query_vector = tfidf_vectorizer.transform([query])

    # Calculating cosine similarity between query and content
    cosine_similarities = cosine_similarity(query_vector, tfidf_matrix)

    # Get content indexes with sort similarities
    doc_indices = cosine_similarities.argsort()[0][::-1]

    # Send the best answer
    n = 0
    for item in answers[doc_indices[n]].split(" "):
        for stop_word in STOP_WORDS:
            if stop_word in item.lower():
                n += 1
                break

    most_similar_ans = answers[doc_indices[n]]

    return most_similar_ans


def main():
    print(send_question("В какие сроки заключается договор по итогам неконкурентной закупки?", "content"))


if __name__ == "__main__":
    main()
