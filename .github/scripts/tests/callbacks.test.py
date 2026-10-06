"""Execute documented callbacks with synthetic metadata, without a station."""

import inspect
import json
from pathlib import Path
import re
import unittest
import warnings

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
AIP = ROOT / "skills/aip-builder"


def examples(path):
    return re.findall(r"^```python\s*\n(.*?)^```\s*$", path.read_text(), re.M | re.S)


def callback(structured=False, classes=None):
    namespace = {"__name__": "documented_callback"}
    if structured:
        probe = examples(AIP / "resources/developer-guide/05-callback-init-probe.md")
        merge = examples(AIP / "resources/developer-guide/07-callback-merge-push.md")
        source = "\n".join([probe[0], *probe[2:], merge[0]])
    else:
        source = examples(AIP / "SKILL.md")[0]
    exec(compile(source, "documented-callback", "exec"), namespace)
    methods = {
        name: value for name, value in namespace.items()
        if inspect.isfunction(value) or isinstance(value, (staticmethod, classmethod))
    }
    instance = type("DocumentedCallback", (), methods)()
    instance.pgie_classes = classes
    instance.initialize()
    return instance


def batch(objects, source_id=0, size=2):
    return {"batch_meta": {"max_frames_in_batch": size, "frame_meta_list": [{
        "source_id": source_id, "frame_num": 1, "ntp_timestamp": 100,
        "num_obj_meta": len(objects) if isinstance(objects, list) else None,
        "obj_meta_list": objects, "frame_user_meta_list": [],
    }]}}


class CallbackTests(unittest.TestCase):
    def merge(self, cb, inputs):
        with warnings.catch_warnings():
            warnings.simplefilter("error", RuntimeWarning)
            result = cb.merge_and_analyze([cb.parse_batch_meta(data) for data in inputs], [])
        json.dumps(result, allow_nan=False)
        return result

    def test_counts_zero_and_statistics(self):
        for structured in (False, True):
            with self.subTest(structured=structured):
                cb = callback(structured, ["person", "car"])
                result = self.merge(cb, [batch([{"class_id": 0}] * 3), batch([])])
                stats = result.get("0", result.get(0))["obj_counter"]["person"]
                self.assertEqual(stats["max_val"], 3)
                self.assertEqual(stats["min_val"], 0)
                self.assertEqual(stats["mean_val"], 1.5)

    def test_callback_output_matches_complete_flow_fixture_contract(self):
        flow = json.loads((ROOT / "skills/node-red-flow-architect/resources/"
                           "people-count-flow.json").read_text())
        expected = json.loads(next(node for node in flow
                                   if node["id"] == "people-valid")["payload"])
        for structured in (False, True):
            cb = callback(structured, ["person"])
            data = batch([{"class_id": 0}] * 3)
            data["batch_meta"]["frame_meta_list"].extend(
                batch([{"class_id": 0}], source_id=1)["batch_meta"]["frame_meta_list"])
            result = json.loads(json.dumps(self.merge(cb, [data]), allow_nan=False))
            projected = {key: {
                "source_id": value["source_id"],
                "obj_counter": {"person": {"max_val": value["obj_counter"]["person"]["max_val"]}},
            } for key, value in result.items()}
            self.assertEqual(projected, expected)

    def test_sources_are_independent_and_unknown_samples_are_excluded(self):
        for structured in (False, True):
            with self.subTest(structured=structured):
                cb = callback(structured, ["person"])
                first = batch([{"class_id": 0}] * 3)
                first["batch_meta"]["frame_meta_list"].extend(
                    batch([], source_id=1)["batch_meta"]["frame_meta_list"])
                result = self.merge(cb, [first, batch(None)])
                person = lambda sid: result.get(str(sid), result.get(sid))["obj_counter"]["person"]
                self.assertEqual(person(0)["min_val"], 3)
                self.assertEqual(person(0)["mean_val"], 3)
                self.assertEqual(person(1)["max_val"], 0)

    def test_invalid_metadata_warning_is_bounded_and_counter_is_not(self):
        for structured in (False, True):
            cb = callback(structured, ["person"])
            with self.assertLogs("documented_callback", level="WARNING") as captured:
                for _ in range(10):
                    cb.parse_batch_meta(None)
            self.assertEqual(len(captured.records), 1)
            self.assertEqual(cb.invalid_metadata_count, 10)

    def test_invalid_source_ids_do_not_raise_or_count(self):
        for structured in (False, True):
            for sid in (0.5, True, -1, "0", None, [], {}):
                with self.subTest(structured=structured, sid=sid):
                    cb = callback(structured, ["person"])
                    result = self.merge(cb, [batch([], source_id=sid)])
                    if result:
                        for source in result.values():
                            self.assertIsNone(source["obj_counter"]["person"]["max_val"])
                    self.assertGreater(cb.invalid_metadata_count, 0)

    def test_malformed_detections_are_unknown_not_zero(self):
        for structured in (False, True):
            for objects in (None, "bad", {}, [None], [{"class_id": 0.5}],
                            [{"class_id": True}], [{"class_id": 99}]):
                with self.subTest(structured=structured, objects=objects):
                    cb = callback(structured, ["person"])
                    result = self.merge(cb, [batch(objects)])
                    if result:
                        self.assertIsNone(result[0]["obj_counter"]["person"]["max_val"])
                    self.assertGreater(cb.invalid_metadata_count, 0)

    def test_invalid_initial_size_retries_on_next_valid_batch(self):
        for size in (-1, 0, 0.5, True, "2", None, 10**9):
            with self.subTest(size=size):
                cb = callback(True, ["person"])
                result = self.merge(cb, [batch([], size=size)])
                self.assertEqual(result, {})
                self.assertTrue(cb.first_time)
                result = self.merge(cb, [batch([{"class_id": 0}])])
                self.assertEqual(result[0]["obj_counter"]["person"]["max_val"], 1)

    def test_missing_metadata_and_no_primary_model(self):
        for structured in (False, True):
            for classes in (None, []):
                with self.subTest(structured=structured, classes=classes):
                    cb = callback(structured, classes)
                    self.assertEqual(self.merge(cb, [None, {}, {"batch_meta": None}]), {})
                    result = self.merge(cb, [batch([])])
                    for source in result.values():
                        self.assertNotIn("person", source["obj_counter"])

    def test_no_person_class_never_invents_person_zero(self):
        for structured in (False, True):
            cb = callback(structured, ["car"])
            result = self.merge(cb, [batch([]), batch([{"class_id": 0}])])
            for source in result.values():
                self.assertNotIn("person", source["obj_counter"])

    def test_bad_frame_numbers_and_rectangles_do_not_break_counting(self):
        cb = callback(True, ["person"])
        data = batch([{"class_id": 0, "rect_params": {"left": "bad"}}])
        data["batch_meta"]["frame_meta_list"][0]["frame_num"] = {"bad": 1}
        result = self.merge(cb, [data])
        self.assertEqual(result[0]["obj_counter"]["person"]["max_val"], 1)
        self.assertIsNone(result[0]["frame_number_from"])
        self.assertEqual(cb.obj_coords_dict[0], [])

    def test_empty_and_malformed_merge_entries(self):
        for structured in (False, True):
            cb = callback(structured, ["person"])
            cb.parse_batch_meta(batch([]))
            self.assertEqual(cb.merge_and_analyze([], []), {})
            self.assertEqual(cb.merge_and_analyze([None, "bad", {}], []), {})


if __name__ == "__main__":
    unittest.main()
