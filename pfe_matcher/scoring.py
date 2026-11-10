from .models import Match
from .retrieval import TopicIndex
from .skills import normalize_skills

COVERAGE_WEIGHT = 70
SIMILARITY_WEIGHT = 30


def match_topics(topics, profile_skills, profile_text="", top=5, min_score=0):
    skills = normalize_skills(profile_skills)
    index = TopicIndex(topics)
    query = " ".join(skills) + " " + profile_text
    sims = index.similarities(query)
    peak = max(sims) if sims else 0.0
    results = []
    for topic, sim in zip(index.topics, sims):
        required = topic.skills
        matched = [s for s in required if s in skills]
        missing = [s for s in required if s not in skills]
        coverage = len(matched) / len(required) if required else 0.0
        similarity = sim / peak if peak > 0 else 0.0
        score = round(COVERAGE_WEIGHT * coverage + SIMILARITY_WEIGHT * similarity)
        results.append(Match(topic, score, coverage, similarity, matched, missing))
    results.sort(key=lambda m: (m.score, m.coverage), reverse=True)
    return [m for m in results if m.score >= min_score][:top]
