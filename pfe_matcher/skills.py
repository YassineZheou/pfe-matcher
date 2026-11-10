import re

TAXONOMY = {
    "Python": ["python"],
    "Java": ["java"],
    "JavaScript": ["javascript", "js"],
    "TypeScript": ["typescript"],
    "Angular": ["angular"],
    "React": ["react", "reactjs"],
    "Spring Boot": ["spring boot", "springboot"],
    "FastAPI": ["fastapi"],
    "SQL": ["sql"],
    "PostgreSQL": ["postgresql", "postgres"],
    "Power BI": ["power bi", "powerbi"],
    "Power Automate": ["power automate"],
    "Docker": ["docker"],
    "Kubernetes": ["kubernetes", "k8s"],
    "CI/CD": ["ci/cd", "cicd"],
    "LLM": ["llm", "llms"],
    "RAG": ["rag"],
    "NLP": ["nlp", "traitement du langage"],
    "LangChain": ["langchain"],
    "Hugging Face": ["hugging face", "huggingface"],
    "spaCy": ["spacy"],
    "TensorFlow": ["tensorflow", "keras"],
    "MLOps": ["mlops", "mlflow"],
    "Airflow": ["airflow"],
    "Streamlit": ["streamlit"],
    "Scrapy": ["scrapy"],
    "Selenium": ["selenium"],
    "Azure": ["azure"],
    "Databricks": ["databricks"],
    "ServiceNow": ["servicenow"],
    "SAP": ["sap"],
    "Embarqué": ["embarqué", "embedded", "iot", "arduino", "stm32"],
}


def _pattern(alias):
    return re.compile(r"(?<!\w)" + re.escape(alias) + r"(?!\w)", re.IGNORECASE)


_COMPILED = {
    skill: [_pattern(alias) for alias in aliases]
    for skill, aliases in TAXONOMY.items()
}

_LOOKUP = {
    alias.lower(): skill
    for skill, aliases in TAXONOMY.items()
    for alias in aliases + [skill]
}


def extract_skills(text):
    found = [
        skill
        for skill, patterns in _COMPILED.items()
        if any(p.search(text) for p in patterns)
    ]
    return sorted(found)


def normalize_skills(raw):
    result = []
    for item in raw:
        key = item.strip().lower()
        if not key:
            continue
        skill = _LOOKUP.get(key)
        if skill and skill not in result:
            result.append(skill)
    return result
