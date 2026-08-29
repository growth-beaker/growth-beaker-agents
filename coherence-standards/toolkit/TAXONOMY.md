---
okf_version: "0.2"
type: Reference
title: Taxonomy — standards extraction
description: "The coherence-standards taxonomy: every rail domain an agent must observe."
tags: [standards, meta, taxonomy]
generated: { by: "claude-code/claude-opus-5", at: "2026-08-28" }
verified: []
stale_after: 2027-02-28
---

# Coherence Standards Taxonomy
## The guardrails an agent must follow when exploring a solution space
### Enterprise brownfield edition — v0.1 (working draft)

**Scope.** Every standard an agent (or human product builder) should observe when producing specs, prototypes, or code inside an existing enterprise application. Prototypes are treated as code: the working assumption is that prototype and production code blur, and a prototype-relaxation subset (e.g., security waivers inside the sandbox) will be flagged in a later pass rather than maintained as a separate universe.

**How to read.** Grouped by domain. Each domain carries an **agent extraction sources** note: where a standards-extraction agent could mine this from an existing repo and its surrounding systems — the seed of a tool that generates these rails for any codebase. Enforcement (hook / lint / gate) is deliberately deferred to the abstraction pass; a domain-level note marks how automatable each area typically is.

**The delivery guarantee (rule zero).** A rail that never reaches the agent's context is not a rail. Every standard below must ultimately be addressable from the agent's working context (AGENTS.md index, path-scoped files, machine-readable configs) or it will function only as a gate-rejection generator.

---

## 1. Specification & Requirements

*How intent is written down so that agents build the right thing and gates can judge it.*

- **1.1** Spec template with required sections: problem, affected users/personas, scope, non-goals, acceptance criteria, open questions, rollout notes
- **1.2** Acceptance criteria notation (Given/When/Then or EARS); one testable clause per criterion
- **1.3** Stable requirement IDs; every spec linked to a ticket; ticket links survive revisions
- **1.4** Non-goals section mandatory (scope creep prevention is a written artifact, not a memory)
- **1.5** NFR checklist: performance, accessibility, security, privacy, i18n — each addressed or explicitly waived with reason
- **1.6** Scope sizing rule: what one gate submission may contain (one feature / one bounded context)
- **1.7** Assumption register: unknowns flagged, never silently resolved
- **1.8** Open-questions section with owners; unresolved blockers named before gate
- **1.9** Impacted-systems section: services, schemas, events, and teams touched
- **1.10** Rollout & rollback section: flag strategy, migration ordering, revert path
- **1.11** Success metrics defined up front, with the analytics events that will measure them named per the event taxonomy (§17)
- **1.12** Deviation declaration block: which rails this work knowingly breaks and why
- **1.13** Spec versioning and change log; material changes re-gated
- **1.14** Terminology sourced from the domain glossary (§2) only
- **1.15** User roles referenced from the canonical role/permission list (§2.9)
- **1.16** Minimum edge-case enumeration: empty, error, permission-denied, concurrent-edit
- **1.17** Compliance screening questions: does this touch PII, payments, or regulated data (routes to §10 checklists)

*Agent extraction sources: existing PRD/spec folder, ticket templates, definition-of-ready docs, past gate feedback.*

*Enforcement profile: template presence machine-checkable; content quality is gate judgment.*

---

## 2. Domain Model & Ubiquitous Language

*The single highest-frequency incoherence agents produce is inventing vocabulary. This domain exists to stop it.*

- **2.1** Canonical glossary of entities, verbs, and states; agents must use it verbatim
- **2.2** No synonyms for existing concepts ("client" when the codebase says "account" is a rejection)
- **2.3** New-term proposal process: coining a term is a gate item, never an inline choice
- **2.4** Extend existing entities over creating parallel ones; duplicate concepts forbidden
- **2.5** Bounded-context map respected: entities referenced across contexts only via the owning context's interface
- **2.6** Canonical enums and status vocabularies; no new status sets without ADR
- **2.7** State machines documented for stateful entities; transitions occur only via defined operations/events
- **2.8** Domain invariants written down (e.g., order total equals sum of lines) and cited in specs and tests
- **2.9** Canonical role and permission nouns; UI copy, code, and authz use the same words
- **2.10** Unit conventions: quantities, units of measure, rounding rules
- **2.11** Identifier semantics: business keys vs surrogate keys; which is exposed where
- **2.12** Casing parity: the same domain term is spelled/cased consistently in schema, code, API, and UI

