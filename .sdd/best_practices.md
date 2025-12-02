### 1. Scope Analysis Summary

* **Appetite:** Batch
* **Key Constraints (explicit/implicit):**

  * No explicit “DO NOT” constraints in the prompt.
  * Implicit constraints:

    * Must be safe-by-default (no blind destructive deletes).
    * Must support multiple subscriptions/regions.
    * Must stay within Python/Azure SDK/Azure CLI/Bicep; no need to become a full SaaS.

**Reasoning:**
You are defining a best-practices guide for a new/parallel tool (“analog awswipe for Azure”), covering architecture, ops, security, and governance. This is more than a “quick fix”, but not a full rewrite of an existing system. Hence appetite = **Batch**.

---

### 2. TL;DR (≤10 bullets)

1. **Core role:** azurewipe is a **safe, tag-aware janitor** that discovers, quarantines, and deletes orphaned/idle Azure resources across subscriptions and regions to reduce cost and operational noise.([Microsoft Tech Community][1])
2. **Primary pattern (MVP):** Python CLI using **Azure SDK for Python** + **Azure CLI authentication**, with a three-phase lifecycle: `discover → quarantine (tags/locks) → delete`, leveraging Azure Resource Graph for discovery wherever possible.([Microsoft Learn][2])
3. **Scale-up pattern:** Scheduled cleanups via **Azure Functions / container app with managed identity**, Resource Graph queries, and centralized state (Table/SQL/Cosmos) with approvals and audit trail.([Microsoft Learn][3])
4. **SDK vs CLI vs REST:** Prefer **Azure SDK (track 2)** for core logic (pagination, retries, models), use **Azure CLI** for auth/bootstrap and quick ops, fall back to **REST** only for gaps or bleeding-edge APIs.([Microsoft Learn][2])
5. **Deletion order:** Clean resource groups and dependent resources in a safe order: VMs → NICs → IPs → disks, NSGs, route tables, application gateways, then empty resource groups; always respect locks, soft delete, and backup retention.([Microsoft Tech Community][1])
6. **Authentication:** Use **managed identities** in Azure (Functions/Container Apps), **service principals** for CI/CD automation, and **interactive az login** only for local/dev. Store no secrets in code; use **Key Vault**.([Microsoft Learn][3])
7. **What changed by 2025:** Bicep is the recommended IaC language over raw ARM JSON; Resource Graph is the standard way to query estates; soft delete defaults have tightened (Key Vault, Backup, Storage), and Azure Monitor Logs add new cost-optimized tiers.([Microsoft Learn][4])
8. **Throttling:** Azure Resource Manager and many services enforce request limits (429/503); azurewipe must use SDK retry policies and backoff, and limit parallelism.([Azure Docs][5])
9. **Metric profile (weights):** PerfGain 0.15, SecRisk 0.25, DevTime 0.10, Maintainability 0.20, Cost impact 0.20, DX 0.10.
10. **Key risks:** False-positive deletes, incomplete discovery, mis-handled locks/soft-delete, throttling causing partial runs, and overly broad permissions.

---

### 3. Landscape — What’s new in 2025 (Python/Azure SDK/Azure CLI/Bicep)

**Azure SDK for Python**

* Modern “track 2” libraries follow common design guidelines: strong typing, long-running operation helpers, and standardized HTTP pipeline with **retry policies and logging**.([Microsoft Learn][2])
* The HTTP pipeline supports pluggable policies (retries, logging, distributed tracing), which you should configure consistently for azurewipe.([Microsoft Learn][6])

**Azure CLI v2**

* Azure CLI v2 remains the primary CLI and has extensive support for **Microsoft Entra ID**, **service principals**, and **managed identities**, including first-class commands for each login pattern.([Microsoft Learn][3])
* CLI integrates with **Resource Graph** (`az graph query`), which is central for estate-wide orphan discovery.([Microsoft Learn][7])

