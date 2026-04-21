# What's New in FastMCP 3.0 (Jeremiah Lowin)

## Identification
- url: https://jlowin.dev/blog/fastmcp-3-whats-new
- type: blog post
- author: Jeremiah Lowin (FastMCP author)
- last-updated: 2026-01-20
- authority level: semi-official

## Scope
Release post for FastMCP 3.0. Describes the architectural unification around three primitives: **Components** (tools, resources, prompts), **Providers** (sources of components — `LocalProvider`, `FileSystemProvider`, `SkillsProvider`, `OpenAPIProvider`, `ProxyProvider`, `FastMCPProvider`), and **Transforms** (composable middleware — `Namespace`, `ToolTransform`, `VersionFilter`, `Visibility`). Quote from the post: "mounting is just two primitives combined: a Provider that sources components from another server + a Transform that adds a namespace prefix." Also introduces per-component authorization (OAuth scopes + custom auth checks), session-scoped state, component versioning with semver, OpenTelemetry tracing, background tasks, tool timeouts, pagination, hot reload, callable decorated functions, and automatic thread-pool management. Four breaking changes documented in a separate upgrade guide; most users need minimal or no code changes.

## Takeaway summary
The design payoff of the 3.0 redesign: what used to be separate subsystems (mount, OpenAPI import, proxy-to-remote, tool filtering, auth) all reduce to composing Providers + Transforms. This is the mental model to adopt when building non-trivial FastMCP servers — whenever you want behavior that's currently unique to your server, ask whether it can be expressed as a Transform. Session-scoped state and per-component authorization are the features most likely to change how a production deployment is structured: per-tool scopes mean you can expose a coarse set of tools to anon users and unlock others on auth-elevation without reloading the server. Read this post together with the upgrade guide before starting anything new on FastMCP.

## Use for
- Should I start new FastMCP work on 2.x or 3.x?
- How do Providers + Transforms compose for mounting, proxying, OpenAPI import, tool filtering?
- What's new for production (OpenTelemetry, background tasks, tool timeouts, pagination)?
- What are the four breaking changes from 2.x?

## Relationship to other resources
Supersedes `blog-jlowin-fastmcp-middleware.md` in scope — Transforms subsume the 2.9 middleware model. Read alongside `fastmcp-docs.md` for the full reference.

## Quality notes
Recent release (early 2026) — ecosystem adoption may be uneven. Verify your deployment target supports the 3.x feature set before relying on it.
