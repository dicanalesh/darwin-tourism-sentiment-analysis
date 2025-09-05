import pandas as pd
import re
import sys
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

# --- Configuration ---
NUM_CLUSTERS = 6
TOP_TERMS_PER_CLUSTER = 15
EXAMPLE_REVIEWS_PER_CLUSTER = 2

# --- Setup output encoding ---
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except TypeError:
        import functools
        print = functools.partial(print, encoding="utf-8")

# --- Ensure NLTK data ---
try:
    stopwords.words('english')
except LookupError:
    nltk.download('stopwords', quiet=True)

# --- Text Cleaning Function ---
def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'https', '', text)
    text = re.sub(r'\<.*?>', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = re.sub(r'\w*\d\w*', '', text)
    stop_words = set(stopwords.words('english'))
    stop_words.update(['kakadu', 'park'])
    words = text.split()
    filtered_words = [word for word in words if word not in stop_words]
    return ' '.join(filtered_words)

# --- Main Clustering ---
try:
    print("--- Starting Clustering Analysis ---")
    # 1. Load and Clean Data
    df = pd.read_excel("KAKADU.xlsx")
    df.rename(columns={'wiI7pd': 'review'}, inplace=True)
    df['review_cleaned'] = df['review'].apply(clean_text)
    
    # Drop rows where review is empty after cleaning
    df.dropna(subset=['review_cleaned'], inplace=True)
    df = df[df['review_cleaned'].str.strip() != '']

    # 2. Vectorize with TF-IDF
    print("Vectorizing text with TF-IDF...")
    vectorizer = TfidfVectorizer(max_df=0.9, min_df=5, stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(df['review_cleaned'])

    # 3. Apply K-Means Clustering
    print(f"Applying K-Means with {NUM_CLUSTERS} clusters...")
    kmeans = KMeans(n_clusters=NUM_CLUSTERS, random_state=42, n_init=10)
    kmeans.fit(tfidf_matrix)
    df['cluster'] = kmeans.labels_

    # 4. Display Results
    print("\n--- Clustering Results ---")
    order_centroids = kmeans.cluster_centers_.argsort()[:, ::-1]
    terms = vectorizer.get_feature_names_out()

    for i in range(NUM_CLUSTERS):
        cluster_size = df[df['cluster'] == i].shape[0]
        print(f"\n\n--- Cluster #{i+1} ({cluster_size} reviews) ---")
        
        # Print Top Terms
        top_terms = ", ".join([terms[ind] for ind in order_centroids[i, :TOP_TERMS_PER_CLUSTER]])
        print(f"Top Terms: {top_terms}")
        
        # Print Example Reviews
        print("\nExample Reviews:")
        example_reviews = df[df['cluster'] == i]['review'].head(EXAMPLE_REVIEWS_PER_CLUSTER)
        for review_text in example_reviews:
            print(f"- {review_text[:300].strip()}...")
            print("-" * 20)

except ImportError:
    print("\nCould not perform clustering. Ensure scikit-learn is installed.")
except Exception as e:
    print(f"\nAn error occurred: {e}")