**Bicep vs ARM templates**

* Microsoft explicitly recommends **Bicep** as the preferred authoring language over raw ARM JSON; Bicep compiles to ARM templates, giving full ARM capabilities with more concise syntax.([Microsoft Learn][4])
* ARM is not deprecated but considered “low-level”; new work should generally use Bicep, with ARM as the deployment substrate.

**Azure Resource Graph (ARG)**

* ARG is the recommended way to query large estates over many subscriptions/management groups; you can use Kusto-based queries to find **unattached disks, orphaned NICs, NSGs, public IPs, empty resource groups** and similar.([LinkedIn][8])

**Soft delete & backup**

* **Key Vault:** Soft delete is on by default with a default retention (e.g. 90 days), and purge protection is recommended for cryptographic keys.([Microsoft Learn][9])
* **Storage blobs/containers:** Soft delete can be enabled with 1–365 day retention; Microsoft recommends at least 7 days and many production setups use this with versioning for safety.([Microsoft Learn][10])
* **Azure Backup:** Soft delete is enforced by default and cannot be disabled from the portal, to ensure recovery from accidental deletions.([Microsoft Learn][11])

**Monitoring & logging**

* Azure Monitor Logs introduced new tiers and “Auxiliary” tables to manage noisy/low-value data more cheaply, which is relevant for azurewipe’s logging strategy.([Microsoft Learn][12])
* Activity Log remains the main control-plane log at subscription/management-group scope, capturing create/update/delete of resources.([Microsoft Learn][13])

**Request limits & throttling**

* Azure Resource Manager and many data-plane services implement request limits; they return **429** for throttling and **503/504** for temporary overload; you are expected to respect `Retry-After` headers and apply backoff strategies.([Azure Docs][5])

---

### 4. Architecture Patterns (Azure cleanup tools)

#### Pattern A — “Safe Local/CI Janitor” (MVP)

**When to use**

* Single or few subscriptions, exploratory phase, or strong human-in-the-loop requirement.
* You want a **Python CLI** that engineers can run locally or via CI.

**Core design**

* **Auth:** `az login` (interactive) or `az login --service-principal` for CI; azurewipe uses `DefaultAzureCredential`/`AzureCliCredential` from `azure-identity`.([Microsoft Learn][3])
* **Discovery:** use **Azure Resource Graph** for breadth, fall back to **Azure SDK** list APIs where ARG is insufficient.([Microsoft Learn][7])
* **Lifecycle:** `azurewipe discover` → `azurewipe quarantine` (apply tags/locks or log) → `azurewipe delete`.
* **State:** local JSON/SQLite or a small storage (e.g. Azure Table) to remember candidates and actions.

**Pros**

* Minimal infra dependencies, quick to ship.
* Strong operator visibility; ideal for early rollout and PoCs.

**Cons**

* No continuous enforcement; must be scheduled externally.
* Less suitable for large org-wide estates.

**Validation**

* Unit tests for filters; CLI dry-runs on a test subscription; verify that `discover` finds expected targets and `quarantine` only tags, not deletes.

---

#### Pattern B — “Central Orchestrated Cleaner” (Scale-up)

**When to use**

* Many subscriptions/management groups, need continuous cleanup and auditability.

**Core design**

* **Compute:** Azure Functions (timer-trigger), Container Apps, or WebJobs with **managed identity**.([Microsoft Learn][3])
* **Discovery:** ARG queries scoped to management groups; results stored in Cosmos DB / SQL / Log Analytics.([Microsoft Learn][7])
* **Policy:** configuration in a central repo/Bicep: which resource types, tags, and environments are eligible.
* **Lifecycle:** asynchronous workflows (e.g. Durable Functions or queue-based) to handle `discover → quarantine → delete` with approvals.

**Pros**

* Estate-wide visibility, automation, and consistent policy.
* Easy integration with Azure Monitor, Activity Log, and incident systems.

**Cons**

