import wikipedia
import logging
from typing import Dict, List, Optional
import spacy
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import random

print("external_sources.py is being imported")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except:
    logging.warning("SpaCy model not found. Downloading now...")
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# In-memory cache to track fetched topics
fetched_topics_cache = set()

# Define stop words that are not useful for Wikipedia searches
STOP_CHUNKS = {"what", "who", "why", "how", "which", "are", "do", "does", "did", "have", "has", "had", "your"}

def extract_key_terms(topic: str, top_n: int = 3) -> List[str]:
    """
    Extract key terms from the topic using spaCy's noun chunks and entities.
    Prioritizes noun chunks over entities and excludes those with stop words.
    """
    doc = nlp(topic)
    key_terms = []

    # Extract noun chunks
    noun_chunks = list(doc.noun_chunks)
    for chunk in noun_chunks:
        chunk_text = chunk.text.lower()
        if not any(stop_word in chunk_text for stop_word in STOP_CHUNKS):
            key_terms.append(chunk.text)
        if len(key_terms) >= top_n:
            break

    # If not enough, extract entities
    if len(key_terms) < top_n:
        entities = list(doc.ents)
        for ent in entities:
            ent_text = ent.text.lower()
            if ent_text not in key_terms and not any(stop_word in ent_text for stop_word in STOP_CHUNKS):
                key_terms.append(ent.text)
            if len(key_terms) >= top_n:
                break

    # If still not enough, extract most common nouns
    if len(key_terms) < top_n:
        nouns = [token.text for token in doc if token.pos_ == "NOUN" and token.text.lower() not in STOP_CHUNKS]
        most_common_nouns = [word for word, _ in Counter(nouns).most_common(top_n)]
        key_terms.extend(most_common_nouns[:top_n - len(key_terms)])

    # Remove duplicates and limit to top_n
    key_terms = list(dict.fromkeys(key_terms))[:top_n]
    logging.info(f"Extracted key terms: {key_terms}")
    return key_terms

def fetch_wikipedia_summary(term: str, sentences: int = 2, lang: str = 'en') -> Dict[str, Optional[str]]:
    print(f"fetch_wikipedia_summary called with term: {term}")
    """
    Fetch a summary from Wikipedia for the given term.
    """
    try:
        wikipedia.set_lang(lang)
        search_results = wikipedia.search(term)
        if not search_results:
            logging.warning(f"No Wikipedia results found for '{term}'")
            return {"summary": None, "confidence": "none"}

        # Attempt to fetch the first non-fetched page
        for result in search_results:
            result_lower = result.lower()
            if result_lower in fetched_topics_cache:
                continue
            try:
                page = wikipedia.page(result, auto_suggest=False)
                summary = wikipedia.summary(page.title, sentences=sentences)
                logging.info(f"Successfully fetched summary for '{page.title}'")
                fetched_topics_cache.add(page.title.lower())
                return {"summary": summary, "confidence": "high"}
            except wikipedia.exceptions.DisambiguationError as e:
                logging.warning(f"Disambiguation error for '{result}': {e.options}")
                # Score disambiguation options based on relevance
                best_option = score_disambiguation_option(term, e.options)
                if best_option and best_option.lower() not in fetched_topics_cache:
                    try:
                        page = wikipedia.page(best_option, auto_suggest=False)
                        summary = wikipedia.summary(page.title, sentences=sentences)
                        logging.info(f"Successfully fetched summary for disambiguated topic '{page.title}'")
                        fetched_topics_cache.add(page.title.lower())
                        return {"summary": summary, "confidence": "medium"}
                    except Exception as ex:
                        logging.error(f"Error fetching disambiguated topic '{best_option}': {str(ex)}")
                        continue
            except wikipedia.exceptions.PageError:
                logging.warning(f"No Wikipedia page found for '{result}'")
                continue
            except Exception as e:
                logging.error(f"Error fetching summary for '{result}': {str(e)}")
                continue

        # If all search results are exhausted
        return {"summary": f"No suitable Wikipedia page found for '{term}'.", "confidence": "none"}

    except Exception as e:
        logging.error(f"Error fetching summary for '{term}': {str(e)}")
        return {"summary": None, "confidence": "none"}

def score_disambiguation_option(term: str, options: List[str]) -> Optional[str]:
    """
    Score disambiguation options based on their relevance to the original term.
    Returns the most relevant option or None if no relevant option is found.
    """
    best_score = 0
    best_option = None
    for option in options:
        combined_text = f"{term} {option}"
        try:
            vectorizer = TfidfVectorizer().fit_transform([term, option, combined_text])
            similarity = cosine_similarity(vectorizer[0:1], vectorizer[-1:]).flatten()[0]
            if similarity > best_score:
                best_score = similarity
                best_option = option
        except Exception as e:
            logging.error(f"Error scoring disambiguation option '{option}': {str(e)}")
            continue
    logging.info(f"Disambiguation scoring: Best option for '{term}' is '{best_option}' with score {best_score}")
    return best_option if best_score > 0.1 else None  # Threshold can be adjusted

