---
depends_on: []
---

# M###: [Milestone Name]

## Goal
[One paragraph: what does this milestone deliver and why does it matter?
What can a user DO that they couldn't before?]

## Success Criteria
- [ ] User can [complete specific end-to-end flow]
- [ ] [Measurable criterion 2]
- [ ] No regressions in existing functionality

## Architecture Decisions
[Key decisions made during discussion. All slices must respect these.
Example:
- Auth: NextAuth.js credentials + GitHub OAuth (Clerk deferred — vendor risk)
- Search: PostgreSQL full-text tsvector (Meilisearch → M003)
- Images: Client-side resize 1200px max before S3 upload]

## Data Models
[Schema definitions relevant to this milestone.]

## API Contracts
[Key endpoints and their request/response shapes.
Example:
POST /api/auth/register
  Body: { email, password }
  Response: { user: { id, email }, token }
  Errors: 409 (email taken), 422 (validation)]

## Slices
| # | Name | Risk | Depends | Demo Line |
|---|------|------|---------|-----------|
| S01 | [name] | high | — | [what user can do after S01] |
| S02 | [name] | medium | S01 | [demo] |

## Known Constraints
[Third-party API quirks, performance requirements, regulatory constraints.]

## Open Questions
- [ ] [Question needing resolution]
