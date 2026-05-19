# Wave: Prior-art link verification + adjacencies

## Existing links verification

| Pattern | Doc URL | Status | Canonical URL (if different) | Notes |
|---|---|---|---|---|
| DevContainer spec | https://containers.dev/ | ok | — | Microsoft-stewarded open spec; site current (2026 copyright). |
| DevContainer Features | https://containers.dev/features | ok | — | Live registry of official + community Features; resolves cleanly. |
| GitHub Codespaces | https://docs.github.com/en/codespaces | ok | — | Canonical docs landing; mature, comprehensive. |
| Prettier sharing configs | https://prettier.io/docs/configuration#sharing-configurations | redirect-ish | https://prettier.io/docs/sharing-configurations | The anchor links to a "Next" page; canonical content lives on its own page now. Old URL still works but doesn't show the content inline — better to link the dedicated page. |
| ESLint shareable configs | https://eslint.org/docs/latest/extend/shareable-configs | ok | — | Canonical; updated for flat config era. |
| Terraform modules | https://developer.hashicorp.com/terraform/language/modules | ok | — | Current (v1.15.x latest as of fetch). |
| Helm charts | https://helm.sh/docs/topics/charts/ | ok | — | Canonical; banner notes "not yet updated for Helm 4" but page is current and authoritative. |
| Backstage | https://backstage.io/ | ok | — | Canonical. CNCF **Incubating** (still, as of 2026); not yet graduated despite preparation. |
| Salesforce SFDX | https://developer.salesforce.com/tools/salesforcedx | **404 dead** | https://developer.salesforce.com/tools/sfdxcli | Old `/salesforcedx` path is gone. Replacement page focuses on the unified `sf` CLI (v2); `sfdx` (v7) is deprecated, no further updates, sfdx-style command reference was removed June 2024. |
| Stripe CLI | https://docs.stripe.com/stripe-cli | ok | — | Canonical; landing page structure intact. |

## Per-pattern current-state notes

- **DevContainer + Features:** Spec is stable and Microsoft-stewarded; Features ecosystem is broad and actively curated. Strong, durable analog for the Claude Code plugin shape.
- **Prettier / ESLint shareable configs:** Both ecosystems are mature; ESLint has fully pivoted to flat-config (`eslint.config.js`); Prettier docs now host sharing as a dedicated page. Still the cleanest precedent for "config as npm package."
- **Terraform modules / Helm charts:** Both remain the dominant composable-template shapes in their domains. Helm is mid-transition toward v4; chart authoring conventions unchanged. Terraform Registry continues to anchor module discovery.
- **Backstage:** CNCF Incubating since 2022; still Incubating in 2026 (community preparing for graduation). Monthly releases, active ecosystem, and a Certified Backstage Associate program launched. Dominant open-source IDP.
- **Salesforce SFDX:** Migrated. `sfdx` (v7) is deprecated; current product is **Salesforce CLI (`sf`, v2)** under oclif. The `developer.salesforce.com/tools/salesforcedx` page is **404** — update the doc link.
- **Stripe CLI:** Still the textbook example of opinionated, auth-aware vendor CLI distribution; no structural changes.

## Suggested adjacencies (patterns to consider adding)

1. **oclif (Open CLI Framework)** — https://oclif.io/
   Why it fits: The framework underneath both Salesforce `sf` and Heroku CLI. Native plugin model: users run `sf plugins install <pkg>` and the CLI gains new top-level commands. This is the *plugin-host CLI* archetype — direct analog to "Claude Code as a CLI that hosts plugins." Worth borrowing: plugin discovery UX, command-namespace conventions, install/update flows.

2. **GitHub CLI extensions (`gh extension`)** — https://docs.github.com/en/github-cli/github-cli/using-github-cli-extensions
   Why it fits: User-scoped, git-repo-distributed extensions named `gh-<extension>` that anyone can author and `gh extension install` pulls. Lighter than oclif — closer in spirit to "skill packages distributed via git URL." Strong precedent for low-ceremony, registry-free extension distribution.

3. **Krew (kubectl plugin manager)** — https://krew.sigs.k8s.io/
   Why it fits: Community-curated, cross-platform plugin index for `kubectl`. Demonstrates the *separate-package-manager-for-a-host-CLI* shape: SIG-governed plugin index, manifest-based publishing, audited curation. Relevant when thinking about scaling beyond a single marketplace.

4. **Renovate config presets** — https://docs.renovatebot.com/config-presets/
   Why it fits: Repo-hosted shareable presets referenced as `github>org/repo` — no npm publishing required, version pinning via git refs, presets-extend-presets composition. Tighter analog to "git-distributed Claude config" than Prettier/ESLint (which require npm).

5. **GitHub Actions reusable workflows** — https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows
   Why it fits: `workflow_call` + typed `inputs`/`secrets` = composable, versioned workflow templates referenced by `org/repo/.github/workflows/x.yml@ref`. Directly analogous to "shareable slash-command-as-workflow" — same parameterization-and-versioning problem.

6. **Open Policy Agent / Rego** — https://www.openpolicyagent.org/
   Why it fits: Org-policy-as-code engine. The "hard gate" pole of the enforcement axis already in the doc — externalized policy expressed in Rego, queried by hooks/gateways. If the survey ever adds an "org-policy-as-code" sub-shape for managed-settings / hooks governance, OPA is the canonical reference.

## Summary

Nine of ten links are good; **the Salesforce SFDX link (404)** should be replaced with `https://developer.salesforce.com/tools/sfdxcli` and the surrounding prose updated to reflect the `sfdx` → `sf` (v2, oclif-based) migration. The Prettier anchor link works but `prettier.io/docs/sharing-configurations` is the cleaner canonical. Strongest adjacencies to add are **oclif**, **`gh` extensions**, **Krew**, **Renovate presets**, and **GitHub Actions reusable workflows** — together they round out the "host-CLI plugins," "git-distributed configs," and "reusable workflow templates" lanes the current doc only partially covers. **OPA** is the right reference if policy-as-code becomes its own sub-shape.