* Higher complexity (multi-component system).
* Requires platform team ownership and governance.

**Validation**

* End-to-end test subscription and/or dedicated management group; track Activity Log events and logs to ensure each step is recorded and reversible.

---

### 5. Conflicting Practices & Alternatives

#### Azure SDK vs Azure CLI for automation

* **Azure SDK (Python):**

  * Pros: testable, composable, access to models, built-in retries and pagination.([Microsoft Learn][2])
  * Cons: more code; you manage auth and configuration.
* **Azure CLI:**

  * Pros: great for quick scripts and CI steps; built-in auth and ARG integration (`az graph query`).([Microsoft Learn][3])
  * Cons: harder to test at scale; parsing CLI output; not ideal inside long-running daemons.

**Guideline for azurewipe:**

* Use **Azure SDK** for core logic. Use **CLI** mainly to bootstrap credentials locally and for one-off operations (e.g. installation scripts).

#### Resource Graph vs direct API enumeration

* **Resource Graph:**

  * Optimized for cross-subscription KQL queries; ideal for finding orphaned disks, NICs, NSGs, public IPs, empty groups, etc.([LinkedIn][8])
  * Can combine resource properties, tags, activity signals.
* **Direct SDK enumeration:**

  * Needed for services not well covered by ARG, or when you need detailed configuration/state.([Journey Of The Geek][14])

**Guideline:**

* Default to **ARG for discovery**, **SDK for action**. If ARG does not easily provide a needed signal, add targeted SDK enumeration.

#### Subscription-level vs Resource Group-level cleanup

* **Subscription-level:**

  * Pros: maximum coverage; easier for centralized FinOps teams.
  * Cons: bigger blast radius; must rely heavily on tags and conventions.
* **Resource Group-level:**

  * Pros: safer; can target specific “playgrounds” or non-prod RGs.
  * Cons: might miss orphaned resources outside curated RGs.

**Guideline:**

* Start with **explicit RG scopes** (e.g. `*-sandbox`, `*-dev`), then expand to full subscriptions once tagging and policies are mature.

#### Soft delete vs hard delete

* Many services (Key Vault, Backup, Storage) support or enforce soft delete.([Microsoft Learn][9])
* Hard delete is only safe when:

  * Soft delete is disabled for good reason, or
  * There are external backups and clear RPO/RTO agreements.

**Guideline:**

* azurewipe should **prefer soft delete + purge after retention**, or rely on existing soft delete features and avoid purging automatically.

---

### 6. Priority 1 — Safety & Idempotent Deletion

**Why**

* Azure orphan cleanup touches production resources; mis-deletes are expensive. FastTrack and orphan-resource guidance highlight cost savings but also emphasize misconfiguration risk.([Microsoft Tech Community][1])

**Scope**

* Three-phase lifecycle; locks; soft delete; backups.

**Key decisions**

1. **Lifecycle:** every candidate resource goes through
   `DISCOVERED → QUARANTINED → DELETED`, with explicit timestamps and reasons.
2. **Locks:** if a resource or RG has a **Delete or ReadOnly lock**, azurewipe:

   * Logs and skips by default.
   * Optionally flags “policy drift” in reports.([Microsoft Learn][15])
3. **Soft delete:** azurewipe should **respect soft delete & retention**, never purging by default (especially for Key Vault, Backup, Storage).([Microsoft Learn][9])
4. **Backups:** where soft delete does not exist (e.g. some network resources), rely on ARM/Bicep templates or external backups; azurewipe can export resource JSON or generate Bicep snippets before deletion.([Microsoft Learn][4])
5. **Idempotency:** deletion operations must be idempotent (safe to retry), and the state store must record `resource_id + action + run_id`.

**Implementation outline**

