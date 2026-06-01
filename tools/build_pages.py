from __future__ import annotations

import argparse
import html
import json
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "Tools"
TEMPLATE_DIR = TOOLS / "build_templates"
DATA_FILE = TOOLS / "build_data" / "tree_inventory.json"
PREVIEW_DIR = TOOLS / "build_preview"

ASCII_KEY = """      ___
     / _ \\
    / /_\\ \\
   /  _  _\\___
  /__/ \\_____/
      ||
      ||==[ ]==[ ]==
      ||"""


def load_data() -> dict:
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def load_template(name: str) -> str:
    return (TEMPLATE_DIR / name).read_text(encoding="utf-8")


def esc(value: object) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def raw(value: object) -> str:
    return "" if value is None else str(value)


def render_template(name: str, values: dict[str, object]) -> str:
    text = load_template(name)
    for key, value in values.items():
        text = text.replace("{{ " + key + " }}", raw(value))
    leftovers = re.findall(r"{{\s*([a-zA-Z0-9_]+)\s*}}", text)
    if leftovers:
        raise ValueError(f"{name} missing template values: {', '.join(sorted(set(leftovers)))}")
    return text


def base_page(site: dict, title: str, content: str, *, body_class: str = "") -> str:
    return render_template(
        "base.html",
        {
            "title": esc(title),
            "stylesheet": esc(site.get("stylesheet", "../../../style.css")),
            "script": esc(site.get("script", "../../../script.js?v=generated-pages-1")),
            "body_class": f' class="{esc(body_class)}"' if body_class else "",
            "content": content,
        },
    )


def nav_links(items: list[dict[str, str]]) -> str:
    links = "".join(f'        <li><a href="{esc(item["href"])}">{esc(item["label"])}</a></li>\n' for item in items)
    return f"      <ul class=\"nav-links\">\n{links}      </ul>"


def audio_block(src: str | None) -> str:
    if not src:
        return ""
    return (
        "      <section class=\"audio-panel\">\n"
        "        <button class=\"audio-button\" data-audio-target=\"reward-audio\">Play Signal</button>\n"
        "        <audio id=\"reward-audio\" preload=\"none\">\n"
        f"          <source src=\"{esc(src)}\" type=\"audio/wav\">\n"
        "        </audio>\n"
        "        <p class=\"audio-status\" aria-live=\"polite\"></p>\n"
        "      </section>"
    )


def normalized_js_array(values: list[str]) -> str:
    return ", ".join(json.dumps(value) for value in values)


def validator_script(branch_id: str, bud: dict, success_href: str) -> str:
    form_id = f"{branch_id}-node-{int(bud['number']):02d}-form"
    input_id = f"{branch_id}-node-{int(bud['number']):02d}-answer"
    status_id = f"{branch_id}-node-{int(bud['number']):02d}-status"
    accepted_terms = bud.get("accepted_terms", [])
    term_checks = []
    for group in accepted_terms:
        terms = " && ".join(f'key.indexOf("{term}") !== -1' for term in group)
        term_checks.append(f"        if ({terms}) return true;")
    term_block = "\n".join(term_checks)
    return f"""      <script>
        (function () {{
          const form = document.getElementById("{form_id}");
          const input = document.getElementById("{input_id}");
          const status = document.getElementById("{status_id}");
          function compact(value) {{
            return String(value || "").trim().toLowerCase().replace(/[^a-z0-9]/g, "");
          }}
          function accepts(value) {{
            const key = compact(value);
            const rejected = new Set([{normalized_js_array(bud.get("rejected", []))}]);
            if (rejected.has(key)) return false;
            const exact = new Set([{normalized_js_array(bud.get("accepted", []))}]);
            if (exact.has(key)) return true;
{term_block}
            return false;
          }}
          form.addEventListener("submit", function (event) {{
            event.preventDefault();
            const key = compact(input.value);
            if (!key) {{
              status.textContent = {json.dumps(bud.get("empty_status", "empty response"))};
              return;
            }}
            if (accepts(input.value)) {{
              status.textContent = {json.dumps(bud.get("success_status", "packet accepted"))};
              window.location.href = "{success_href}";
            }} else {{
              status.textContent = {json.dumps(bud.get("fail_status", "packet rejected"))};
              window.location.href = "../../fail/care_gate_failed.html";
            }}
          }});
        }}());
      </script>"""


