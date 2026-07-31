#!/usr/bin/env bash
# PreToolUse hook (Bash matcher): deny raw git/gh with a redirect to the /git skill.
# Fires before permission rules, so the redirect reason reaches the model; the
# Bash(git/gh) deny rules in the same settings file remain the fail-closed backstop.
# Matches git/gh at any command position (start, &&, ||, ;, |, $(, `) — mirroring
# how the deny rules treat compound commands — while paths containing "git"
# (e.g. this skill's own scripts/gitflow.py) never match.
# Installed by `gitflow.py setup-deny`; source of truth is the git skill folder.
cmd=$(jq -r '.tool_input.command // empty' 2>/dev/null)
# Strip quoted spans first: a command that merely MENTIONS git/gh in a string
# (echo text, heredoc content, test fixtures) is not an invocation.
stripped=$(printf '%s' "$cmd" | sed "s/'[^']*'//g; s/\"[^\"]*\"//g")
if printf '%s' "$stripped" | grep -qE '(^|&&|\|\||;|\||\$\(|`)[[:space:]]*(git|gh)([[:space:]]|$)'; then
  jq -cn '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny", permissionDecisionReason:
    "Raw git/gh is boxed; the /git skill driver is the only route to them. Use the /git skill instead: /git commit · push · ci · checkpoint · pr-open/status/merge/cleanup · contribute (upstream repos) · release · doctor. Read-only history: uv run ~/.claude/skills/git/scripts/gitflow.py read -- <git read verb>. Do not retry the raw command or work around the box."}}'
fi
exit 0