* For each resource:

  * **Discover:** via ARG / SDK; classify as orphan based on type-specific heuristics (e.g. disks with empty `managedBy`, NICs not attached, NSGs not associated).([Cloud, Systems Management and Automation][16])
  * **Quarantine:** add tags like `azurewipe:phase=quarantine`, `azurewipe:reason=orphan_disk`, `azurewipe:since=…`; optionally disable/stop (VMs).
  * **Delete:** after TTL (7–30 days), revalidate orphan conditions and tags; check no deny tag (e.g. `azurewipe:protect=true`); then call delete.

**Validation**

* Unit tests for lifecycle transitions.
* E2E run on a test subscription where known orphan resources are created, quarantined, and then deleted; verify Activity Log and soft delete logs.([Microsoft Learn][13])

---

### 7. Priority 2 — Multi-Subscription/Region Scanning

**Why**

* Orphans appear across many subscriptions and regions; manual scanning is infeasible.

**Key decisions**

1. **Scope:** azurewipe supports:

   * A list of subscriptions (IDs), or
   * Management group scopes for discovery via ARG.([Microsoft Learn][7])
2. **Discovery engine:** default to **Resource Graph** for cross-subscription queries; SDK fallback only for gaps.
3. **Throttling behavior:** respect ARM request limits and any service-specific 429/503 responses; configure SDK retries.([Azure Docs][5])

**Implementation outline**

* Use `az account list` or management APIs to enumerate subscriptions/mgmt groups.([Microsoft Learn][3])
* For each scope, run KQL queries via **azure-resourcegraph** SDK or `az graph query`, such as:

  ```bash
  az graph query -q "
    Resources
    | where type =~ 'microsoft.compute/disks'
    | where managedBy == '' or properties.diskState =~ 'Unattached'
  "
  ```

([Microsoft Learn][7])

* Implement a concurrency controller for:

  * parallel subscriptions;
  * limits per API (based on observed 429 rates, retry headers, and ARM throttling docs).([Azure Docs][5])

**Validation**

* Run discovery in a lab tenant with multiple subscriptions; verify:

  * All target subscriptions are scanned.
  * Throttling rate is within acceptable bounds (<1–2% of calls).

---

### 8. Priority 3 — Tagging & Governance

**Why**

* Tagging+policy is the main way to align cleanup with ownership and business context.

**Key decisions**

1. **Tag filters:** azurewipe must support:

   * Allow tags (e.g. `cleanup=allow`),
   * Deny tags (`cleanup=deny` or `azurewipe:protect=true`),
   * Environment tags (`env=dev/test/prod`).([Microsoft Learn][7])
2. **Azure Policy:** recommend policies that:

   * Require `Owner`/`CostCenter` tags.
   * Deny creation of untagged resources in certain scopes.([Microsoft Learn][4])
3. **RG conventions:** e.g. `rg-<app>-<env>` with `env` tag on RG, used as default environment for contained resources.

**Implementation outline**

* Tag evaluation module:

  * Classify resources as `eligible`, `protected`, or `unknown` based on tags.
* Integration with Policy:

  * Provide Bicep/ARM samples for tag policies that align with azurewipe’s expectations.([Microsoft Learn][4])

**Validation**

* Use **ARG tag queries** to verify tag coverage and azurewipe classification logic.([Microsoft Learn][7])

---

### 9. Testing Strategy

**Unit tests**

* Use `pytest` for:

  * KQL query generation helpers.
  * Tagging/eligibility logic.
  * Ordering/dependency resolution for deletion.

**Integration tests**

* Use **azure-devtools** / `pytest` with recorded responses, or a dedicated test subscription:

  * Validate Azure SDK interactions (list, delete, lock detection).([Microsoft Learn][17])

**E2E tests**

* Scenario:

  * Create orphan resources (disks, NICs, IPs, empty RGs) via Bicep templates.([Microsoft Learn][4])
  * Run azurewipe in dry-run; check that they are discovered and quarantined.
  * Run delete; ensure they are deleted and Activity Log shows correct operations.([Microsoft Learn][13])

**Validation**