*Agent extraction sources: ORM models/entities, database schema, existing enum definitions, permission tables, UI string catalogs — plus an LLM pass to reconcile them into one glossary.*

*Enforcement profile: glossary-linting is semi-automatable; new-term detection is a strong hook candidate.*

---

## 3. Data & Persistence

- **3.1** Schema naming conventions: table/column casing, singular vs plural, prefix rules
- **3.2** ID format: UUID version, prefixing scheme (e.g., `acct_`), generation location
- **3.3** Foreign-key and index naming conventions; required indexes for FK columns
- **3.4** Nullability rules and column defaults; NOT NULL as the default posture
- **3.5** Migration style: expand/contract only; backward compatible with running code
- **3.6** Migration naming, ordering, and one-way discipline; no destructive change in the same release as the code change
- **3.7** Reference/seed data managed as versioned migrations, not manual inserts
- **3.8** Date/time: UTC at rest, ISO 8601 at interfaces; timezone policy for user-facing display
- **3.9** Money: integer minor units plus currency code; floats forbidden
- **3.10** PII classification tags on fields at creation time
- **3.11** Encryption-at-rest classes and which classifications require them
- **3.12** Soft-delete vs hard-delete policy per entity class; uniqueness interaction rules
- **3.13** Mandatory audit columns (created/updated at/by) and who writes them
- **3.14** Tenant isolation: tenant_id on every tenant-scoped table; composite indexes lead with tenant
- **3.15** Tenant scoping enforced structurally (row-level security or mandatory scoped-query helpers); raw cross-tenant queries forbidden
- **3.16** Data ownership boundaries: which service owns each table; cross-boundary writes forbidden
- **3.17** Retention schedule per data classification, wired to deletion jobs (§10.5)
- **3.18** Archival conventions for cold data
- **3.19** Read-model/denormalization rules: when allowed, how kept consistent, who owns refresh
- **3.20** Transaction boundary conventions: unit-of-work per use case; no transactions spanning external calls
- **3.21** Optimistic locking/version columns for user-editable entities
- **3.22** Large objects in object storage, not the database; pointer conventions
- **3.23** Search-index synchronization pattern (outbox/CDC), never dual writes

*Agent extraction sources: schema dump, migration history (rich source of house conventions), ORM configs, existing RLS policies, DBA runbooks.*

*Enforcement profile: highly machine-checkable — migration linters, schema tests, tenant-scoping static checks.*

---

## 4. Interface Contracts — Synchronous APIs

- **4.1** Resource naming: plurality, casing, and noun choice from the glossary
- **4.2** Nesting depth ceiling; when to flatten with filters instead
- **4.3** Verb semantics: GET safe and idempotent; POST/PUT/PATCH/DELETE rules
- **4.4** PATCH semantics pinned (merge-patch vs JSON-patch)
- **4.5** Query parameter conventions for filtering, sorting, searching
- **4.6** Pagination standard: cursor vs offset, envelope shape, default and max page sizes
- **4.7** Sparse fieldsets / expansion conventions if supported
- **4.8** Single error response schema; central error-code registry; no ad-hoc error strings
- **4.9** Status code usage rules (including 409 vs 422, 401 vs 403)
- **4.10** Idempotency keys on unsafe POSTs; server-side dedupe window
- **4.11** Concurrency control: ETag/If-Match conventions for updates
- **4.12** Timeout declarations per endpoint; documented retry semantics for clients
- **4.13** Rate limiting conventions and headers
- **4.14** Versioning strategy, deprecation windows, sunset headers
- **4.15** Additive-only changes within a version; breaking change = new version + ADR
- **4.16** OpenAPI spec mandatory, linted against the house ruleset (Spectral-style)
- **4.17** Contract-first: spec exists before implementation; clients generated, not handwritten
- **4.18** Internal vs public API tiers with explicitly different rule strictness
- **4.19** Bulk operation conventions: request shape, partial-failure reporting
- **4.20** Long-running operations: 202 + status resource pattern
- **4.21** File upload/download conventions: signed URLs, size limits, content-type validation
- **4.22** API message localization policy (error messages localized or code-only)
- **4.23** GraphQL (where applicable): schema naming, nullability posture, connection-based pagination, error conventions, persisted queries, N+1 resolution pattern
- **4.24** gRPC (where applicable): proto style guide, package naming, error model, deadline propagation

