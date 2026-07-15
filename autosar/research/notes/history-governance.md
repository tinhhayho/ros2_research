# AUTOSAR: History, Governance, Releases, and Document Landscape

> Research notes for the ros2_research repo. Audience: embedded/firmware engineers new to
> automotive software platforms. Written 2026-07-15. All load-bearing claims carry a source
> reference `[n]` keyed to the Sources section. Where a fact could not be verified from a
> primary source, it is flagged in Open Questions.

## Executive summary

AUTOSAR (AUTomotive Open System ARchitecture) is a worldwide development partnership founded in
2003 by BMW, Bosch, Continental, DaimlerChrysler and Volkswagen (joined soon after by Siemens
VDO), with Ford, PSA and Toyota joining in late 2003 and GM in 2004 [3][8]. It publishes an open,
royalty-free-to-read standard organized as three "standards": **Foundation (FO)**, the older
**Classic Platform (CP)** for statically-configured real-time ECUs (OSEK heritage), and the
newer **Adaptive Platform (AP)** for high-performance, service-oriented POSIX compute [2][3].
Since **R19-11** (November 2019) all three are shipped as one annual `R{yy}-11` release with a
single XML schema; the latest is **R25-11**, published 2025-11-27 and presented at the virtual
release event on 2025-12-04 [1][4][5]. AUTOSAR today has **~339 partners** across eight
membership tiers [7], governed by a Core-Partner-controlled board. Specification PDFs are
downloadable by anyone, but commercial exploitation requires a license/partnership [4][6]. The
partnership is repositioning around the Software-Defined Vehicle (SDV): a 2022 "opening
strategy," a Vehicle API, DDS on the Classic Platform (new in R25-11), and a January 2026
leadership refresh that added DENSO, Huawei and Vector as Core Partners [10][11][13].

## 1. Founding story and governance

The idea crystallized in **2002**: "Initial discussions on the common challenge and objectives
were held by **BMW, Bosch, Continental, DaimlerChrysler and Volkswagen**. The partners were
joined soon afterwards by **Siemens VDO**" (kick-off workshop August 2002) [3]. In **July 2003**
the "Initial AUTOSAR Development Agreement [was] signed off by the Core Partners," and AUTOSAR
was announced publicly in **September 2003 at the VDI Conference in Baden-Baden** [3]. The core
group then grew: **Ford** joined November 2003; **Peugeot Citroën (PSA)** and **Toyota** in
December 2003; **General Motors** in November 2004 [3][8]. In February 2008 "Siemens VDO became
part of Continental. Since this, Siemens VDO was no longer a self-contained Core Partner" [3].

**Governance structure** (AUTOSAR Introduction Part 1) is layered [7]:
- **Executive Board** — top governance body.
- **Steering Committee** — strategic management; per the official-roles chart this level is
  reserved to **Core Partners** [7].
- **Project Leader Team** — technical steering, open to Core Partners and Premium Partner Plus.
- **Working Groups (WGs)** — the standardization work; R25-11 involved "more than 200 AUTOSAR
  partners across **20 working groups**" [5]. Working-group participation extends down to
  Premium and Development Partners [7].

Support functions run through an Internal Affairs Office (IAO): Business Administration,
Communication, Technical Management (standards, SW dev/integration), and Deliverable Management
(change/quality/release management) [7]. The registered address is Hörgertshausen, Germany [3].

## 2. Membership tiers and current partner count

The Introduction deck lists **eight partnership types** with fees and mandatory contribution [7]:

| Tier | Annual fee | Annual contribution |
|---|---|---|
| Premium Partner Plus (PP+) | €90,000 | 5 FTE + 1 FTE project leader |
| Premium Partner | €31,000 | 1.5 FTE |
| Development Partner | €10,000 | 0.5 FTE |
| Associate Partner | €21,000 | none |
| Associate Partner [Light] | free | none |
| Attendee | free | individual agreement |
| Subscriber | €3,000 | none |
| Core Partner | (governance tier — the ~10 companies that own/steer the partnership) |

