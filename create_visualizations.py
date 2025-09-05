import pandas as pd
import re
from nltk.corpus import stopwords
import nltk
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import sys

# Set default encoding to UTF-8
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except TypeError:
        import functools
        print = functools.partial(print, encoding="utf-8")

# --- Ensure NLTK data is available ---
try:
    stopwords.words('english')
except LookupError:
    nltk.download('stopwords', quiet=True)

# --- Text Cleaning Function (re-used from previous script) ---
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
    # Add custom words to ignore in the word cloud
    stop_words.update(['kakadu', 'park'])
    words = text.split()
    filtered_words = [word for word in words if word not in stop_words]
    return ' '.join(filtered_words)

# --- Main Visualization ---
try:
    print("Reading and cleaning data for visualization...")
    df = pd.read_excel("KAKADU.xlsx")
    df.rename(columns={'wiI7pd': 'review'}, inplace=True)
    df['review_cleaned'] = df['review'].apply(clean_text)

    # Combine all cleaned reviews into a single text block
    all_reviews_text = " ".join(review for review in df['review_cleaned'].dropna())

    print("Generating Word Cloud...")
    # Generate the word cloud
    wordcloud = WordCloud(
        width=1200,
        height=600,
        background_color='white',
        colormap='viridis',
        collocations=False # To avoid ngram collocations
    ).generate(all_reviews_text)

    # Save the word cloud to a file
    plt.figure(figsize=(12, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.savefig("kakadu_wordcloud.png")
    print("\nSuccessfully generated and saved 'kakadu_wordcloud.png'")
    print("This image file contains the word cloud visualization.")

except ImportError:
    print("\nCould not generate visualizations.")
    print("Please ensure 'wordcloud' and 'matplotlib' are installed: pip install wordcloud matplotlib")
except Exception as e:
    print(f"\nAn error occurred: {e}")
