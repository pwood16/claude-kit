# Prose style: machine-writing tells to cut

Applies to any prose deliverable a human will read: brain pages, dispatch reports, PR bodies,
design docs, ADRs, decks. Code, commit subjects, and terse status lines are out of scope.

The constructions below are statistical markers of machine authorship. Prose that carries
them reads as unconsidered even when the content is right. Prefer plain declaratives and
let specifics (a number, a named example) do the work of emphasis.

## The tells

1. **Negation / antithesis** (hard ban). "It's not X, it's Y", "less about X and more
   about Y", "X, not just Y". State what the thing is; delete the disclaimed half.
2. **Em dashes for punchy emphasis** where a comma or full stop does the job. Structural
   uses (list separators, ranges) are fine.
3. **Forced triplets.** Three adjectives or three bullets when the true count is two
   or four. Three is fine when there are genuinely three things; if cutting the weakest
   item loses nothing, the count was manufactured.
4. **Fragments as standalone paragraphs** for manufactured drama.
5. **Uniform rhythm.** Every paragraph three sentences of 15–20 words, the same shape
   throughout. Vary sentence and paragraph length deliberately.
6. **TED-talk pseudo-insight.** Lines that sound like a conclusion and assert nothing.
   Test: if the line could close any document on any topic unchanged ("Ultimately,
   this is about trust"), cut it.

## How to check a draft

Run this as a separate pass after the draft is finished. These patterns appear during
generation, so catch them afterward: re-read the completed draft hunting specifically
for the six above.

Then check at the document level. A page can pass sentence by sentence and still define
its subject by negation five times over. Count the sentences that characterize the
subject through contrast or absence ("avoids", "without", "unlike", "no longer").
Cited factual limitations ("the API rejects batch writes") are data and stay. When
more than about one sentence in five frames the subject by contrast, rewrite those
sentences as statements of what the subject does.

When a flagged sentence loses its punch after the cut, the punch was the construction.
Replace it with a specific claim or delete the sentence.
