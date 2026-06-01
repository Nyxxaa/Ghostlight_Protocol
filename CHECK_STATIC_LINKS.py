from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(".")
IGNORED_PARTS = {"Archived", "References", "build_templates", "build_preview"}


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for key, value in attrs:
            if key in {"href", "src"} and value:
                self.refs.append(value)


def main() -> int:
    missing: list[tuple[Path, str]] = []
    for path in ROOT.rglob("*.html"):
        if any(part in IGNORED_PARTS for part in path.parts):
            continue
        parser = LinkParser()
        parser.feed(path.read_text(encoding="utf-8"))
        for ref in parser.refs:
            if ref.startswith(("http:", "https:", "javascript:", "#", "mailto:")):
                continue
            ref_path = ref.split("?", 1)[0]
            target = (path.parent / ref_path).resolve()
            try:
                target.relative_to(ROOT.resolve())
            except ValueError:
                continue
            if not target.exists():
                missing.append((path, ref))

    print(f"missing_count {len(missing)}")
    for path, ref in missing[:100]:
        print(f"{path} -> {ref}")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
