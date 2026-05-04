# Sample

Mirrors of `https://github.com/Azure/azure-mcp`. C# MCP server for Azure cloud APIs. 1.2k stars, MIT, default branch `main` (read-only). Repository archived: GitHub archival flag set Feb 6, 2026; README body states "This repository is archived as of August 25, 2025." The two dates disagree — the August 2025 README notice predates the official GitHub-archived flag (Feb 2026); most likely the code stopped getting updates in Aug 2025 but the repo was formally archived four months later. Code consolidated into `microsoft/mcp` umbrella as the `Azure.Mcp.Server` component under `/servers/`.

## Server runtime

### .NET / C#

C# MCP server (78.6% C# in repo) compiled to a .NET binary, inherited by the successor `microsoft/mcp` umbrella (88% C# there).

## Container artifacts

### Dockerfile (single-stage, build-from-source)

Dockerfile present at repo root.

## Repository layout

### Umbrella consolidation

Originally a per-domain Azure MCP repo collapsed into the `microsoft/mcp` org-level monorepo with `/servers/<name>/` subdirectories (Azure.Mcp.Server, Fabric.Mcp.Server) and `/core/` shared C# libraries. Transitional period observed — original repo archived (Feb 2026) months after code-freeze (Aug 2025) per README notice, with the gap signaling the redirect had to stabilize before formal archival.

## Release and lifecycle

### Archived

Repository marked archived by the maintainer. Code still functions; no further fixes. Two-stage archival pattern — README body declared archival (~Aug 2025) ahead of formal GitHub archival flag (Feb 2026), running the repo in "read-only maintenance" mode for months before the org-level archival.

## Host integration

### VS Code / VS Code Insiders / Visual Studio family

Successor `microsoft/mcp` documents VS Code, VS Code Insiders, Visual Studio 2022, and Eclipse integrations via the platform's marketplaces.

### JetBrains IDE

Successor documents IntelliJ IDEA integration.
