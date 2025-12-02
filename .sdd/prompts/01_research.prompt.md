# Best Practices Research Template

Instruction for AI: produce a practical, evidence‑backed best practices guide tailored to this project and stack.

---

## Project Context
- Project: azurewipe
- Description: AzureWipe — автоматизированный инструмент для очистки Azure ресурсов. Удаляет orphaned ресурсы во всех регионах и подписках, аналог awswipe для Azure.
- Tech stack: Python/Azure SDK/Azure CLI/Bicep
- Domain: cloud-infrastructure
- Year: 2025

## CRITICAL: Scope Analysis (DO THIS FIRST)

Before generating any content, analyze the goal/description for scope signals:

**Detect Appetite:**
- `Small` signals: "minor", "small", "tiny", "quick fix", "tweak"
- `Batch` signals: "several", "few changes", "update", "improve"
- `Big` signals: "refactor", "redesign", "rewrite", "major", "complete overhaul"

**Detect Constraints:**
- Look for: "DO NOT", "don't", "NOT", "never", "without"
- Extract the full constraint phrase

---

## Task
Create a comprehensive best‑practices guide for azurewipe that is:
1) Current — relevant to 2025; mark deprecated/outdated items.
2) Specific — tailored to Python/Azure SDK/Azure CLI and cloud-infrastructure.
3) Practical — include concrete commands/config/code.
4) Complete — cover architecture, quality, ops, security, and technical debt.
5) Risk‑aware — define metric profile (PerfGain, SecRisk, DevTime, Maintainability, Cost, DX) with weights, plus 3–5 key risks.
6) Conflict‑aware — call out conflicting or mutually exclusive practices.
7) Verification‑ready — note how to validate each recommendation.

## Output Structure (Markdown)

### 1. Scope Analysis Summary
- Appetite: [Small/Batch/Big]
- Key Constraints: [List]
- Reasoning: [Why]

### 2. TL;DR (≤10 bullets)
- Key decisions and patterns
- Azure SDK vs CLI vs REST API trade-offs
- Resource deletion order and dependencies
- Authentication patterns (az login, service principal, managed identity)
- What changed in Azure 2025

### 3. Landscape — What's new in 2025
For Python/Azure SDK/Azure CLI:
- Azure SDK updates (azure-mgmt-* packages)
- Azure CLI v2 features
- Bicep vs ARM templates
- Azure Resource Graph for discovery
- Deprecations and EOL

### 4. Architecture Patterns (2–4 for Azure cleanup tools)
Pattern A — [NAME] (MVP)
- When to use; Steps; Pros/Cons

Pattern B — [NAME] (Scale‑up)
- When to use; Migration from A

### 5. Conflicting Practices & Alternatives
- Azure SDK vs Azure CLI for automation
- Resource Graph vs direct API enumeration
- Subscription-level vs Resource Group-level cleanup
- Soft delete vs hard delete for storage/keyvault

### 6. Priority 1 — Safety & Idempotent Deletion
- Three-phase lifecycle: discover → quarantine (tag) → delete
- Resource locks handling
- Soft delete and recovery options
- Backup before deletion

### 7. Priority 2 — Multi-Subscription/Region Scanning
- Subscription enumeration
- Azure Resource Graph queries
- Throttling and rate limits
- Parallel execution

### 8. Priority 3 — Tagging & Governance
- Azure Policy integration
- Tag-based filtering
- Resource Group conventions

### 9. Testing Strategy
- Unit tests with mocks
- Integration tests with Azure
- Frameworks: pytest, azure-devtools

### 10. Observability & Operations
- Structured logging
- Azure Monitor integration
- Activity Log

### 11. Security Best Practices
- Azure RBAC
- Service Principal vs Managed Identity
- Least privilege for deletion operations
- Key Vault for secrets

### 12. Performance & Cost
- Azure Resource Graph for efficient queries
- Batch operations
- Cost Management API integration

### 13. CI/CD Pipeline
- GitHub Actions / Azure DevOps
- Azure CLI in CI

### 14. Code Quality Standards
- Python style (black, ruff, mypy)
- Azure SDK patterns

### 15. Anti‑Patterns to Avoid
- Deleting without dry-run
- Ignoring resource locks
- Hardcoding subscription IDs
- Not handling soft-delete

### 16. Red Flags & Smells
- No pagination in resource enumeration
- Missing retry logic
- No structured logging

### 17. Evidence & Citations
- Azure documentation links
- Best practices guides

### 18. Verification
- How to validate recommendations
- Confidence levels

### 19. Technical Debt & Migration Guidance
- From ARM to Bicep
- SDK version upgrades

## Requirements
1) No chain‑of‑thought. Provide final answers with short reasoning.
2) If browsing needed, state what to check; produce provisional answer with TODOs.
3) Keep it implementable today.
4) Do not fabricate APIs; mark uncertain items as TODO.
