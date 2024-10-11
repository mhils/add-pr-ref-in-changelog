#!/usr/bin/env python3
import json
import os
import re
from pathlib import Path


def parse_github_event(event) -> str:
    try:
        authors = "@" + event["pull_request"]["user"]["login"]
        pr_num = event["pull_request"]["number"]
        pr_url = event["pull_request"]["html_url"]
        change_link = f"[#{pr_num}]({pr_url})"
    except KeyError:
        if len(event["commits"]) == 1:
            author = event["head_commit"]["author"].get("username", None)
            authors = "@" + author if author else ""
            commit_url = event["head_commit"]["url"]
            change_link = f"[{event['head_commit']['id'][:7]}]({commit_url})"
        else:
            authors = ", ".join(
                dict.fromkeys(
                    f"@{username}"
                    for c in event["commits"]
                    if (username := c["author"].get("username"))
                )
            )
            compare_url = event["compare"]
            change_link = (
                f"[{event['before'][:7]}...{event['after'][:7]}]({compare_url})"
            )
    return f"{change_link}, {authors}".removesuffix(", ")


def patch(contents: str, ref: str) -> str:
    def add_ref(m) -> str:
        if m[0].strip().endswith(")"):
            return m[0]
        space = re.sub("[*-]", " ", m[1])
        # insert ref between last non-whitespace character and rest.
        return re.sub(r"^([\s\S]+?)(\s*)$", rf"\g<1>\n{space}({ref})\g<2>", m[0])

    try:
        head, unreleased, rest = re.split("^(?=##)", contents, 2, re.MULTILINE)
    except ValueError as e:
        raise ValueError("Invalid changelog format.") from e

    unreleased = re.sub(
        r"""
        ^([ \t]*[*\-][ ]+)(?:.(?!^\1))+
        """,
        add_ref,
        unreleased,
        flags=re.VERBOSE | re.DOTALL | re.MULTILINE,
    )

    if "\n" in unreleased.strip():
        unreleased = unreleased.rstrip() + "\n\n"

    return f"{head}{unreleased}{rest}"


if __name__ == "__main__":
    event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text())
    try:
        ref = parse_github_event(event)
    except Exception:
        print(f"Failed to parse {event=}")
        raise

    changelog = Path("CHANGELOG.md")
    changelog.write_text(patch(changelog.read_text("utf8"), ref), "utf8")
