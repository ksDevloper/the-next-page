import re
import html
import unicodedata

# Common English words used to detect if text is predominantly in English
COMMON_ENGLISH_WORDS = {
    'the', 'and', 'is', 'in', 'of', 'to', 'a', 'with', 'for', 'that', 
    'this', 'on', 'at', 'it', 'from', 'by', 'as', 'an', 'his', 'her', 
    'their', 'was', 'he', 'she', 'they', 'but', 'not', 'or', 'has', 
    'have', 'had', 'who', 'what', 'when', 'where', 'why', 'how', 'all', 
    'one', 'new', 'more', 'about', 'out', 'up', 'down', 'into', 'over', 
    'after', 'life', 'world', 'time', 'book', 'story', 'first', 'two',
    'been', 'were', 'which', 'will', 'would', 'there', 'could', 'their'
}

# Strong foreign stop words indicating non-English text
FOREIGN_STOPWORDS = {
    # French
    'le', 'la', 'les', 'des', 'du', 'dans', 'pour', 'avec', 'cette', 'aux', 
    'qui', 'sur', 'mais', 'son', 'sa', 'ses', 'leur', 'leurs', 'est', 'sont',
    # Spanish
    'el', 'los', 'las', 'del', 'para', 'por', 'como', 'pero', 'con', 'una', 
    'unos', 'unas', 'sus', 'este', 'esta',
    # German
    'der', 'die', 'das', 'und', 'von', 'mit', 'auf', 'ist', 'ein', 'eine', 
    'einen', 'einem', 'fuer', 'nicht', 'sich', 'dem', 'den',
    # Italian
    'della', 'delle', 'degli', 'sono', 'questo', 'questa', 'per',
    # Dutch
    'het', 'een', 'van', 'voor', 'zijn',
    # Portuguese
    'uma', 'dos', 'das', 'nao', 'mais'
}

def repair_mojibake(text: str) -> str:
    """Repairs common double-encoded UTF-8 artifacts (mojibake) and normalizes to standard English ASCII."""
    if not isinstance(text, str) or not text:
        return ""

    replacements = [
        ('â€™', "'"),
        ('â€˜', "'"),
        ('â€œ', '"'),
        ('â€\x9d', '"'),
        ('â€', '"'),
        ('â€”', ' - '),
        ('â€“', ' - '),
        ('â€¦', '...'),
        ('â€¢', '•'),
        ('\u2018', "'"),
        ('\u2019', "'"),
        ('\u201c', '"'),
        ('\u201d', '"'),
        ('\u2014', ' - '),
        ('\u2013', ' - '),
        ('\u2026', '...'),
        ('Ã©', 'e'),
        ('Ã¨', 'e'),
        ('Ãª', 'e'),
        ('Ã«', 'e'),
        ('Ã¡', 'a'),
        ('Ã ', 'a'),
        ('Ã¢', 'a'),
        ('Ã¤', 'a'),
        ('Ã³', 'o'),
        ('Ã²', 'o'),
        ('Ã´', 'o'),
        ('Ã¶', 'o'),
        ('Ã±', 'n'),
        ('Ã§', 'c'),
        ('Ã®', 'i'),
        ('Ã¯', 'i'),
        ('Ã­', 'i'),
        ('Ãº', 'u'),
        ('Ã¹', 'u'),
        ('Ã¼', 'u'),
        ('Å¡', 's'),
        ('Å¾', 'z'),
        ('Ä‡', 'c'),
        ('Ä\x8d', 'c'),
        ('Ã¸', 'o'),
        ('Ã¥', 'a'),
        ('Ã¦', 'ae'),
        ('Â«', '"'),
        ('Â»', '"'),
        ('Â', ' '),
    ]
    for bad, good in replacements:
        text = text.replace(bad, good)

    # Decode HTML entities
    text = html.unescape(text)

    # Convert non-breaking spaces
    text = text.replace('\xa0', ' ').replace('\u200b', '')

    # Convert accented Latin characters to standard base English ASCII letters
    normalized = unicodedata.normalize('NFKD', text)
    text = ''.join(c for c in normalized if not unicodedata.combining(c))

    return text


