from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

FRENCH_STOP_WORDS = [
    "le", "la", "les", "un", "une", "des", "du", "de", "d", "l", "et", "ou",
    "en", "au", "aux", "pour", "par", "sur", "dans", "avec", "sans", "est",
    "sont", "ce", "cette", "ces", "qui", "que", "se", "sa", "son", "ses",
    "il", "elle", "on", "a", "à", "the", "and", "of", "to", "in", "for",
]


class TopicIndex:
    def __init__(self, topics):
        self.topics = list(topics)
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            sublinear_tf=True,
            strip_accents="unicode",
            lowercase=True,
            stop_words=FRENCH_STOP_WORDS,
        )
        corpus = [f"{t.title} {t.text}" for t in self.topics]
        self.matrix = self.vectorizer.fit_transform(corpus) if corpus else None

    def similarities(self, query):
        if self.matrix is None or not query.strip():
            return [0.0] * len(self.topics)
        vector = self.vectorizer.transform([query])
        return list(cosine_similarity(vector, self.matrix)[0])

    def search(self, query, top=5):
        sims = self.similarities(query)
        ranked = sorted(zip(self.topics, sims), key=lambda pair: pair[1], reverse=True)
        return [(t, float(s)) for t, s in ranked[:top] if s > 0]