Fees/contributions are quoted verbatim from the deck [7]. As of the current Introduction deck the
regional breakdown sums to **339 total partners**: North America 41 (2 Core, 8 Premium, 5 Dev,
20 Associate, 6 Attendee), Europe 128 (6 Core, 1 PP+, 26 Premium, 21 Dev, 44 Associate, 30
Attendee), Asia 164 (1 Core, 2 PP+, 30 Premium, 30 Dev, 90 Associate, 11 Attendee), Africa 6 (5
Dev, 1 Attendee) [7].

**Current Core Partners (July 2026)**, read from the live core-partner page logos: **AUMOVIO**
(the spun-off former Continental automotive-electronics business), **BMW, Bosch, DENSO, General
Motors, Huawei, Mercedes-Benz, Toyota, Vector Informatik, Volkswagen** [9][13]. **DENSO, Huawei
and Vector Informatik were promoted to Core Partner in January 2026** (announced 15.01.2026);
DENSO had been a Premium Partner since 2004 and a Strategic Partner from 2019 [13]. Note that
**Ford and PSA/Stellantis, both founding-era Core Partners, are no longer shown as Core
Partners** — the core circle has shifted toward suppliers and Asian OEMs (see Surprises).

## 3. The three standards and the document landscape

AUTOSAR is not one document but a **standard set** with three members [4]:
- **Foundation (FO)** — cross-platform "glue": common requirements, the meta-model/XML schema,
  the methodology and protocols (e.g. SOME/IP, time sync) shared by CP and AP, to "enforce
  interoperability between the AUTOSAR platforms" [2].
- **Classic Platform (CP)** — statically configured, real-time ECUs; OS derived from **OSEK/VDX**
  [2][12]. (Technical detail is covered by sibling agents.)
- **Adaptive Platform (AP)** — POSIX-based, service-oriented, dynamic; first released 2017 [3].

**Document types** (the prefix in every filename `AUTOSAR_<PLATFORM>_<TYPE>_<Name>.pdf`, and in
every requirement ID `[<TYPE>_<Module>_<nnnn>]`) [15][16]:

| Prefix | Meaning | Purpose |
|---|---|---|
| **EXP** | Explanatory | High-level background/rationale (e.g. `EXP_Introduction`, `EXP_SOVD`) |
| **TR** | Technical Report | Methodology, release overviews, predefined names (e.g. `TR_ReleaseOverview`) |
| **RS** | Requirements Specification | "Requirements on …" — what a module/feature must do |
| **SRS** | Software Requirements Spec | Older CP requirement documents (requirements on BSW) |
| **SWS** | Software Specification | Detailed, testable spec of a software module (e.g. `SWS_CanIf`) |
| **TPS** | Template Specification | The meta-model templates (e.g. `TPS_SoftwareComponentTemplate`) |
| **PRS** | Protocol Requirements Spec | Wire protocols (SOME/IP, time-sync, DoIP) |

AUTOSAR itself describes the "depth" spectrum as ranging from high-level documents (EXP, TR) down
to fine-grained specifications (SWS, TPS, PRS) [15]. `ASWS` (an auxiliary/abstract SWS) also
appears in CP filenames but its exact expansion is not confirmed here (Open Questions).

## 4. Release history (verified table)

Sources: AUTOSAR History page [3] for dates; the R25-11 CP/AP Release Overview schema-mapping
tables [4] for the internal-number and schema mapping.

**Classic Platform (separate era):** 1.0 (May 2005), 2.0 (May 2006), 2.1 (Nov 2006), 3.0 (Dec
2007), 3.1 (Aug 2008), 4.0 (Dec 2009), 3.2 (May 2011), 4.1.0 (Mar 2013), 4.2.1 (Oct 2014), 4.2.2
(Jul 2015), 4.3.0 (Oct 2016), 4.3.1 (Dec 2017), **4.4.0 (Oct 2018)** — last standalone CP [3].