*Agent extraction sources: existing OpenAPI/proto files, route tables, the ten most-called endpoints as exemplars, current Spectral/linter configs, API gateway configs.*

*Enforcement profile: the most automatable domain in the taxonomy — contract linting as a pre-gate hook.*

---

## 5. Events & Asynchronous Messaging

- **5.1** Topic/queue naming conventions and ownership
- **5.2** Event naming: past-tense domain events (`InvoicePaid`), from glossary vocabulary
- **5.3** Schema registry usage; compatibility mode (backward/forward) pinned
- **5.4** Standard envelope: event id, occurred_at, correlation id, causation id, tenant id
- **5.5** Event versioning rules; upcasting conventions
- **5.6** Delivery assumption is at-least-once; every consumer idempotent
- **5.7** Ordering guarantees documented per topic; consumers never assume more than declared
- **5.8** Reliable publish via outbox pattern; no dual writes
- **5.9** Dead-letter conventions and replay procedure
- **5.10** Event vs command distinction; commands are not broadcast
- **5.11** Webhook conventions: signing, retries, timeout, receiver verification
- **5.12** Scheduled/cron job naming, ownership, and overlap protection
- **5.13** Long-running workflow conventions (saga/process manager library and naming)

*Agent extraction sources: broker topology, schema registry contents, existing consumer code, outbox tables, DLQ runbooks.*

---

## 6. Code Structure & Style

- **6.1** Formatter config is canonical; no debates, no overrides  `[scanner: DELETE — see SCANNER-COVERAGE.md]`
- **6.2** Linter config is canonical; inline disables require a ticket reference  `[scanner: THIN — see SCANNER-COVERAGE.md]`
- **6.3** File and module naming conventions per language
- **6.4** Project layout: placement rules for new code (feature folders vs layers) — "where does this file go" has one answer
- **6.5** Module boundaries and import direction rules, mechanically enforced (dependency-cruiser or equivalent); domain never imports infrastructure
- **6.6** Public vs internal module APIs: what may be imported from outside (index/barrel discipline)
- **6.7** Function/class size and complexity guidance  `[scanner: THRESHOLD — see SCANNER-COVERAGE.md]`
- **6.8** Naming semantics: boolean prefixes (is/has/can), handler prefixes (on/handle), async suffix conventions
- **6.9** No magic numbers; constants named and located conventionally  `[scanner: DELETE — see SCANNER-COVERAGE.md]`
- **6.10** Immutability preferences; mutation idioms where allowed  `[scanner: THIN — see SCANNER-COVERAGE.md]`
- **6.11** Null/absence handling idiom (Optional/Maybe/nullable types) — one idiom, used everywhere  `[scanner: THIN — see SCANNER-COVERAGE.md]`
- **6.12** Error idiom: exceptions vs result types; custom error taxonomy; errors never swallowed  `[scanner: THIN — see SCANNER-COVERAGE.md]`
- **6.13** Async idioms: no floating promises; cancellation/structured concurrency conventions  `[scanner: DELETE — see SCANNER-COVERAGE.md]`
- **6.14** Dependency injection pattern; service locators and hidden singletons forbidden
- **6.15** Clock and randomness injected, never called statically from domain logic
- **6.16** Generated code never hand-edited; regeneration commands documented beside it
- **6.17** TODOs carry a ticket and an owner; stale-TODO policy  `[scanner: THIN — see SCANNER-COVERAGE.md]`
- **6.18** Dead-code removal policy; commented-out code forbidden  `[scanner: DELETE — see SCANNER-COVERAGE.md]`
- **6.19** Docstring/comment format; comments explain why, not what
- **6.20** File headers/license headers where required
- **6.21** Language feature policy: which syntax level/features are allowed (tied to toolchain pins)  `[scanner: DELETE — see SCANNER-COVERAGE.md]`