def clean_author_name(author_str: str) -> str:
    """
    Cleans author name(s) into clear English Latin text:
    - Removes mojibake and normalizes accents (e.g. Mary GrandPré -> Mary GrandPre)
    - Strips foreign scripts (Greek, Cyrillic, Arabic, Chinese, etc.)
    - Removes duplicates and extra spacing
    """
    if not isinstance(author_str, str) or not author_str.strip() or author_str.strip() in ['nan', 'None']:
        return "Unknown Author"

    cleaned = repair_mojibake(author_str)

    # Split multiple authors
    parts = [p.strip() for p in cleaned.split(',') if p.strip()]
    english_parts = []

    for part in parts:
        # Keep only standard English letters, digits, spaces, periods, hyphens, and apostrophes
        latin_only = re.sub(r'[^a-zA-Z0-9\s\.\-\']', '', part).strip()
        
        # Filter out 1-char leftover noise or purely numeric tokens
        if len(latin_only) >= 2 and not latin_only.isdigit():
            latin_only = re.sub(r'\s+', ' ', latin_only)
            english_parts.append(latin_only)

    if not english_parts:
        return "Author"

    # Deduplicate while preserving order
    seen = set()
    deduped = []
    for p in english_parts:
        p_lower = p.lower()
        if p_lower not in seen:
            seen.add(p_lower)
            deduped.append(p)

    return ", ".join(deduped[:3])


def is_foreign_text(text: str) -> bool:
    """Detects if text is predominantly in a foreign language (non-English)."""
    words = [w.lower().strip(".,!?:;\"'()[]-") for w in text.split()]
    if len(words) < 8:
        return False

    # Check for presence of strong foreign stopwords
    foreign_matches = sum(1 for w in words if w in FOREIGN_STOPWORDS)
    if foreign_matches >= 3 or (foreign_matches >= 2 and len(words) < 25):
        return True

    # Check common English stopwords (excluding single letter 'a' and 'i')
    common_en = {'the', 'and', 'is', 'in', 'of', 'to', 'with', 'for', 'that', 'this', 'on', 'at', 'it', 'from', 'by', 'as', 'an', 'his', 'her', 'their', 'was', 'he', 'she', 'they', 'but', 'not', 'or'}
    en_matches = sum(1 for w in words if w in common_en)
    if (en_matches / len(words)) < 0.08:
        return True

    return False


def clean_description_english(desc: str, title: str = "", author: str = "", genre: str = "") -> str:
    """
    Ensures book description is presented in clear, engaging English:
    1. If missing, null, or empty: generates a clean English contextual description.
    2. If present: repairs mojibake and fixes punctuation.
    3. If detected as foreign language text (French, Spanish, German, etc.):
       synthesizes an informative English summary with genre and author attribution.
    """
    if not isinstance(genre, str) or not genre:
        genre_clean = "Literary"
    else:
        genre_clean = genre.split(',')[0].strip() if genre.strip() else "Literary"

    author_clean = clean_author_name(author)
    title_clean = title.title() if title else "This work"

    if not isinstance(desc, str) or not desc.strip() or desc.strip() in ['nan', 'N/A', 'None']:
        return f"A popular {genre_clean} book written by {author_clean}."

    text = repair_mojibake(desc)

    # Clean leading punctuation artifacts
    text = re.sub(r'^[\"\',;\s]+', '', text)
    text = re.sub(r'(\s*,\s*)+', ', ', text)
    text = re.sub(r'\"\s*,\s*', '" ', text)
    text = re.sub(r'^\s*,\s*', '', text)
    text = re.sub(r'\s+', ' ', text).strip()

    # Detect foreign language text and replace with simple English summary
    if is_foreign_text(text):
        genres_list = [g.strip() for g in genre.split(',') if g.strip()][:2] if isinstance(genre, str) else []
        genre_phrase = f"{', '.join(genres_list)}" if genres_list else genre_clean
        return (
            f"A popular {genre_clean} book by {author_clean}. "
            f"'{title_clean}' is a great read for fans of {genre_phrase}."
        )

    return text
