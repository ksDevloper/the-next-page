import os
import sqlite3
import pandas as pd
from clean_text_util import clean_author_name, clean_description_english

DB_PATH = "books.db"

def build_database():
    print("=" * 60)
    print("Building SQLite Database for The Next Page...")
    print("=" * 60)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Popular Books Table
    print("\n[1/2] Creating 'popular_books' table...")
    pop_df = pd.read_csv("popular_books.csv")
    pop_df["author"] = pop_df["author"].apply(clean_author_name)
    pop_df.to_sql("popular_books", conn, if_exists="replace", index=False)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_pop_title ON popular_books(title);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_pop_rating ON popular_books(rating);")
    print(f"-> Successfully saved {len(pop_df)} popular books to SQLite table 'popular_books'.")

    # 2. Main Books Corpus Table
    print("\n[2/2] Creating 'books' table from books_final.csv (90,134 records)...")
    print("Reading books_final.csv...")
    books_df = pd.read_csv("books_final.csv")
    
    # Ensure title column exists
    if 'title' not in books_df.columns:
        books_df['title'] = books_df['cleaned_title'].fillna('').astype(str).str.title()

    # Clean author names
    books_df['author'] = books_df['author'].fillna('Unknown Author').apply(clean_author_name)

    # Add primary key 'id' matching 0-indexed row position for TF-IDF matrix alignment
    books_df['id'] = range(len(books_df))

    # Reorder columns with 'id' first
    cols = ['id'] + [c for c in books_df.columns if c != 'id']
    books_df = books_df[cols]

    print("Writing to SQLite (this may take a few seconds)...")
    books_df.to_sql("books", conn, if_exists="replace", index=False)

    # Create indexes for ultra-fast lookups
    print("Creating database indexes...")
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_books_id ON books(id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_books_cleaned_title ON books(cleaned_title);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_books_title ON books(title);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_books_author ON books(author);")

    conn.commit()
    conn.close()

    db_size_mb = os.path.getsize(DB_PATH) / (1024 * 1024)
    print("=" * 60)
    print(f"DATABASE READY: '{DB_PATH}' created ({db_size_mb:.2f} MB)")
    print("Tables created:")
    print("  - popular_books (50 rows, indexed)")
    print("  - books (90,134 rows, indexed by id, cleaned_title, title, author)")
    print("=" * 60)

if __name__ == "__main__":
    build_database()
