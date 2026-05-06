import argparse
import json
from pathlib import Path

from .analyze import analyze_threads
from .normalize import normalize_communications
from .render import render_action_brief, render_crm_updates


def main():
    parser = argparse.ArgumentParser(description="Turn client calls/emails/notes into action notes and CRM recommendations.")
    parser.add_argument("--input", default="examples/client-communications.json")
    parser.add_argument("--mode", choices=("brief", "crm"), default="brief")
    args = parser.parse_args()

    raw = json.loads(Path(args.input).read_text())
    analysis = analyze_threads(normalize_communications(raw))
    if args.mode == "crm":
        print(render_crm_updates(analysis))
    else:
        print(render_action_brief(analysis))


if __name__ == "__main__":
    main()