* Coverage thresholds for core logic (≥80%).
* Explicit tests for:

  * Resources with locks.
  * Soft-deleted but not purged items.

---

### 10. Observability & Operations

**Logging**

* Structured JSON logs with `run_id`, `subscription_id`, `resource_id`, `action`, `phase`, `reason`.
* No secrets; optionally log ARM request IDs.

**Azure Monitor integration**

* Send logs to **Log Analytics**, optionally using Auxiliary tier for verbose per-resource logs.([Microsoft Learn][12])
* Use **Activity Log** to cross-check deletes and configuration changes.([Microsoft Learn][13])

**Dashboards**

* Workbooks or Grafana panels:

  * Number of discovered/quarantined/deleted resources over time.
  * Estimated cost savings from deletions (see Cost Management APIs).([Microsoft Learn][18])

**Validation**

* Smoke test: run azurewipe with logging, then query Log Analytics and Activity Log to confirm that each step is traceable.

---

### 11. Security Best Practices

**Azure RBAC**

* Use least-privilege roles per scope:

  * Custom role for azurewipe that can read all resources and delete only specific types (disks, NICs, IPs, etc.).([Microsoft Learn][15])

**Auth pattern**

* **Local/dev:** `az login` + `AzureCliCredential`.([Microsoft Learn][3])
* **CI:** **service principal** with secret/cert; login via `az login --service-principal` or `ClientSecretCredential`.([Microsoft Learn][19])
* **In-Azure:** **managed identity** (system- or user-assigned) via `ManagedIdentityCredential`.([Microsoft Learn][3])

**Secrets**

* Store any non-managed credentials in **Key Vault**; soft delete and purge protection should be on by default.([Microsoft Learn][9])

**Validation**

* Security review of azurewipe’s custom role and principal.
* Automated tests to verify:

  * azurewipe fails safely when given insufficient permissions.
  * No secret values appear in logs.

---

### 12. Performance & Cost

**Discovery**

* Use **Resource Graph** for bulk queries instead of per-resource list calls, reducing API traffic and time.([LinkedIn][8])

**Throttling & retries**

* Respect rate limits:

  * Watch for **429** and **503**; read `Retry-After` headers and back off.([Azure Docs][5])
* Use SDK retry policies rather than custom loops.

**Cost visibility**

* Use **Cost Management/Consumption APIs** (Python SDK or REST) to estimate cost baselines and savings for resource types that azurewipe deletes.([Microsoft Learn][20])

**Validation**

* Measure runtime and API call counts on a sample estate; ensure runs complete within agreed windows and do not exceed expected ARM throttling thresholds.

---

### 13. CI/CD Pipeline

**CI**

* Use GitHub Actions or Azure DevOps:

  * Steps: `black` + `ruff` + `mypy` + tests (`pytest`).
  * Optionally run a “dry-run on test subscription” nightly using a service principal.

**CD**

* Package azurewipe as:

  * Python package (for CLI usage).
  * Docker image (for Functions/Container Apps).
* Deploy infra parts (Functions, identities, log targets, policies) via **Bicep** templates.([Microsoft Learn][4])

**Validation**

* Pipeline checks:

  * All tests and linters pass.
  * For infra changes, deploy to a test environment first and run regression cleanup runs before promoting.

---

### 14. Code Quality Standards

* **Style:** `black` formatting, `ruff` linting, `mypy` typing.
* **SDK patterns:** follow Azure Python SDK design guidelines; avoid private methods and raw responses where typed models exist.([Microsoft Learn][2])
* **Structure:** separate concerns:

  * `discovery/`, `classification/`, `actions/`, `state/`, `cli/`.
* **Validation:**

  * CI ensures style/typing; review checklists enforce safety rules for deletion logic.

---

### 15. Anti-Patterns to Avoid

