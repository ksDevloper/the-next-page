# 📚 The Next Page

### Discover What to Read Next.

A fast, simple, and intelligent book recommendation system powered by **TF-IDF Vectorization** and **Cosine Similarity**.

Explore a curated collection of the **Top 50 Most Popular Books** or discover your next favourite read through personalized recommendations from a library of **90,134+ books**.

---

## ✨ Features

- 📖 **Popular Books Showcase:** Explore 50 curated popular books with ratings, reviews, genres, and descriptions.
- 🤖 **Intelligent Recommendations:** Get the top 5 similar books based on your selected title.
- 🔍 **Smart Book Search:** Search across 90,134+ titles with autocomplete suggestions.
- 🧠 **TF-IDF & Cosine Similarity:** Discover books with similar authors, themes, descriptions, and genres.
- 🌍 **English Normalization:** Handle multilingual metadata, text encoding issues, and inconsistent author names.
- 🎭 **Genre Filtering:** Filter books by Fantasy, Fiction, Romance, Young Adult, Sci-Fi, Classics, and more.
- ⭐ **Book Ratings & Popularity:** Sort books by average rating, number of reviews, and total ratings.
- 🖼️ **Book Cover Previews:** View book covers alongside descriptions and recommendations.
- ⚡ **Fast Recommendations:** Efficient similarity computation using sparse matrix operations.

---

## 📑 Table of Contents

