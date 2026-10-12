# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- Three or four sentences: what a user asks for, and what they get back. -->

A user asks for a thrift item in plain language, optionally with a size and a price ceiling such as "vintage graphic tee under $30". FitFindr searches the local listings, keeps the best keyword match that fits the filters, and pairs that item with pieces from the user's wardrobe. They get back the chosen listing, one or two outfits that name clothes they already own, and a short post-style caption that mentions the item, its price, and the platform. If nothing matches, they get a message telling them to raise the budget, drop the size, or change the words, and the outfit and caption steps do not run.

---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Loads every listing, keeps those at or under `max_price` when a ceiling is given, keeps those whose `size` string contains the requested size when a size is given, then ranks the rest by how many query words appear in the title, description, or style tags.
- **Inputs:** `description` (str), `size` (str or None), `max_price` (float or None). `None` skips that filter. A size match is a case-sensitive substring of the listing's size, so `"M"` matches `"S/M"`.
- **Returns:** A list of listing dicts, highest keyword score first, at most `config.SEARCH_RESULT_LIMIT` (10). Each dict has `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`.
- **When it has nothing:** An empty list. No match, every remaining score of 0, or filters that eliminate every listing all return `[]`.

### `suggest_outfit`

- **What it does:** Asks the model for one or two outfits built around a listing. With a wardrobe, the prompt lists each owned piece and tells the model to name those pieces. With an empty wardrobe, the prompt asks for general styling ideas and forbids naming clothes the user owns.
- **Inputs:** `new_item` (dict, a listing), `wardrobe` (dict with an `items` key holding a list of wardrobe item dicts).
- **Returns:** A non-empty string of outfit suggestions from `generate()`.
- **When it has nothing:** An empty `wardrobe["items"]` still returns a non-empty string of general styling advice. It does not return `""` and it does not raise.

### `create_fit_card`

- **What it does:** Asks the model for a two-to-four sentence caption that reads like a post, mentions the item, its price, and its platform once each, and uses the outfit suggestion for the vibe.
- **Inputs:** `outfit` (str), `new_item` (dict, a listing).
- **Returns:** A non-empty caption string from `generate()`.
- **When it has nothing:** If `outfit` is empty or only whitespace, returns a sentence naming the item, price, and platform, and does not call the model.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If `search_listings` returns an empty list, put a message in `session["error"]` that tells the user to raise the budget, drop the size, or change the words, and return the session without calling `suggest_outfit`. Otherwise take the first result, call `suggest_outfit`, call `create_fit_card`, and return the session.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Regex in `agent.py::parse_query`. A `$` followed by a number becomes `max_price` (float). The word `size` plus the next token becomes `size` (str). Those pieces, plus the word `under`, are stripped out of the remaining text, which is `description`. Missing price or size stays `None`.

**What moves through the session:** `query` is set by `new_session`. Then `parsed` (description, size, max_price), then `search_results`. On an empty list, `error` is set and the function returns, leaving `selected_item`, `outfit_suggestion`, and `fit_card` as `None`. On a match, `selected_item` is `search_results[0]`, then `outfit_suggestion`, then `fit_card`.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask 'vintage graphic tee under $30'

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Here is an outfit that combines your new thrift find with pieces exclusively from your wardrobe:

**Y2K Streetwear Look**
* **New Item:** Y2K Baby Tee — Butterfly Print
* **Bottoms:** Baggy straight-leg jeans, dark wash
* **Outerwear:** Vintage black denim jacket
* **Shoes:** Chunky white sneakers
* **Accessories:** Black crossbody bag

  Fit card: Scored this literal dream Y2K butterfly baby tee on depop for just $18! Styled it with my baggiest dark wash jeans, a vintage black denim jacket, and chunky white sneakers for the ultimate early-2000s streetwear vibe. 🦋✨

