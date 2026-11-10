import argparse
import json
import sys

from . import store
from .llm import LLMUnavailable, generate_motivation
from .parser import parse_topics, read_file
from .retrieval import TopicIndex
from .scoring import match_topics

DEFAULT_DB = "pfe.db"


def split_skills(value):
    return [s for s in (part.strip() for part in value.split(",")) if s]


def cmd_ingest(args):
    topics = parse_topics(read_file(args.file))
    count = store.replace_topics(args.db, topics)
    print(f"{count} sujets enregistrés dans {args.db}")
    return 0 if count else 1


def cmd_match(args):
    topics = store.load_topics(args.db)
    if not topics:
        print("Base vide : lance d'abord la commande ingest.", file=sys.stderr)
        return 1
    results = match_topics(topics, split_skills(args.skills), top=args.top)
    if args.json:
        print(json.dumps([m.to_dict() for m in results], ensure_ascii=False, indent=2))
        return 0
    for rank, m in enumerate(results, 1):
        print(f"{rank}. {m.topic.ref}  score {m.score}/100  {m.topic.title}")
        print(f"   couvert : {', '.join(m.matched) or '-'}")
        print(f"   manquant : {', '.join(m.missing) or '-'}")
    if args.letter and results:
        best = results[0]
        try:
            print()
            print(generate_motivation(best.topic, best.matched, best.missing))
        except LLMUnavailable as error:
            print(f"LLM indisponible : {error}", file=sys.stderr)
            return 2
    return 0


def cmd_search(args):
    topics = store.load_topics(args.db)
    for topic, sim in TopicIndex(topics).search(args.query, top=args.top):
        print(f"{topic.ref}  {sim:.2f}  {topic.title}")
    return 0


def cmd_export(args):
    count = store.export_csv(store.load_topics(args.db), args.output)
    print(f"{count} sujets exportés dans {args.output}")
    return 0


def build_parser():
    parser = argparse.ArgumentParser(prog="pfe-matcher")
    parser.add_argument("--db", default=DEFAULT_DB)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("ingest")
    p.add_argument("file")
    p.set_defaults(func=cmd_ingest)

    p = sub.add_parser("match")
    p.add_argument("--skills", required=True)
    p.add_argument("--top", type=int, default=5)
    p.add_argument("--json", action="store_true")
    p.add_argument("--letter", action="store_true")
    p.set_defaults(func=cmd_match)

    p = sub.add_parser("search")
    p.add_argument("query")
    p.add_argument("--top", type=int, default=5)
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("export")
    p.add_argument("--output", default="topics.csv")
    p.set_defaults(func=cmd_export)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)