1. **Deleting without dry-run and quarantine**

   * Why: high risk of irreversible outages; contradicts soft delete / backup protections.([Microsoft Learn][11])
   * Instead: enforce lifecycle and minimum TTLs.

2. **Ignoring resource locks**

   * Why: locks exist for a reason; ignoring them breaks governance.([Microsoft Learn][15])
   * Instead: skip and report locked resources.

3. **Hardcoding subscription IDs and environments**

   * Why: brittle; doesn’t scale to new subscriptions or management groups.
   * Instead: configuration files and ARG scopes.

4. **No pagination or retry logic**

   * Why: Azure REST APIs paginate and throttle; ignoring this leads to missing results and flaky runs.([Journey Of The Geek][14])

5. **Inline credentials or secrets**

   * Why: leaks; violates security best practices.([Microsoft Learn][3])

---

### 16. Red Flags & Smells

* **Code smells**

  * Giant script mixing KQL, SDK calls, and deletion logic.
  * No unit tests around eligibility and dependency resolution.

* **Operational smells**

  * No logs in Azure Monitor; only console prints.([Microsoft Learn][12])
  * No configuration for subscriptions, only “current az login context”.

* **Process smells**

  * Changes to deletion logic deployed without any test subscription run.
  * Soft delete/backup settings unknown or ignored.([Microsoft Learn][11])

Each smell should trigger at least:

* A **“doctor” command** (e.g. `azurewipe doctor`) that reports missing safety features.
* Creation of explicit “janitor tickets” to fix tagging, logging, or policy gaps.

---

### 17. Evidence & Citations

Key references shaping this guide:

* Azure orphan resources, workbooks, and cost-saving stories.([Microsoft Tech Community][1])
* Azure SDK for Python fundamentals, HTTP pipeline, and guidelines.([Microsoft Learn][2])
* Azure CLI authentication and managed identity patterns.([Microsoft Learn][3])
* Bicep vs ARM and recommended IaC direction.([Microsoft Learn][4])
* Resource Graph starter queries for tags and networking.([Microsoft Learn][7])
* Soft delete behavior for Key Vault, Storage, and Backup.([Microsoft Learn][9])
* Azure Monitor, Activity Log, and cost/usage docs.([Microsoft Learn][12])
* ARM throttling and 429/503 retry guidance.([Azure Docs][5])
* Cost Management and Consumption APIs.([Microsoft Learn][20])

---

### 18. Verification

**How to validate recommendations**

* **Safety model:**

  * Run azurewipe in a seeded test subscription with known orphans and protected resources; verify that:

    * All orphans are discovered, quarantined, then deleted.
    * Locked and protected/tagged resources are never deleted.

* **Performance & throttling:**

  * Stress-test discovery with many subscriptions and resources; ensure 429/503 errors are low and automatically retried/backed off.

* **Governance:**

  * Validate tag-based filters using Resource Graph (e.g. `Resources | where tags.cleanup == 'allow'`).([Microsoft Learn][7])

**Confidence levels (subjective)**

* Architecture, discovery, and lifecycle model: **High**, based on Azure orphan guides and SDK/CLI docs.
* Exact IAM/custom role definitions and tag schemas: **Medium**, as they must be tuned for each org.
* Long-term defaults on soft-delete/Monitor pricing: **Low–Medium**; re-check docs annually.

---

### 19. Technical Debt & Migration Guidance

**Common debt sources for azurewipe-type tools**

* Hard-coded KQL and heuristics scattered in code.
* Mixing CLI calls, SDK calls, and raw REST with no abstraction.
* Old ARM JSON templates instead of Bicep modules.([Microsoft Learn][4])

**Migration directions**

* **From ARM to Bicep:**

  * Decompile existing ARM templates into Bicep, then refactor into reusable modules for test resource creation and “restore” scenarios.([Microsoft Learn][21])
* **SDK upgrades:**

  * Track Azure SDK Python release notes and upgrade regularly (e.g. quarterly), ensuring retry/pagination behavior is still correct.([Azure][22])

