from __future__ import annotations

import csv
import hashlib
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(".")
SIGNAL = ROOT / "signal"
BRANCHES = SIGNAL / "branches"
CROWNED_WYRM = SIGNAL / "crowned_wyrm"
LOCKED_FRUIT_KEYS = {
    "document_control": "corrected_scope_matters",
    "core_self": "integrated_pattern_kept_whole",
    "aesthetic": "beauty_is_deliberate_signal",
    "food_joy": "joy_makes_survival_easier",
    "social_communication": "ask_before_assuming",
    "doctrine": "harmony_is_integration",
    "learning_memory": "structure_makes_memory_usable",
    "communication_language": "clarity_reduces_ambiguity",
    "creative_technical": "tools_change_function_repeats",
    "joy_play": "play_keeps_the_signal_alive",
    "daily_functioning": "one_next_thing_opens_access",
    "body_load": "capacity_is_not_character",
    "future_path": "future_is_built_not_claimed",
    "mind_regulation": "respect_the_pattern",
    "repair": "care_repairs_in_behavior",
    "consent_privacy": "knowledge_is_not_permission",
    "household_support": "support_the_system_without_taking_it",
    "pets": "gentleness_keeps_the_house_alive",
    "life_history": "witness_without_consuming",
    "relationships_attachment": "consistency_is_the_claim",
    "bureaucracy_systems": "records_reduce_the_burden",
    "shadow_archive": "hard_truth_requires_soft_hands",
    "quick_reference": "help_without_ownership",
    "change_log_self": "corrected_maps_protect_the_self",
    "appendices": "source_labels_preserve_safety",
}
HEARTWOOD_BRANCHES = {"life_history", "relationships_attachment", "shadow_archive", "quick_reference"}


def fail(message: str) -> None:
    raise AssertionError(message)