**Adaptive Platform (separate era):** **17-03 (March 2017, first AP release)**, 17-10 (Oct 2017),
18-03 (Mar 2018), 18-10 (Oct 2018), **19-03 (Mar 2019)** — last standalone AP [3][4].

**Foundation (separate era):** **R1.0.0 (October 2016, first Foundation release, alongside CP
4.3.0)**, 1.4.0 (Mar 2018), 1.5.0 (Oct 2018), 1.5.1 (Mar 2019) [3][4].

**Unified era (`R{yy}-11`, one release / one schema for all three):**

| Release | Date | Internal (CP) no. | XML schema |
|---|---|---|---|
| R19-11 | Nov 2019 | R4.5.0 | AUTOSAR_00048 |
| R20-11 | Nov 2020 | R4.6.0 | AUTOSAR_00049 |
| R21-11 | Nov 2021 | R4.7.0 | AUTOSAR_00050 |
| R22-11 | Nov 2022 | R4.8.0 | AUTOSAR_00051 |
| R23-11 | Nov 2023 | R4.9.0 | AUTOSAR_00052 |
| R24-11 | Dec 2024 (event 2024-12-05) | R4.10.0 | AUTOSAR_00053 |
| **R25-11** | **published 2025-11-27; event 2025-12-04** | **R4.11.0** | **AUTOSAR_00054** |

Mapping and internal numbers are quoted from the R25-11 overview [4]. R25-11 is officially a
**minor release** ("in Evolution … supersedes R24-11") [4]. Its release event drew "more than 800
participants representing over 250 companies," with "approximately 1,900 incorporation tasks
across the three AUTOSAR Standards" [5].

## 5. What changed at R19-11

The R25-11 overview states it plainly: "Until the Releases **CP R4.4.0 and AP R19-03**, AUTOSAR
released the platforms separately where a Foundation release went along with each platform
release … Starting with release **R19-11, all platforms are released as one AUTOSAR release and
therefore come along with one schema version**" [4]. So R19-11 unified three things at once:
(a) the **naming** — dropping CP's `4.x.y` and AP's `yy-mm` in favor of a common annual
`R{yy}-11` label (the platform release number is "e.g. R20-11 for the November 2020 release" [4]);
(b) the **cadence** — one synchronized November release per year; and (c) the **schema** — a single
`AUTOSAR_000nn` XML meta-model version usable across CP and AP so that AP and CP ECUs can coexist
in one vehicle project [4]. The Foundation standard (introduced 2016) is what carries the shared
meta-model, methodology and protocols that make this cross-platform compatibility possible [2][4].
The CP internal version line did **not** reset — it continues as R4.5.0 (R19-11) … R4.11.0
(R25-11) [4].

## 6. How to legally read the specs

Every AUTOSAR PDF is **publicly downloadable without a login** (these notes were built by fetching
CP/AP/FO PDFs directly, no credentials). The legal boundary is in each document's disclaimer:
"This work may be utilized or reproduced without any modification, in any form or by any means,
**for informational purposes only** … The **commercial exploitation** of the material contained in
this work **requires a license** to such intellectual property rights" [4]. So: free to read and
study; a partnership/license is required to build and sell products from it. The 2022 opening
strategy noted "the introduction of an **additional license is under consideration, which would
allow the use of AUTOSAR specifications and implementations for non-AUTOSAR partners, e.g.
universities and startups**, before actual industrialization or without intention of commercial
exploitation" [10] — whether that license has formally launched is unverified (Open Questions).

## 7. Prehistory and neighboring standards

- **OSEK/VDX** — the 1990s German/French automotive OS+communication standard is the direct
  ancestor of the Classic Platform OS; CP is "the standard for embedded real-time ECUs based on
  OSEK" [12].
- **ISO 26262** (functional safety) and **ISO/SAE 21434** (cybersecurity) are the safety/security
  regimes AUTOSAR mechanisms (E2E, memory protection, SecOC) are designed to support [14].
