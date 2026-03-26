# Directory Traversal Patterns

## File Map

### Dependencies
```
.claude/skills/blueprint/blueprint_cli.py
.claude/skills/blueprint/references/reconcile-entity.md
```

### Created
```
references/crawl-scripts/
```

Reusable primitives and proven recipes for extracting entities from directory websites during Phase 1 landscape exploration. Directory crawl agents read this file when developing or executing a crawl approach.

## Approach Discovery Workflow

When a directory entity has no `[CRAWL METHOD]:` note, agent develops an approach before starting extraction:

1. Check `[ACCESSIBILITY]:` note on directory entity — determines whether browser tools are needed
2. Navigate to directory URL with Playwright
3. Inspect page structure — probe for data sources before resorting to per-element interaction
  1. Run JS eval to check: `data-*` attributes on interactive elements, hidden containers with pre-loaded content, inline `<script>` tags with JSON data, API endpoints in network requests
  2. Check network requests during page interaction — bio/detail content may come from same-page data rather than API calls
4. Select primitives and compose into recipe based on directory structure
5. Record approach as `[CRAWL METHOD]:` note on directory entity
6. Save extraction script to `references/crawl-scripts/{entity_id}-{short_name}.js`
7. Add `[CRAWL SCRIPT]:` pointer note on directory entity

## Primitives

Atomic building blocks for directory extraction. Each primitive is independently useful and composable with others. Recipes combine primitives for specific directory types.

### Same-Origin Fetch

Fetch pages via JavaScript `fetch()` within an existing browser context on the same domain. Avoids page navigation entirely — no snapshot tokens consumed. Requires browser already on the same domain (one initial `browser_navigate` call establishes domain context).

```javascript
const html = await (await fetch('/directory?page=1')).text();
```

**Replaces:** `browser_navigate` + `browser_evaluate` (2 calls, ~3K tokens wasted on snapshot) with single `browser_evaluate` (1 call, no snapshot).

### DOMParser Extraction

Parse fetched HTML into a queryable document without affecting the live page. Same DOM APIs as a live page — `querySelectorAll`, `getAttribute`, `textContent`.

```javascript
const doc = new DOMParser().parseFromString(html, 'text/html');
const items = doc.querySelectorAll('.member-card');
```

**Pairs with:** Same-Origin Fetch (parse fetched HTML) or any source that produces HTML strings.

### Dynamic Accumulation

Process items sequentially, measuring accumulated result size against a character budget. Stops before exceeding budget and returns a resumption point. Self-regulating — adapts to variable data density.

```javascript
const MAX_CHARS = 40000;  // ~10K tokens, leaves room for registration work
let totalChars = 0;
const results = [];
for (let page = START_PAGE; page <= END_PAGE; page++) {
  const pageData = await extractPage(page);
  const pageSize = JSON.stringify(pageData).length;
  if (totalChars + pageSize > MAX_CHARS && results.length > 0) {
    return JSON.stringify({ results, nextPage: page, complete: false });
  }
  results.push(pageData);
  totalChars += pageSize;
}
return JSON.stringify({ results, nextPage: null, complete: true });
```

**Properties:**
- Always returns at least one item (guard: `results.length > 0`)
- `nextPage` is exact checkpoint — agent passes it as `START_PAGE` in next call
- Progress is monotonic — everything before `nextPage` is done
- Works with any data source (pages, API responses, list items)

### Domain Regex Filtering

Extract website domains from text content using regex patterns. Catches explicit URLs, bare domain mentions, and domains from email addresses. Excludes common email providers.

```javascript
const urlPattern = /\b[\w-]+\.(com|net|org|co|io|us|ca|uk|edu|me|info|biz|pro)\b/gi;
const emailPattern = /[\w.-]+@[\w.-]+\.\w+/gi;

const domains = [...new Set((text.match(urlPattern) || []).map(d => d.toLowerCase()))];
const emails = text.match(emailPattern) || [];
emails.forEach(e => {
  const d = e.split('@')[1].toLowerCase();
  if (!domains.includes(d)) domains.push(d);
});
const filtered = domains.filter(d => !d.match(/^(gmail|yahoo|hotmail|outlook|aol|icloud)\./));
```

**Agent responsibility:** Platform/employer domains (linkedin.com, medium.com, espn.com) pass the regex but are not personal websites — agent filters these during registration based on context.

### HTML Stripping

Clean HTML tags from text before storing as notes. Applied to any text extracted from HTML content.

```javascript
const clean = raw.replace(/<br\s*\/?>/gi, ' ').replace(/<[^>]*>/g, '');
```

### Batch Registration

Combine extraction results into single `register-batch` CLI call. Notes only written for new entities; already-registered entities listed for manual reconciliation.

```
./cli.py claude blueprint register-batch --json '[
  {"name": "...", "url": "...", "description": "...", "relevance": 3, "notes": ["fact1", "fact2"]},
  ...
]' --source-url "https://directory-url.com" --db references/research.db
```

**Output:** Summary count + already-registered entity IDs with URLs (actionable items only).

### URL Parameter Construction

Build directory search URLs directly from observed parameter patterns, bypassing wizard/guided flows. Combine multiple filters into single URL to avoid duplicate processing.

