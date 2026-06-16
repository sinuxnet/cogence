# ADR-005: AI Generates Summaries, Not Facts

## Status

Accepted

## Date

2026-06-16

## Context

Cogence uses AI to transform engineering activity into business-readable intelligence. AI can be used in two fundamentally different ways:

**Option 1: AI Generates Everything**
- AI extracts facts from commits
- AI interprets those facts
- AI generates summaries
- All data flows through AI

**Option 2: Structured Data + AI Interpretation**
- System extracts facts from commits (structured data)
- Facts stored in database
- AI only interprets and summarizes facts
- Clear separation between facts and interpretation

The critical question is: Should AI be trusted to generate factual data, or should it only interpret verified facts?

AI models can hallucinate, misinterpret, or invent information. When AI generates both facts and summaries, errors compound:
- Wrong commit count → wrong summary
- Misidentified contributor → wrong attribution
- Invented repository → false information

This violates Cogence's "Trust Is Mandatory" principle.

## Decision

**Raw facts come from Git. AI only interprets facts.**

### Architecture

**Structured Data (System Extracts)**:
- Commit count: 15
- Repository list: ["backend", "frontend", "mobile"]
- Contributor list: ["Sean", "Donald", "Florentino"]
- Timestamp ranges
- File change counts
- Commit messages (raw text)

**AI Interpretation (AI Generates)**:
- Executive summary
- Business language translation
- Trend observations
- Management notes
- Contextual insights

### Example

**Stored as Structured Data**:
```json
{
  "period": "2026-06-16",
  "commits": 15,
  "repositories": ["customer-portal", "api-gateway"],
  "contributors": [
    {"name": "Sean", "commits": 7, "repos": ["customer-portal"]},
    {"name": "Donald", "commits": 5, "repos": ["api-gateway"]},
    {"name": "Florentino", "commits": 3, "repos": ["customer-portal"]}
  ]
}
```

**AI Generates Summary**:
```
Engineering focused on customer-facing improvements yesterday.
The team made 15 commits across 2 projects, with primary attention
on the customer portal. Sean led customer platform enhancements
while Donald improved backend infrastructure.
```

**Never Let AI Invent Facts**:
- ❌ AI should NOT determine commit count
- ❌ AI should NOT identify contributors
- ❌ AI should NOT list repositories
- ✅ AI SHOULD interpret what the facts mean
- ✅ AI SHOULD translate technical to business language
- ✅ AI SHOULD identify patterns and trends

## Consequences

### Positive

- **Trustworthy facts**: Numbers and names come from Git, not AI
- **Verifiable data**: Every fact can be traced to source
- **Reduced hallucination risk**: AI cannot invent commits or contributors
- **Aligns with "Trust Is Mandatory"**: Facts are reliable, interpretations are transparent
- **Debugging capability**: Can verify AI summaries against structured data
- **Audit trail**: Clear separation between what happened (facts) and what it means (interpretation)
- **Regeneration possible**: Can regenerate summaries without re-fetching Git data
- **Multiple interpretations**: Same facts can be summarized differently for different audiences

### Negative

- **More complex architecture**: Requires structured data extraction layer
- **Storage overhead**: Must store both structured data and AI summaries
- **Dual processing**: Extract facts, then interpret them (two steps)
- **Potential inconsistency**: AI summary might not perfectly match structured data
- **Limited AI flexibility**: AI cannot "discover" facts, only interpret provided ones

## Alternatives Considered

### AI Extracts Everything

Let AI parse commit data and generate both facts and summaries in one pass.

**Rejected because:**
- AI can hallucinate commit counts, contributor names, repository names
- No way to verify accuracy without re-parsing
- Violates "Trust Is Mandatory" principle
- Cannot regenerate summaries without re-querying Git
- Debugging is nearly impossible
- Users cannot trust the numbers

### Hybrid: AI Extracts Some Facts

System extracts basic facts (counts), AI extracts complex facts (themes, patterns).

**Rejected because:**
- Unclear boundary between system and AI responsibility
- Still allows AI to invent some facts
- Doesn't fully solve trust problem
- Adds complexity without clear benefit

### No AI, Only Structured Data

Don't use AI at all, just present structured data.

**Rejected because:**
- Defeats Cogence's purpose (business-readable intelligence)
- Managers don't want raw data, they want insights
- Structured data alone doesn't answer "So what?"
- Misses opportunity for natural language summaries

## Implementation Guidelines

### System Responsibilities (No AI)

Extract and store:
- Commit SHA, author, timestamp, message
- Repository name
- Files changed (paths)
- Line counts (insertions, deletions)
- Aggregate counts (total commits, unique contributors, active repos)

### AI Responsibilities (Interpretation Only)

Generate:
- Executive summary in business language
- Contributor activity descriptions
- Project focus observations
- Management notes
- Trend identification

### Prompt Engineering

AI prompts must include structured facts:

```
Generate an executive summary based on these facts:
- 15 commits made yesterday
- 3 contributors: Sean (7 commits), Donald (5 commits), Florentino (3 commits)
- 2 repositories: customer-portal, api-gateway
- Commit messages: [list of actual messages]

Translate technical details to business language.
Focus on outcomes, not implementation.
```

### Validation

Every AI-generated summary should be validated against structured data:
- Commit counts must match
- Contributor names must match
- Repository names must match
- No invented information

## Relationship to Other ADRs

This decision reinforces:
- **ADR-001 (Commits Are Source of Truth)**: Git provides facts, not AI
- **ADR-002 (Business Language)**: AI translates facts to business language

This decision is reinforced by:
- **Principle 7: Trust Is Mandatory**: Facts must be reliable and traceable
- **Principle 4: Explainability Over Mystery**: Clear separation between facts and interpretation

## Revisit Conditions

This decision should be reconsidered when:

1. **Never for factual data**: AI should never generate commit counts, contributor names, or repository lists
2. **Advanced pattern recognition**: If AI needs to identify complex patterns that cannot be pre-computed
3. **Semantic analysis**: If understanding commit intent requires AI interpretation of raw data
4. **Real-time processing**: If structured extraction becomes a performance bottleneck

Even in future versions:
- Core facts (counts, names, timestamps) must come from system, not AI
- AI interpretations must be clearly labeled as interpretations
- Users must be able to verify AI summaries against structured data

This is an architectural principle, not just an MVP decision.