2 model calls this session, 438 prompt + 139 output tokens
```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
[{'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', 'description': 'Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.', 'category': 'tops', 'style_tags': ['y2k', 'vintage', 'graphic tee', 'cottagecore'], 'size': 'S/M', 'condition': 'excellent', 'price': 18.0, 'colors': ['white', 'pink', 'purple'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', 'description': 'Vintage-style bootleg tee with faded graphic. Slightly boxy fit. 100% cotton, soft and worn-in.', 'category': 'tops', 'style_tags': ['graphic tee', 'vintage', 'grunge', 'streetwear', 'band tee'], 'size': 'L', 'condition': 'good', 'price': 24.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', 'description': 'Sheer black mesh long-sleeve. Great for layering under a graphic tee or over a bralette. Stretchy material, fits true to size.', 'category': 'tops', 'style_tags': ['y2k', 'grunge', 'goth', 'layering'], 'size': 'S/M', 'condition': 'excellent', 'price': 15.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_033', 'title': 'Vintage Band Tee — Faded Grey', 'description': 'Faded grey band-style tee with distressed graphic. Crew neck. Fits boxy. Well-loved but no holes or major damage.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'band tee', 'graphic tee', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 19.0, 'colors': ['grey', 'charcoal'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_015', 'title': 'Vintage Graphic Hoodie — Faded Black', 'description': 'Faded black pullover hoodie with barely-visible vintage graphic on the chest. Cozy interior. Some pilling but adds to the worn-in look.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'graphic', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 26.0, 'colors': ['black', 'charcoal'], 'brand': None, 'platform': 'depop'}]
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
Here is one outfit combining your new Vintage Levi's 501 Jeans with pieces from your wardrobe:

**Casual Everyday Look**
*   **Bottoms:** Vintage Levi's 501 Jeans — Medium Wash
*   **Tops:** White ribbed tank top
*   **Outerwear:** Oversized grey crewneck sweatshirt
*   **Shoes:** Chunky white sneakers
*   **Accessories:** Black crossbody bag
```

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
Finally scored the ultimate laid-back, effortlessly cool look with these vintage Levi's 501s I just grabbed on depop for $38. Paired them with crisp white sneakers and a beat-up tee for that ultimate 90s coffee-run aesthetic. The light knee fading gives them that perfectly lived-in vibe right out of the box!
```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- _What I asked for:_ How to rank listings by a keyword-overlap score and drop anything scoring under 1.
- _What came back:_ Pair each listing with its score, keep pairs whose score is at least 1, sort by score descending, and return only the listing dicts up to `SEARCH_RESULT_LIMIT`.
- _What I changed:_ I used that shape in `search_listings`. The score counts shared words across the title, description, and style tags, which is what the sort is ranking.

**Moment 2**

- _What I asked for:_ Whether `if max_price and listing["price"] <= max_price` would skip the price filter when the query has no dollar amount.
- _What came back:_ It avoids the `float <= None` crash, and it also drops every listing, because `None` is false and the comparison never runs.
- _What I changed:_ I replaced it with an explicit branch: when `max_price` is `None`, keep every listing; otherwise keep `listing["price"] <= max_price`.

**Moment 3**

- _What I asked for:_ Whether this unit's instructions said to change a criterion after the test.
- _What came back:_ No. Revise a criterion only when it cannot be measured, leave the original line, and do not lower a target because a try missed it. The re-run is a change to the program, scored against the same five criteria.
- _What I changed:_ I left `criteria.md` as written in the previous unit. Criterion 1 stays "at least 4 of 5" even though the after-run was 3 of 5.

**Moment 4**

- _What I asked for:_ How to handle a bad API key, and then how to read the after-run once two tries stopped early.
- _What came back:_ Catch `ModelUnavailable` in `run_agent` and say the model could not be reached, including what to check. On the after-run, the two failures were a 503 from the model after search had already returned listings, not the new keyword filter.
- _What I changed:_ `agent.py::run_agent` now sets `session["error"]` on `ModelUnavailable` instead of crashing. I recorded those two tries as FAIL and did not rerun them until the service looked healthy.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
| --------- | ------ | ----- | ----- | ----- | ----- | ----- | ------- |
| 1. Matching query returns a fit card | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Empty search stops before suggest_outfit | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. Selected item is the one passed on | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Five different fit cards name price and platform | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Nothing over the price ceiling | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

Produced by `run_eval.py::main` into `results/run_2026-10-07_1910_before.md`, from `agent.py::run_agent`. Caching was off. Criterion 4's five tries are the first try of five different listings (baby tee, track jacket, flannel, corduroy, bomber), which is what that criterion asks for.

**Real output from one try**, pasted as text:

Criterion 1, try 1. `agent.py::run_agent` selected the Y2K Baby Tee ($18.0, depop) and `tools.py::create_fit_card` returned:

```
Found the ultimate early 2000s butterfly tee on depop for just $18, and I am so obsessed! Today I styled it with baggy dark wash jeans, chunky white sneakers, and a black crossbody bag for the most effortless streetwear vibe. It’s giving total retro mall-rat energy in the best way possible.
```

Criterion 2, try 1. `agent.py::run_agent` stopped with no selected item and no fit card:

```
Nothing matched those keywords, size, and price. Try a higher budget, drop the size, or use different words.
```

Criterion 3, try 1. The trace from `agent.py::run_agent` shows the same jacket in search, in `suggest_outfit`, and in `create_fit_card`:

```
[2] search_listings (via MCP)
      out: 7 items: 90s Track Jacket — Navy/White Stripe, ...