def render_branch_start(site: dict, branch: dict) -> str:
    branch_id = branch["id"]
    content = render_template(
        "branch_start.html",
        {
            "breadcrumb": esc(f"{branch_id} // branch"),
            "h1": esc(f"GHOSTLIGHT PROTOCOL // {branch['name'].upper()} BRANCH"),
            "branch_purpose": esc(branch["branch_purpose"]),
            "access_note": esc(branch["access_note"]),
            "wwc_sections": esc(branch["wwc_sections"]),
            "nav": nav_links(
                [
                    {"href": "node_01.html", "label": "enter branch"},
                    {"href": f"../../{branch['trunk_layer']}.html", "label": branch["trunk_label"]},
                    {"href": "../../hub.html", "label": "hub"},
                ]
            ),
        },
    )
    return base_page(site, f"GHOSTLIGHT PROTOCOL // {branch['name'].upper()} BRANCH", content, body_class="no-auto-branch-form")


def render_bud(site: dict, branch: dict, bud: dict) -> str:
    num = int(bud["number"])
    branch_id = branch["id"]
    next_href = f"node_{num:02d}_reward.html"
    form_id = f"{branch_id}-node-{num:02d}-form"
    input_id = f"{branch_id}-node-{num:02d}-answer"
    status_id = f"{branch_id}-node-{num:02d}-status"
    content = render_template(
        "bud.html",
        {
            "breadcrumb": esc(f"{branch_id} // bud {num:02d} // difficulty {bud['difficulty']}"),
            "h1": esc(bud["h1"]),
            "theme": esc(bud["theme"]),
            "prompt": esc(bud["prompt"]),
            "body": esc(bud["body"]),
            "warning": esc(bud["warning"]),
            "answer_prompt": esc(bud["answer_prompt"]),
            "form_id": esc(form_id),
            "input_id": esc(input_id),
            "status_id": esc(status_id),
            "label": esc(bud["label"]),
            "placeholder": esc(bud["placeholder"]),
            "nav": nav_links(
                [
                    {"href": f"../../{branch['trunk_layer']}.html", "label": f"return to {branch['trunk_label']}"},
                    {"href": "../../hub.html", "label": "hub"},
                ]
            ),
            "validator_script": validator_script(branch_id, bud, next_href),
        },
    )
    return base_page(site, f"GHOSTLIGHT PROTOCOL // {branch['name']} // {bud['h1']}", content)


def render_bloom(site: dict, branch: dict, bud: dict, next_bud: dict | None) -> str:
    num = int(bud["number"])
    bloom = bud["bloom"]
    nav = []
    if next_bud:
        nav.append({"href": f"node_{int(next_bud['number']):02d}.html", "label": "next bud"})
    nav.extend(
        [
            {"href": f"../../{branch['trunk_layer']}.html", "label": f"return to {branch['trunk_label']}"},
            {"href": "../../hub.html", "label": "hub"},
        ]
    )
    content = render_template(
        "bloom.html",
        {
            "breadcrumb": esc(f"{branch['id']} // bud {num:02d} bloom"),
            "h1": esc(bloom["h1"]),
            "reveal_text": esc(bloom["reveal_text"]),
            "audio": audio_block(site.get("audio_src")),
            "nav": nav_links(nav),
        },
    )
    return base_page(site, f"GHOSTLIGHT PROTOCOL // {branch['name']} // Bud {num:02d} Bloom", content)


def render_fruit(site: dict, branch: dict, bud: dict) -> str:
    fruit = bud["fruit"]
    nav = []
    if fruit.get("next_trunk"):
        nav.append(fruit["next_trunk"])
    nav.extend(
        [
            {"href": f"../../{branch['trunk_layer']}.html", "label": f"return to {branch['trunk_label']}"},
            {"href": "../../hub.html", "label": "hub"},
        ]
    )
    content = render_template(
        "fruit.html",
        {
            "breadcrumb": esc(f"{branch['id']} // branch fruit"),
            "h1": esc(fruit["h1"]),
            "synthesis_text": esc(fruit["synthesis_text"]),
            "fruit_key": esc(branch["fruit_key"]),
            "color_class": esc(branch["color"]),
            "color_label": esc(branch["color"]),
            "ascii_key": esc(ASCII_KEY),
            "audio": audio_block(site.get("audio_src")),
            "nav": nav_links(nav),
        },
    )
    return base_page(site, f"GHOSTLIGHT PROTOCOL // {branch['name']} // Fruit", content)


