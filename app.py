import os
import sys
import pickle
import sqlite3
import pandas as pd
from flask import Flask, render_template, request, jsonify

# Import recommendation engine and text cleaner
from book_recommander import hybrid_recommendation_for_ui, clean_input, safe_val
from clean_text_util import clean_author_name, clean_description_english

app = Flask(__name__)

# --- Data Caching on Server Startup ---
print("=" * 60)
print("Initializing The Next Page Book Recommender...")
print("=" * 60)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "books.db")
POPULAR_CSV_PATH = os.path.join(BASE_DIR, "popular_books.csv")
BOOKS_FINAL_CSV_PATH = os.path.join(BASE_DIR, "books_final.csv")
BOOKS_FINAL_GZ_PATH = os.path.join(BASE_DIR, "books_final.csv.gz")
TFIDF_PKL_PATH = os.path.join(BASE_DIR, "tfidf_matrix.pkl")

# 1. Load Data (from SQLite database if available, else CSV/GZ fallback)
# Memory-optimized: only load columns needed by the web UI
needed_cols = ['author', 'desc', 'genre', 'img', 'isbn', 'rating', 'reviews', 'totalratings', 'cleaned_title']

if os.path.exists(DB_PATH):
    print(f"[1/3] Loading database '{DB_PATH}' via SQLite...")
    conn = sqlite3.connect(DB_PATH)
    popular_df = pd.read_sql("SELECT * FROM popular_books", conn)
    print(f"[2/3] Loading books catalogue from SQLite ({len(popular_df)} popular volumes)...")
    cols_sql = ", ".join(needed_cols + (['title'] if 'title' in needed_cols else []))
    books_df = pd.read_sql(f"SELECT {cols_sql} FROM books ORDER BY id ASC", conn)
    conn.close()
else:
    print("[1/3] Loading popular_books.csv...")
    popular_df = pd.read_csv(POPULAR_CSV_PATH)
    corpus_source = BOOKS_FINAL_CSV_PATH if os.path.exists(BOOKS_FINAL_CSV_PATH) else BOOKS_FINAL_GZ_PATH
    print(f"[2/3] Loading books corpus from {os.path.basename(corpus_source)} (90,134 records)...")
    books_df = pd.read_csv(corpus_source, usecols=needed_cols)

popular_books_list = []
all_popular_genres = set()

for _, row in popular_df.iterrows():
    genres_raw = str(row.get('genre', '')).split(',') if pd.notna(row.get('genre')) else []
    genres_clean = [g.strip() for g in genres_raw if g.strip()]
    for g in genres_clean[:3]:
        all_popular_genres.add(g)

    b_title = str(row.get('title', 'Untitled'))
    b_author = clean_author_name(str(row.get('author', 'Unknown Author')))
    b_desc = clean_description_english(str(row.get('desc', '')), b_title, b_author, ", ".join(genres_clean))

    popular_books_list.append({
        "title": b_title,
        "author": b_author,
        "rating": safe_val(row.get('rating'), "N/A"),
        "reviews": safe_val(row.get('reviews'), 0),
        "totalratings": safe_val(row.get('totalratings'), 0),
        "image_url": safe_val(row.get('img'), ""),
        "genre": genres_clean,
        "genre_str": ", ".join(genres_clean[:3]),
        "isbn": safe_val(row.get('isbn'), ""),
        "desc": b_desc
    })

popular_genres = sorted(list(all_popular_genres))

# Ensure title column is available for display
if 'title' not in books_df.columns:
    books_df['title'] = books_df['cleaned_title'].fillna('').astype(str).str.title()

# Pre-cache cleaned titles and authors for ultra-fast autocomplete
search_cache = [
    {
        "cleaned": str(row_clean),
        "title": str(row_title),
        "author": clean_author_name(str(row_author))
    }
    for row_clean, row_title, row_author in zip(
        books_df['cleaned_title'].fillna(''),
        books_df['title'].fillna(''),
        books_df['author'].fillna('Unknown')
    )
]

# 3. Load TF-IDF Feature Matrix
print("[3/3] Loading tfidf_matrix.pkl...")
with open(TFIDF_PKL_PATH, "rb") as f:
    tfidf_matrix = pickle.load(f)

print("=" * 60)
print(f"Engine Ready! Loaded {len(popular_books_list)} popular books, {len(books_df)} corpus books.")
print("=" * 60)


@app.route("/")
def index():
    """Page 1: Curated showcase of Top 50 Most Popular Books."""
    return render_template(
        "popular.html",
        books=popular_books_list,
        genres=popular_genres,
        total_count=len(popular_books_list),
        active_page="popular"
    )


@app.route("/recommend", methods=["GET", "POST"])
def recommend():
    """Page 2: Interactive Book Recommendation Studio."""
    query = request.args.get("q", "").strip()
    if request.method == "POST":
        query = request.form.get("title", "").strip() or query

    result = None
    error_message = None

    if query:
        payload = hybrid_recommendation_for_ui(query, books_df, tfidf_matrix, top_n=5)
        if "error" in payload:
            error_message = payload["error"]
        else:
            result = payload

    # Sample inspiration titles for quick 1-click discovery
    curated_samples = [
        "A Game of Thrones",
        "The Wise Man's Fear",
        "Harry Potter and the Deathly Hallows",
        "Godaan",
        "The House of Hades",
        "Gitanjali"
    ]

    return render_template(
        "recommend.html",
        query=query,
        result=result,
        error_message=error_message,
        samples=curated_samples,
        active_page="recommend"
    )


@app.route("/api/autocomplete")
def autocomplete():
    """Ultra-fast live typeahead suggestions for search queries."""
    q = request.args.get("q", "").strip().lower()
    if not q or len(q) < 2:
        return jsonify([])

    cleaned_q = clean_input(q)
    matches = []

    # Fast substring scan over pre-indexed title cache
    for item in search_cache:
        if cleaned_q in item["cleaned"]:
            matches.append({
                "title": item["title"],
                "author": item["author"]
            })
            if len(matches) >= 8:
                break

    return jsonify(matches)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