[3] suggest_outfit
      in:  90s Track Jacket — Navy/White Stripe ($45.0, poshmark), wardrobe items=10
[4] create_fit_card
      in:  outfit for 90s Track Jacket — Navy/White Stripe ($45.0, poshmark)
```

Criterion 4, first try of each listing. Each card from `tools.py::create_fit_card` names the price and the platform, and the five strings differ:

```
baby tee:    Found this insanely cute Y2K baby tee on depop for just $18...
track jacket: I am so obsessed with this 90s track jacket I just scored on poshmark for $45!
flannel:     Scored this oversized red and black flannel on thredUp for just $22...
corduroy:    Score! Snagged these rust corduroy wide-leg pants on depop for just $32.
bomber:      Just scored the ultimate 90s leather bomber on depop for $75...
```

Criterion 5, try 1. `tools.py::search_listings` for `vintage denim` at max $20 returned these prices, all at or under 20: 18, 20, 12, 16, 18, 19, 14. `agent.py::run_agent` selected the Y2K Baby Tee at $18.0.

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| #   | Criterion | Target | Verdict | How I decided |
| --- | --------- | ------ | ------- | ------------- |
| 1   | Matching query returns a fit card | 4 of 5 | MET | All 5 tries returned a fit card after search, suggest_outfit, and create_fit_card. |
| 2   | Empty search stops before suggest_outfit | 5 of 5 | MET | All 5 tries set the change-what message and the trace has no suggest_outfit step. |
| 3   | Selected item is the one passed on | 5 of 5 | MET | All 5 tries show the same title in search_results[0], suggest_outfit, and create_fit_card. |
| 4   | Fit card names price and platform | 5 of 5 | MET | Five different listings each named their price and platform, and no two cards were the same string. |
| 5   | Price ceiling holds | 5 of 5 | MET | All 5 tries returned the same 7 listings, and every price was <= 20. |

**Diagnoses**

Nothing missed. The targets were not all equally hard. Criteria 2 and 5 are plain code: an empty list, and a numeric comparison. They were going to be 5 of 5 unless the branch or the filter was wrong. Criterion 1's 4 of 5 allowance was not needed for this phrasing, because "vintage graphic tee" shares those words with a real listing.

The criterion I would tighten is search relevance, not the price ceiling. On "vintage denim under $20", `tools.py::search_listings` kept any listing with one shared word, so the selected item was a $18 baby tee that contains "vintage" and not "denim". The ceiling still held. The miss, if I had written the criterion that way, would be the tool: `keyword_score` counts overlap and the loop keeps anything at 1 or above.

---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```
$ python app.py ask 'vintage graphic tee under $30' --trace
[1] parse_query
      in:  vintage graphic tee under $30
      out: description='vintage graphic tee', size=None, max_price=30.0
[2] search_listings (via MCP)
      in:  description='vintage graphic tee', size=None, max_price=30.0
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
[3] suggest_outfit
      in:  Y2K Baby Tee — Butterfly Print ($18.0, depop), wardrobe items=10
      out: Here is an outfit that combines your new thrift find with pieces exclusively from your wardrobe:  **Y2K Street…
[4] create_fit_card
      in:  outfit for Y2K Baby Tee — Butterfly Print ($18.0, depop)
      out: Scored this literal dream Y2K butterfly baby tee on depop for just $18! Styled it with my baggiest dark wash j…