*Agent extraction sources: lint/formatter configs (the ground truth), the 20 most-recently-touched files as style exemplars, dependency graph analysis, existing architecture tests.*

*Enforcement profile: near-fully machine-checkable; this domain should consume zero gate attention.*

---

## 7. Application Runtime Patterns

- **7.1** Input validation at every boundary with the blessed schema library; validated types flow inward
- **7.2** AuthN/AuthZ via platform middleware only; no hand-rolled checks in feature code
- **7.3** Transaction scope pattern: one unit-of-work per use case; no external calls inside transactions
- **7.4** N+1 prohibition; eager-loading/dataloader conventions  `[scanner: THIN — see SCANNER-COVERAGE.md]`
- **7.5** Every list paginated end-to-end (API through UI)
- **7.6** Caching conventions: allowed layers, key naming scheme, TTL classes, invalidation events
- **7.7** Background jobs: queue naming, retry/backoff policy, max attempts, timeout, idempotency requirement
- **7.8** Resilience defaults: retries with jitter, circuit breaker via the blessed library, bulkhead limits
- **7.9** Timeout budgets per hop; total request budget documented
- **7.10** Graceful shutdown: drain handling for servers and workers
- **7.11** Feature flags: naming scheme, default-off, kill-switch class for risky paths, cleanup ticket created with the flag
- **7.12** Configuration via typed config module fed from environment/config service; no literals
- **7.13** Secrets from the vault only; never in code, config files, or logs
- **7.14** Stateless services; session state in the designated store
- **7.15** Temp file and local disk usage conventions
- **7.16** Outbound email/notifications via the platform service, never direct SMTP/APIs
- **7.17** Third-party calls wrapped in an adapter with a test fake; no SDK calls scattered through feature code
- **7.18** Business-logic time handling: tenant timezone rules, DST-safe date math via the blessed library

*Agent extraction sources: middleware stack, existing adapters folder, job definitions, resilience library configs, incident postmortems (rich source of "we standardized this after it burned us").*

---

## 8. Architecture & Technology Decisions

- **8.1** Approved stack registry: languages, frameworks, datastores, pinned major versions
- **8.2** ADR format, numbering, storage location; ADRs are in-repo and agent-readable
- **8.3** ADR-required triggers: new datastore, new service, new architectural pattern, new external dependency category
- **8.4** Default to extending an existing service; creating a service is an ADR, never an exploration choice
- **8.5** Sync vs async communication decision rules
- **8.6** Shared library vs duplication policy (rule of three; who owns extracted libs)
- **8.7** Layering pattern named (hexagonal/clean/etc.) and mechanically enforced where possible  `[scanner: THIN — see SCANNER-COVERAGE.md]`
- **8.8** Cross-service data access via API or events only; shared databases forbidden
- **8.9** Services designed idempotent and restart-safe
- **8.10** Multi-region and data-residency constraints that shape any new feature
- **8.11** Legacy strangler conventions: the wrap-don't-modify module list (see §23.4)
- **8.12** Internal API deprecation lifecycle: announce, dual-run, remove
- **8.13** Performance budgets per tier (e.g., p95 per endpoint class) as design inputs
- **8.14** Capacity assumptions documented for anything with a queue, cache, or fan-out

*Agent extraction sources: existing ADR folder, service inventory, infrastructure diagrams, dependency manifests across services.*

---

## 9. Security

