"""Regression tests use synthetic fixtures, never station data."""

from datetime import date, timedelta
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location(
    "validate_skills", Path(__file__).resolve().parents[1] / "validate_skills.py"
)
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        self.skill = self.root / "skills/demo-skill"
        self.skill.mkdir(parents=True)
        self.write("skills/demo-skill/SKILL.md",
                   "---\nname: demo-skill\ndescription: Use for synthetic examples.\n"
                   'version: "1.0"\nupdated: 2026-01-01\n---\n# Demo\n')
        self.write("skills/demo-skill/resources/example.md", "# Example\n")
        self.refresh_locks()

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def refresh_locks(self):
        self.write("skills-lock.json", json.dumps({"skills": {"demo-skill": {
            "skillPath": "skills/demo-skill/SKILL.md",
            "computedHash": hashlib.sha256((self.skill / "SKILL.md").read_bytes()).hexdigest(),
        }}}))
        self.write("resources-lock.json", json.dumps({
            "version": 1, "resources": validator.resource_hashes(self.root),
        }))

    def errors(self):
        return "\n".join(validator.validate(self.root))

    def test_valid_package(self):
        self.assertEqual(self.errors(), "")

    def test_root_disclosure_is_checked(self):
        self.write("README.md", "Station: " + "192." + "168.23.45\n")
        self.assertIn("README.md: possible credential", self.errors())

    def test_sensitive_text_checks_generic_credentials(self):
        sample = "sample" + "-only" + "-placeholder"
        credential = "pass" + "word" + "=" + '"' + sample + '"\n'
        path = self.write("README.md", credential)
        self.assertIn(
            "possible credential",
            validator.check_sensitive_text(path, self.root)[0],
        )

    def test_binary_asset_is_not_decoded(self):
        path = self.root / "hero.png"
        path.write_bytes(b"\x89PNG\0\xff")
        self.assertEqual(self.errors(), "")

    def test_root_links_are_checked(self):
        self.write("README.md", "[missing](docs/missing.md)\n")
        self.assertIn("missing/out-of-scope", self.errors())

    def test_skill_link_cannot_escape(self):
        self.write("README.md", "# Package\n")
        path = self.write("skills/demo-skill/resources/example.md",
                          "[outside](../../../README.md)\n")
        self.assertTrue(validator.check_links(self.skill, path, self.root))

    def test_encoded_link_and_anchor(self):
        self.write("skills/demo-skill/resources/a b.md", "# Section\n")
        path = self.write("skills/demo-skill/resources/example.md",
                          "[inside](a%20b.md#section)\n[web](https://example.com)\n")
        self.assertEqual(validator.check_links(self.skill, path, self.root), [])

    def test_python_fences(self):
        path = self.write("skills/demo-skill/resources/example.md",
                          "```python\nx = 1\n```\n```py\nif True\n```\n")
        errors = validator.check_python_examples(path, self.root)
        self.assertEqual(len(errors), 1)
        self.assertIn(":5:", errors[0])

    def test_resource_changes_and_additions_require_lock(self):
        self.write("skills/demo-skill/resources/example.md", "# Changed\n")
        self.assertIn("stale resource", self.errors())
        self.refresh_locks()
        self.assertEqual(self.errors(), "")
        self.write("skills/demo-skill/resources/new.md", "# New\n")
        self.assertIn("stale resource", self.errors())

    def test_resource_removal_requires_lock(self):
        (self.skill / "resources/example.md").unlink()
        self.assertIn("stale resource", self.errors())

    def test_empty_and_missing_skill_package(self):
        self.assertEqual(validator.validate(self.root / "missing"), ["skills directory is missing"])
        (self.skill / "SKILL.md").unlink()
        self.assertIn("missing SKILL.md", self.errors())

    def test_stale_skill_hash(self):
        with (self.skill / "SKILL.md").open("a") as handle:
            handle.write("\nChanged\n")
        self.assertIn("stale computedHash", self.errors())

    def test_malformed_lock_shapes(self):
        for value in ([], {"skills": []}, {"skills": {"demo-skill": None}}):
            with self.subTest(value=value):
                self.write("skills-lock.json", json.dumps(value))
                self.assertIn("lockfile", self.errors())

    def test_invalid_json(self):
        self.write("example.json", "{")
        self.assertIn("invalid JSON", self.errors())

    def test_tracked_generated_file_is_rejected(self):
        self.write(".gitignore", ".agents/\n")
        self.write(".agents/local.md", "# Local\n")
        self.assertEqual(self.errors(), "")
        subprocess.run(["git", "add", "-f", ".agents/local.md"],
                       cwd=self.root, check=True)
        self.assertIn("generated agent files", self.errors())

    def test_missing_tracked_file_is_rejected(self):
        path = self.write("removed.md", "# Removed\n")
        subprocess.run(["git", "add", "removed.md"], cwd=self.root, check=True)
        path.unlink()
        self.assertIn("tracked file is missing", self.errors())

    def test_symlink_is_rejected(self):
        (self.root / "link.md").symlink_to(self.skill / "SKILL.md")
        self.assertIn("symlinks are not supported", self.errors())

    def test_duplicate_frontmatter(self):
        path = self.write("duplicate.md", "---\nname: one\nname: two\n---\n")
        with self.assertRaisesRegex(ValueError, "duplicate"):
            validator.frontmatter(path)

    def test_unterminated_frontmatter(self):
        path = self.write("unterminated.md", "---\nname: demo\n---not-a-delimiter\n")
        with self.assertRaisesRegex(ValueError, "unterminated"):
            validator.frontmatter(path)


