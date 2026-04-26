"""Transcripts subsystem — extract user/assistant chat from Claude Code transcripts.

Reads ~/.claude/projects/<project>/*.jsonl and writes simplified
`<stem>_chat.json` extracts beside each source. Public surface:

    project_list()                — encoded project folder names
    project_path()                — current project's transcripts directory
    chat_export(projects)         — write extracts; idempotent via git blob hash
    chat_clean(projects)          — remove extracts; sources untouched
"""

from ._transcripts import *  # noqa: F401,F403