1. [Project Overview](#-project-overview)
2. [Application Pages](#-application-pages)
3. [Dataset Analysis](#-dataset-analysis)
4. [Machine Learning Architecture](#-machine-learning-architecture)
5. [Text Normalization](#-text-normalization--multilingual-handling)
6. [Design System](#-design-system)
7. [Project Structure](#-project-structure)
8. [Tech Stack](#-tech-stack)
9. [Installation & Setup](#-installation--setup)
10. [Deployment](#-deployment)
11. [Future Improvements](#-future-improvements)

---

## 📖 Project Overview

**The Next Page** is a book discovery and recommendation platform designed to help readers find their next book without spending hours searching.

The application provides two main experiences:

### 1. Popular Books (`/`)

Explore a curated collection of 50 popular and highly rated books.

Users can:
- Browse popular books.
- Filter books by genre.
- Sort by ratings, reviews, and popularity.
- Read complete book descriptions.
- View book covers and bibliographic information.
- Find similar books with a single click.

### 2. Recommendation Studio (`/recommend`)

Discover new books based on a title you already love.

The recommendation engine searches an expanded corpus of **90,134 books**, identifies the selected title, and calculates similarity scores to recommend the five closest matches.

Each recommendation includes:
- Book title
- Author
- Genre
- Average rating
- Book cover
- ISBN (when available)
- Similarity percentage
- Shared genre information

---

## 📊 Dataset Analysis

The project uses two CSV datasets for different purposes.

### File 1: `popular_books.csv`

<text>**Purpose:** Curated collection of the Top 50 popular books displayed on the homepage.</text>

| Attribute | Details |
|---|---|
| Total Records | 50 |
| Total Columns | 13 |
| Average Rating | 4.22–4.62 |
| Rating Count | 97,450–2,984,351 |
| Missing Values | 13 missing ISBN values |

**Columns:**

| Column | Description |
|---|---|
| `title` | Official book title |
| `author` | Author name(s) |
| `desc` | Book synopsis |
| `genre` | Book genres |
| `img` | Book cover URL |
| `isbn` | ISBN identifier |
| `rating` | Average community rating |
| `reviews` | Number of written reviews |
| `totalratings` | Total number of ratings |
| `cleaned_author` | Normalized author name |
| `cleaned_desc` | Cleaned synopsis |
| `cleaned_title` | Normalized title |
| `cleaned_genre` | Normalized genre tokens |

### File 2: `books_final.csv`

<text>**Purpose:** Main recommendation corpus used by the machine learning engine.</text>

| Attribute | Details |
|---|---|
| Total Records | 90,134 |
| Total Columns | 13 |
| Average Rating | Approximately 3.91 |
| Missing Descriptions | 4,180 |
| Missing Genres | 8,014 |
| Missing ISBN | 11,470 |
| Missing Titles | 0 |

**Columns:**

| Column | Description |
|---|---|
| `title` | Official book title |
| `author` | Original author name |
| `desc` | Raw book synopsis |
| `genre` | Goodreads genres and tags |
| `img` | Book cover URL |
| `isbn` | ISBN identifier |
| `rating` | Average community rating |
| `reviews` | Number of written reviews |
| `totalratings` | Total ratings count |
| `cleaned_author` | Normalized author name |
| `cleaned_desc` | Cleaned synopsis |
| `cleaned_title` | Normalized title |
| `cleaned_genre` | Normalized genre |
| `tags` | Combined NLP feature text |

**Note:** The full dataset includes additional iconic titles and is used to generate the TF-IDF feature matrix.

---

## 🧠 Machine Learning Architecture

The recommendation system uses **Content-Based Filtering** to identify books with similar textual characteristics.

### Recommendation Pipeline

```text
           User Input
               |
               v
       Text Normalization
               |
               v
        Book Title Matching
               |
       +-------+-------+
       |               |
    Exact Match    Fuzzy Match
       |               |
       +-------+-------+
               |
               v
       Matched Book Index
               |
               v
      Extract TF-IDF Vector
               |
               v
       Cosine Similarity
               |
               v
       Rank Similar Books
               |
               v
        Exclude Input Book
               |
               v
       Top 5 Recommendations
```

### 1. TF-IDF Vectorization

The system combines multiple textual features:

- Author
- Book title
- Genres
- Book description

These features are combined into a single text field called `tags`.

TF-IDF converts the textual information into numerical vectors using a maximum vocabulary size of **15,000 features**.

### 2. Cosine Similarity

Cosine similarity measures the similarity between two book vectors.

Formula:

\[
\text{Similarity}(A,B)=
\frac{A\cdot B}{\|A\|\|B\|}
\]

A higher similarity score indicates that two books have more similar textual characteristics.

### 3. Recommendation Generation

1. Normalize the user-entered title.
2. Find the matching book in the dataset.
3. Retrieve its TF-IDF vector.
4. Calculate similarity against all other books.
5. Sort similarity scores in descending order.
6. Exclude the selected book.
7. Return the top 5 recommendations.

**Performance:** The sparse matrix implementation enables efficient similarity computation across the 90,134-book corpus.

---

## 🌍 Text Normalization & Multilingual Handling

Book metadata can contain encoding errors, inconsistent author names, and descriptions in different languages.

The project implements a text-cleaning pipeline to improve consistency.

### 1. Encoding Correction
- Fixes common UTF-8 and Windows-1252 encoding issues.
- Decodes HTML entities.
- Normalizes punctuation and whitespace.

### 2. Author Name Normalization

Uses Unicode NFKD decomposition to normalize accented Latin characters.

Examples:

| Original | Normalized |
|---|---|
| Mary GrandPré | Mary GrandPre |
| Carlos Ruiz Zafón | Carlos Ruiz Zafon |
| Antoine de Saint-Exupéry | Antoine de Saint-Exupery |
| Benjamin Alire Sáenz | Benjamin Alire Saenz |

### 3. Description Handling

- Detects missing descriptions.
- Identifies potentially non-English descriptions using language-specific stopwords.
- Generates English fallback overviews for missing or foreign-language descriptions.

**Note:** Generated fallback descriptions are simplified overviews, not verified translations of the original synopsis.

---

## 🎨 Design System — Athenaeum Editorial

The interface follows a classic literary and editorial design philosophy.

Instead of conventional SaaS-style gradients, it uses warm paper backgrounds, refined typography, and book-inspired visual elements.

### Color Palette

| Color | Hex Code | Usage |
|---|---|---|
| Parchment Cream | `#FBF8F2` | Main background |
| Antique White | `#FFFFFF` | Card surfaces |
| Iron Gall Ink | `#1C1917` | Primary text |
| Stone Grey | `#78716C` | Secondary text |
| Oxblood Leather | `#8B2635` | Primary accents |
| Amber Ochre | `#C5832B` | Ratings and highlights |
| Rule Border | `#E7E0D3` | Borders and dividers |

### Typography

- **Cormorant Garamond:** Headings and display typography.
- **Plus Jakarta Sans:** Interface elements, metadata, and search.

### Special UI Elements

- Archival-style book catalogue cards.
- Leather-inspired book spine ribbons.
- Roman numeral indexing.
- Similarity affinity badges.
- Interactive Curator's Slip for book descriptions.

---

## 🏗️ Project Structure

```text
the-next-page/
│
├── app.py
├── clean_text_util.py
├── book_recommander.py
│
├── data/
│   ├── popular_books.csv
│   └── books_final.csv
│
├── models/
│   └── tfidf_matrix.pkl
│
├── templates/
│   ├── base.html
│   ├── popular.html
│   └── recommend.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   │
│   └── js/
│       └── main.js
│
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## 🛠️ Tech Stack

| Category | Technologies |
|---|---|
| Backend | Python, Flask |
| Frontend | HTML, CSS, JavaScript |
| Machine Learning | Scikit-learn |
| NLP | TF-IDF Vectorization |
| Similarity Algorithm | Cosine Similarity |
| Data Processing | Pandas, NumPy |
| Model Storage | Pickle |
| Dataset | Goodreads Book Records |
| Deployment | Hugging Face Spaces |

---

## 🚀 Installation & Setup

Follow these steps to run the project locally.

### Prerequisites

- Python 3.9+
- pip
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/the-next-page.git
```

### 2. Navigate to the Project Directory

```bash
cd the-next-page
```

### 3. Create a Virtual Environment

**Windows:**

```powershell
python -m venv venv
venv\Scripts\activate
```

**Linux / macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the Application

```bash
python app.py
```

### 6. Open in Browser

```text
http://127.0.0.1:5000
```

---

## ☁️ Deployment

### Option 1: Hugging Face Spaces

Hugging Face Spaces supports Docker-based application deployment.

1. Create an account on [Hugging Face](https://huggingface.co/).
2. Create a new Space.
3. Select **Docker** as the SDK.
4. Upload or push your project files.
5. Configure the application to listen on port `7860`.
6. Wait for the Docker build to complete.
7. Access your publicly hosted application.

**Important:** Free-tier hardware and storage limits can change. Check the current Space hardware specifications before deployment. Make sure your model and dataset fit within the available resources.

### Option 2: LocalTunnel

For quickly sharing your locally running application:

1. Start Flask:

```bash
python app.py
```

2. Open another terminal and execute:

```bash
npx localtunnel --port 5000
```

3. Open the generated public URL.

**Note:** LocalTunnel is suitable for temporary demonstrations, not permanent 24/7 hosting.

---

## 🔮 Future Improvements

Potential improvements for future versions:

- [ ] Personalized recommendations based on reading history.
- [ ] Hybrid recommendation system combining content-based and collaborative filtering.
- [ ] Advanced semantic search using sentence embeddings.
- [ ] User accounts and personal reading lists.
- [ ] Book reviews and ratings from users.
- [ ] Advanced filters for publication year, language, and author.
- [ ] Goodreads or other book catalogue API integration.
- [ ] Improved multilingual support.
- [ ] Mobile-first responsive experience.

---

## 🤝 Contributing

Contributions, suggestions, and feature requests are welcome!

1. Fork the repository.
2. Create a new feature branch.
3. Commit your changes.
4. Push the branch.
5. Open a Pull Request.

---

## 📄 License

This project is intended for educational and personal development purposes.

Add an appropriate open-source license, such as the MIT License, if you want others to reuse and modify the code.

---

## ❤️ Acknowledgements

- [Goodreads](https://www.goodreads.com/) — Book metadata and reader ratings.
- [Scikit-learn](https://scikit-learn.org/) — TF-IDF vectorization and similarity computation.
- [Flask](https://flask.palletsprojects.com/) — Backend web framework.
- [Google Fonts](https://fonts.google.com/) — Typography.

---

<p align="center">

### 📚 The Next Page

**Every great journey begins with the next book.**

*Discover it. Read it. Repeat.*

</p>
