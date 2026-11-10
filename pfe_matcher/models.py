from dataclasses import asdict, dataclass, field


@dataclass
class Topic:
    ref: str
    title: str
    text: str
    skills: list = field(default_factory=list)
    duration_min: int | None = None
    duration_max: int | None = None
    places: int | None = None

    def to_dict(self):
        return asdict(self)


@dataclass
class Match:
    topic: Topic
    score: int
    coverage: float
    similarity: float
    matched: list
    missing: list

    def to_dict(self):
        return {
            "ref": self.topic.ref,
            "title": self.topic.title,
            "score": self.score,
            "coverage": round(self.coverage, 2),
            "similarity": round(self.similarity, 2),
            "matched": self.matched,
            "missing": self.missing,
            "duration_min": self.topic.duration_min,
            "duration_max": self.topic.duration_max,
            "places": self.topic.places,
        }
