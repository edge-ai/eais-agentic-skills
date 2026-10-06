# External Documentation Lookup via Context7

When you need documentation beyond what is covered in a skill's SKILL.md, use the **Context7 MCP tools** to query official docs on demand.

## How to Use

1. Call `mcp--context7--resolve-library-id` with a keyword to confirm the exact library ID
2. Call `mcp--context7--query-docs` with the library ID and a targeted question
3. Do NOT call Context7 more than **3 times per question** — refine queries rather than repeating

## For UIBuilder Dashboard Tasks

**Libraries:**

| Library ID | Best for |
|------------|----------|
| `/nicedoc/node-red-contrib-uibuilder` | UIBuilder API, configuration, messaging protocol |

**Example queries:**
- `"UIBuilder ESM client API methods"`
- `"How to send messages from browser to Node-RED with uibuilder"`
- `"UIBuilder security and authentication"`
- `"UIBuilder middleware and Express routes"`

**When to query:**
- UIBuilder client API methods beyond `onChange` and `send`
- UIBuilder security/auth configuration
- Custom middleware or API endpoints
- UIBuilder's caching or build behavior