- Multiple service/category filters with OR logic in one URL
- Pagination via `&paged=N` or `&page=N` or `&offset=N`
- Test `per_page` parameter for larger result sets (not always respected)
- Use `sort_by` parameters to prioritize most relevant results first

### Progress Note Update

Update `[CRAWL PROGRESS]:` note on directory entity after each batch. Remove previous note, add new one with current position.

```
./cli.py claude blueprint remove notes --entity-id {directory_id} --note-ids PROGRESS_NOTE_ID --db references/research.db
./cli.py claude blueprint upsert notes --entity-id {directory_id} --notes "[CRAWL PROGRESS]: Processed pages 1-N of M. X entities registered. Resume on page N+1." --db references/research.db
```

## Recipes

Proven combinations of primitives for specific directory types. When a directory matches a recipe, follow it. When no recipe fits, compose a new one from available primitives and document it.

### Paginated HTML with Data Attributes

**Directory type:** Server-rendered pages with member data embedded in DOM data attributes (e.g., `data-bio`, `data-member-name`). Content appears via JS modals or toggles but data is in the HTML.

**Primitives used:** Same-Origin Fetch + DOMParser Extraction + Dynamic Accumulation + Domain Regex Filtering + HTML Stripping + Batch Registration + Progress Note Update

**Flow:**
1. Initial `browser_navigate` to directory domain (establishes same-origin context)
2. Loop: `browser_evaluate` with accumulating fetch script
  1. For each page in budget: fetch HTML, parse with DOMParser, extract data attributes, filter to members with domains, strip HTML from text
  2. Returns batch with `nextPage` checkpoint
3. Agent constructs `register-batch` JSON from returned batch
4. Single `register-batch` CLI call
5. Reconcile any already-registered entities individually
6. Update `[CRAWL PROGRESS]:` note
7. Repeat from step 2 with `nextPage` until `complete: true`

**Example:** EFA member directory — `.view-bio-btn` elements with `data-member-name`, `data-member-id`, `data-bio-full` attributes. See `references/crawl-scripts/e68-efa.js`.

### JS-Rendered SPA

**Directory type:** Single-page application where member listings require JavaScript rendering. Content loaded dynamically via client-side routing or API calls.

**Primitives used:** (Browser navigation + snapshot) OR (API endpoint discovery + Same-Origin Fetch) + Dynamic Accumulation + Batch Registration + Progress Note Update

**Flow:**
1. Navigate to directory with `browser_navigate`
2. Check network requests for underlying API endpoints
  1. If API found: switch to Same-Origin Fetch against API endpoint (much more efficient)
  2. If no API: use browser interaction (click, scroll) to load content, extract from snapshots
3. Accumulate and register per recipe above

**Example:** Author Accelerator /matchme — JS-rendered coach directory. Approach TBD pending Playwright crawl.

### API-Backed Directory

**Directory type:** Directory with a discoverable REST/GraphQL API that returns structured data (JSON).

**Primitives used:** Same-Origin Fetch (to API endpoint) + Dynamic Accumulation + Batch Registration + Progress Note Update

**Flow:**
1. Initial `browser_navigate` to directory domain
2. Discover API endpoint from network requests or page source
3. Loop: `browser_evaluate` with accumulating fetch to API
  1. Parse JSON response directly (no DOMParser needed)
  2. Extract name, URL, description from structured fields
4. `register-batch` + progress update per standard flow

**Note:** API responses are typically smaller and more structured than HTML, so accumulation budgets can be larger.

### Static Content Pages

**Directory type:** Curated lists, blog posts, or articles that link to example entities. No pagination or dynamic content — each page is a standalone source.

**Primitives used:** Same-Origin Fetch (or WebFetch) + DOMParser Extraction + Batch Registration

**Flow:**
1. Fetch each source page
2. Extract links and context from page content
3. Register entities from extracted links

**Example:** Reedsy blog articles — curated author website examples with analysis.

## Crawl Script Storage

Directory-specific extraction scripts saved as files for reuse across sessions:

- **Location:** `references/crawl-scripts/{entity_id}-{short_name}.js`
- **Pointer:** `[CRAWL SCRIPT]: references/crawl-scripts/{entity_id}-{short_name}.js` note on directory entity
- **Content:** Complete JS function with comments documenting URL parameters, DOM selectors, pagination, and variable placeholders (START_PAGE, END_PAGE, MAX_CHARS)
- **Retrieval:** Agent reads file path from `[CRAWL SCRIPT]:` note, loads script, adjusts START_PAGE from `[CRAWL PROGRESS]:` note

Examine all crawl scripts across directories: `ls references/crawl-scripts/`

## Tagged Note Convention

Directory entities use tagged notes for crawl state:

| Tag | Purpose | Mutability |
|-----|---------|------------|
| `[ACCESSIBILITY]:` | How to access directory content | Set during registration |
| `[CRAWL METHOD]:` | Human-readable description of approach | Stable — updated only if approach changes |
| `[CRAWL SCRIPT]:` | File path pointer to executable JS script | Stable — set once when script is saved |
| `[CRAWL PROGRESS]:` | Current position within crawl | Updated after each batch |