- **9.1** Authentication through platform SSO/OIDC only; custom auth is an automatic rejection
- **9.2** Token handling: storage location, lifetime, rotation, audience validation
- **9.3** Central authorization model; permission naming scheme; policy-as-code location
- **9.4** Object-level authorization on every fetch (IDOR prevention): all reads scoped to caller's tenancy and permissions — no "fetch by id" without scope
- **9.5** Hide-vs-403 rules per resource class (consistent with §13.13)
- **9.6** Input validation and output encoding conventions; template auto-escaping never disabled  `[scanner: THIN — see SCANNER-COVERAGE.md]`
- **9.7** Parameterized queries only; dynamic SQL forbidden  `[scanner: DELETE — see SCANNER-COVERAGE.md]`
- **9.8** SSRF protections on outbound fetches (allowlisted hosts, no user-supplied URLs unproxied)  `[scanner: THIN — see SCANNER-COVERAGE.md]`
- **9.9** File upload security: content sniffing, size caps, AV scan hook, no execution paths
- **9.10** Approved cryptography list; custom crypto forbidden; hashing/signing conventions  `[scanner: THIN — see SCANNER-COVERAGE.md]`
- **9.11** Secrets scanning in pre-commit and CI  `[scanner: DELETE — see SCANNER-COVERAGE.md]`
- **9.12** Security headers/CSP baseline for web surfaces  `[scanner: THIN — see SCANNER-COVERAGE.md]`
- **9.13** CORS policy conventions; no wildcard origins with credentials  `[scanner: DELETE — see SCANNER-COVERAGE.md]`
- **9.14** Privileged-action audit logging: what, who, when, immutable sink
- **9.15** Threat-model triggers: which spec categories require one before the gate
- **9.16** Severity taxonomy and fix-SLA references for anything found during exploration

*Agent extraction sources: auth middleware, existing permission definitions, security scanning configs, past pentest findings, CSP headers in current responses.*

---

## 10. Privacy & Compliance

- **10.1** Data classification scheme, used in both specs (§1.17) and schemas (§3.10)
- **10.2** Lawful-basis/consent flags recorded where collection is consent-based
- **10.3** Purpose limitation: new collection states its purpose; reuse beyond purpose is a gate item
- **10.4** DSAR coverage: subject export and deletion paths must include any new tables/fields
- **10.5** Retention and deletion jobs exist for every new data class, per the retention schedule
- **10.6** PII minimization defaults; masked-display idiom for sensitive fields
- **10.7** No PII in logs, analytics events, URLs, or error messages
- **10.8** Regional residency routing rules for data at rest and in transit
- **10.9** Records-of-processing update trigger when new processing is introduced
- **10.10** Regulated-domain checklists where applicable: SOX change-control touchpoints, HIPAA/PCI scoping boundaries and what may never enter scope

*Agent extraction sources: privacy policy, existing DSAR implementation, data classification docs, DPA/vendor agreements, current deletion jobs.*

---

## 11. Observability & Operations

- **11.1** Structured logging schema (fields, casing) and level usage rules
- **11.2** Correlation/trace ID propagation across every hop, including jobs and events
- **11.3** Metric naming conventions; label cardinality limits
- **11.4** Baseline metrics required per service (RED/USE) and per new endpoint
- **11.5** Tracing spans around all external calls; span naming conventions
- **11.6** Alert rules have owners and runbook links; alert naming scheme
- **11.7** SLO definitions location; which features require SLOs at creation
- **11.8** Health/readiness endpoint conventions
- **11.9** Dashboards-as-code location and naming
- **11.10** Log retention classes by data sensitivity (ties to §10)
- **11.11** Cost attribution tags on any new resource

*Agent extraction sources: logging config, current dashboards, alert rule repo, tracing setup, past incident reviews.*

---

## 12. Frontend Engineering

- **12.1** Framework and app-shell conventions; approved meta-framework features
- **12.2** State management pattern: server-state library vs local state rules; global state criteria
- **12.3** Data-fetching conventions: hooks/query layer, cache keys, invalidation, suspense policy
- **12.4** Routing conventions: URL structure, param naming, deep-linkability requirement
- **12.5** Component file structure: co-located styles/tests/stories; naming
- **12.6** Props conventions: naming, controlled-component defaults, event handler signatures
- **12.7** Styling: tokens only; utility-vs-module rules; z-index scale; spacing scale
- **12.8** Asset pipeline: icon system usage, image optimization, font loading
- **12.9** Bundle budgets per route; code-splitting rules; dependency weight review  `[scanner: THRESHOLD — see SCANNER-COVERAGE.md]`
- **12.10** Web-vitals thresholds as acceptance criteria for UI work  `[scanner: THRESHOLD — see SCANNER-COVERAGE.md]`
- **12.11** Error boundaries at defined levels; client errors reported to the standard sink
- **12.12** Client logging/analytics only via the wrapper SDK (ties to §17)
- **12.13** Feature-flag SDK usage pattern; no flag checks scattered in JSX
- **12.14** Forms: blessed library; validation schemas shared/derived from API schemas
- **12.15** Date/number/currency formatting via the shared l10n utilities only
- **12.16** SSR/hydration constraints; what may not run on the server
- **12.17** Supported browser/device matrix