```

**Empty search**

```
$ python app.py ask 'designer ballgown size XXS under $5' --trace
[1] parse_query
      in:  designer ballgown size XXS under $5
      out: description='designer ballgown XXS', size='XXS', max_price=5.0
[2] search_listings (via MCP)
      in:  description='designer ballgown XXS', size='XXS', max_price=5.0
      out: [] (empty)
      →    branch: empty, stopping
```

**On the MCP move:** `search_listings` is registered in `mcp_server.py` and `run_agent` calls it through `mcp_client.call_tool` instead of calling the function directly. The return is still a list of listing dicts. The trace names that step `search_listings (via MCP)`. The empty query still stops after that step, before `suggest_outfit`.

**The three failures**

Empty search, `python app.py ask 'designer ballgown size XXS under $5'`:

```
Nothing matched those keywords, size, and price. Try a higher budget, drop the size, or use different words.
```

Empty wardrobe, `python app.py ask 'linen trousers under $35' --empty-wardrobe`. `tools.py::suggest_outfit` returned general advice, not a crash and not `""`. It did not name pieces from the example closet:

```
Here are two versatile styling ideas for your wide-leg linen trousers:

**1. Effortless Coastal Chic (Warm Weather)**
*   **Top:** A fitted, ribbed white tank top or a structured black crop top...
*   **Footwear:** Leather slide sandals or flat strappy sandals.
```

Model unavailable. One character of `GEMINI_API_KEY` was changed, then `python app.py ask 'suede chelsea boots under $45'` (a query that was not already cached). The key was put back afterward. `agent.py::run_agent` caught `ModelUnavailable` and stopped:

```
The model couldn't be reached, so I stopped before writing the outfit and the caption. The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com.
```

---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:** In `tools.py::search_listings`, a listing is kept only when every query word appears in the title, description, or style tags. Before, one shared word was enough.

**Which failure it was meant to fix:** No criterion missed. The before run of "vintage denim under $20" still selected a baby tee that contained "vintage" and not "denim". This change is that search, not a rewrite of any criterion.

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
| --------- | ------ | ----- | ----- | ----- | ----- | ----- | ------- |
| 1. Matching query returns a fit card | 4 of 5 | PASS | PASS | PASS | FAIL | FAIL | MISSED (3/5) |
| 2. Empty search stops before suggest_outfit | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. Selected item is the one passed on | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Five different fit cards name price and platform | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Nothing over the price ceiling | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

From `results/run_2026-10-07_1918_after.md`, produced by `run_eval.py::main` calling `agent.py::run_agent`. Criterion 4 is again the first try of each of the five listings.

**Did it help, and how do I know:**

It did not help the scores. Criterion 1 went from 5 of 5 to 3 of 5. Tries 4 and 5 found the baby tee, then stopped because the model returned 503 UNAVAILABLE. That is the model, not the new filter: search still returned 3 listings. Criterion 5 still has nothing over $20, but only because the same query now returns an empty list and the loop stops. Before, it returned 7 listings, all at or under $20, led by the wrong garment. The filter removed that tee and also removed every other partial match, so the query no longer returns a denim item either.

---

## What's Still Broken

**Criterion 1, after the change: MISSED (3/5), target 4 of 5.** Tries 4 and 5 of `vintage graphic tee under $30` found the baby tee, then `generate()` raised `ModelUnavailable` on `503 UNAVAILABLE` ("high demand"). The handler in `agent.py::run_agent` stopped the run, so there is no fit card. I would treat a 503 like the rate-limit path in `generate()` and retry after a short wait, instead of using the same message as a bad API key. I stopped there because the service was the thing failing, and another five-by-five run would not show whether a retry works until that 503 goes away.

**The search change, which is not a missed criterion.** "vintage denim under $20" now returns an empty list. Criterion 5 still passes only because an empty list contains nothing over $20. Before, it returned seven listings at or under $20, led by a tee that shared the word "vintage". Requiring every query word removed that tee and also every partial match, and no listing under $20 contains both words. I would score a listing higher for matching more words and still keep a one-word match when nothing matches all of them. I did not do that. The milestone allows one measured change, and a second filter would make this after-run not comparable to the before-run.

<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
