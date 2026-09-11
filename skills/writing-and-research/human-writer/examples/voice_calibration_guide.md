# Voice Calibration Guide: Matching User Writing Style

How to analyze and mirror a specific person's natural voice when rewriting synthetic text.

---

## 1. The 6 Dimensions of Human Voice

When a user submits a writing sample, inspect these 6 dimensions before rewriting:

| Dimension | Questions to Ask | Low Setting | High Setting |
| :--- | :--- | :--- | :--- |
| **1. Cadence / Length** | Are sentences clipped or flowing? | Short, telegraphic (5–10 words) | Periodic, multi-clause (25–35 words) |
| **2. Vocabulary Register** | Do they write like an academic or a barista? | Gritty, colloquial ("stuff", "messy") | Technical, precise ("heuristic", "deterministic") |
| **3. Openings** | How do paragraphs start? | Sudden ("Look,", "Here's the thing:") | Formal contextual frame ("In evaluating...") |
| **4. Punctuation Habits** | What symbols do they overuse? | Minimal (periods only) | Expressive (parentheses, dashes, colons) |
| **5. Personal Stance** | Do they use first-person pronouns? | Third-person detached ("one observes") | First-person opinionated ("I noticed", "my take:") |
| **6. Transitions** | How do ideas connect? | Juxtaposition (no connector word) | Conversational ("Anyway,", "On the other hand,") |

---

## 2. Sample Ingestion Walkthrough

### User Provided Sample:
> "We spent three weeks debugging a race condition in the auth worker. Turns out Redis wasn't dropping keys on expiration—it was just waiting for a passive read. Annoying, but whatever. Switched to an active sweep and latency dropped back down to 14ms. If you're seeing weird memory spikes in Redis, check your eviction policy first."

### Voice Profile Extracted:
- **Cadence**: Short punchy sentences (avg 11 words). One-word interjections (*"Annoying, but whatever."*).
- **Register**: Practical engineering slang (*"Turns out"*, *"weird memory spikes"*, *"flying blind"*).
- **Punctuation**: Em dash used once naturally; contractions preferred (*wasn't*, *you're*).
- **Stance**: First-person plural/singular mix (*"We spent"*, *"If you're seeing"*).

### Rewriting Target Using This Voice:
- **Raw AI Draft**:
  *The caching infrastructure represents a pivotal cornerstone of system reliability, boasting multi-layered eviction mechanisms that serve to optimize throughput.*
- **Calibrated Rewrite**:
  *The cache is what keeps the whole thing from falling over. We use a couple of eviction rules to keep memory from bloating up under heavy load.*
