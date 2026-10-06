#!/usr/bin/env python3
"""Validate the bundled skill package without third-party dependencies."""

from __future__ import annotations

import argparse
import ast
from datetime import date
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
REQUIRED_FRONTMATTER = ("name", "description", "version", "updated")
SECRET_PATTERNS = (
    re.compile(r"\b10(?:\.\d{1,3}){3}\b"),
    re.compile(r"\b192\.168(?:\.\d{1,3}){2}\b"),
    re.compile(r"\b172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}\b"),
    re.compile(r"(?i)password\s*[:=]\s*[\"'][^<\n\"']{6,}[\"']"),
)
LINK_PATTERN = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
FENCE_PATTERN = re.compile(r"^```(?:python|py)\s*\n(.*?)^```\s*$", re.M | re.S)
GENERATED_DIRS = {".agents", ".claude", ".codex", ".cursor", ".windsurf"}


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("missing YAML frontmatter")
    delimiter = re.search(r"^---\s*$", text[4:], re.M)
    if delimiter is None:
        raise ValueError("unterminated YAML frontmatter")
    end = 4 + delimiter.start()
    values: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            raise ValueError("frontmatter must use single-line key/value fields")
        key, value = line.split(":", 1)
        key = key.strip()
        if key in values:
            raise ValueError(f"duplicate frontmatter field {key}")
        values[key] = value.strip().strip("\"'")
    return values


def check_metadata(metadata: dict[str, str], name: str) -> list[str]:
    errors = []
    for key in REQUIRED_FRONTMATTER:
        if not metadata.get(key):
            errors.append(f"missing frontmatter field {key}")
    if metadata.get("name") != name:
        errors.append("name does not match directory")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        errors.append("name must use lowercase letters, digits and single hyphens")
    if not re.fullmatch(r"\d+\.\d+(?:\.\d+)?", metadata.get("version", "")):
        errors.append("version must be a numeric major.minor or major.minor.patch")
    updated = metadata.get("updated", "")
    try:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", updated):
            raise ValueError
        if date.fromisoformat(updated) > date.today():
            errors.append("updated date is in the future")
    except ValueError:
        errors.append("updated must be a valid YYYY-MM-DD date")
    return errors


def check_links(scope: Path, path: Path, root: Path = ROOT) -> list[str]:
    errors = []
    for target in LINK_PATTERN.findall(path.read_text(encoding="utf-8")):
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        target = target.removeprefix("<").removesuffix(">")
        target_path = (path.parent / unquote(target.split("#", 1)[0])).resolve()
        if not target_path.exists() or not target_path.is_relative_to(scope.resolve()):
            errors.append(f"{path.relative_to(root)} links to missing/out-of-scope {target}")
    return errors