*Agent extraction sources: package.json + lockfile, existing component directory, current bundle analysis, router config, top-20 components as exemplars.*

---

## 13. UX Interaction Patterns

*How the product behaves — the layer above the design system, and the one agents most confidently get wrong.*

- **13.1** Pattern precedence: existing pattern > new composition of components > new pattern (gate item)
- **13.2** Empty states required for every list/collection view; content model for them
- **13.3** Loading policy: skeleton vs spinner by expected latency; thresholds defined
- **13.4** Error states always offer a recovery action; error copy formula
- **13.5** Destructive actions: confirmation pattern; undo offered where feasible
- **13.6** Optimistic updates: where allowed; rollback and conflict behavior
- **13.7** Form UX: validation timing, error placement, autosave policy, dirty-state handling
- **13.8** Navigation: IA placement rules for new features; URL and back-button behavior
- **13.9** Modality decision tree: modal vs drawer vs full page
- **13.10** Notification/toast budget, stacking, and persistence rules
- **13.11** Search and filter conventions: debounce, empty-result behavior, saved filters
- **13.12** Table/list conventions: density, sorting, bulk actions, column visibility
- **13.13** Permission-aware UI: hide vs disable rules per permission class (consistent with §9.5)
- **13.14** First-run/onboarding and empty-organization states
- **13.15** Keyboard shortcut registry; no unregistered global shortcuts
- **13.16** Unsaved-changes guard convention
- **13.17** Real-time patterns: live update vs refresh semantics, presence conventions, conflict indication

*Agent extraction sources: screenshots/storybook of existing flows, design-pattern documentation, support tickets about inconsistency, session recordings of canonical flows.*

*Enforcement profile: the least automatable domain — this is what the human at the gate is for.*

---

## 14. Visual Design System

- **14.1** Design tokens only: color, type, spacing, radius, shadow — raw values forbidden
- **14.2** Component library versions and allowed variants/slots; forks forbidden
- **14.3** New-component proposal flow; bespoke components require design sign-off at the gate
- **14.4** Iconography: single set, sizing and color rules
- **14.5** Illustration/imagery style constraints
- **14.6** Data-visualization palette and chart-type conventions
- **14.7** Density modes and when each applies
- **14.8** Theming constraints (dark mode support requirements for new UI)
- **14.9** Motion tokens: durations, easings; reduced-motion compliance
- **14.10** Layout grid and breakpoint tokens

*Agent extraction sources: token files (ground truth), component library source, Figma/Paper libraries, design lint configs.*

---

## 15. Content & Communication

- **15.1** Voice and tone principles for product copy
- **15.2** Capitalization and punctuation rules (sentence case, serial comma, etc.)
- **15.3** UI terminology mirrors the domain glossary (§2) exactly
- **15.4** Microcopy patterns: verb-first buttons, error copy formula, confirmation phrasing
- **15.5** All user-facing strings in message catalogs; key naming conventions; no hardcoded strings
- **15.6** ICU pluralization/interpolation usage; no string concatenation for sentences
- **15.7** Translatability constraints: expansion tolerance, no text in images
- **15.8** Locale formatting for dates/numbers/currency via shared utilities (with §12.15)
- **15.9** RTL support requirements for new UI
- **15.10** Transactional email/notification templates, sender identities, and footer requirements
- **15.11** In-product announcement/changelog pattern
- **15.12** Legal strings (terms, disclaimers, consent language) sourced from the approved registry only — never drafted by the agent

*Agent extraction sources: message catalogs, existing email templates, style guide docs, top-100 strings as voice exemplars.*

---

## 16. Accessibility

