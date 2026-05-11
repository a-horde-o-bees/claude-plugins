# Transcripts `purposes-set` requires shell command-substitution for JSON arg

The `ocd-run transcripts purposes-set <session> '<json>'` CLI takes the JSON payload as a positional argument. For anything past a one- or two-key map, callers write the JSON to a file and inject the file contents into the positional arg via shell command-substitution — which trips the auto-approval matcher and forces a permission prompt on every call.

## Where it bit

Building a time-blocks report across 8 sessions × ~30 exchanges each (Monaco ERP-to-QBO migration, project `-home-dev-projects-monaco-lock-company--erp-migration`). Each session needed one `purposes-set` call to persist 17–127 per-exchange purpose summaries. The agent has no parseable-from-stdin path, so the working pattern was:

```
Write JSON to /tmp/sN_purposes.json
ocd-run transcripts purposes-set <session> "$(python3 -c "import sys; sys.stdout.write(open('/tmp/sN_purposes.json').read())")"
```

The `"$(python3 -c ...)"` form is shell command-substitution and is unparseable for static allowlisting — every invocation surfaced a permission prompt during the report build.

## Suggested fix

Add `--from-file <path>` (and/or accept JSON on stdin when no positional given) to `purposes-set`:

```
ocd-run transcripts purposes-set <session> --from-file /tmp/sN_purposes.json
```

Plain command line; statically analyzable; no shell interpolation needed. Same pattern likely applies to other verbs that take structured-data positional args (`purposes-clear` accepts a list, presumably similar shape).

## Scope

`ocd:transcripts` skill / CLI. The MCP-side `purposes_set` tool already accepts the JSON natively (it's just MCP argument shape); the friction is specifically the CLI's positional-JSON arg shape, which forces the shell-escape workaround for multi-exchange writes.