**Ongoing debt management**

* Include azurewipe in a regular **“platform janitor”** backlog:

  * Update KQL patterns for new services.
  * Extend to new orphan resource types as guidance emerges.
  * Revisit throttling/concurrency defaults as estates grow.

This gives you a 2025-aligned, Azure-specific playbook that you can now translate into concrete specs and tickets for azurewipe’s implementation.

[1]: https://techcommunity.microsoft.com/blog/fasttrackforazureblog/azure-orphan-resources/3492198 "Azure Orphan Resources"
[2]: https://learn.microsoft.com/en-us/azure/developer/python/sdk/fundamentals/language-design-guidelines "Azure SDK Language Design Guidelines for Python"
[3]: https://learn.microsoft.com/en-us/cli/azure/authenticate-azure-cli?view=azure-cli-latest "Sign in with Azure CLI — Login and Authentication"
[4]: https://learn.microsoft.com/en-us/azure/azure-resource-manager/templates/overview "ARM templates - Azure Resource Manager"
[5]: https://docs.azure.cn/en-us/azure-resource-manager/management/request-limits-and-throttling "Understand how Azure Resource Manager throttles requests"
[6]: https://learn.microsoft.com/en-us/azure/developer/python/sdk/fundamentals/http-pipeline-retries "Understanding HTTP pipeline and retries in the Azure SDK ..."
[7]: https://learn.microsoft.com/en-us/azure/governance/resource-graph/samples/starter "Starter Resource Graph query samples - Azure"
[8]: https://www.linkedin.com/pulse/optimizing-azure-how-find-unused-resources-save-costs-a-atallah-lwrtf "Optimizing Azure: Find Unused Resources and Save on ..."
[9]: https://learn.microsoft.com/en-us/answers/questions/25697/what-are-azure-key-vaults-soft-delete-and-purge-pr "What are Azure Key Vault's soft-delete and purge ..."
[10]: https://learn.microsoft.com/en-us/azure/storage/blobs/soft-delete-blob-enable "Enable soft delete for blobs - Azure Storage"
[11]: https://learn.microsoft.com/en-us/azure/backup/secure-by-default "Secure by Default with soft delete for Azure Backup"
[12]: https://learn.microsoft.com/en-us/azure/azure-monitor/logs/data-platform-logs "Azure Monitor Logs overview"
[13]: https://learn.microsoft.com/en-us/azure/azure-monitor/platform/activity-log "Activity log in Azure Monitor"
[14]: https://journeyofthegeek.com/2019/08/24/debugging-azure-sdk-for-python-using-fiddler/ "Debugging Azure SDK for Python Using Fiddler"
[15]: https://learn.microsoft.com/en-us/azure/templates/microsoft.keyvault/2024-04-01-preview/vaults "Microsoft.KeyVault vaults 2024-04-01-preview"
[16]: https://www.cloudsma.com/2021/02/find-orphaned-azure-resources/ "Find Orphaned Azure Resources - with Azure Resource Graph"
[17]: https://learn.microsoft.com/en-us/azure/cosmos-db/nosql/best-practice-python "Best practices for Python SDK - Azure Cosmos DB"
[18]: https://learn.microsoft.com/en-us/python/api/overview/azure/cost-management?view=azure-python "Azure Cost Management SDK for Python - latest"
[19]: https://learn.microsoft.com/en-us/cli/azure/authenticate-azure-cli-service-principal?view=azure-cli-latest "Sign in with Azure CLI using a service principal"
[20]: https://learn.microsoft.com/en-us/rest/api/cost-management/query/usage?view=rest-cost-management-2025-03-01 "Query - Usage - REST API (Azure Cost Management)"
[21]: https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/compare-template-syntax "Comparing JSON and Bicep for templates - Azure"
[22]: https://azure.github.io/azure-sdk/releases/2024-01/python.html "Azure SDK for Python (January 2024)"