- **16.1** WCAG 2.2 AA as the floor; target stated per surface
- **16.2** Semantic HTML first; ARIA per APG patterns only where semantics fall short
- **16.3** Focus management: order, visible focus, trap rules for modals, return-focus on close
- **16.4** Full keyboard operability, including alternatives for drag/hover interactions
- **16.5** Contrast enforced via tokens (with §14.1)  `[scanner: THIN — see SCANNER-COVERAGE.md]`
- **16.6** Form labeling: programmatic labels, descriptions, and error association  `[scanner: THIN — see SCANNER-COVERAGE.md]`
- **16.7** Live regions for async updates; politeness levels
- **16.8** Media alternatives: alt-text policy, captions/transcripts  `[scanner: THIN — see SCANNER-COVERAGE.md]`
- **16.9** Motion and flash limits; reduced-motion respected
- **16.10** Minimum target sizes
- **16.11** Testing gates: automated axe-clean plus the manual checklist for the pattern class used

*Agent extraction sources: existing a11y lint configs, component library a11y docs, past audit reports.*

---

## 17. Analytics & Experimentation

- **17.1** Event taxonomy: object_action naming, registry in repo
- **17.2** Property naming and typing conventions; required context properties (tenant, surface, version)
- **17.3** Tracking plan lives in the repo; new events reviewed at the gate with the spec's success metrics (§1.11)
- **17.4** No PII in event names or payloads (with §10.7)
- **17.5** Client vs server event-source rules; dedupe conventions
- **17.6** Experimentation: flag conventions, assignment logging, exposure events, guardrail metrics
- **17.7** Metric definitions centralized — one queryable source for terms like "activation"
- **17.8** Consent/sampling gating integrated with the privacy layer

*Agent extraction sources: existing tracking plan, analytics SDK wrapper, event stream sample, metric definition repo.*

---

## 18. Testing & Quality

- **18.1** Test-pyramid expectations per change class (schema change vs UI change vs new endpoint)
- **18.2** Test naming and AAA structure; colocation rules
- **18.3** Factories/fixtures reused; builders over ad-hoc data; no copy-pasted setup
- **18.4** Determinism: no sleeps, fake timers, seeded randomness, injected clock (§6.15)
- **18.5** Unit tests network-isolated; adapters covered by contract tests against fakes
- **18.6** E2E selector convention (data-testid registry); no text/CSS selectors
- **18.7** Accessibility assertions included in component tests (with §16.11)
- **18.8** Visual regression scope and baseline update process
- **18.9** Performance tests on designated hot paths with thresholds (§8.13)  `[scanner: THRESHOLD — see SCANNER-COVERAGE.md]`
- **18.10** Coverage/mutation thresholds policy per module class  `[scanner: THRESHOLD — see SCANNER-COVERAGE.md]`
- **18.11** Flaky-test quarantine and fix-SLA process  `[scanner: THIN — see SCANNER-COVERAGE.md]`
- **18.12** No production data in tests; synthetic data generation conventions

*Agent extraction sources: existing test suites (structure exemplars), factory definitions, CI config, flaky-test history.*

---

## 19. Dependencies & Supply Chain

- **19.1** Package allowlist/denylist with a request process; unvetted installs blocked
- **19.2** License allowlist; copyleft policy
- **19.3** Version pinning and lockfile discipline; lockfile changes reviewed
- **19.4** Upgrade cadence; renovate/dependabot config is the authority
- **19.5** Vulnerability fix SLA by severity  `[scanner: THIN — see SCANNER-COVERAGE.md]`
- **19.6** Provenance checks: scoped registries, typosquat protection, package-existence verification hooks (the guardrail form of hallucinated dependencies)
- **19.7** Vendoring/forking policy and where forks live
- **19.8** Native/binary dependency policy
- **19.9** Internal package publishing conventions: naming, versioning, ownership

*Agent extraction sources: lockfiles, current SCA tool configs, internal registry contents, license scan reports.*

---

## 20. Version Control & Change Management

- **20.1** Branch naming and maximum lifetime; trunk-based expectations
- **20.2** Conventional commits with the house scope vocabulary
- **20.3** PR size guidance; stacked-PR conventions for large work
- **20.4** PR description template: spec link, screenshots for UI, risk notes, test evidence
- **20.5** Required checks list; merge strategy (squash) and history rules
- **20.6** Changelog generation rules from commit metadata
- **20.7** Revert-first policy for production breakage
- **20.8** Code ownership map; review routing rules
- **20.9** Monorepo path conventions and CODEOWNERS hygiene

