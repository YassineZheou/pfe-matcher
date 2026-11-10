# PFE Matcher

Outil en ligne de commande et API qui lit un catalogue de sujets de PFE (PDF ou texte), en extrait
la durée, le nombre de places et les technologies demandées, puis classe les sujets selon les
compétences d'un candidat en indiquant ce qui manque pour chacun.

Le dépôt contient un catalogue de démonstration fictif (`data/`). Aucun sujet réel n'est inclus.

## Fonctionnement

1. **Lecture du PDF** : `pdfplumber`, avec `pypdf` en secours.
2. **Découpage en sujets** : une regex repère les en-têtes de type `REF 001 : Titre`, puis lit la
   durée (`Durée : 4 à 6 mois`) et les places.
3. **Extraction des technologies** : dictionnaire d'alias (`taxonomy` dans `pfe_matcher/skills.py`)
   avec correspondance par mot entier, pour que `Java` ne soit pas détecté dans `JavaScript` ni
   `SQL` dans `PostgreSQL`.
4. **Recherche** : index TF-IDF (unigrammes et bigrammes, scikit-learn) et similarité cosinus.
5. **Score de 0 à 100**, explicable : 70 % de couverture des technologies du sujet par le profil,
   30 % de similarité TF-IDF normalisée par la meilleure similarité du catalogue.
6. **Stockage** : SQLite. Export CSV (séparateur `;`, ouvrable dans Excel ou Power BI).
7. **Lettre de motivation (optionnel)** : paragraphe généré par un LLM via l'API Groq. Le prompt
   n'envoie que les compétences couvertes et manquantes, et demande de ne rien inventer.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
python -m pytest -q
```

## Utilisation

```bash
python -m pfe_matcher ingest data/sample_book.pdf
python -m pfe_matcher match --skills "Python,FastAPI,PostgreSQL,Docker,Streamlit" --top 3
python -m pfe_matcher search "orchestration de pipeline de données"
python -m pfe_matcher export --output topics.csv
```

Sortie de la commande `match` sur le catalogue de démonstration :

```
1. DEMO 006  score 74/100  Observabilité d'un cluster Kubernetes
   couvert : Docker, Python
   manquant : Kubernetes
2. DEMO 004  score 62/100  Classification d'immobilisations par apprentissage automatique
   couvert : Python, Streamlit
   manquant : MLOps, TensorFlow
3. DEMO 003  score 58/100  Pipeline de données Jira vers tableau de bord
   couvert : PostgreSQL, Python
   manquant : Airflow, Power BI
```

Pour générer une lettre pour le meilleur sujet : copier `.env.example` vers `.env`, renseigner
`GROQ_API_KEY`, l'exporter dans l'environnement, puis ajouter `--letter` à la commande `match`.

## API

```bash
uvicorn pfe_matcher.api:app --reload
```

Documentation interactive sur `http://127.0.0.1:8000/docs`.

| Méthode | Route | Rôle |
|---|---|---|
| GET | `/health` | état du service |
| POST | `/topics` | envoi d'un PDF ou d'un fichier texte |
| GET | `/topics` | liste des sujets enregistrés |
| GET | `/match?skills=Python,SQL&top=5` | classement selon un profil |
| GET | `/search?q=scraping` | recherche par similarité |

Docker :

```bash
docker build -t pfe-matcher .
docker run -p 8000:8000 -v pfe-data:/data pfe-matcher
```

## Tests

37 tests (`unittest`, exécutables avec pytest) : extraction des technologies, parsing, scoring,
recherche, base de données, CLI, client LLM avec transport simulé, API. Les tests de l'API sont
ignorés automatiquement si FastAPI n'est pas installé.

## Limites

- Les en-têtes de sujets doivent suivre le format `REF 001 : Titre`. Un catalogue avec une mise en
  page différente demande d'adapter la regex `HEADER` dans `parser.py`.
- Les PDF scannés ne sont pas gérés (pas d'OCR).
- La couverture est un ratio : un sujet où peu de technologies sont détectées peut passer devant un
  sujet plus riche dont le profil couvre moins de technologies (voir le résultat ci-dessus).
- Les poids 70/30 et la liste de technologies sont des choix manuels, pas un modèle appris.
- Le TF-IDF ne comprend pas les synonymes : « apprentissage automatique » et « machine learning »
  sont deux termes distincts.
- Le client LLM n'a été testé qu'avec un transport simulé, pas avec une vraie clé Groq.

## Licence

MIT