def read(path: Path) -> str:
    if not path.exists():
        fail(f"missing file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def require(path: Path) -> None:
    if not path.exists():
        fail(f"missing file: {path.relative_to(ROOT)}")


def canonical_start_gate(branch_dir: Path) -> Path:
    gates = sorted(branch_dir.glob("start_gate_[A-D].html"))
    accepted = []
    for gate in gates:
        text = read(gate)
        if "receiver packet did not preserve the signal" not in text:
            accepted.append(gate)
    if len(accepted) != 1:
        fail(f"{branch_dir.name}: expected exactly one accepted start gate, found {len(accepted)}")
    return accepted[0]


def canonical_node_gate(branch_dir: Path, node_id: str) -> Path:
    candidates = sorted(branch_dir.glob(f"{node_id}_gate_*.html"))
    canonical = []
    for path in candidates:
        text = read(path)
        if "technical puzzle:" in text and "care key:" in text and "equivalent signal accepted" not in text:
            canonical.append(path)
    if len(canonical) != 1:
        fail(f"{branch_dir.name}/{node_id}: expected one canonical gate, found {len(canonical)}")
    return canonical[0]


def canonical_node_reward(branch_dir: Path, node_id: str, care_key: str) -> Path:
    candidates = sorted(branch_dir.glob(f"{node_id}_reward_{care_key}__*.html"))
    canonical = []
    for path in candidates:
        text = read(path)
        if "puzzle check:" in text and "node key:" in text and "equivalent signal accepted" not in text:
            canonical.append(path)
    if len(canonical) != 1:
        fail(f"{branch_dir.name}/{node_id}: expected one canonical reward, found {len(canonical)}")
    return canonical[0]


def validate_no_txt() -> dict[str, int]:
    ignored_parts = {"Archived", "References"}
    ignored_names = {"FINAL_PAYLOAD_LOCKED.txt"}
    txt_files = [
        path
        for path in ROOT.rglob("*.txt")
        if path.name not in ignored_names and not any(part in ignored_parts for part in path.parts)
    ]
    if txt_files:
        fail(f"public .txt files remain: {txt_files[0].relative_to(ROOT)}")
    txt_refs = []
    for path in ROOT.rglob("*"):
        if any(part in ignored_parts for part in path.parts):
            continue
        if path.is_file() and path.suffix.lower() in {".html", ".log", ".md", ".js", ".css"}:
            try:
                if ".txt" in path.read_text(encoding="utf-8"):
                    txt_refs.append(path)
            except UnicodeDecodeError:
                continue
    if txt_refs:
        fail(f"public .txt references remain: {txt_refs[0].relative_to(ROOT)}")
    return {"txt_files": 0, "txt_references": 0}


def validate_trunk() -> dict[str, int]:
    trunk_pages = [
        SIGNAL / "hub.html",
        SIGNAL / "layer_01.html",
        SIGNAL / "layer_02.html",
        SIGNAL / "layer_03.html",
        SIGNAL / "layer_04.html",
        SIGNAL / "layer_05.html",
        SIGNAL / "layer_06.html",
        CROWNED_WYRM / "start.html",
        CROWNED_WYRM / "puzzle.html",
        CROWNED_WYRM / "treasure.html",
    ]
    for page in trunk_pages:
        require(page)

    for i in range(1, 7):
        require(SIGNAL / f"layer_{i:02d}_reward.html")

    for page in trunk_pages[:7]:
        text = read(page)
        stale_reward_dir = "trunk_" + "rewards/"
        if f'href="{stale_reward_dir}' in text:
            fail(f"{page.relative_to(ROOT)} exposes a clickable trunk reward path")

    forbidden_reward_links = [
        'href="../layer_',
        'href="../crowned_wyrm/',
        'href="../final_payload.html"',
    ]
    for reward in sorted(SIGNAL.glob("layer_*_reward.html")):
        text = read(reward)
        for forbidden in forbidden_reward_links:
            if reward.name == "layer_01_reward.html" and forbidden == 'href="../layer_' and 'href="../layer_02.log"' in text:
                continue
            if forbidden in text:
                fail(f"{reward.relative_to(ROOT)} exposes a clickable trunk continuation")

    layer_06 = read(SIGNAL / "layer_06_reward.html")
    if "deeper access requires deeper stewardship" not in layer_06:
        fail("layer_06 reward stewardship signal missing")
    if "crowned_wyrm/start.html" not in layer_06:
        fail("layer_06 reward does not point to Crowned Wyrm threshold")
    if "Heartwood branch doors held at threshold" not in layer_06:
        fail("layer_06 reward does not group Heartwood branches separately")
    for branch in HEARTWOOD_BRANCHES:
        if f"branches/{branch}/start.html" not in layer_06:
            fail(f"Heartwood branch missing from layer_06 grouping: {branch}")
    return {"trunk_pages": len(trunk_pages), "layer_fruits": 6}


def validate_branches() -> dict[str, int]:
    branch_dirs = sorted(path for path in BRANCHES.iterdir() if path.is_dir())
    starts = 0
    buds = 0
    bud_fruits = 0

    for branch_dir in branch_dirs:
        start = branch_dir / "start.html"
        require(start)
        start_text = read(start)
        if "node_01.html" not in start_text and "start_gate_" not in start_text:
            fail(f"{branch_dir.name}: start does not point to first node or start gate")
        starts += 1

        node_files = sorted(branch_dir.glob("node_*.html"))
        node_files = [p for p in node_files if re.match(r"node_\d+\.html$", p.name)]
        if not node_files:
            fail(f"{branch_dir.name}: no branch nodes found")

        for node in node_files:
            node_id = node.stem
            node_text = read(node)
            reward = branch_dir / f"{node_id}_reward.html"
            if reward.exists():
                require(reward)
            else:
                reward_candidates = sorted(branch_dir.glob(f"{node_id}_reward*.html"))
                if not reward_candidates:
                    fail(f"{branch_dir.name}/{node_id}: no reward page found")
            if "node_" not in node_text and "reward" not in node_text:
                fail(f"{branch_dir.name}/{node_id}: node lacks branch navigation text")
            buds += 1
            bud_fruits += 1

    return {
        "branches": len(branch_dirs),
        "starts": starts,
        "buds": buds,
        "bud_fruits": bud_fruits,
    }


def validate_aliases() -> dict[str, int]:
    alias_pages = 0
    for path in BRANCHES.glob("*/*.html"):
        text = read(path)
        if "equivalent signal accepted" in text:
            alias_pages += 1
            meta = re.search(r'url=([^"]+)"', text)
            if not meta:
                fail(f"{path.relative_to(ROOT)} alias missing meta refresh")
            target = path.parent / meta.group(1)
            require(target)
    trunk_aliases = sorted(SIGNAL.glob("layer_05_*.html"))
    return {"branch_alias_pages": alias_pages, "trunk_layer_05_alias_pages": len(trunk_aliases)}


def validate_audio() -> dict[str, int]:
    canonical_rewards = 0
    with_buttons = 0
    for path in BRANCHES.glob("*/*reward*.html"):
        text = read(path)
        if "equivalent signal accepted" in text:
            continue
        canonical_rewards += 1
        if 'data-audio-target="reward-audio"' in text and "../../../Assets/audio" in text:
            with_buttons += 1
    if canonical_rewards != with_buttons:
        fail(f"audio coverage mismatch: {with_buttons}/{canonical_rewards}")
    return {"canonical_reward_audio_pages": with_buttons}


def validate_fruit_keys() -> dict[str, int]:
    old_prose_keys = [
        "values are real only when they survive contact with behavior.",
        "beauty is signal; consent is the door.",
        "joy makes survival easier.",
        "the clean question keeps the signal human.",
        "the whole doctrine protects what each part alone could distort.",
        "structure makes memory usable.",
        "tools change; function repeats.",
        "future requires load-bearing steps.",
        "repair is changed behavior.",
        "consent keeps the signal safe.",
        "sanctuary is shared stability.",
        "care beings are not props.",
        "love becomes safe when choice has behavior.",
        "witness without consuming.",
    ]
    for path in BRANCHES.glob("*/*.html"):
        text = read(path)
        for old_key in old_prose_keys:
            if old_key in text:
                fail(f"old prose fruit key remains in {path.relative_to(ROOT)}: {old_key}")

    for branch, key in LOCKED_FRUIT_KEYS.items():
        branch_dir = BRANCHES / branch
        require(branch_dir / "start.html")
        if branch in HEARTWOOD_BRANCHES and "heartwood //" not in read(branch_dir / "start.html"):
            fail(f"Heartwood branch start is not labeled as Heartwood: {branch}")
        found = False
        for path in branch_dir.glob("*reward*.html"):
            text = read(path)
            if key in text and "fruit key" in text:
                found = True
                break
        if not found:
            fail(f"locked fruit key missing or not extractable for {branch}: {key}")

    start_text = read(CROWNED_WYRM / "start.html")
    for key in LOCKED_FRUIT_KEYS.values():
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
        if digest not in start_text:
            fail(f"Crowned Wyrm colored door missing locked key hash for {key}")
    return {"locked_fruit_keys": len(LOCKED_FRUIT_KEYS)}


def validate_crowned_wyrm() -> dict[str, str]:
    required = [
        CROWNED_WYRM / "start.html",
        CROWNED_WYRM / "puzzle.html",
        CROWNED_WYRM / "treasure.html",
        CROWNED_WYRM / "fail.html",
        CROWNED_WYRM / "pass_windows.csv",
        CROWNED_WYRM / "burst_manifest.csv",
        CROWNED_WYRM / "validator_hash.html",
    ]
    for path in required:
        require(path)

    start_text = read(CROWNED_WYRM / "start.html")
    for phrase in [
        "No live targets",
        "No real interception",
        "No unauthorized systems",
        "Only the synthetic signal may be touched",
        "permission to send a signal back",
    ]:
        if phrase not in start_text:
            fail(f"Crowned Wyrm start missing boundary phrase: {phrase}")

    puzzle_text = read(CROWNED_WYRM / "puzzle.html")
    for needle in [
        "pass_windows.csv",
        "burst_manifest.csv",
        "validator_hash.html",
        "Tools/final_boss_validator.py",
        "elevation_deg + snr_db - abs(drift_ppm)",
        "XOR 0x13",
        "sealed fictional signal",
        "No live targets",
    ]:
        if needle not in puzzle_text:
            fail(f"Crowned Wyrm puzzle missing required link or instruction: {needle}")
    if "treasure.html" not in puzzle_text or "ghostlightCrownedWyrmAccepted" not in puzzle_text:
        fail("Crowned Wyrm puzzle does not validate into treasure.html")

    treasure_text = read(CROWNED_WYRM / "treasure.html")
    contact_tool = "Dis" + "cord"
    contact_user = "wynter" + "1990"
    for phrase in [
        "FLAG{dark_signal_received}",
        contact_tool,
        contact_user,
        "respectful contact",
        "You did not win a person",
    ]:
        if phrase not in treasure_text:
            fail(f"Crowned Wyrm treasure missing required phrase: {phrase}")

    contact_hits = []
    ignored_parts = {"Archived", "References"}
    for path in ROOT.rglob("*"):
        if any(part in ignored_parts for part in path.parts):
            continue
        if path.is_file() and path.suffix.lower() in {".html", ".md", ".js", ".css", ".py", ".csv"}:
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if contact_tool in text or contact_user in text:
                contact_hits.append(path)
    allowed = {CROWNED_WYRM / "treasure.html"}
    leaked = [path for path in contact_hits if path not in allowed]
    if leaked:
        fail(f"final contact route leaked outside treasure: {leaked[0].relative_to(ROOT)}")

    pass_rows = list(csv.DictReader((CROWNED_WYRM / "pass_windows.csv").open(newline="", encoding="utf-8")))
    valid = [
        row
        for row in pass_rows
        if row["consent"] == "Y" and row["real_world_source"] == "N" and row["lab_lock"] == "Y"
    ]
    best = max(valid, key=lambda row: int(row["elevation_deg"]) + int(row["snr_db"]) - abs(int(row["drift_ppm"])))
    bursts = list(csv.DictReader((CROWNED_WYRM / "burst_manifest.csv").open(newline="", encoding="utf-8")))
    frames = sorted((row for row in bursts if row["pass_id"] == best["pass_id"]), key=lambda row: int(row["interleave_index"]))
    key = bytes(byte ^ 0x13 for byte in b"".join(bytes.fromhex(row["payload_hex"]) for row in frames)).decode("utf-8")
    if key in puzzle_text or key in treasure_text:
        fail("Crowned Wyrm key is exposed in public pages")

    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
    expected = re.search(r"([a-f0-9]{64})", read(CROWNED_WYRM / "validator_hash.html"))
    if not expected or digest != expected.group(1):
        fail("derived Crowned Wyrm key does not match validator hash")

    result = subprocess.run(
        [sys.executable, "Tools/final_boss_validator.py", key],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        fail("Crowned Wyrm validator rejected derived key")
    return {"valid_pass": best["pass_id"], "validator": "accepted"}


def main() -> int:
    checks = {}
    checks.update(validate_no_txt())
    checks.update(validate_trunk())
    checks.update(validate_branches())
    checks.update(validate_aliases())
    checks.update(validate_audio())
    checks.update(validate_fruit_keys())
    checks.update(validate_crowned_wyrm())
    for key, value in checks.items():
        print(f"{key}: {value}")
    print("sanity_check: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"sanity_check: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
