import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import re
from nltk.corpus import stopwords
import sys
import io

# Set default encoding to UTF-8
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except TypeError:
        import functools
        print = functools.partial(print, encoding="utf-8")

# --- Download necessary NLTK data ---
try:
    stopwords.words('english')
except LookupError:
    #print("Downloading NLTK stopwords...")
    nltk.download('stopwords', quiet=True)
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    #print("Downloading NLTK VADER...")
    nltk.download('vader_lexicon', quiet=True)

# --- Text Cleaning Function ---
def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower() # lowercase
    text = re.sub(r'\[.*?\]', '', text) # remove text in square brackets
    text = re.sub(r'https', '', text) # remove https
    text = re.sub(r'\<.*?>', '', text) # remove html tags
    text = re.sub(r'[^a-zA-Z\s]', '', text) # remove punctuation
    text = re.sub(r'\w*\d\w*', '', text) # remove words containing numbers
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    words = text.split()
    filtered_words = [word for word in words if word not in stop_words]
    return ' '.join(filtered_words)


# --- Main Analysis ---
try:
    df = pd.read_excel("KAKADU.xlsx")

    # --- 1. Data Cleaning and Preparation ---
    df.rename(columns={
        'd4r55': 'author',
        'RfnDt': 'author_info',
        'rsqaWe': 'date',
        'wiI7pd': 'review'
    }, inplace=True)

    # Clean the review text
    df['review_cleaned'] = df['review'].apply(clean_text)

    # --- 2. Sentiment Analysis ---
    sia = SentimentIntensityAnalyzer()
    df['sentiment_scores'] = df['review_cleaned'].apply(lambda x: sia.polarity_scores(x))
    df['sentiment_compound'] = df['sentiment_scores'].apply(lambda x: x['compound'])

    # Classify sentiment
    def classify_sentiment(score):
        if score >= 0.05:
            return 'Positive'
        elif score <= -0.05:
            return 'Negative'
        else:
            return 'Neutral'

    df['sentiment'] = df['sentiment_compound'].apply(classify_sentiment)

    # --- 3. Show Sentiment Results ---
    print("--- Sentiment Analysis Results ---")
    sentiment_counts = df['sentiment'].value_counts()
    print(sentiment_counts.to_markdown(headers=['Sentiment', 'Count']))

    print("\n--- Examples of Negative Reviews ---")
    negative_reviews = df[df['sentiment'] == 'Negative'][['review']].head()
    for i, row in negative_reviews.iterrows():
        print(f"- {row['review'][:200].strip()}...")
        print("-" * 20)

    # --- 4. Topic Modeling ---
    print("\n--- Topic Modeling ---")
    try:
        from sklearn.feature_extraction.text import CountVectorizer
        from sklearn.decomposition import LatentDirichletAllocation

        def print_top_words(model, feature_names, n_top_words):
            print("\nTop Words for Each Topic:")
            for topic_idx, topic in enumerate(model.components_):
                message = f"Topic #{topic_idx+1}: "
                message += ", ".join([feature_names[i]
                                     for i in topic.argsort()[:-n_top_words - 1:-1]])
                print(message)

        # Vectorize the cleaned text data
        vectorizer = CountVectorizer(max_df=0.95, min_df=2, stop_words='english')
        tf = vectorizer.fit_transform(df['review_cleaned'].dropna()) # dropna for safety

        # Apply LDA
        n_topics = 5
        lda = LatentDirichletAllocation(n_components=n_topics, random_state=42, n_jobs=-1)
        lda.fit(tf)

        # Print the topics
        tf_feature_names = vectorizer.get_feature_names_out()
        print_top_words(lda, tf_feature_names, 10)

    except ImportError:
        print("\nCould not perform Topic Modeling. Scikit-learn library not found.")
        print("Please install it with: pip install scikit-learn")
    except Exception as e:
        print(f"\nAn error occurred during Topic Modeling: {e}")


except FileNotFoundError:
    print("Error: KAKADU.xlsx not found. Make sure the file is in the same directory.")
except Exception as e:
    print(f"An error occurred: {e}")
    print("\nPlease ensure you have 'pandas', 'openpyxl', 'nltk' and 'scikit-learn' installed.")