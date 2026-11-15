# 📚 The Next Page — Discover What to Read Next

A fast, simple, and intelligent book recommendation system powered by TF-IDF vectorization and cosine similarity over a catalog of **90,134 books**, featuring a curated collection of the **Top 50 Most Popular Books**.

---

## 📑 Table of Contents
1. [Project Overview](#project-overview)
2. [Dataset Analysis & Column Breakdown](#dataset-analysis--column-breakdown)
   - [File 1: `popular_books.csv` (Curated Top 50 Bestsellers)](#file-1-popular_bookscsv)
   - [File 2: `books_final.csv` (Full Corpus of 90,134 Titles)](#file-2-books_finalcsv)
   - [Structural Comparison & Observations](#structural-comparison--observations)
3. [English Normalization & Multilingual Handling](#english-normalization--multilingual-handling)
4. [Machine Learning & Recommendation Architecture](#machine-learning--recommendation-architecture)
5. [Visual Design System: "Athenaeum Editorial"](#visual-design-system-athenaeum-editorial)
6. [Application Architecture & Pages](#application-architecture--pages)
7. [Quickstart & Execution Guide](#quickstart--execution-guide)

---

## 1. Project Overview

This application serves two distinct literary experiences:
1. **The Popular Books Showcase (`/`)**: Displays the 50 most celebrated and widely-rated volumes from Goodreads records. Readers can sort by rating, review count, or popularity, filter by literary genre (Fantasy, Young Adult, Fiction, Romance, Sci-Fi, Classics, etc.), read full English synopses, and jump straight to companion recommendations.
2. **The Companion Recommender Studio (`/recommend`)**: Readers input any book title they have enjoyed. The system cleanses and matches the query against the expanded corpus of **90,134 titles**, calculates cosine distance over 15,000 TF-IDF features (combining author style, themes, synopsis, and genres), and presents the **top 5 companion books to read next**.

---

## 2. Dataset Analysis & Column Breakdown

### File 1: `popular_books.csv`
- **Total Records:** 50 rows
- **Total Columns:** 13 columns
- **Purpose:** Curated showcase of top-rated, widely read global bestsellers (total ratings ranging from 97,450 to 2,984,351 per volume).

| # | Column Name | Data Type | Null Count | Description & Role | Sample Value |
|---|-------------|-----------|------------|--------------------|--------------|
| 1 | `author` | `string` | 0 | Primary author name(s). Cleaned and Latinized into standard English. | `J.K. Rowling, Mary GrandPre` |
| 2 | `desc` | `string` | 0 | Full synopsis / book blurb from Goodreads. Clean English prose with zero encoding artifacts. | *Harry Potter is leaving Privet Drive for the last time...* |
| 3 | `genre` | `string` | 0 | Comma-delimited list of categorized genres. | `Fantasy,Young Adult,Fiction` |
| 4 | `img` | `string` (URL) | 0 | Direct image URL to Goodreads CDN book cover. | `https://i.gr-assets.com/.../1361039443l/136251.jpg` |
| 5 | `isbn` | `string` | 13 | Standard Book Identifier (ISBN-10 or ISBN-13). | `0545010225` |
| 6 | `rating` | `float64` | 0 | Average community rating (Scale: 1.0 to 5.0). Range: `4.22` to `4.62`. | `4.62` |
| 7 | `reviews` | `int64` | 0 | Written reader reviews (Range: `10,516` to `68,974`). | `68,974` |
| 8 | `totalratings` | `int64` | 0 | Total community ratings cast (Range: `97,450` to `2,984,351`). | `2,984,351` |
| 9 | `title` | `string` | 0 | Official book title in proper casing and punctuation. | `Harry Potter and the Deathly Hallows` |
| 10 | `cleaned_author` | `string` | 0 | Lowercased, alphanumeric normalized author string for search indexing. | `jk rowling mary grandpre` |
| 11 | `cleaned_desc` | `string` | 0 | Lowercased, punctuation-stripped synopsis text for NLP modeling. | *harry potter is leaving privet drive for the last time...* |
| 12 | `cleaned_title` | `string` | 0 | Lowercased, punctuation-stripped title used for fuzzy matching. | `harry potter and the deathly hallows` |
| 13 | `cleaned_genre` | `string` | 0 | Space-delimited lowercase genre tokens. | `fantasy youngadult fiction` |

---

### File 2: `books_final.csv`
- **Total Records:** 90,134 rows (expanded with 156 additional iconic titles)
- **Total Columns:** 13 columns
- **Purpose:** Full literary repository used by the TF-IDF feature matrix (`tfidf_matrix.pkl`) to compute cosine similarities.

| # | Column Name | Data Type | Null Count | Description & Role | Sample Value |
|---|-------------|-----------|------------|--------------------|--------------|
| 1 | `author` | `string` | 0 | Original author attribution. Dynamically converted to English text on retrieval. | `George R.R. Martin` / `Munshi Premchand` |
| 2 | `desc` | `string` | 4,180 | Raw synopsis. Missing or foreign language entries are dynamically handled. | *Here is the first volume in George R. R. Martin’s...* |
| 3 | `genre` | `string` | 8,014 | Goodreads community tags/genres. | `Fantasy,Fiction,Epic Fantasy` |
| 4 | `img` | `string` (URL) | 0 | Direct book cover CDN link. | `https://i.gr-assets.com/.../1001053.jpg` |
| 5 | `isbn` | `string` | 11,470 | ISBN identifier. | `0553103547` |
| 6 | `rating` | `float64` | 0 | Community rating (Scale: 1.0 to 5.0). Mean across corpus: ~3.91. | `4.44` |
| 7 | `reviews` | `int64` | 0 | Text review count. | `54,037` |
| 8 | `totalratings` | `int64` | 0 | Total ratings count. | `2,097,707` |
| 9 | `cleaned_author`| `string` | 676 | Lowercased, alphanumeric normalized author string. | `george rr martin` |
| 10 | `cleaned_desc` | `string` | 4,977 | Cleaned synopsis text. | *here is the first volume in george r r martins...* |
| 11 | `cleaned_title`| `string` | 0 | Normalized title used for index matching. **0 nulls across all 90,134 rows.** | `a game of thrones` / `godaan` |
| 12 | `cleaned_genre`| `string` | 8,014 | Cleaned space-delimited genre tokens. | `fantasy fiction epicfantasy` |
| 13 | `tags` | `string` | 0 | **NLP Feature Bag**: Concatenation of cleaned author, genre, title, and synopsis tokens used to generate the TF-IDF matrix. | `george rr martin fantasy fiction epicfantasy...` |

---

## 3. English Normalization & Multilingual Handling

To ensure all author names and book descriptions are consistently presented in readable English across both pages:

1. **Mojibake Decoding & ASCII Punctuation Normalization:**
   * Removes Windows-1252 / double-encoded UTF-8 corruption (*e.g.*, `â€™` -> `'`, `â€œ` -> `"`, `â€”` -> `—`, `â€¦` -> `...`).
   * Decodes HTML entities and normalizes spacing around punctuation.

2. **Author Name Latinization:**
   * Converts all accented Latin letters to their standard English base letters via NFKD decomposition (*e.g.*, `Mary GrandPré` -> `Mary GrandPre`, `Carlos Ruiz Zafón` -> `Carlos Ruiz Zafon`, `Antoine de Saint-Exupéry` -> `Antoine de Saint-Exupery`, `Benjamin Alire Sáenz` -> `Benjamin Alire Saenz`).
   * Strips out non-Latin scripts (Cyrillic, Greek, Arabic, Chinese characters) while retaining the English transliteration.

3. **Foreign Description Detection & English Synthesis:**
   * Scans descriptions against common language stopword distributions (French, Spanish, German, Dutch, Italian, Serbian, Portuguese).
   * For descriptions detected as non-English or missing: generates an English overview specifying the book's title, cleaned author, and primary literary genres.

---

## 4. Machine Learning & Recommendation Architecture

```
User Query: "A Game of Thrones"
      │
      ▼
Text Normalization (regex: lowercase, strip punctuation)
      │
      ▼
Exact / Substring Match (O(1) dictionary / hash lookup)
      │──> If fuzzy: difflib.get_close_matches (cutoff 0.55)
      ▼
Matched Corpus Row Index in 90,134 Corpus (e.g. Row 15,482)
      │
      ▼
Extract Target Vector from tfidf_matrix (CSR Matrix 1 x 15,000)
      │
      ▼
Cosine Similarity: target_vector • tfidf_matrix.T (Flatten to array of size 90,134)
      │
      ▼
Argsort Top 5 Indices (excluding target index)
      │
      ▼
Hydrate UI Payload (English Title, English Author, Genre, Rating, Cover, ISBN, Thematic Similarity %)
```

- **Speed:** Sub-50ms recommendation computation using sparse matrix vector products.
- **Explainability:** Returns matching engine tag, similarity percentages, and shared genre tags.

---

## 5. Visual Design System: "Athenaeum Editorial"

We deliberately reject standard digital clichés (such as neon blue-to-purple SaaS gradients, generic Inter typography, nested card-in-card layouts, and unreadable gray-on-gray captions).

### Color Palette
- **Parchment Cream (`#FBF8F2`):** Primary background offering warm, non-glare reading comfort.
- **Warm Antique White (`#FFFFFF`):** High-contrast card surface.
- **Deep Iron Gall Ink (`#1C1917`):** Primary editorial text, offering sharp typographic contrast.
- **Stone Grey (`#78716C`):** Subdued secondary metadata, ISBNs, and subtle dividers.
- **Oxblood Leather (`#8B2635`):** Hero accents, search triggers, active navigation markers, and bookmarks.
- **Amber Ochre (`#C5832B`):** Star ratings, similarity percentages, and curated badges.
- **Rule Border Tint (`#E7E0D3`):** Fine hairline borders inspired by bookbinding rules.

### Typography
- **Primary Display & Headings:** `Cormorant Garamond` (Google Fonts serif) — classical proportions reminiscent of letterpress typography.
- **UI, Metadata & Search:** `Plus Jakarta Sans` — ultra-legible, refined geometric sans-serif for responsive search inputs, ratings, and filters.

### Memorable Design Element
- **The Book Spine Ribbon & Bibliographic Index:**
  Each recommended title is presented like an archival catalogue card featuring a leather-toned spine accent, Roman numeral catalogue indexing (`I`, `II`, `III`, `IV`, `V`), a real-time similarity affinity badge, and an interactive "Curator's Slip" to preview the full Goodreads synopsis.

---

## 6. Application Architecture & Pages

- **`app.py`**: Flask server handling routes, initial model caching, and API endpoints.
- **`clean_text_util.py`**: English text normalization, mojibake decoding, author Latinization, and foreign language handling.
- **`book_recommander.py`**: Cleaned, high-performance recommendation module accepting `(title, books_df, tfidf_matrix, top_n=5)`.
- **`templates/`**:
  - `base.html`: Common layout, navigational header with book-ribbon aesthetics, responsive footer.
  - `popular.html` (Page 1): Curated 50 most popular books with instant genre filtering, sorting (ratings / reviews / readers), synopsis modal, and one-click "Find Companions" bridge.
  - `recommend.html` (Page 2): Real-time book search studio with live autocomplete across 90,134+ titles, active target book inspector, and 5 companion cards.
- **`static/`**:
  - `css/style.css`: Bespoke typography, paper grain textures, book-cover drop shadows, and responsive grid.
  - `js/main.js`: Typeahead search suggestions, live genre filters, modal drawer triggers.

---

## 7. Quickstart & Execution Guide

### Local Development
```powershell
python app.py
```
Open your browser at `http://127.0.0.1:5000`.

---

## 8. How to Publish & Make Your Website Live

To allow anyone on the internet to visit your website, choose either of the two methods below:

### Method A: Free 24/7 Cloud Hosting on Hugging Face Spaces (Recommended)
Because this recommendation engine runs machine learning vectors over 90,134 books, it requires ~588 MB of RAM. **Hugging Face Spaces** provides **16 GB RAM for free** (compared to Render's 512 MB limit):

1. Create a free account at [huggingface.co](https://huggingface.co).
2. Click **New Space** $\rightarrow$ Name it `the-next-page` $\rightarrow$ Select **Docker** (Blank).
3. Clone your Space repository locally or push your files:
   ```powershell
   git init
   git add .
   git commit -m "Deploy The Next Page"
   git remote add origin https://huggingface.co/spaces/<YOUR_USERNAME>/the-next-page
   git push -u origin main
   ```
4. Hugging Face will automatically build the `Dockerfile` and give you a permanent live public link:
   `https://<YOUR_USERNAME>-the-next-page.hf.space`

---

### Method B: Instant Public Link via LocalTunnel (Live in 30 Seconds)
If you want to quickly share your running website with friends or teachers right now:

1. Keep your website running:
   ```powershell
   python app.py
   ```
2. Open a second PowerShell terminal in this folder and run:
   ```powershell
   npx localtunnel --port 5000
   ```
3. It will give you a public URL (e.g. `https://cool-book-finder.loca.lt`). Anyone in the world can open that URL directly on their phone, laptop, or tablet!
#   t h e - n e x t - p a g e  
 