- **ASAM SOVD** (Service-Oriented Vehicle Diagnostics, now standardized as ISO 17978-3, HTTP/REST
  + JSON + OAuth) has been **adopted into the AUTOSAR Adaptive Platform** as an explanatory
  standard (`AP_EXP_SOVD`, present R22-11 through R24-11) — AUTOSAR published an AP update in
  response to ASAM's SOVD release [17].
- **JASPAR** (Japan) is a partner body through which DENSO promotes AUTOSAR adoption [13].
- **COVESA** and the **Eclipse SDV** working group are parallel/adjacent open-SDV efforts, not
  part of AUTOSAR [10, secondary].

## 8. SDV roadmap statements

The anchor is AUTOSAR's **"Opening Strategy – Software Defined Vehicle Ecosystem" (05.05.2022)**:
"The scope is extended to the interaction between onboard and offboard software, which finally
represents the complete Software Defined Vehicle (SDV) … AUTOSAR decided to introduce a new
standard called **'Vehicle API'** to simplify to interact with AUTOSAR in the vehicle for the
world outside AUTOSAR, i.e. connecting the IoT world. This standard will be developed in a **new
framework, which will also be open to non-AUTOSAR Partners** … clarify the opening protocols on
network level, such as **SOME/IP** … and **Dlt (Diagnostics, Log and Trace)**" [10]. The same PR
launched **Premium Partner Plus** (2022) to give partners "extended influence on shaping the
AUTOSAR standards" [10].

Fresher signals (last ~18 months):
- **R25-11 (Nov 2025)** introduced, on the *Classic* Platform, "**DDS Support on Classic
  Platform**" and a "**Vehicle Data Protocol**" concept — both SDV/data-centric moves (DDS is the
  same middleware family ROS 2 uses) [4].
- **January 2026 press release**: "AUTOSAR Partnership **Announces New Leadership and Core
  Partners, Strengthening Its Role in the Software-Defined Vehicle Ecosystem**," coinciding with
  the DENSO/Huawei/Vector Core-Partner promotions [11][13]. DENSO framed its Core-Partner role
  around "pioneering the evolution of automotive software platforms for the **Software-Defined
  Vehicle (SDV) era**" [13].

## Key facts

| # | Fact | Source URL | Exact quote (if load-bearing) | Conf. |
|---|---|---|---|---|
| 1 | Founding partners: BMW, Bosch, Continental, DaimlerChrysler, VW; joined soon by Siemens VDO (2002) | autosar.org/about/history | "Initial discussions … held by BMW, Bosch, Continental, DaimlerChrysler and Volkswagen … joined soon afterwards by Siemens VDO" | high |
| 2 | Initial Development Agreement signed July 2003; public debut Sept 2003 Baden-Baden | autosar.org/about/history | "Initial AUTOSAR Development Agreement signed off by the Core Partners" (July 2003) | high |
| 3 | Ford Nov 2003; PSA + Toyota Dec 2003; GM Nov 2004 joined as Core Partners | autosar.org/about/history | "Peugeot Citroën … and Toyota … joined as Core Partners" (Dec 2003) | high |
| 4 | Latest release R25-11, published 2025-11-27, event 2025-12-04, internal R4.11.0, schema AUTOSAR_00054 | R25-11 CP Release Overview PDF | "2025-11-27 R25-11 … R25-11 supersedes R24-11"; "AUTOSAR_00054 R25-11 R4.11.0" | high |
| 5 | R19-11 unified: separate until CP R4.4.0/AP R19-03, one release+schema since R19-11 | R25-11 CP Release Overview PDF | "Starting with release R19-11, all platforms are released as one AUTOSAR release … one schema version" | high |
| 6 | First AP release = 17-03 (March 2017); first Foundation release = R1.0.0 (Oct 2016) | autosar.org/about/history | "2017 March … Adaptive Platform Release 2017-03"; "2016 October … Foundation Release 1.0.0" | high |
| 7 | ~339 total partners (NA 41 / EU 128 / Asia 164 / Africa 6) | EXP_Introduction_Part1 PDF | regional bullet lists summing to 339 | high |
| 8 | Membership fees: PP+ €90k, Premium €31k, Development €10k, Associate €21k, Subscriber €3k | EXP_Introduction_Part1 PDF | fee row of "Types of partnership" table | high |
| 9 | Specs free to read; commercial exploitation requires a license | R25-11 CP Release Overview PDF | "The commercial exploitation of the material … requires a license to such intellectual property rights" | high |
| 10 | DENSO, Huawei, Vector Informatik promoted to Core Partner, announced 15.01.2026 | autosar.org/news-events/.../welcome-our-three-new-core-partners | "welcome DENSO Corporation, Huawei Technologies …, and Vector Informatik GmbH as new AUTOSAR Core Partners" | high |
| 11 | 2022 Opening Strategy: new "Vehicle API" standard, open framework, opens SOME/IP + DLT | autosar.org/news-events/.../autosar-opening-strategy-software-defined-vehicle-ecosystem | "a new standard called 'Vehicle API' … developed in a new framework, which will also be open to non-AUTOSAR Partners" | high |
| 12 | R25-11 CP adds "DDS Support on Classic Platform" and "Vehicle Data Protocol" | R25-11 CP Release Overview PDF | TOC entries §2.1.1.5 "DDS Support on Classic Platform", §2.1.1.1 "Vehicle Data Protocol" | high |
| 13 | Current Core Partners incl. AUMOVIO (ex-Continental); Ford/PSA no longer core | autosar.org/about/partners/core-partner | logo alt-tags: AUMOVIO, BMW, GM, HUAWEI, Mercedes-Benz, Bosch, TOYOTA, VECTOR, VOLKSWAGEN | med |
| 14 | AP adopted ASAM SOVD (ISO 17978-3) as `AP_EXP_SOVD` | asam.net/standards/detail/sovd + AP_EXP_SOVD PDF | SOVD "based on HTTP/REST, JSON and OAuth" | high |
| 15 | CP OS descends from OSEK/VDX | en.wikipedia.org/wiki/AUTOSAR | CP is "the standard for embedded real-time ECUs based on OSEK" | med |