def get_related_topics(topic: str, results: int = 10) -> List[str]:
    """
    Get a list of topics related to the given topic.
    """
    try:
        related = wikipedia.search(topic, results=results)
        # Shuffle to introduce variety
        random.shuffle(related)
        # Exclude already fetched topics
        filtered_related = [t for t in related if t.lower() not in fetched_topics_cache]
        logging.info(f"Found {len(filtered_related)} related topics for '{topic}'")
        return filtered_related[:5]  # Return top 5 unique related topics
    except Exception as e:
        logging.error(f"Error finding related topics for '{topic}': {str(e)}")
        return []

def extract_key_terms_from_summary(summary: str, n: int = 5) -> List[str]:
    """
    Extract key terms from a given summary using NLP.
    """
    doc = nlp(summary)
    words = [token.lemma_.lower() for token in doc if not token.is_stop and token.is_alpha]
    return [word for word, _ in Counter(words).most_common(n)]

def check_relevance(original_term: str, related_term: str, threshold: float = 0.2) -> bool:
    """
    Check if a related term is relevant to the original term using TF-IDF and cosine similarity.
    """
    try:
        vectorizer = TfidfVectorizer().fit_transform([original_term, related_term])
        cosine_sim = cosine_similarity(vectorizer[0], vectorizer[1])[0][0]
        logging.info(f"Cosine similarity between '{original_term}' and '{related_term}': {cosine_sim}")
        return cosine_sim >= threshold
    except Exception as e:
        logging.error(f"Error checking relevance between '{original_term}' and '{related_term}': {str(e)}")
        return False

def fetch_wikipedia_info(topic: str, sentences: int = 2, lang: str = 'en') -> Dict[str, any]:
    """
    Fetch Wikipedia summary and related topics for a given topic.
    """
    key_terms = extract_key_terms(topic)
    summary, confidence = None, "none"

    # Attempt to fetch summary based on extracted key terms
    for term in key_terms:
        result = fetch_wikipedia_summary(term, sentences, lang)
        if result["summary"]:
            summary = result["summary"]
            confidence = result["confidence"]
            break  # Stop at the first successful fetch

    if not summary:
        # If no summary found, attempt to search using the full topic
        result = fetch_wikipedia_summary(topic, sentences, lang)
        if result["summary"]:
            summary = result["summary"]
            confidence = result["confidence"]

    if confidence == "none":
        related_topics = get_related_topics(topic)
    else:
        related_topics = get_related_topics(topic)  # Fetch related topics regardless

    relevant_topics = [t for t in related_topics if check_relevance(topic, t)]
    return {
        "summary": summary,
        "confidence": confidence,
        "related_topics": relevant_topics[:5]  # Limit to top 5 relevant topics
    }

def fetch_robust_wikipedia_info(topic: str, sentences: int = 2, lang: str = 'en') -> Dict[str, any]:
    """
    Attempt to fetch Wikipedia info for the main topic, falling back to related topics if necessary.
    If no information is found, use NLP to extract key terms and search for those.
    """
    info = fetch_wikipedia_info(topic, sentences, lang)

    if info['confidence'] == 'none':
        # Try related topics
        for related_topic in info.get('related_topics', []):
            related_info = fetch_wikipedia_info(related_topic, sentences, lang)
            if related_info['confidence'] != 'none':
                info['summary'] = f"Information on related topic '{related_topic}': {related_info['summary']}"
                info['confidence'] = 'medium'
                break

        # If still no information, use NLP to extract key terms from the original summary (if any)
        if info['confidence'] == 'none' and info.get('summary'):
            key_terms = extract_key_terms_from_summary(info['summary'])
            for term in key_terms:
                if check_relevance(topic, term):
                    term_info = fetch_wikipedia_info(term, sentences, lang)
                    if term_info['confidence'] != 'none':
                        info['summary'] = f"Information on related term '{term}': {term_info['summary']}"
                        info['confidence'] = 'low'
                        info['related_topics'] = term_info.get('related_topics', [])
                        break

        # Final check if still no information found
        if info['confidence'] == 'none':
            info['summary'] = f"No information found for '{topic}' or related terms."
            info['related_topics'] = []

    # Add key points extraction
    if info['summary']:
        info['key_points'] = extract_key_points(info['summary'])
    else:
        info['key_points'] = []

    return info

def extract_key_points(text: str, n: int = 5) -> List[str]:
    """
    Extract key points from a given text using NLP.
    """
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents]
    return sentences[:n]

if __name__ == "__main__":
    # Example usage
    topic = "What the craziest real experiments and what are your opinions?"  # Original debate topic
    info = fetch_robust_wikipedia_info(topic, sentences=3)
    print(f"Information for '{topic}':")
    print(f"Summary: {info['summary']}")
    print(f"Confidence: {info['confidence']}")
    print(f"Related topics: {', '.join(info['related_topics'])}")
    print(f"Key Points: {info['key_points']}")
