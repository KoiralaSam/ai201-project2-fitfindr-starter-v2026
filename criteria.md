# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**
4 of 5, not 5 of 5, because search is a plain word overlap on the title, description, and style tags. A phrasing that does not share those words comes back empty even when a person would call it a match. When the list is not empty, the loop always continues to the fit card, so the miss comes from the keywords, not from the branch.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
5 of 5 is reasonable here because this path never calls the model. `run_agent` checks for an empty list and returns before `suggest_outfit`. The same empty list produces the same stop every time. Criterion 1 can miss when the words do not overlap; this one is already past that, and the only question is whether the branch fires.

---

## 3. The chosen listing is the one the later tools receive

On a matching query, `session["selected_item"]["id"]` equals `session["search_results"][0]["id"]`, and that same id is the `new_item` passed into both `suggest_outfit` and `create_fit_card` — in 5 of 5 tries.

**Why this target:**
5 of 5, because the handoff is the session dict, not a guess by the model. `run_agent` stores `search_results[0]` and passes that object into the next two tools. A miss here would be the loop picking a different row, which this code does not do. Wording inside the outfit or the caption can still drift; this criterion checks the id, which does not.

---

## 4. A fit card names the price and the platform

For 5 different selected listings, each fit card mentions that listing's price and its platform, and no two of the five cards are the same string — 5 of 5.

**Why this target:**
The caption calls the model, so the sentences are allowed to change. What would be unacceptable is a card that drops the price or the platform, or five different items producing one shared caption. Those two facts are in the prompt, so 5 of 5 is a fair check. Requiring the same words every time would fight `TEMPERATURE` at 0.9, and judging "vibe" would not be something another person could score from the sentence alone.

---

## 5. A price ceiling drops anything over it

For 5 queries that include `under $N`, every listing in `session["search_results"]` has `price` less than or equal to N — 5 of 5.

**Why this target:**
5 of 5, because the ceiling is a number comparison in `search_listings`, not a model judgment. When `max_price` is missing, the filter is skipped on purpose; this criterion only covers queries that actually name a dollar amount. I did not add size to the same rule. Size is a substring check, and a letter like `l` matches inside `XL`, so a 5 of 5 size claim would be stricter than the filter can support.



---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
