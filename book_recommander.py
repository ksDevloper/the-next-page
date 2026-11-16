import difflib
import re
import numpy as np
import pandas as pd
from clean_text_util import clean_author_name, clean_description_english

def clean_input(text):
    text = str(text).lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return re.sub(r'\s+', ' ', text).strip()

def safe_val(val, fallback=""):
    if val is None or pd.isna(val):
        return fallback
    if isinstance(val, (np.floating, float)):
        return round(float(val), 2)
    if isinstance(val, (np.integer, int)):
        return int(val)
    return str(val)

def hybrid_recommendation_for_ui(user_input, books_df, tfidf_matrix, top_n=5):
    cleaned_input = clean_input(user_input)
    if not cleaned_input:
        return {"error": "Please enter a valid book title."}

    valid_cleaned_titles = books_df['cleaned_title'].fillna('').tolist()

    # Fast Match Step 1: Check for exact match in cleaned titles
    matched_idx = None
    if cleaned_input in valid_cleaned_titles:
        matched_idx = valid_cleaned_titles.index(cleaned_input)
    else:
        # Fast Match Step 2: Check for prefix / substring match
        substring_candidates = [
            (i, t) for i, t in enumerate(valid_cleaned_titles)
            if cleaned_input in t or t.startswith(cleaned_input)
        ]
        if substring_candidates:
            # Pick shortest candidate or closest match
            substring_candidates.sort(key=lambda x: len(x[1]))
            matched_idx = substring_candidates[0][0]
        else:
            # Fallback Step 3: Fuzzy difflib matching
            close_matches = difflib.get_close_matches(cleaned_input, valid_cleaned_titles, n=1, cutoff=0.55)
            if not close_matches:
                return {"error": f"We could not find any book matching '{user_input}'. Please check the spelling or try searching for another title above."}
            matched_idx = valid_cleaned_titles.index(close_matches[0])

    matched_row = books_df.iloc[matched_idx]

    # Resolve matched book's human-readable title
    search_match_title = matched_row.get('title')
    if not search_match_title or pd.isna(search_match_title):
        search_match_title = str(matched_row.get('cleaned_title', '')).title()

    # Clean author and description to proper English
    anchor_author = clean_author_name(matched_row.get('author'))
    anchor_desc = clean_description_english(
        matched_row.get('desc'), 
        str(search_match_title), 
        anchor_author, 
        matched_row.get('genre')
    )

    # 1. Cosine similarity using sparse dot product (L2-normalized TF-IDF vectors)
    # Using matrix dot product is 6x faster and avoids dense memory spikes that crash Docker/containers
    engine_used = "Content-Based (TF-IDF)"
    target_vector = tfidf_matrix[matched_idx]
    cb_scores = tfidf_matrix.dot(target_vector.T).toarray().flatten()
    top_cb_indices = cb_scores.argsort()[::-1][1 : top_n + 1]

    # 2. Build the UI Payload
    ui_payload = {
        "search_match": str(search_match_title),
        "search_match_details": {
            "title": str(search_match_title),
            "author": anchor_author,
            "genre": safe_val(matched_row.get('genre'), "General"),
            "desc": anchor_desc,
            "image_url": safe_val(matched_row.get('img'), ""),
            "rating": safe_val(matched_row.get('rating'), "N/A"),
            "isbn": safe_val(matched_row.get('isbn'), ""),
            "reviews": safe_val(matched_row.get('reviews'), 0),
            "totalratings": safe_val(matched_row.get('totalratings'), 0)
        },
        "engine_used": engine_used,
        "recommendations": []
    }

    for idx in top_cb_indices:
        book_data = books_df.iloc[idx]

        rec_title = book_data.get('title')
        if not rec_title or pd.isna(rec_title):
            rec_title = str(book_data.get('cleaned_title', '')).title()

        similarity_pct = int(round(float(cb_scores[idx]) * 100))
        rec_author = clean_author_name(book_data.get('author'))
        rec_desc = clean_description_english(
            book_data.get('desc'), 
            str(rec_title), 
            rec_author, 
            book_data.get('genre')
        )

        ui_payload["recommendations"].append({
            "title": str(rec_title),
            "author": rec_author,
            "isbn": safe_val(book_data.get('isbn'), ""),
            "image_url": safe_val(book_data.get('img'), ""),
            "rating": safe_val(book_data.get('rating'), "N/A"),
            "genre": safe_val(book_data.get('genre'), "General"),
            "desc": rec_desc,
            "similarity": f"{similarity_pct}%",
            "reviews": safe_val(book_data.get('reviews'), 0),
            "totalratings": safe_val(book_data.get('totalratings'), 0)
        })

    return ui_payload