*Agent extraction sources: git history statistics, existing PR templates, CODEOWNERS, branch protection settings.*

---

## 21. Build, Deploy & Environments

- **21.1** Reproducible builds: toolchain versions locked and provided (containerized dev)
- **21.2** Container base images from the golden registry only
- **21.3** IaC module registry; resource naming and tagging standards
- **21.4** Environment promotion path; config parity rules between environments
- **21.5** Migration execution ordering relative to deploys (with §3.5)
- **21.6** Release versioning scheme
- **21.7** Feature-flag-based release as the default; long-lived release branches forbidden
- **21.8** Rollback procedure conventions per service class
- **21.9** Progressive delivery defaults (canary percentages, bake times) for risky classes
- **21.10** Artifact signing and SBOM generation in the pipeline

*Agent extraction sources: CI/CD configs, IaC repo, existing Dockerfiles, deployment runbooks.*

---

## 22. Embedded AI Features

*Applies when the product itself ships LLM-powered functionality.*

- **22.1** Prompt templates stored and versioned in the repo; no inline prompts in feature code
- **22.2** Model/provider allowlist and routing configuration; provider swaps are config, not code
- **22.3** PII redaction before provider calls; per-provider data-sharing flags honored
- **22.4** Output validation/guardrail layer required between model and user or system action
- **22.5** Eval sets required for any prompt/model change; regression gate before merge
- **22.6** Token/cost budgets per feature; usage logged with attribution
- **22.7** User-facing AI disclosure and feedback affordances per the UX pattern
- **22.8** Determinism policy per feature class (temperature, seeds, caching)
- **22.9** Defined fallback behavior on provider failure or guardrail rejection

*Agent extraction sources: existing prompt files, provider SDK usage, current eval harness, AI feature specs.*

---

## 23. Brownfield Meta-Rules

*The rules about the rules — what an agent does when standards conflict, are missing, or are knowingly unmet. In a brownfield codebase these fire in the first hour.*

- **23.1** Precedence order when rails conflict: security/compliance > interface contracts > global standards > local module idiom > agent preference — written down, not assumed
- **23.2** Neighborhood rule: within a legacy module, match local style for intra-module code; global standards still govern its external interfaces
- **23.3** Exemption registry: modules where standards are knowingly unmet, each with an owner and expiry — agents neither flag nor "fix" these
- **23.4** Wrap-don't-modify list: legacy modules that may only be extended via facade/strangler, never edited internally
- **23.5** Propose-don't-invent: when no rail covers the situation, the agent flags the gap at the gate rather than choosing silently; the gate's answer becomes a new rail
- **23.6** Deviation mechanics: declared deviations (§1.12) are reviewed at the gate; accepted deviations update the rail or enter the exemption registry — undeclared deviation is a rejection
- **23.7** Boy-scout limits: opportunistic refactors outside the change's scope are capped (or forbidden during exploration) to keep diffs reviewable
- **23.8** Standards changelog: rails are versioned; agents cite the rail version they built against
- **23.9** Delivery guarantee (rule zero restated): every rail above is reachable from agent context — indexed in AGENTS.md, expressed as machine config where possible — or it does not count as a rail

*Agent extraction sources: tribal knowledge interviews, git blame on the oldest modules, existing "here be dragons" comments, onboarding docs.*

---

## Appendix: counts and next passes

~240 standards across 23 domains. Deliberately over-complete — pruning is the next pass, and cutting is cheaper than discovering a gap at the gate.

**Planned passes:**
1. **Prototype-relaxation flags** — mark the subset waived inside the sandbox (most of §9–§11, §18–§21), defining the graduation delta a chosen exploration must close
2. **Abstraction pass** — collapse to the fence-post chips for slide 6 and the guardrail-stack appendix table (rail → enforcement → where it lives)
3. **Extraction-agent spec** — the tool that mines a target repo via each domain's extraction sources and drafts these rails as AGENTS.md + machine configs, with confidence scores and gaps flagged for human confirmation
