# Self-Evaluation Conformity Instructions

Reformat target convention or rule file for structural, notation, and formatting conformity. Semantic content is not modified — differences in meaning between target and criteria are observations for user review, not violations to fix.

1. Discover criteria — run conventions CLI to find applicable conventions and rules
    ```
    python3 ${CLAUDE_PLUGIN_ROOT}/run.py skills.conventions list-matching <target-file>
    ```
    1. If no criteria match: report "no criteria apply" and stop
    2. If file tagged `[fail: N lines]`: report auto-fail with line count and stop
    3. If file tagged `[warn: N lines]`: note warning, proceed with targeted reads for large file
2. Read all criteria files listed in output
3. Read target file
4. Evaluate target file against its criteria — categorize each finding:
    1. Structural fix — change affects how content is expressed (formatting, notation, indentation, heading structure, grammar) without altering what rules or guidance the file provides
    2. Observation — change would alter what rules or guidance the file provides; target may intentionally define stricter, looser, or alternative guidance for its domain
    - All rules are required unless convention text explicitly marks them as "recommended" or "optional"; report optional non-conformities but do not fix
5. Evaluate internal consistency:
    1. Terminology — ensure the same concepts use the same terms throughout
    2. Cross-references — ensure internal references (section names, step numbers) match their targets
    3. Completeness — ensure no references to concepts, steps, or sections that do not exist
    4. Identify fixes for inconsistencies found
6. Apply structural fixes and internal consistency fixes directly to target file using Edit tool. Do not modify semantic content — never change what rules the file defines, what guidance it provides, or what constraints it establishes.

After processing, provide report:
1. Changes applied with brief rationale
2. Observations — semantic differences between target and criteria requiring user judgment
3. Issues NOT fixed because they require user judgment (structural decisions with semantic implications)
4. Criteria files used
