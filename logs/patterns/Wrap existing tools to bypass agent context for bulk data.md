# Wrap existing tools to bypass agent context for bulk data

When data flows from external source to local storage in bulk, the agent should orchestrate the move but not be in the data path itself. Data crossing agent context is paid in tokens proportional to its size — every record paid for whether the agent processes it or just passes through.

Build a callable utility that wraps the *same tools* the agent would use (MCP server, API client, file reader). The utility makes the calls, persists results, returns only summary metrics. Don't rebuild auth/transport/error handling that the existing tools already provide.

## When to use

- Bulk data ingestion from MCP server or API to disk
- ETL flows where the agent orchestrates the move but doesn't interpret the data
- Any flow where data records would inflate agent context proportional to their count

## Solution shape

1. Identify the tool the agent would normally call (e.g. `mcp__qbo__search_customers`).
2. Build a Python utility that:
    - Talks to the same MCP server (via the MCP SDK / subprocess launch with stdio transport), or wraps the same API client the MCP exposes
    - Makes the bulk calls, parses results
    - Writes records directly to disk in target format
    - Returns counts and any anomaly summary
3. Agent invokes the utility; receives summary; data never crosses agent context.

## Anti-pattern: agent as pass-through pipe

1. Agent calls API or MCP tool
2. Tool returns data records to agent context
3. Agent re-emits records via Write tool
4. Records land at destination

Pays each record twice in tokens — once entering context, once being re-emitted. For 500+ records, cost compounds linearly with size.

## Anti-pattern: subagent as pass-through pipe

Delegating to a subagent reduces *main-agent* context but doesn't fix the underlying waste — the subagent's context still inflates with the data it's ferrying. Net agent tokens consumed are the same; only the distribution shifts.

## Anti-pattern: rebuilding what the existing tools provide

If the MCP server already handles OAuth, token refresh, error mapping, pagination, response shaping — don't reimplement those in the utility. Wrap the MCP server. The utility's job is to bypass *agent context*, not to duplicate *infrastructure*.

## Pitfalls

- Building a one-off utility for a single ingest. Worth it when ingest is repeated, or when data volume × token-per-record makes the build pay back.
- The utility takes some setup (MCP SDK, subprocess management). Amortize across uses.

## Example

The Monaco QBO comprehensive snapshot pull (~46 MCP calls, hundreds of records, 27 file writes) was delegated to a subagent. Subagent did the work — but data still flowed through its context. A better shape: a Python utility that uses the MCP Python SDK to launch the same `quickbooks-online-mcp-server` process and send tool-call requests via stdio transport. The utility makes the bulk search calls, parses the responses, writes JSONL to disk, returns only entity counts. The agent's role becomes "invoke the utility, check counts" — never ferrying records through context. The MCP server's OAuth handling, pagination, and error mapping all stay where they are.
