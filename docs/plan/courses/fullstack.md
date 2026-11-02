# Full-Stack Builder (`fullstack`): course design

Status: **proposed**, written 2026-11-02. No code and no catalog change. Sources: `course-catalog.md` section 3.4, `build.md` sections 5, 7, 8 and 10.

## Audience and prerequisites

The capstone for practical builders: learners who can write a client, an API and a database separately, and now join them.

- **Required:** `node` and `git`.
- **Suggested:** `cs`.

## Outline

| Unit | Title | Lessons (proposed IDs) |
| --- | --- | --- |
| `fullstack.u01` | Scope it | `fullstack.choose-a-project`, `fullstack.write-the-brief`, `fullstack.api-contract-first` |
| `fullstack.u02` | Build one slice | `fullstack.one-vertical-slice`, `fullstack.client-to-api`, `fullstack.useful-errors` |
| `fullstack.u03` | Trust it | `fullstack.integration-tests`, `fullstack.ci-on-your-repo`, `fullstack.read-a-ci-failure` |
| `fullstack.u04` | Protect it | `fullstack.auth-and-private-data`, `fullstack.threat-model`, `fullstack.rate-limits` |
| `fullstack.u05` | Run it | `fullstack.local-staging-production`, `fullstack.logs`, `fullstack.rollback` |
| `fullstack.u06` | Show it | `fullstack.readme-and-demo`, `fullstack.explain-trade-offs`, `fullstack.real-user-feedback` |

This platform's own handoffs and threat model can serve as worked examples, once checked for anything private.

## Projects and evidence

**Full-stack planner, then a capstone** (`build.md` section 7): a working project, README, tests, a demo and an explanation of trade-offs. Rubric: behaviour 40%, testing and debugging 20%, explanation and design 15%, usability and accessibility 15%, reproducibility and documentation 10% (a proposal to pilot).

Evidence is a **rubric review of a project the learner builds on their own machine**. A private demo or local delivery is acceptable. **No public posting or paid hosting is needed for a badge.** A self-review is labelled self-reported, and a project badge follows the published rubric (`build.md` section 10).

## Runtime and safety

**None in the product.** Everything runs on the learner's machine. The platform stores a checklist, a self-review and optionally a link.

| Threat | Control |
| --- | --- |
| A learner's app collects real people's data | `fullstack.auth-and-private-data` says to use made-up data, and to get help before inviting real users |
| A pasted link leads somewhere harmful | Plain text, shown escaped, and never fetched by the server. Reviewers are warned |
| Deployment costs surprise a learner | Deployment is optional. Say plainly what costs money, and never require a card |
| A secret in a public repository | `git.committed-a-secret`, and a checklist item |

## Dependencies

None in the product.

## Checker features required

- **ENG-09** rubric and self-review types.
- **PROJ-01,** the unit project mechanism.
- A human reviewer flow, if reviewed evidence is wanted. **It does not exist,** and it would need a way to choose and protect reviewers.

## Risks

- **Few will reach it.** Build it last, and with real learners' input.
- **Reviewing takes people.** Without reviewers, the evidence stays self-reported, and the label must say so.
- **Young learners and real users.** A 13 year old collecting strangers' data is a real concern, so `fullstack.real-user-feedback` needs care.
- **Tools change,** so keep them in dated lessons.

## Open questions for Lucas

Each recommendation is **recommended, not yet confirmed**.

1. Is there human review, or only self-review? *Recommended: self-review at first, with labels saying so.*
2. Should deployment be taught at all? *Recommended: as an optional tutorial with a free path, if one still exists when this is written. Check at that time.*
3. Can this project's own repository be a worked example? *Recommended: selected excerpts only. The repository is private, and it holds decisions you may not want public.*
