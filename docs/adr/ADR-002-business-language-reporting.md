# ADR-002: Business Language Over Technical Language

## Status

Accepted

## Date

2026-06-16

## Context

Cogence's primary users are non-technical managers (CEOs, founders, engineering managers, product managers) who need to understand engineering activity without technical expertise.

Engineering teams naturally communicate using technical terminology:
- Framework names (NestJS, React, FastAPI)
- Infrastructure tools (Docker, Kubernetes, Redis)
- Technical concepts (AST, webhooks, microservices)
- Implementation details (database migrations, API endpoints)

However, managers care about business outcomes:
- What customer problems were solved?
- What features were improved?
- What risks were addressed?
- What business capabilities were enhanced?

The fundamental question is: Should Cogence reports use engineering language or business language?

## Decision

**Reports target managers, not developers.**

All Cogence reports, summaries, and insights must be written in business language that non-technical readers can understand.

### Language Guidelines

**Avoid technical terminology:**
- NestJS → Backend improvements
- React → User interface enhancements
- Redis → Performance improvements
- Docker → Deployment infrastructure
- PostgreSQL → Database updates
- API endpoints → Integration capabilities

**Prefer business outcomes:**
- Authentication improvements
- Customer workflow enhancements
- Performance improvements
- Security updates
- User experience improvements
- Data processing capabilities

## Consequences

### Positive

- **Accessible to target users**: Managers can understand reports without technical knowledge
- **Aligns with "Business First" principle**: Focuses on outcomes, not implementation
- **Increases report adoption**: Non-technical leaders will actually read and use reports
- **Reduces cognitive load**: Readers don't need to translate technical terms
- **Focuses on value**: Emphasizes what was accomplished, not how it was built
- **Broader organizational understanding**: Reports can be shared with non-engineering stakeholders

### Negative

- **Loss of technical precision**: Engineers may find reports too abstract
- **Translation complexity**: AI must map technical commits to business concepts
- **Potential ambiguity**: Business language may be less specific than technical terms
- **Context dependency**: Same technical change might map to different business outcomes
- **Developer frustration**: Engineers may feel their work is oversimplified
- **Translation errors**: Risk of misinterpreting technical work as wrong business outcome

## Alternatives Considered

### Technical Language with Glossary

Use technical terms but provide a glossary for non-technical readers.

**Rejected because:**
- Requires readers to constantly reference glossary
- Adds friction to report consumption
- Violates "Human-Centered Reporting" principle
- Managers won't use reports that require technical translation
- Defeats the purpose of automatic intelligence

### Dual Reports (Technical + Business)

Generate two versions: one for engineers, one for managers.

**Rejected because:**
- Doubles report generation complexity
- Creates maintenance burden
- Cogence's mission is business intelligence, not engineering analytics
- Engineers already have technical tools (Git, GitHub, Jira)
- Dilutes focus from primary user (managers)

### Hybrid Approach with Technical Details in Footnotes

Business language in main report, technical details available on demand.

**Rejected for MVP because:**
- Adds complexity to report structure
- May tempt managers to dive into technical details unnecessarily
- Can be added later if users request it
- MVP should validate core value first

## Implementation Notes

### AI Prompt Engineering

The AI summarization system must be explicitly instructed to:
1. Translate technical terms to business outcomes
2. Focus on "what" and "why", not "how"
3. Use language a non-technical CEO would understand
4. Avoid framework names, tool names, and technical jargon

### Example Translations

| Technical Commit | Business Translation |
|-----------------|---------------------|
| "Migrate to NestJS controllers" | "Backend architecture improvements" |
| "Add Redis caching layer" | "Performance optimization" |
| "Implement JWT authentication" | "Security enhancements" |
| "Refactor React components" | "User interface improvements" |
| "Add Docker compose configuration" | "Deployment infrastructure updates" |

## Revisit Conditions

This decision should be reconsidered when:

1. **Engineers become primary users**: If Cogence pivots to serve engineering teams directly
2. **Technical audience requests**: If managers consistently ask for more technical detail
3. **Compliance requirements**: If regulatory or audit needs require technical precision
4. **Multi-audience product**: If Cogence expands to serve both technical and non-technical users
5. **User feedback indicates confusion**: If business language creates more confusion than clarity

For MVP v1, business language is mandatory. Future versions may offer technical detail as optional enhancement.