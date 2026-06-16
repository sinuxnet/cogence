# ADR-003: No Code Analysis In MVP

## Status

Accepted

## Date

2026-06-16

## Context

When building an engineering intelligence platform, there is a strong temptation to analyze source code itself:

- Abstract Syntax Trees (AST) for code structure analysis
- Static analysis for code quality metrics
- Complexity scoring (cyclomatic complexity, cognitive complexity)
- Dependency analysis
- Code smell detection
- Architecture pattern recognition
- Security vulnerability scanning
- Test coverage analysis

These capabilities seem valuable and technically interesting. Modern tools make code analysis relatively accessible.

However, code analysis introduces significant complexity:

- **Language-specific parsers**: Different parser for each programming language
- **Build context requirements**: Need to understand project structure, dependencies
- **Computational cost**: Parsing and analyzing code is resource-intensive
- **Storage requirements**: Storing ASTs or analysis results requires significant space
- **Maintenance burden**: Parsers break with language updates
- **Scope creep risk**: Analysis capabilities can expand infinitely

The fundamental question is: Does Cogence need to understand source code to provide business intelligence?

## Decision

**Cogence v1 analyzes engineering activity, not source code.**

The MVP will NOT include:
- Abstract Syntax Tree (AST) parsing
- Repository scanning beyond commit metadata
- Static code analysis
- Code quality metrics
- Complexity scoring
- Architecture analysis
- Security scanning
- Dependency analysis

Cogence will only analyze commit metadata:
- Commit messages
- Author information
- Timestamps
- Files changed (paths only)
- Line counts (insertions/deletions)

## Consequences

### Positive

- **Dramatically simpler architecture**: No language-specific parsers needed
- **Faster MVP delivery**: Eliminates months of parser integration work
- **Lower computational cost**: Metadata analysis is lightweight
- **Language agnostic**: Works with any programming language
- **Smaller storage footprint**: Only metadata stored, not code or ASTs
- **Easier maintenance**: No parser updates when languages evolve
- **Validates core hypothesis**: Tests whether commit metadata alone provides value
- **Aligns with "Incremental Intelligence"**: Start simple, add sophistication later
- **Focuses on activity, not quality**: Matches Cogence's mission of understanding what happened

### Negative

- **Limited technical insight**: Cannot detect code quality issues
- **No architecture understanding**: Cannot identify design patterns or anti-patterns
- **Missing security signals**: Cannot detect potential vulnerabilities
- **No complexity metrics**: Cannot measure code maintainability
- **Dependency blindness**: Cannot track library usage or technical debt
- **Shallow understanding**: Relies entirely on commit messages for context
- **May miss important patterns**: Some engineering issues only visible in code

## Alternatives Considered

### Lightweight AST Analysis

Parse code for basic structure (functions, classes) without deep analysis.

**Rejected because:**
- Still requires language-specific parsers
- "Lightweight" analysis inevitably grows more complex
- Adds significant development time for uncertain value
- Violates "Incremental Intelligence" principle
- Can be added later if proven necessary

### Commit Message + Diff Analysis

Analyze git diffs to understand what changed without full AST parsing.

**Rejected because:**
- Diffs are noisy and hard to interpret meaningfully
- Still requires some code understanding
- Adds complexity without clear business value
- Commit messages should already describe changes
- Can be added as future enhancement if needed

### Third-Party Code Analysis Integration

Integrate with existing tools (SonarQube, CodeClimate, etc.).

**Rejected because:**
- Adds external dependency
- Requires users to run additional tools
- Increases integration complexity
- Not all organizations use these tools
- Moves away from "single source of truth" (commits)
- Can be added later as optional enhancement

## Relationship to Other ADRs

This decision reinforces:
- **ADR-001 (Commits Are Source of Truth)**: Commits provide sufficient signal
- **ADR-002 (Business Language)**: Code analysis produces technical metrics, not business insights
- **ADR-004 (Signals Over Surveillance)**: Code quality metrics can become surveillance tools

## Implementation Notes

### What We DO Analyze

From commit metadata:
- Commit frequency and timing
- Repository activity patterns
- Contributor participation
- File change patterns (which areas of codebase are active)
- Commit message content (for AI summarization)

### What We DON'T Analyze

From source code:
- Function/class definitions
- Code complexity
- Code quality
- Architecture patterns
- Security vulnerabilities
- Test coverage
- Dependencies

## Revisit Conditions

This decision should be reconsidered when:

1. **MVP validation complete**: After proving commit-based intelligence provides value
2. **Clear quality gaps identified**: When users consistently need code quality insights
3. **Security requirements emerge**: If security analysis becomes critical user need
4. **Technical debt tracking requested**: If understanding code maintainability becomes valuable
5. **Competitive pressure**: If competitors offer code analysis as differentiator
6. **Specific use case emerges**: If a clear business question requires code analysis

Code analysis should only be added if:
- Users explicitly request it
- It solves a specific business problem
- Simpler approaches have been exhausted
- The value justifies the complexity

For MVP v1, commit metadata provides sufficient signal to validate Cogence's core value proposition.