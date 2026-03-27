# Conformity Instructions

Reformat target file to conform with project conventions.

1. Discover criteria — run conventions CLI to find applicable conventions and rules
    ```
    python3 ${CLAUDE_PLUGIN_ROOT}/skills/conventions/scripts/conventions_cli.py list-matching <target-file>
    ```
    1. If no criteria match: report "no criteria apply" and stop
    2. If file tagged `[fail: N lines]`: report auto-fail with line count and stop
    3. If file tagged `[warn: N lines]`: note warning, proceed with targeted reads for large file
2. Read all criteria files listed in output
3. Read target file
4. Evaluate target file against its criteria
5. For each {convention} in {applicable-conventions}:
    1. Assess conformity with specific rule citations
    2. Identify fixes for non-conformities found
    - All rules are required unless convention text explicitly marks them as "recommended" or "optional"; report optional non-conformities but do not fix
6. After convention conformity, evaluate internal consistency:
    1. Terminology — ensure same concepts use same terms throughout
    2. Cross-references — ensure internal references (section names, step numbers) match their targets
    3. Completeness — ensure no references to concepts, steps, or sections that do not exist
    4. Identify fixes for inconsistencies found
7. Apply all identified fixes directly to target file using Edit tool. Preserve semantic meaning — reformat and rephrase, never change what file communicates.

After processing, provide report:
1. Changes applied with brief rationale
2. Issues NOT fixed because they require user judgment (semantic ambiguity, structural decisions)
3. Criteria files used
