"""Dictionary module: loads user vocabulary from JSON, provides lookup and lemmatization."""

import json
import os
import html as html_mod

# Only the MOST common English words — things any learner absolutely knows
# This is intentionally conservative; the user's own dictionary covers most words
CET4_BLOCKLIST = {
    # Core function words
    'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
    'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
    'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
    'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what',
    'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go', 'me',
    'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know',
    'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could',
    'them', 'see', 'other', 'than', 'then', 'now', 'look', 'only', 'come',
    'its', 'over', 'think', 'also', 'back', 'after', 'use', 'two', 'how',
    'our', 'work', 'first', 'well', 'way', 'even', 'new', 'want',
    'because', 'any', 'these', 'give', 'day', 'most', 'us', 'is', 'are',
    'was', 'were', 'been', 'has', 'had', 'did', 'does', 'doing', 'being',
    'said', 'may', 'must', 'should', 'shall', 'might', 'need',
    # Pronouns & determiners
    'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her',
    'us', 'them', 'my', 'your', 'his', 'its', 'our', 'their',
    'this', 'that', 'these', 'those', 'what', 'which', 'who',
    # Basic adjectives only the most elementary
    'good', 'new', 'first', 'last', 'long', 'great', 'little',
    'other', 'old', 'right', 'big', 'high', 'small', 'large',
    'next', 'early', 'young', 'important', 'bad', 'same', 'able',
    'better', 'best', 'sure', 'clear', 'hard', 'light', 'dark',
    'free', 'full', 'close', 'easy', 'low', 'short', 'simple',
    # Very common prepositions/conjunctions/adverbs
    'up', 'so', 'out', 'just', 'now', 'how', 'then', 'more', 'also',
    'here', 'well', 'only', 'very', 'even', 'back', 'there', 'down',
    'still', 'in', 'as', 'to', 'of', 'for', 'with', 'on', 'at', 'from',
    'by', 'about', 'over', 'between', 'after', 'before', 'under',
    'above', 'into', 'near', 'since', 'during', 'along', 'across',
    'behind', 'without', 'upon',
    'and', 'but', 'or', 'yet', 'if', 'because', 'while', 'until',
    'when', 'where', 'than',
    # Numbers
    'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight',
    'nine', 'ten', 'hundred', 'thousand', 'million', 'billion',
    # Basic pronouns
    'all', 'each', 'every', 'both', 'few', 'many', 'much', 'some',
    'any', 'no', 'not', 'one', 'another', 'self',
    # Common proper nouns
    'un', 'eu', 'nato',
}


class Dictionary:
    def __init__(self, dict_path=None):
        self.entries = {}
        if dict_path and os.path.exists(dict_path):
            with open(dict_path, 'r', encoding='utf-8') as f:
                raw = json.load(f)
            # Unescape HTML entities in phonetics and definitions
            for k, v in raw.items():
                self.entries[k] = {
                    'phonetic': html_mod.unescape(v.get('phonetic', '')),
                    'pos': v.get('pos', ''),
                    'definition': html_mod.unescape(v.get('definition', '')),
                }
        self._lookup = {k.lower(): v for k, v in self.entries.items()}

    def lookup(self, word):
        """Look up a word. Returns (phonetic, pos, definition) or None."""
        word_lower = word.lower()
        if word_lower in CET4_BLOCKLIST:
            return None
        if word_lower in self._lookup:
            entry = self._lookup[word_lower]
            phonetic = entry.get('phonetic', '')
            definition = entry.get('definition', '')
            if phonetic or definition:
                return (phonetic, entry.get('pos', ''), definition)
        # Try lemmatization
        lemma = self._lemmatize(word_lower)
        if lemma != word_lower and lemma in self._lookup:
            if lemma not in CET4_BLOCKLIST:
                entry = self._lookup[lemma]
                phonetic = entry.get('phonetic', '')
                definition = entry.get('definition', '')
                if phonetic or definition:
                    return (phonetic, entry.get('pos', ''), definition)
        return None

    def _lemmatize(self, word):
        """Conservative lemmatization."""
        if len(word) <= 3:
            return word
        if word.endswith('ies') and len(word) > 5:
            base = word[:-3] + 'y'
            if base in self._lookup and word not in self._lookup:
                return base
        if word.endswith('ves') and len(word) > 5:
            base = word[:-3] + 'f'
            if base in self._lookup and word not in self._lookup:
                return base
        if word.endswith(('ses', 'xes', 'zes', 'shes', 'ches')):
            base = word[:-2]
            if base in self._lookup and word not in self._lookup:
                return base
        if word.endswith('s') and not word.endswith('ss') and len(word) > 4:
            base = word[:-1]
            if base in self._lookup and word not in self._lookup:
                return base
        if word.endswith('ed') and len(word) > 5:
            base = word[:-2]
            if base in self._lookup and word not in self._lookup:
                return base
            if len(base) > 1 and base[-1] == base[-1]:
                base2 = base[:-1]
                if base2 in self._lookup:
                    return base2
        if word.endswith('ing') and len(word) > 6:
            base = word[:-3]
            if base in self._lookup and word not in self._lookup:
                return base
            if len(base) > 1 and base[-1] == base[-1]:
                base2 = base[:-1]
                if base2 in self._lookup:
                    return base2
        if word.endswith('ly') and len(word) > 6:
            base = word[:-2]
            if base in self._lookup and word not in self._lookup:
                return base
        if word.endswith('er') and len(word) > 5:
            base = word[:-2]
            if base in self._lookup and word not in self._lookup:
                return base
        if word.endswith('est') and len(word) > 6:
            base = word[:-3]
            if base in self._lookup and word not in self._lookup:
                return base
        return word