## Sources

1. https://www.autosar.org/news-events/detail/release-r25-11-is-now-available — "Release R25-11 is Now Available" — AUTOSAR — primary
2. https://en.wikipedia.org/wiki/AUTOSAR — AUTOSAR overview (Foundation purpose, OSEK, tiers) — Wikipedia — secondary
3. https://www.autosar.org/about/history — "History of AUTOSAR" (full dated timeline) — AUTOSAR — primary
4. https://www.autosar.org/fileadmin/standards/R25-11/CP/AUTOSAR_CP_TR_ReleaseOverview.pdf — Classic Platform Release Overview R25-11 (schema/release table, disclaimer, R25-11 concepts) — AUTOSAR — primary
5. https://www.autosar.org/fileadmin/user_upload/2025_12_18_AUTOSAR-PR_Release_Event.pdf — R25-11 Release Event press release (participation stats) — AUTOSAR — primary
6. https://www.autosar.org/faq — AUTOSAR FAQ (partnership & exploitation) — AUTOSAR — primary
7. https://www.autosar.org/fileadmin/user_upload/AUTOSAR_Introduction_PDF/AUTOSAR_EXP_Introduction_Part1.pdf — AUTOSAR Introduction Part 1 (tiers, fees, governance, 339 partners) — AUTOSAR — primary
8. https://www.wardsauto.com/general-motors/gm-to-join-autosar — "GM to Join Autosar" — WardsAuto — secondary
9. https://www.autosar.org/about/partners/core-partner — Core Partners page (current logos) — AUTOSAR — primary
10. https://www.autosar.org/news-events/detail/autosar-opening-strategy-software-defined-vehicle-ecosystem — "AUTOSAR Opening Strategy – SDV Ecosystem" (2022-05-05) — AUTOSAR — primary
11. https://news.europawire.eu/autosar-partnership-announces-new-leadership-and-core-partners-strengthening-its-role-in-the-software-defined-vehicle-ecosystem/eu-press-release/2026/01/12/11/13/23/167657/ — "AUTOSAR Announces New Leadership and Core Partners …" (2026-01-12) — EuropaWire — secondary
12. https://www.autosar.org/fileadmin/standards/R24-11/AP/AUTOSAR_AP_TR_ReleaseOverview.pdf — Adaptive Platform Release Overview — AUTOSAR — primary
13. https://www.autosar.org/news-events/detail/welcome-our-three-new-core-partners — "Welcome our three new Core Partners!" (2026-01-15) — AUTOSAR — primary
14. https://www.autosar.org/fileadmin/standards/R24-11/AP/AUTOSAR_AP_EXP_SOVD.pdf — Explanation of Service-Oriented Vehicle Diagnostics (AP) — AUTOSAR — primary
15. https://www.autosar.org/fileadmin/standards/R24-11/FO/AUTOSAR_FO_TPS_StandardizationTemplate.pdf — Standardization Template (document-type conventions) — AUTOSAR — primary
16. https://www.autosar.org/fileadmin/standards/R21-11/CP/AUTOSAR_SWS_StandardTypes.pdf — Specification of Standard Types (example SWS + requirement-ID scheme) — AUTOSAR — primary
17. https://www.asam.net/standards/detail/sovd/ — ASAM SOVD standard page — ASAM — primary

