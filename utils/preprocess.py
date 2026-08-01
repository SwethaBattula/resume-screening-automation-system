"""NLP Preprocessing Module.

Performs text cleaning, punctuation removal, lowercasing, stopword removal,
tokenization, and lemmatization using spaCy and NLTK with automatic model loading
and fallback capabilities.
"""

import string
import re
from typing import List, Dict, Any, Optional
import nltk
from utils.logger import setup_logger

logger = setup_logger("utils.preprocess")

# Lazy-loaded globals
_nlp_model = None
_nltk_stopwords = None
_nltk_lemmatizer = None


def _ensure_nltk_resources() -> None:
    """Ensures required NLTK resources (stopwords, wordnet, punkt) are downloaded."""
    global _nltk_stopwords, _nltk_lemmatizer
    try:
        if _nltk_stopwords is None:
            try:
                from nltk.corpus import stopwords

                _nltk_stopwords = set(stopwords.words("english"))
            except LookupError:
                nltk.download("stopwords", quiet=True)
                from nltk.corpus import stopwords

                _nltk_stopwords = set(stopwords.words("english"))

        if _nltk_lemmatizer is None:
            try:
                from nltk.stem import WordNetLemmatizer

                _nltk_lemmatizer = WordNetLemmatizer()
            except LookupError:
                nltk.download("wordnet", quiet=True)
                from nltk.stem import WordNetLemmatizer

                _nltk_lemmatizer = WordNetLemmatizer()
    except Exception as exc:
        logger.warning(f"Error ensuring NLTK resources: {exc}")
        if _nltk_stopwords is None:
            _nltk_stopwords = {"a", "an", "the", "and", "or", "in", "on", "at", "to", "for", "with", "is", "was", "of"}


def _get_spacy_nlp() -> Optional[Any]:
    """Lazily loads spaCy en_core_web_sm pipeline."""
    global _nlp_model
    if _nlp_model is None:
        try:
            import spacy

            try:
                _nlp_model = spacy.load("en_core_web_sm")
            except OSError:
                logger.info("spaCy model 'en_core_web_sm' not found. Downloading...")
                from spacy.cli import download

                download("en_core_web_sm")
                _nlp_model = spacy.load("en_core_web_sm")
        except Exception as exc:
            logger.warning(f"Failed to load spaCy model: {exc}. Will fallback to NLTK.")
            _nlp_model = False
    return _nlp_model if _nlp_model else None


def clean_text_simple(text: Optional[str]) -> str:
    """Performs basic text cleaning: removes non-printable characters and extra whitespace.

    Args:
        text (Optional[str]): Raw input text.

    Returns:
        str: Cleaned text string.
    """
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def remove_punctuation(text: str) -> str:
    """Removes punctuation from text while preserving spaces and letters.

    Args:
        text (str): Input string.

    Returns:
        str: String with punctuation stripped.
    """
    if not text:
        return ""
    translator = str.maketrans("", "", string.punctuation)
    return text.translate(translator)


def preprocess_text(text: Optional[str]) -> Dict[str, Any]:
    """Performs complete NLP preprocessing pipeline on input text.

    Pipeline steps:
    1. Lowercase conversion
    2. Punctuation removal
    3. Tokenization
    4. Stopword removal
    5. Lemmatization

    Args:
        text (Optional[str]): Raw text to preprocess.

    Returns:
        Dict[str, Any]: Preprocessing result dictionary containing:
            - 'clean_text': Lowercased cleaned raw string.
            - 'tokens': List of cleaned, lemmatized non-stopword tokens.
            - 'lemma_string': Space-separated string of lemmatized tokens.
    """
    if not text or not text.strip():
        return {
            "clean_text": "",
            "tokens": [],
            "lemma_string": "",
        }

    lowercased = text.lower()
    nlp = _get_spacy_nlp()

    tokens: List[str] = []

    if nlp is not None:
        try:
            doc = nlp(lowercased)
            for token in doc:
                if not token.is_stop and not token.is_punct and not token.is_space and len(token.lemma_.strip()) > 1:
                    clean_lemma = token.lemma_.strip().lower()
                    clean_lemma = remove_punctuation(clean_lemma)
                    if clean_lemma:
                        tokens.append(clean_lemma)
        except Exception as exc:
            logger.warning(f"spaCy preprocessing failed: {exc}. Using NLTK fallback.")
            nlp = None

    if nlp is None:
        _ensure_nltk_resources()
        # NLTK Fallback
        no_punct = remove_punctuation(lowercased)
        words = no_punct.split()
        for word in words:
            word = word.strip()
            if word not in _nltk_stopwords and len(word) > 1:
                lemmatized = _nltk_lemmatizer.lemmatize(word) if _nltk_lemmatizer else word
                tokens.append(lemmatized)

    return {
        "clean_text": lowercased,
        "tokens": tokens,
        "lemma_string": " ".join(tokens),
    }
