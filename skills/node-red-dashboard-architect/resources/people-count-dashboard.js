import "../uibuilder/uibuilder.esm.min.js";
import { createApp } from "../uibuilder/vendor/vue/dist/vue.esm-browser.js";

// Synthetic contract: paired with Flow Architect's people-count-flow.json.
const SOURCE_IDS = [0, 1];
const ALARM_STATES = ["normal", "in_fault", "acknowledged_fault", "acknowledged_normal"];

function emptySources() {
  return Object.fromEntries(SOURCE_IDS.map((id) =>
    [id, { source_id: id, count: null, alarm: "unknown" }]));
}

const app = createApp({
  data() {
    return { bySource: emptySources(), messages: [], error: "" };
  },
  computed: {
    sources() {
      return SOURCE_IDS.map((id) => this.bySource[id]);
    },
  },
  methods: {
    formatCount(value) {
      return typeof value === "number" && Number.isFinite(value) ? value : "unknown";
    },
    invalidate(reason) {
      this.bySource = emptySources();
      this.error = reason;
    },
    clearMessages() {
      this.messages = [];
    },
  },
  mounted() {
    uibuilder.onChange("msg", (msg) => {
      if (!msg || typeof msg !== "object" || Array.isArray(msg)) {
        console.warn("Invalid people-count message envelope");
        this.invalidate("Invalid message envelope");
        return;
      }
      this.messages.unshift(msg);
      if (this.messages.length > 100) this.messages.length = 100;
      if (msg.topic === "unknown") {
        this.invalidate(typeof msg.payload?.reason === "string"
          ? msg.payload.reason : "Measurements unavailable");
      } else if (msg.topic === "counts") {
        const entries = msg.payload;
        const valid = Array.isArray(entries) && entries.length === SOURCE_IDS.length
          && SOURCE_IDS.every((id) => entries.filter((entry) => entry?.source_id === id).length === 1)
          && entries.every((entry) => Number.isInteger(entry.count) && entry.count >= 0);
        if (!valid) {
          console.warn("Invalid complete two-source count snapshot");
          this.invalidate("Invalid count snapshot");
          return;
        }
        for (const entry of entries) {
          this.bySource[entry.source_id] = {
            source_id: entry.source_id, count: entry.count, alarm: "unknown",
          };
        }
        this.error = "";
      } else if (msg.topic === "alarm") {
        const id = msg.source_id;
        const alarm = msg.payload?.alarm;
        if (!SOURCE_IDS.includes(id)) {
          console.warn("Alarm for an unconfigured source");
          this.invalidate("Unconfigured alarm source");
          return;
        }
        if (!alarm || !ALARM_STATES.includes(alarm.state)
            || typeof alarm.triggered !== "boolean"
            || !Number.isInteger(alarm.currentValue) || alarm.currentValue < 0
            || this.bySource[id].count !== alarm.currentValue) {
          console.warn("Unknown or invalid alarm result");
          this.bySource[id] = { source_id: id, count: null, alarm: "unknown" };
          this.error = "Unknown or invalid alarm result";
          return;
        }
        this.bySource[id].alarm = alarm.state;
      } else {
        console.warn("Unexpected people-count message topic");
        this.invalidate("Unexpected message topic");
      }
    });
  },
});

app.mount("#app");
