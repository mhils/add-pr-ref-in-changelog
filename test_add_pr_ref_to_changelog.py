import json
from pathlib import Path

import pytest

from add_pr_ref_to_changelog import parse_github_event, patch

testdata = Path(__file__).parent / "testdata"


@pytest.mark.parametrize(
    "filename",
    ["CHANGELOG.md", "CHANGELOG-dashes.md", "CHANGELOG-empty-unreleased-section.md"],
)
def test_patch(filename):
    contents = (testdata / filename).read_text()
    patched = (testdata / filename).with_suffix(".patched.md").read_text()
    assert patch(contents, "ref") == patched


def test_patch_invalid():
    with pytest.raises(ValueError):
        patch("not a changelog", "ref")


@pytest.mark.parametrize(
    "filename,ref",
    [
        (
            "pull_request.json",
            "[#7](https://github.com/mhils/autofixer/pull/7), @mhils",
        ),
        (
            "single_commit.json",
            "[8463e35](https://github.com/mhils/autofixer/commit/8463e355f504ef51cf32ce88b1d15a5d424ad751), @mhils",
        ),
        (
            "multiple_commits.json",
            "[d08930e...c6f4df3](https://github.com/mhils/autofixer/compare/d08930e22592...c6f4df3d4d6d), @mhils, @torvalds",
        ),
        (
            "bot_commits.json",
            "[b331ac2...4725e1e](https://github.com/mitmproxy/mitmproxy/compare/b331ac2520e5...4725e1e12ce8)",
        ),
        (
            "bot_commit.json",
            "[738f791](https://github.com/mitmproxy/pdoc/commit/738f791ac9b6ae94a548e1f57adf8acbb0eb0b3e)",
        ),
    ],
)
def test_parse_event(filename, ref):
    event = json.loads((testdata / filename).read_text())
    assert parse_github_event(event) == ref