## Surprises

- **The founding OEM Ford and PSA/Stellantis appear to have left the Core Partner circle.** The
  current core-partner logos are AUMOVIO, BMW, Bosch, DENSO, GM, Huawei, Mercedes-Benz, Toyota,
  Vector, VW [9][13]. The core has tilted toward Tier-1 suppliers (Bosch, DENSO, Vector) and Asian
  players (Toyota, Huawei) — contradicting the common "AUTOSAR = German OEM club" mental model.
- **"Continental" is now "AUMOVIO"** in the core list [9] — Continental spun off its automotive
  business, so the founding partner survives under a new name (worth double-checking the exact
  corporate lineage before repeating).
- **Two Chinese/Asian shifts in one release cycle**: Huawei became a Core Partner (Jan 2026) [13],
  and Asia (164) now has more AUTOSAR partners than Europe (128) [7] — AUTOSAR is no longer
  Europe-centric by headcount.
- **AUTOSAR is putting DDS on the *Classic* Platform (R25-11)** [4] — the same middleware family
  ROS 2 uses. This is directly relevant to this repo's ROS 2 vs. automotive-stack framing: the two
  worlds are converging on data-centric transport.
- The **CP internal version never reset** — R25-11 is internally "R4.11.0" [4], so "AUTOSAR 4.x"
  is still alive under the marketing name, which can confuse people who think 4.4.0 was the end.

## Open questions

- **Exact current Core Partner count and full list.** Logo alt-tags gave 9–10 names [9]; I could
  not load a clean text roster to confirm DENSO's logo is present or whether any other OEM (e.g.
  Volvo, Hyundai) is also Core. *Best guess (labeled guess): 10 Core Partners — AUMOVIO, BMW,
  Bosch, DENSO, GM, Huawei, Mercedes-Benz, Toyota, Vector, VW.*
- **Whether the non-partner "university/startup" license from the 2022 opening strategy actually
  launched**, and its terms [10]. Status unverified. *Guess: still limited/experimental.*
- **Exact R19-11 and R20-11..R23-11 publication days.** History page gives month/year only [3];
  I only have the precise day (2025-11-27) for R25-11 from its overview [4].
- **Precise meaning of the `ASWS` prefix** seen in CP filenames (likely "Auxiliary/Abstract
  Software Specification") — not confirmed from a primary definition.
- **The 339 partner total is a snapshot from the current Introduction deck** [7]; a chart in the
  same deck shows historical totals peaking around 366, so the exact "as of" date of 339 is not
  pinned. R25-11 PR separately says "more than 200 partners" were *active in working groups* [5],
  which is a different (participation) metric, not total membership.
- **Full membership breakdown by the eight named tiers globally** (the deck gives it regionally,
  not one clean global tally) — reconstructed sum is 339 but per-tier global totals are inferred.
