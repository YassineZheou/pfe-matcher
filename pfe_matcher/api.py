import os

from fastapi import FastAPI, File, HTTPException, Query, UploadFile

from . import __version__, store
from .parser import parse_topics, read_bytes
from .retrieval import TopicIndex
from .scoring import match_topics

app = FastAPI(
    title="PFE Matcher",
    version=__version__,
    description="Extraction de sujets de PFE et classement selon un profil.",
)


def db_path():
    return os.environ.get("PFE_DB", "pfe.db")


@app.get("/health")
def health():
    return {"status": "ok", "version": __version__}


@app.post("/topics")
async def upload_topics(file: UploadFile = File(...)):
    data = await file.read()
    topics = parse_topics(read_bytes(file.filename or "", data))
    if not topics:
        raise HTTPException(status_code=422, detail="Aucun sujet détecté")
    return {"count": store.replace_topics(db_path(), topics)}


@app.get("/topics")
def list_topics():
    return [t.to_dict() for t in store.load_topics(db_path())]


@app.get("/match")
def match(skills: str = Query(...), top: int = Query(5, ge=1, le=50)):
    topics = store.load_topics(db_path())
    if not topics:
        raise HTTPException(status_code=404, detail="Base vide")
    listed = [s.strip() for s in skills.split(",") if s.strip()]
    return [m.to_dict() for m in match_topics(topics, listed, top=top)]


@app.get("/search")
def search(q: str = Query(..., min_length=2), top: int = Query(5, ge=1, le=50)):
    index = TopicIndex(store.load_topics(db_path()))
    return [
        {"ref": t.ref, "title": t.title, "similarity": round(s, 3)}
        for t, s in index.search(q, top=top)
    ]