class MetadataTests(unittest.TestCase):
    def metadata(self, **changes):
        return dict(name="demo", description="Use for demos.", version="1.0",
                    updated=date.today().isoformat(), **changes)

    def test_version_and_dates(self):
        base = self.metadata()
        self.assertEqual(validator.check_metadata(base, "demo"), [])
        for version in ("latest", "1", "1.x"):
            self.assertTrue(validator.check_metadata({**base, "version": version}, "demo"))
        for updated in ("2026-02-30", "2026-1-1",
                        (date.today() + timedelta(days=1)).isoformat()):
            self.assertTrue(validator.check_metadata({**base, "updated": updated}, "demo"))

    def test_required_fields_and_name(self):
        for key in validator.REQUIRED_FRONTMATTER:
            base = self.metadata()
            del base[key]
            self.assertTrue(validator.check_metadata(base, "demo"))
        self.assertTrue(validator.check_metadata(self.metadata(), "different"))

    def test_private_address_patterns(self):
        for address in ("10." + "23.45.67", "192." + "168.23.45",
                        "172." + "16.23.45", "172." + "31.23.45"):
            self.assertTrue(any(pattern.search(address) for pattern in validator.SECRET_PATTERNS))
        for address in ("203.0.113.10", "172." + "15.23.45", "10.2"):
            self.assertFalse(any(pattern.search(address) for pattern in validator.SECRET_PATTERNS))


class FlowTests(unittest.TestCase):
    def flow(self):
        return [{"id": "tab", "type": "tab"},
                {"id": "node", "type": "inject", "z": "tab", "wires": [[]]}]

    def test_valid_flow_and_subflow(self):
        self.assertEqual(validator.check_flow(self.flow()), [])
        nodes = [{"id": "sub", "type": "subflow"},
                 {"id": "inner", "type": "change", "z": "sub", "wires": []},
                 {"id": "instance", "type": "subflow:sub", "wires": []}]
        self.assertEqual(validator.check_flow(nodes), [])

    def test_malformed_shapes(self):
        for nodes in ({}, [], [None], [{"type": "tab"}],
                      [{"id": "node", "type": None, "z": [], "wires": "bad"}]):
            with self.subTest(nodes=nodes):
                self.assertTrue(validator.check_flow(nodes))

    def test_duplicate_and_dangling_ids(self):
        nodes = self.flow()
        nodes.append(dict(nodes[1]))
        self.assertIn("flow node IDs must be unique", validator.check_flow(nodes))
        nodes = self.flow()
        nodes[1]["wires"] = [["missing"]]
        self.assertTrue(validator.check_flow(nodes))
        nodes[1]["wires"] = [[{}]]
        self.assertTrue(validator.check_flow(nodes))
        nodes[1]["z"] = "missing"
        self.assertTrue(validator.check_flow(nodes))

    def test_inject_json_and_deletion_confirmation(self):
        nodes = self.flow()
        nodes[1].update(payloadType="json", payload="{")
        self.assertTrue(validator.check_flow(nodes))
        nodes[1]["payload"] = json.dumps({"action": "delete", "confirm": False})
        self.assertEqual(validator.check_flow(nodes), [])
        nodes[1]["payload"] = json.dumps({"action": "delete", "confirm": True})
        self.assertTrue(validator.check_flow(nodes))
        nodes[1]["payload"] = json.dumps({"action": "delete", "confirm": False})
        nodes[1]["once"] = True
        self.assertTrue(validator.check_flow(nodes))

    def test_wires_cannot_target_inputless_nodes(self):
        for node_type in ("inject", "catch", "status", "complete", "callback"):
            with self.subTest(node_type=node_type):
                nodes = self.flow()
                nodes.append({"id": "target", "type": node_type, "z": "tab"})
                nodes[1]["wires"] = [["target"]]
                self.assertIn("node: wire targets inputless node target",
                              validator.check_flow(nodes))
        nodes[-1]["type"] = "debug"
        self.assertEqual(validator.check_flow(nodes), [])

    def test_tls_default_is_preserved(self):
        nodes = self.flow()
        nodes[1]["allowInsecureTls"] = True
        self.assertEqual(validator.check_flow(nodes), [])
        nodes[1]["allowInsecureTls"] = False
        self.assertTrue(validator.check_flow(nodes))
        nodes[1]["type"] = "eais-server"
        del nodes[1]["allowInsecureTls"]
        self.assertTrue(validator.check_flow(nodes))

    def test_tab_is_not_a_subflow(self):
        nodes = self.flow()
        nodes[1]["type"] = "subflow:tab"
        self.assertTrue(validator.check_flow(nodes))


class ApiIndexTests(unittest.TestCase):
    def spec(self):
        return {"paths": {"/example": {"get": {"operationId": "example_get"}}}}

    def index(self):
        return "| GET | `/example` | Example | `example_get` | No | None |\n"

    def test_matching_index(self):
        self.assertEqual(validator.check_api_index(self.spec(), self.index()), [])

    def test_missing_stale_and_duplicate_rows(self):
        for index in ("", self.index().replace("GET", "POST"),
                      self.index().replace("/example", "/other"), self.index() * 2):
            self.assertTrue(validator.check_api_index(self.spec(), index))

    def test_invalid_shapes(self):
        for spec in ([], {"paths": []}, {"paths": {"/example": []}},
                     {"paths": {"/example": {"get": {}}}}):
            self.assertTrue(validator.check_api_index(spec, self.index()))


if __name__ == "__main__":
    unittest.main()
