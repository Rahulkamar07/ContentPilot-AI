# ContentPilot AI - Quality Assurance & Testing Matrix

## Document Metadata

| Attribute | Value |
| :--- | :--- |
| **Document ID** | `DOC-32-TESTING-MATRIX` |
| **Author** | Principal QA Engineer & Software Architect |
| **Status** | Approved / Enterprise Specification |
| **Current Version** | `1.0.0` |
| **Last Updated** | `2026-07-31` |

### Version History
| Version | Date | Author | Description |
| :--- | :--- | :--- | :--- |
| `1.0.0` | 2026-07-31 | QA Lead | Comprehensive testing matrix & CI quality gate specification. |

---

## 1. Testing Pyramid Coverage Matrix

```
                      /\
                     /  \     End-to-End Browser Tests (Playwright E2E) [5%]
                    /    \    Load Tests (Locust) & Security Scans (ZAP) [10%]
                   /------\
                  /        \   API & Database Integration Tests (Pytest / AsyncPG) [25%]
                 /----------\
                /            \ Domain Unit Tests (Pytest / Vitest / Mocks) [60%]
               /--------------\
```

| Test Level | Framework / Tool | Scope / Targets | Minimum Coverage Target | Run Phase |
| :--- | :--- | :--- | :---: | :--- |
| **Domain Unit** | `pytest` | Domain Entities, Services, Prompt Parsers | **90%** | Every PR / Pre-commit |
| **UI Unit** | `vitest` + `@testing-library/react` | React components, Zustand stores | **80%** | Every PR |
| **API Integration** | `pytest-asyncio` + `httpx` | FastAPI controllers & DB session models | **85%** | Every PR / Staging |
| **E2E UI Flow** | `playwright` | Login, Queue approval, Workspace settings | **Critical Flows** | Staging Deployment |
| **Load Testing** | `locust` | 1,000 concurrent users, 10k queue items | **SLA Latency** | Weekly / Release |
| **Security Audit** | `bandit`, `npm audit`, `trivy` | Python code, Node packages, Docker images | **Zero Critical** | Nightly CI |

---

## 2. CI/CD Quality Gate Standards

A Pull Request (PR) cannot be merged to `main` unless:
1. All Pytest and Vitest test suites pass with 0 failures.
2. Code coverage on new/modified lines is $\ge 85\%$.
3. Docker image vulnerability scan by Trivy detects zero `HIGH` or `CRITICAL` CVEs.

---

## Document Cross-References
- Coding Standards: [CodingStandards.md](file:///d:/Projects/ContentPilot/docs/CodingStandards.md)
- Performance Targets: [29_PerformanceTargets.md](file:///d:/Projects/ContentPilot/docs/29_PerformanceTargets.md)
- Development SDLC: [35_DevelopmentWorkflow.md](file:///d:/Projects/ContentPilot/docs/35_DevelopmentWorkflow.md)
