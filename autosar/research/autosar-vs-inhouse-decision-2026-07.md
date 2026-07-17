# AUTOSAR vs. building an in-house stack — the published, citable decision case

**Researcher D · 2026-07-17.** Scope: assemble *sourced* reasoning for the choose-AUTOSAR
(Classic / Adaptive) vs. roll-your-own decision. Every external claim carries a working URL.
Verbatim quotes are in quotation marks with the exact URL where the quote appears. Each claim
is labelled **regulation-mandated / de-facto-unavoidable / optional / n-a / press**.

Guiding empirical rule (already in the repo deck, restated here because every source below
confirms it): **AUTOSAR's value scales with the number of *organizational* boundaries the
software must cross.** A Tier-1 selling ECUs into many OEM RFQs sits at one extreme (adopt); a
vertically-integrated OEM that owns silicon-to-app sits at the other (can skip).
(`repo:autosar/slides/autosar-deck.md`, decision-map slide.)

---

## 1. The case FOR adopting AUTOSAR

### 1a. Interoperability / RFQ / supplier-exchange — AUTOSAR's own words

The canonical adoption argument is stated by AUTOSAR itself on its FAQ
(<https://www.autosar.org/faq>), all verbatim:

- **Reason for existing (§1.1.2):** the industry needs *"scalable and exchangeable software
  modules. Since these issues can hardly be handled by individual companies instead they
  constitute an industry-wide challenge, leading OEMs, suppliers and tool vendors jointly work
  on an open standard for automotive E/E architecture … Basic idea is the re-use of software
  components so that the rising complexity can also be handled in the future."*
- **Primary goal (§1.1.3):** *"The primary goal of the AUTOSAR development cooperation is the
  standardization of basic system functions and functional interfaces. This enables development
  partners to integrate, exchange and transfer functions within a car network …"* — i.e. the
  handshake is the point.
- **Benefits (§1.1.7), verbatim list:** *"Increased re-use of software … Reduction of costs for
  software development and service in the long term … OEM overlapping re-use of non-competitive
  software modules … Focus on protected, innovative and competitive functions."* And,
  specifically for the RFQ/outsourcing model — *"Specific benefits for new market entrants:
  Transparent and defined interfaces enable new business models — Clear contractual task
  allocation and outsourcing of software implementation accessible."*

**Binding:** *de-facto-unavoidable* for a company that wants to sell ECUs into OEM programs that
specify AUTOSAR (the OEM's RFQ dictates it); *optional* as a pure technology choice. AUTOSAR is
**not** regulation-mandated anywhere.

The founding-era slogan **"Cooperate on standards, compete on implementation"** captures this,
but note the already-verified repo caveat: it traces to Heinecke et al., Euroforum 2006, and is
**not** on AUTOSAR's current official pages (`repo:research/fact-check-2026-07-16.md`, Run 5 C2).

### 1b. The ARXML exchange argument (OEM ↔ supplier handshake)

AUTOSAR's model-driven flow exchanges everything as **ARXML** (fixed-schema "AUTOSAR XML"): the
OEM authors the System Description, hands each supplier an **ECU Extract**, the supplier returns
a configured ECU. This is the concrete artefact behind §1.1.3's "integrate, exchange and transfer
functions." Detailed, already-fact-checked in the repo deck
(`repo:autosar/slides/autosar-deck.md`, slide "The model-driven workflow — ARXML and the
OEM↔supplier handshake"). **Binding:** *de-facto* — it is the interface contract once you are in
an AUTOSAR supply chain.

### 1c. Safety pedigree — certified Classic stacks already exist

You can buy an ISO 26262-certified Classic base instead of building and certifying one. Primary
vendor evidence, **Vector MICROSAR Safe**
(<https://www.presseagentur.com/vector/detail.php?pr_id=5546&lang=en>, 2020-05-11), verbatim:

- *"The AUTOSAR basic software MICROSAR Safe from Vector continues to meet the requirements of
  ISO 26262 up to ASIL D. This is confirmed by the corresponding certificate dated April 23,
  2020. The re-certification was carried out by exida …"*
- *"… MICROSAR Safe with 29 modules was successfully certified for the first time according to
  ISO 26262 up to ASIL D. Now the surveillance assessment took place. It confirms compliance with
  ASIL D for 19 additional modules."*
- *"As a result, AUTOSAR developers in safety-related projects benefit from the fact that the
  most important modules of Vector's AUTOSAR basic software are awarded the highest integrity
  level."*

Corroborating vendor pages: MICROSAR Classic product page
(<https://www.vector.com/int/en/products/products-a-z/embedded-software/microsar-classic/>) and
Vector's RTE ASIL-D certification release
(<https://www.vector.com/us/en/download/autosar-rte-from-vector-receives-certification-for-iso-26262-up-to-asil-d/>).
For the Adaptive side, QNX OS for Safety is ISO 26262 **ASIL-D** certified (the de-facto AP base
OS) — already in the repo deck. **Binding:** ISO 26262 conformance for safety-relevant ECUs is
itself *de-facto-unavoidable* (liability/type-approval driven); using an AUTOSAR stack to get
there is *optional* — but buying a pre-certified stack removes a large qualification effort.

---

## 2. The case FOR skipping — build in-house

### 2a. Rivian — the published, on-record rationale

Vidya Rajagopalan (SVP, Rivian) on **The Garage** podcast (Season 2, Ep. 15, Sonatus),
verbatim (<https://www.sonatus.com/resources/vidya-rajagopalan-of-rivian/>):

> *"We don't use any of the industry offerings such as AUTOSAR. … Our zonal controllers are
> built on a very robust in-house system that the teams have developed and that's given us a
> remarkable amount of agility in terms of how quickly we're able to develop features, develop
> hardware, test and bring it up. And it's really based on top of Free RTOS, but we really added
> a lot of layers to it."*

The rationale is explicit: **agility / development speed** through vertical integration. Repo
already verified this (F3, `repo:research/fact-check-2026-07-16.md`) and scoped it: the
non-AUTOSAR / FreeRTOS statement applies to the **zonal controllers**; central compute is Android
Automotive + Rivian middleware on NVIDIA foundations (Run 4 C5). **Binding:** n/a (a company's
design rationale, not a mandate).

### 2b. Tesla — engineering-culture evidence (press; handle with care)

Verifiable, sourced facts: Tesla runs a **Linux-based, heavily-customised proprietary** vehicle
OS and has publicly released kernel/build sources.
- What OS Tesla uses (press): <https://cars.usnews.com/cars-trucks/features/what-os-does-tesla-use>
- Tesla began releasing its cars' open-source Linux code, 2018 (press):
  <https://www.linux.com/news/tesla-starts-release-its-cars-open-source-linux-software-code-2/>

**Caveat, stated plainly:** a *categorical* "Tesla uses zero AUTOSAR" is **folklore — no primary
source found** (`repo:research/notes/head-to-head-coexistence.md`). What is defensible is only
"Tesla's stack is largely proprietary Linux-based," not a proven absence of AUTOSAR anywhere in
the vehicle. **Binding:** press / n-a; do not present the "no AUTOSAR" absolute as fact.

### 2c. CARIAD / VW — the cautionary tale: in-house *at OEM scale* is hard

This is the counterweight to §2a: rolling your own is not automatically the fast path. Dates and
facts only (press):

- **2023-10-30 (TechCrunch):** VW's software unit CARIAD announced ~**2,000 job cuts**; the
  **software 1.2** platform for the **Porsche Macan EV** and **Audi Q6 e-tron** slipped
  **16–18 months** (originally 2022 → then end-2023 → at least 2025), and **software 2.0** needed
  redevelopment. <https://techcrunch.com/2023/10/30/layoffs-at-vws-cariad-further-delay-software-launch-in-porsche-audi-models/>
- **FY2024 (VW Group report, via InsideEVs):** CARIAD **operating loss €2.431 bn** on revenue
  **€1.327 bn** in 2024 (2023 loss €2.392 bn); **over €7.5 bn cumulative operating losses
  2022–2024**; a further **1,600 layoffs** planned.
  <https://insideevs.com/news/753673/vw-group-cariad-billions-losses-2024/> · VW Group FY2024
  results: <https://www.volkswagen-group.com/en/press-releases/volkswagen-group-with-solid-fy-2024-results-and-a-robust-outlook-19043>
- CARIAD was founded **2020** (as the Car.Software Organisation).

**Binding:** press / n-a — evidence, not editorial. The lesson a team can cite: an OEM without an
existing deep software org paid billions and years to build in-house; the "skip AUTOSAR" upside
(§2a) assumes Rivian/Tesla-grade in-house capability.

---

## 3. The collective third path — Eclipse S-CORE (Safe Open Vehicle Core)

S-CORE is the industry's answer to "we don't want to *only* buy AUTOSAR stacks, but in-house-alone
is too costly" — a **shared open-source** core stack funded by OEMs + Tier-1s + tool/OS vendors.

### 3a. Its own stated motivation (why fund a shared stack)

**Eclipse project charter** (verbatim,
<https://projects.eclipse.org/projects/automotive.score>):
- Purpose/scope: *"The Eclipse Safe Open Vehicle Core project aims to develop an open-source core
  stack for Software Defined Vehicles (SDVs), specifically targeting embedded high-performance
  Electronic Control Units (ECUs)."*
- *"Common Stack & Industry-Wide Collaboration … By achieving efficiencies through a single, joint
  solution instead of multiple specific ones, the project addresses non-differentiating scopes …"*
- *"Speed — The project accelerates development by working in open source, focusing on
  code-centric and iterative methods rather than primarily on textual specifications."*
- Compliance target: *"… ISO 26262 for functional safety … ISO/SAE 21434 … and UNECE WP.29."*
- Project **State: Incubating**.

**Eclipse newsletter, Sept 2025** (verbatim,
<https://newsroom.eclipse.org/eclipse-newsletter/2025/september/eclipse-s-core-new-approach-building-automotive-software-together>)
frames three traditional options and their trade-offs — *proprietary mix* ("adds integration
complexity … slows development"), *single supplier* ("creates dependence on one supplier and
limits quality control"), *in-house* ("increases the effort by far") — then states the S-CORE
thesis: *"Instead of duplicating similar work across companies, the automotive industry could
develop a shared open source platform that is free to use, shaped by a broad community, and
available to all."* Benefit line: *"Reduce duplication: Build the non-differentiating base
together once."*

**ETAS** (Bosch Tier-1, a backer), verbatim, on why it does *both* AUTOSAR and S-CORE
(<https://www.etas.com/ww/en/topics/s-core/>): *"We use robust AUTOSAR solutions for
safety-critical and hard real-time functions. At the same time, we use open-source technologies —
including those that have proven themselves in safety-critical environments, such as S-CORE — to
cover the entire spectrum of application requirements."* and *"A shared open source software
platform for basic functions reduces duplication of work, lowers costs, and creates standards
directly in the code."*

Public vision line (<https://eclipse.dev/score/>): *"Open by Choice. Safe by Design."*; scope
*"all SW-platform layers below the application layer and above the board support package of the
SoC."*

### 3b. Its stated relationship to AUTOSAR

The clearest *live, dated, attributable* statement is from S-CORE maintainer Alexander Lanin in
the project's own "Onboarding Autosar" discussion (**#759, 2025-03-24**, verbatim,
<https://github.com/orgs/eclipse-score/discussions/759>): *"AUTOSAR wants to develop an automotive
grade reference implementation. S-CORE has the necessary processes and tools which AUTOSAR can use
for their development"* and *"Using the same approach will allow for an easier integration of
S-CORE with AUTOSAR."* → S-CORE positions itself as **complementary** — the open *reference
implementation* alongside AUTOSAR's *specifications*, with active alignment, not a rival standard.
(There is a matching handbook framing that "AUTOSAR also aimed to standardize … however Eclipse
S-CORE goes beyond by … providing a reference implementation of the software platform," but the
handbook page has since been restructured to redirect to eclipse.dev/score and the sentence is not
directly extractable at a stable URL today — so I anchor the relationship to #759, which I fetched
live. Medium confidence on the exact handbook wording; high on the #759 quote.)

### 3c. Scope / timeline / who funds it — reuse of already-verified repo facts

Reused from `repo:autosar/slides/autosar-deck.md` and
`repo:research/adaptive-open-source-2026-07.md` (fact-checked in the 2026-07-16 runs):
- **Launched 2025-06-12** as "the automotive industry's first open-source core stack for SDVs."
- **Backers:** BMW Group, Mercedes-Benz, Bosch, ETAS, QNX, Qorix, Accenture (charter's initial
  five: Accenture, BMW, ETAS, Mercedes-Benz, Qorix).
- **Apache-2.0, dual-language C++ / Rust** (never Rust-first).
- Comms module **LoLa** = a *partial* implementation of Adaptive AUTOSAR Communication Management
  (`ara::com`), but its API namespace is **`score::mw::com`, not `ara::com`**, IPC on
  boost.interprocess (not iceoryx); README self-describes **ASIL-B qualified**. So S-CORE is a
  **core SDV stack, not an AP implementation**, and makes **no AP-compatibility claim** either way.

**Binding:** n/a (motivation/positioning statements).

---

## 4. Cost & integration-effort — what is actually citable

**What IS citable (primary):** AUTOSAR's own *partnership / exploitation* fee for its top tier —
Premium Partner Plus — is *"a partnership fee of 90.000€"* plus *"at least five FTE positions to
the AUTOSAR Working Groups"*
(<https://www.autosar.org/news-events/detail/autosar-announces-its-partnership-program-premium-partner-plus>).
The FAQ confirms the fee is tier-dependent: *"The annual AUTOSAR partnership fee and required FTE
contribution depends on the different partnership levels"* (<https://www.autosar.org/faq>, §1.2.4).
Note this is the cost to *co-develop the standard*, **not** a tool-license price.

**What is NOT citable — stated explicitly:** **no citable per-seat / per-project tool-license or
integration-effort figure was found.** Commercial AUTOSAR toolchains (Vector MICROSAR, ETAS
RTA / EB tresos, etc.) are quoted under NDA and their prices are not published; I did **not** find
a defensible public number and did not invent one. (A web aggregation floated other tier fees —
e.g. ~31k€ Development, ~10k€ Associate — but I could only verify the 90.000€ PP+ figure against a
primary AUTOSAR page, so the other tier numbers are reported here as *unverified*, not as fact.)

**Binding:** n/a (factual cost datum). The reading fee is zero — the specs are free to download;
"implementing commercially requires an AUTOSAR partner license" (`repo:autosar/slides/autosar-deck.md`).

---

## 5. Decision criteria matrix — when CP, when AP, when roll-your-own

Each row ties a criterion to a source. "Adopt" = Classic and/or Adaptive; "Skip" = in-house;
"Share" = S-CORE / open.

| Criterion | Points to | Evidence (source) | Binding |
|---|---|---|---|
| **Software crosses many org boundaries** (OEM ↔ multiple Tier-1s; you win/answer RFQs) | **Adopt** (CP or AP) | AUTOSAR FAQ §1.1.7 "outsourcing … accessible", "clear contractual task allocation"; §1.1.3 "integrate, exchange and transfer functions" — <https://www.autosar.org/faq> | de-facto |
| **Need signal-exchange contract with suppliers** | **Adopt** — ARXML handshake | Repo deck ARXML slide; FAQ §1.1.3 | de-facto |
| **Deep MCU control, ASIL up to D, static config** (body / powertrain / chassis) | **CP** | AUTOSAR scope = "body, power train and chassis domains first" (FAQ §1.1.4); Vector MICROSAR Safe 29+19 modules ISO 26262 ASIL-D — <https://www.presseagentur.com/vector/detail.php?pr_id=5546&lang=en> | de-facto |
| **Want a pre-certified safety base rather than building+certifying one** | **Adopt (buy)** | Vector MICROSAR Safe (ASIL-D, exida, cert 2020-04-23) | de-facto |
| **High-performance compute, service-oriented, OTA, C++ on POSIX** | **AP** | Repo deck (AP = SOA/manifest/OTA on POSIX); QNX ASIL-D base | optional |
| **Vertically integrated, own silicon-to-app, prize dev speed/agility** | **Skip** (in-house) | Rivian / Rajagopalan verbatim — <https://www.sonatus.com/resources/vidya-rajagopalan-of-rivian/>; Tesla proprietary-Linux (press) | n/a |
| **…but you lack a deep in-house software org** | **caution against Skip** | CARIAD: €2.431 bn 2024 loss, >€7.5 bn 2022–24, 16–18-mo delays — <https://insideevs.com/news/753673/vw-group-cariad-billions-losses-2024/>, <https://techcrunch.com/2023/10/30/layoffs-at-vws-cariad-further-delay-software-launch-in-porsche-audi-models/> | press |
| **Want to avoid vendor lock-in + duplicated non-differentiating effort, still safety-targeted** | **Share** (S-CORE) | Charter "single, joint solution instead of multiple specific ones" — <https://projects.eclipse.org/projects/automotive.score>; newsletter "shared open source platform"; ETAS "reduces duplication … lowers costs" | n/a |
| **Want an open reference implementation next to AUTOSAR specs (not instead of)** | **Share** (S-CORE, complements CP/AP) | GitHub #759 (2025-03-24) "S-CORE has the necessary processes and tools which AUTOSAR can use" — <https://github.com/orgs/eclipse-score/discussions/759> | n/a |
| **Budget question: co-develop the standard** | cost datum | AUTOSAR PP+ 90.000€ + 5 FTE — <https://www.autosar.org/news-events/detail/autosar-announces-its-partnership-program-premium-partner-plus> | n/a |
| **Budget question: tool licenses / integration effort** | **no public figure** | No citable number found; not invented | n/a |

---

## Source ledger

| Tag | URL | Type |
|---|---|---|
| AUTOSAR FAQ (mission, benefits, RFQ, fee-by-tier) | https://www.autosar.org/faq | primary |
| AUTOSAR Premium Partner Plus (90.000€ + 5 FTE) | https://www.autosar.org/news-events/detail/autosar-announces-its-partnership-program-premium-partner-plus | primary |
| Vector MICROSAR Safe ISO 26262 ASIL-D (29+19 modules, exida) | https://www.presseagentur.com/vector/detail.php?pr_id=5546&lang=en | vendor PR |
| Vector MICROSAR Classic product page | https://www.vector.com/int/en/products/products-a-z/embedded-software/microsar-classic/ | vendor |
| Vector RTE ASIL-D certification | https://www.vector.com/us/en/download/autosar-rte-from-vector-receives-certification-for-iso-26262-up-to-asil-d/ | vendor |
| Rivian — Rajagopalan verbatim (The Garage S2E15) | https://www.sonatus.com/resources/vidya-rajagopalan-of-rivian/ | primary (recorded talk) |
| Tesla OS (Linux-based, proprietary) | https://cars.usnews.com/cars-trucks/features/what-os-does-tesla-use | press |
| Tesla open-source Linux code release (2018) | https://www.linux.com/news/tesla-starts-release-its-cars-open-source-linux-software-code-2/ | press |
| CARIAD layoffs + Macan/Q6 delay (2023-10-30) | https://techcrunch.com/2023/10/30/layoffs-at-vws-cariad-further-delay-software-launch-in-porsche-audi-models/ | press |
| CARIAD FY2024 losses | https://insideevs.com/news/753673/vw-group-cariad-billions-losses-2024/ | press |
| VW Group FY2024 results | https://www.volkswagen-group.com/en/press-releases/volkswagen-group-with-solid-fy-2024-results-and-a-robust-outlook-19043 | primary |
| S-CORE Eclipse charter | https://projects.eclipse.org/projects/automotive.score | primary |
| S-CORE motivation (Eclipse newsletter, Sept 2025) | https://newsroom.eclipse.org/eclipse-newsletter/2025/september/eclipse-s-core-new-approach-building-automotive-software-together | primary |
| S-CORE launch announcement | https://newsroom.eclipse.org/news/announcements/eclipse-foundation-launches-s-core-project-automotive-industrys-first-open | primary |
| ETAS on AUTOSAR + S-CORE | https://www.etas.com/ww/en/topics/s-core/ | vendor |
| S-CORE public vision | https://eclipse.dev/score/ | primary |
| S-CORE ↔ AUTOSAR relationship (#759, 2025-03-24) | https://github.com/orgs/eclipse-score/discussions/759 | primary |
| Repo — deck (ARXML, decision map, LoLa, backers) | repo:autosar/slides/autosar-deck.md | repo |
| Repo — S-CORE / LoLa facts, launch date | repo:research/adaptive-open-source-2026-07.md | repo |
| Repo — Rivian F3, slogan caveat, Tesla folklore | repo:research/fact-check-2026-07-16.md | repo |

## Verification notes / honesty flags

- **"Cooperate on standards, compete on implementation"** is a founding-era phrase, **not** a
  current official AUTOSAR slogan (repo Run 5 C2). Attribute to Heinecke et al., 2006.
- **Tesla "no AUTOSAR"** is unverified folklore — only "proprietary Linux-based" is defensible.
- **S-CORE handbook "goes beyond AUTOSAR … reference implementation"** wording is real but the
  page redirected to eclipse.dev/score; relationship claim anchored to the live #759 quote instead.
- **AUTOSAR tool-license / integration-cost figures: none found.** Only the 90.000€ PP+
  partnership fee is citable. Other tier fees seen in aggregation were **not** primary-verified.
