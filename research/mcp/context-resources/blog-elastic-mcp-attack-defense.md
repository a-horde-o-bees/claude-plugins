# MCP Tools: Attack Vectors and Defense Recommendations (Elastic Security Labs)

## Identification
- url: https://www.elastic.co/security-labs/mcp-tools-attack-defense-recommendations
- type: blog post / security research
- author: Carolina Beretta, Gus Carlock, Andrew Pease (Elastic Security Labs)
- last-updated: 2025-09-19
- authority level: community — corporate security research, cited in industry

## Scope
Categorized threat model for MCP servers across four domains. (1) **Traditional code vulnerabilities**: 43% of tested implementations had command-injection flaws; 30% permitted unrestricted URL fetching; SQL injection in DB-connected servers. (2) **Tool poisoning**: hidden override commands in docstrings, data exfiltration via parameter names (e.g. a "context" field asking for system prompts), Base64 / invisible-Unicode obfuscation, implicit manipulation where benign tools alter sibling tools' behavior. (3) **Rug-pull & name collision**: tools changing behavior post-approval, attackers creating similarly-named malicious tools to bias model selection. (4) **Orchestration injection**: multi-tool attacks — a poisoned tool instructing the model to invoke a preauthorized tool (grep) to steal secrets; GitHub-issue-based attacks exfiltrating private repo contents; SSH-key exfiltration via base64 commands hidden in tool docs. Defenses: containerized sandboxing, least-privilege, vet sources, review all tool prompts and code, prefer clients with auditability + approval workflows, avoid "always allow," log and review tool invocations.

## Takeaway summary
The quantitative data here is the most-cited in the ecosystem: 43% command-injection, 30% unrestricted URL-fetching. Use those when making the case for security review to stakeholders who haven't internalized the severity. The four-category taxonomy (code-vuln, tool-poisoning, rug-pull, orchestration-injection) is useful structurally — most MCP security writing reduces to one of these. The orchestration-injection section is the most under-appreciated class: once a user has approved tools A and B independently, A can prompt the model to invoke B in ways neither user-facing description hints at. Defense recommendations are operational — Docker-sandbox the server and client, avoid always-allow, require human confirmation for sensitive ops.

## Use for
- What fraction of MCP servers in the wild have exploitable vulnerabilities? (source numbers)
- What's the canonical four-category threat taxonomy?
- What's "orchestration injection" and how does it differ from tool poisoning?
- What defenses scale operationally (sandboxing, least-privilege, logging)?

## Relationship to other resources
Empirical companion to `blog-simonw-mcp-prompt-injection.md`'s thesis piece. Specific defenses echo the pitfalls section of `mcp-authorization-tutorial.md` but extend beyond auth into tool governance.

## Quality notes
Recent, empirical, cited by follow-on industry research. Numbers are from a specific sample — don't treat 43% as a universal constant for all-time, but they're the best published estimates.