def package_files(root: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return sorted({root / name for name in result.stdout.split("\0") if name})


def check_sensitive_text(path: Path, root: Path = ROOT) -> list[str]:
    content = path.read_bytes()
    if b"\0" in content:
        return []
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return []
    if any(pattern.search(text) for pattern in SECRET_PATTERNS):
        return [f"{path.relative_to(root)}: possible credential or private infrastructure literal"]
    return []


def check_python_examples(path: Path, root: Path) -> list[str]:
    errors = []
    text = path.read_text(encoding="utf-8")
    for match in FENCE_PATTERN.finditer(text):
        line = text[:match.start(1)].count("\n") + 1
        try:
            ast.parse(match.group(1))
        except SyntaxError as exc:
            errors.append(f"{path.relative_to(root)}:{line + (exc.lineno or 1) - 1}: "
                          f"invalid Python example ({exc.msg})")
    return errors


def check_flow(nodes: object) -> list[str]:
    if not isinstance(nodes, list) or not nodes:
        return ["flow must be a nonempty array"]
    if any(not isinstance(node, dict) for node in nodes):
        return ["flow nodes must be objects"]
    errors = []
    ids = [node.get("id") for node in nodes]
    if any(not isinstance(node_id, str) or not node_id for node_id in ids):
        return ["flow nodes must have nonempty string IDs"]
    if len(ids) != len(set(ids)):
        errors.append("flow node IDs must be unique")
    containers = {node["id"] for node in nodes if node.get("type") in ("tab", "subflow")}
    subflows = {node["id"] for node in nodes if node.get("type") == "subflow"}
    nodes_by_id = {node["id"]: node for node in nodes}
    for node in nodes:
        label = node["id"]
        if not isinstance(node.get("type"), str) or not node["type"]:
            errors.append(f"{label}: missing node type")
        parent = node.get("z", "")
        if not isinstance(parent, str) or (parent and parent not in containers):
            errors.append(f"{label}: unknown tab/subflow")
        wires = node.get("wires", [])
        if not isinstance(wires, list) or any(not isinstance(output, list) for output in wires):
            errors.append(f"{label}: wires must be arrays of target arrays")
        else:
            for output in wires:
                for target in output:
                    if not isinstance(target, str) or target not in ids:
                        errors.append(f"{label}: dangling wire")
                    elif nodes_by_id[target].get("type") in (
                        "inject", "catch", "status", "complete", "callback",
                    ):
                        errors.append(f"{label}: wire targets inputless node {target}")
        if (isinstance(node.get("type"), str) and node["type"].startswith("subflow:")
                and node["type"][8:] not in subflows):
            errors.append(f"{label}: unknown subflow instance")
        if node.get("type") == "inject" and node.get("payloadType") == "json":
            try:
                payload = json.loads(node.get("payload", ""))
            except (TypeError, json.JSONDecodeError):
                errors.append(f"{label}: invalid JSON inject payload")
                continue
            if isinstance(payload, dict) and payload.get("action") == "delete":
                if not payload.get("uuid") and payload.get("confirm") is not False:
                    errors.append(f"{label}: bulk deletion example must require confirmation")
                if node.get("once") or node.get("repeat") or node.get("crontab"):
                    errors.append(f"{label}: deletion must not run automatically")
        if (node.get("type") == "eais-server" or "allowInsecureTls" in node) and node.get("allowInsecureTls") is not True:
            errors.append(f"{label}: reference must preserve the station TLS default")
    return errors


def check_api_index(spec: object, index: str) -> list[str]:
    if not isinstance(spec, dict) or not isinstance(spec.get("paths"), dict):
        return ["API snapshot must contain a paths object"]
    operations = set()
    operation_ids = []
    methods = {"get", "post", "put", "patch", "delete", "head", "options", "trace"}
    for path, item in spec["paths"].items():
        if not isinstance(item, dict):
            return ["API path items must be objects"]
        for method, operation in item.items():
            if method not in methods:
                continue
            if not isinstance(operation, dict) or not isinstance(operation.get("operationId"), str):
                return ["API operations must have string operationId fields"]
            operations.add((method.upper(), path, operation["operationId"]))
            operation_ids.append(operation["operationId"])
    indexed = []
    for line in index.splitlines():
        columns = [column.strip() for column in line.split("|")]
        if len(columns) >= 5 and columns[1].lower() in methods:
            indexed.append((columns[1], columns[2].strip("`"), columns[4].strip("`")))
    errors = []
    if len(operation_ids) != len(set(operation_ids)):
        errors.append("API operation IDs must be unique")
    if len(indexed) != len(set(indexed)):
        errors.append("API index has duplicate operations")
    if set(indexed) != operations:
        errors.append("API index method/path/operationId inventory differs from snapshot")
    return errors


def resource_hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted((root / "skills").glob("*/resources/**/*"))
        if path.is_file() and not path.is_symlink()
    }