def render_failure(site: dict, failure: dict) -> str:
    content = render_template(
        "failure.html",
        {
            "h1": esc(failure["h1"]),
            "explanation": esc(failure["explanation"]),
            "nav": nav_links([{"href": "../hub.html", "label": "hub"}]),
        },
    )
    return base_page(site, failure["title"], content)


def render_pages(data: dict, output_root: Path) -> list[Path]:
    site = data["site"]
    written: list[Path] = []

    for branch in data["branches"]:
        branch_dir = output_root / "signal" / "branches" / branch["id"]
        branch_dir.mkdir(parents=True, exist_ok=True)
        pages = {"start.html": render_branch_start(site, branch)}
        buds = branch["buds"]
        for index, bud in enumerate(buds):
            num = int(bud["number"])
            pages[f"node_{num:02d}.html"] = render_bud(site, branch, bud)
            if "fruit" in bud:
                pages[f"node_{num:02d}_reward.html"] = render_fruit(site, branch, bud)
            else:
                pages[f"node_{num:02d}_reward.html"] = render_bloom(site, branch, bud, buds[index + 1] if index + 1 < len(buds) else None)
        for filename, text in pages.items():
            path = branch_dir / filename
            path.write_text(text, encoding="utf-8", newline="\n")
            written.append(path)

    fail_dir = output_root / "signal" / "fail"
    fail_dir.mkdir(parents=True, exist_ok=True)
    for failure in data.get("failures", []):
        path = fail_dir / f"{failure['id']}.html"
        path.write_text(render_failure(site, failure), encoding="utf-8", newline="\n")
        written.append(path)

    return written


def extract_h1(text: str) -> str:
    match = re.search(r"<h1>(.*?)</h1>", text, re.S | re.I)
    return re.sub(r"\s+", " ", match.group(1)).strip() if match else ""


def compare_preview_to_live(preview_root: Path, generated: list[Path]) -> tuple[int, list[str]]:
    checked = 0
    warnings: list[str] = []
    for preview_path in generated:
        rel = preview_path.relative_to(preview_root)
        live_path = ROOT / rel
        if not live_path.exists():
            warnings.append(f"missing live counterpart: {rel}")
            continue
        checked += 1
        preview_text = preview_path.read_text(encoding="utf-8")
        live_text = live_path.read_text(encoding="utf-8")
        if extract_h1(preview_text).lower() != extract_h1(live_text).lower():
            warnings.append(f"h1 differs: {rel}")
        key_match = re.search(r"<code>([a-z0-9_]+)</code>", preview_text)
        if key_match and key_match.group(1) not in live_text:
            warnings.append(f"fruit key differs: {rel}")
    return checked, warnings


def run_preview() -> int:
    data = load_data()
    if PREVIEW_DIR.exists():
        shutil.rmtree(PREVIEW_DIR)
    generated = render_pages(data, PREVIEW_DIR)
    checked, warnings = compare_preview_to_live(PREVIEW_DIR, generated)
    print(f"generated_pages: {len(generated)}")
    print(f"preview_dir: {PREVIEW_DIR.relative_to(ROOT)}")
    print(f"live_pages_compared: {checked}")
    for warning in warnings[:20]:
        print(f"compare_warning: {warning}")
    return 1 if warnings else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Ghostlight pages from shared templates and structured data.")
    parser.add_argument("--check", action="store_true", help="Generate preview output and fail if it cannot be compared to live pilot pages.")
    parser.add_argument("--preview", action="store_true", help="Generate preview output under Tools/build_preview.")
    args = parser.parse_args()
    return run_preview()


if __name__ == "__main__":
    raise SystemExit(main())
