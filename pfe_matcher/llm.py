import json
import os
import urllib.request

URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"


class LLMUnavailable(RuntimeError):
    pass


def build_prompt(topic, matched, missing):
    return (
        "Rédige un paragraphe de motivation de 5 phrases maximum pour une "
        "candidature de PFE. Utilise uniquement les faits fournis, "
        "n'invente aucune expérience ni aucun chiffre.\n"
        f"Sujet : {topic.ref} - {topic.title}\n"
        f"Compétences du candidat qui correspondent : {', '.join(matched) or 'aucune'}\n"
        f"Compétences à acquérir : {', '.join(missing) or 'aucune'}\n"
        "Présente les compétences à acquérir comme un axe d'apprentissage."
    )


def _post(payload, api_key):
    request = urllib.request.Request(
        URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def generate_motivation(topic, matched, missing, api_key=None, send=None):
    key = api_key or os.environ.get("GROQ_API_KEY")
    if send is None:
        if not key:
            raise LLMUnavailable("GROQ_API_KEY manquante")
        send = _post
    payload = {
        "model": MODEL,
        "temperature": 0.3,
        "messages": [{"role": "user", "content": build_prompt(topic, matched, missing)}],
    }
    data = send(payload, key)
    return data["choices"][0]["message"]["content"].strip()