def read_object(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("expected a JSON object")
    return value


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    skills = root / "skills"
    if not skills.is_dir():
        return ["skills directory is missing"]
    skill_dirs = sorted(path for path in skills.iterdir() if path.is_dir())
    if not skill_dirs:
        errors.append("package must contain at least one skill")
    names: list[str] = []

    for skill_dir in skill_dirs:
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            errors.append(f"{skill_dir.relative_to(root)} is missing SKILL.md")
            continue
        try:
            metadata = frontmatter(skill_file)
        except (OSError, ValueError) as exc:
            errors.append(f"{skill_file.relative_to(root)}: {exc}")
            continue
        errors.extend(f"{skill_file.relative_to(root)}: {error}"
                      for error in check_metadata(metadata, skill_dir.name))
        names.append(skill_dir.name)

    for path in package_files(root):
        relative = path.relative_to(root)
        if any(part in GENERATED_DIRS for part in relative.parts):
            errors.append(f"{relative}: generated agent files must not be tracked")
        if path.is_symlink():
            errors.append(f"{relative}: package symlinks are not supported")
            continue
        if not path.is_file():
            errors.append(f"{relative}: tracked file is missing")
            continue
        errors.extend(check_sensitive_text(path, root))
        if path.suffix == ".md":
            scope = root
            if len(relative.parts) >= 3 and relative.parts[0] == "skills":
                scope = skills / relative.parts[1]
            errors.extend(check_links(scope, path, root))
            errors.extend(check_python_examples(path, root))
        if path.suffix == ".json":
            try:
                value = json.loads(path.read_text(encoding="utf-8"))
                if path.name in ("eais-reference-flow.json", "people-count-flow.json"):
                    errors.extend(f"{relative}: {error}" for error in check_flow(value))
                if path.name in ("ms2-openapi.json", "ms3-openapi.json"):
                    index_path = path.with_name(path.name.replace("-openapi.json", "-endpoints.md"))
                    if not index_path.is_file():
                        errors.append(f"{relative}: endpoint index is missing")
                    else:
                        errors.extend(f"{relative}: {error}" for error in check_api_index(
                            value, index_path.read_text(encoding="utf-8")))
            except (UnicodeError, json.JSONDecodeError) as exc:
                errors.append(f"{relative}: invalid JSON ({exc})")

    if len(names) != len(set(names)):
        errors.append("skill names are not unique")

    try:
        lock = read_object(root / "skills-lock.json")
        locked = lock["skills"]
        if not isinstance(locked, dict):
            raise ValueError("skills must be an object")
    except (OSError, KeyError, ValueError) as exc:
        errors.append(f"skills-lock.json: invalid lockfile ({exc})")
        locked = {}

    if set(locked) != set(names):
        errors.append(f"lockfile skills {sorted(locked)} do not match published skills {sorted(names)}")
    for name in names:
        entry = locked.get(name, {})
        if not isinstance(entry, dict):
            errors.append(f"lockfile entry {name} must be an object")
            continue
        skill_file = skills / name / "SKILL.md"
        expected_hash = hashlib.sha256(skill_file.read_bytes()).hexdigest()
        if entry.get("skillPath") != f"skills/{name}/SKILL.md":
            errors.append(f"lockfile entry {name} has incorrect skillPath")
        if entry.get("computedHash") != expected_hash:
            errors.append(f"lockfile entry {name} has stale computedHash")

    try:
        resource_lock = read_object(root / "resources-lock.json")
        if resource_lock.get("version") != 1:
            errors.append("resources-lock.json: unsupported version")
        if resource_lock.get("resources") != resource_hashes(root):
            errors.append("resources-lock.json: stale resource hashes or inventory")
    except (OSError, ValueError) as exc:
        errors.append(f"resources-lock.json: invalid resource lock ({exc})")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-resource-lock", action="store_true",
                        help="refresh the resource inventory after reviewing resource changes")
    args = parser.parse_args()
    if args.write_resource_lock:
        (ROOT / "resources-lock.json").write_text(
            json.dumps({"version": 1, "resources": resource_hashes(ROOT)}, indent=2) + "\n",
            encoding="utf-8",
        )
        print("Updated resources-lock.json; review the diff before committing.")
        return 0
    errors = validate(ROOT)

    if errors:
        for error in errors:
            fail(error)
        return 1
    print("Validated package files, skill metadata, links, Python examples, flow structure, "
          "API indexes, and skill/resource hashes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
