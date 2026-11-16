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
       Text
