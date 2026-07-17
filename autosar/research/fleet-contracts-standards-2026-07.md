# Vehicle ↔ Outside-World Contracts That Survive Any In-Vehicle Middleware Choice

**Researcher B · 2026-07-17 · module: `autosar/`**

**Question.** Which vehicle↔outside-world contracts hold *regardless* of whether the
in-vehicle stack is AUTOSAR (Classic/Adaptive), a proprietary OEM stack, ROS-based, or
anything else? The thesis this note establishes: **the contracts that bind a car to the
outside world live at the vehicle boundary and are set by regulation and industry
standards — not by the middleware inside. AUTOSAR itself deliberately stops at that
boundary.**

Binding-force vocabulary used below:
- **mandated-for-type-approval** — a vehicle cannot be legally sold / type-approved in the
  named market without it. Regulation-mandated.
- **de-facto (unavoidable)** — not written into any law, but every workshop tool / charger /
  Tier-1 ECU speaks it, so in practice you cannot ship without it.
- **optional** — a standard you *may* adopt (often as evidence toward a mandated process),
  but which is not itself compulsory.
- **n/a** — a scope fact about a standard, not a compliance obligation.

---

## The table (slide-ready)

| Contract | What it governs | Binding force | Market / scope | Source |
|---|---|---|---|---|
| **UN R155 (CSMS)** | Cyber-security *management system* + vehicle-level cyber assessment | **mandated-for-type-approval** | 1958-Agreement parties: EU (new types Jul 2022, all new vehicles Jul 2024), JP, KR, UK… Categories M, N, O(+ECU) | UNECE R155; cybersecurity-lighthouse |
| **UN R156 (SUMS)** | Software-update *management system* + controlled/secure update delivery | **mandated-for-type-approval** | Same regime; categories M, N, O, R, S, T that allow SW updates | UNECE R156 |
| **eCall (EU 2015/758)** | Auto-dial 112 + send location on severe crash (a mandated *connectivity function*) | **mandated-for-type-approval** | EU, new **types** of M1 + N1 from **31 Mar 2018** | EUR-Lex 2015/758; EU Parliament |
| **Emissions OBD interface** (SAE J1962 connector + legislated emission services) | Standardized diagnostic access to emission-related data | **mandated-for-type-approval** | US CARB MY1996+; EU Euro 5/6 (Reg 2017/1151); UNECE R83 | CARB OBD-II fact sheet; EU 2017/1151 |
| **PTI electronic interface (Dir 2014/45/EU)** | Inspection station must read the vehicle's electronic/OBD interface | **mandated** (inspection regime, not type-approval) | EU test stations, equipment req. from **20 May 2023**; ePTI per EN ISO 20730 | Dir 2014/45/EU |
| **UDS (ISO 14229)** | Full ECU diagnostics, security access, reflashing (0x34/0x36/0x37) | **de-facto** (not a legal protocol mandate) | Global; every tester & Tier-1 ECU | ISO 14229-1:2020; AUTOSAR SOVD EXP |
| **DoIP (ISO 13400)** | UDS transport over IP/Automotive Ethernet | **de-facto** | Global; the standardized IP diagnostic transport | ISO 13400-2:2019 |
| **SOVD (ISO 17978)** | HTTP/REST + JSON diagnostic API for HPC + legacy ECUs | **de-facto (emerging)** | Parts 1–3 published **2026**; ex-ASAM SOVD (2022) | ISO 17978-1/-2/-3:2026 |
| **ISO 15118 (Plug & Charge)** | EV↔charger comms, automated auth/billing, V2G | **de-facto** (EU AFIR pushes it on charge-points) | Global DC fast-charge; 15118-2 / 15118-20 | ISO 15118; CharIN |
| **ISO 24089** | Software-update *engineering* process (state of the art) | **optional** (evidence toward R156, not itself compulsory) | Global | ISO 24089:2023; TÜV SÜD; CertX |

---

## 1. UN R155 (CSMS) & UN R156 (SUMS) — regulation-mandated, process not protocol

**What they are.** Two UNECE WP.29 regulations under the 1958 Agreement, applied via
**vehicle type approval**. R155 = Cyber Security Management System (CSMS). R156 = Software
Update Management System (SUMS). You cannot obtain type approval for a new vehicle type in
an adopting market without **both** a certified management system *and* a vehicle-level
assessment.

**They bind the PROCESS, not the middleware/protocol.** This is the crux for the slide.
The R156 definition is explicit:

> "'Software Update Management System (SUMS)' means a systematic approach that defines
> organizational processes and procedures for complying with the requirements for software
> update delivery pursuant to this Regulation."
> — UN Regulation No. 156, §2.4 (text of the regulation; corroborated across multiple
> renderings — the primary PDF at unece.org is Cloudflare-gated in this sandbox).

R156 mandates *authenticity, integrity, anti-rollback, eligibility checks, campaign
management, auditable records* — but names **no update transport, no bus, no middleware**.
It is protocol-agnostic and stack-agnostic by design. R155 is the same shape: it requires a
"systematic risk-based approach defining organisational processes, responsibilities and
governance" (CSMS), assessed and certified — not a specific security stack.

**Who they bind (markets / categories).**
- **R155**: categories **M** (cars/buses) and **N** (vans/trucks); **O** (trailers) if
  fitted with ≥1 ECU; L6/L7 with level-3+ automation. EU: mandatory for **new vehicle types
  from July 2022** and **all new vehicles produced from July 2024**; also Japan, Korea, and
  other 1958-Agreement contracting parties.
- **R156**: categories **M, N, O, R, S, T** (incl. agricultural R/S/T) **that allow software
  updates**. Same type-approval regime and EU timeline.

*Binding: mandated-for-type-approval. It constrains the manufacturer's process + a
vehicle-level assessment — never the in-vehicle middleware. Confidence: high.*

Sources: UNECE R155 landing/PDF (`https://unece.org/sites/default/files/2021-03/R155e.pdf`),
UNECE R156 landing
(`https://unece.org/transport/documents/2021/03/standards/un-regulation-no-156-software-update-and-software-update`)
and PDF (`https://unece.org/sites/default/files/2024-03/R156e%20(2).pdf`),
UNECE press "Three landmark UN vehicle regulations enter into force"
(`https://unece.org/sustainable-development/press/three-landmark-un-vehicle-regulations-enter-force`),
cybersecurity-lighthouse R155/R156 (categories, dates).

---

## 2. ISO 24089 — the engineering standard behind R156 (optional, not mandated)

**ISO 24089:2023 "Road vehicles — Software update engineering"** specifies requirements and
recommendations for SW-update engineering at organizational and project level. It is
**harmonised with UN R156** and effectively operationalises it: R156's approval-oriented
requirements are "redefined and translated into work packages" by ISO 24089, which then
gives practical implementation guidance.

**Precise relationship / binding:** R156 is the *mandatory* type-approval regulation;
**ISO 24089 is a voluntary international standard — it is not mandatory for any vehicle
approval.** It represents current state-of-the-art, and an ISO 24089 assessment/certification
can be *used as evidence* toward demonstrating R156 (SUMS) compliance. So: R156 = what you
must satisfy; ISO 24089 = a recognised way to show you satisfy it.

*Binding: optional (compliance-evidence standard). Confidence: high.*

Sources: ISO 24089:2023 (`https://www.iso.org/standard/77796.html`);
TÜV SÜD ISO 24089 page; CertX "UN R156 and ISO 24089" overview.

---

## 3. UDS (ISO 14229) + DoIP (ISO 13400) — the precision case

This is the sub-question where the labelling matters most. **UDS is not, in itself, a legally
mandated protocol. It is de-facto universal.** But there ARE adjacent legal mandates around
*diagnostic access*, and they must not be conflated with "UDS is mandated." Sub-claims,
each labelled:

**(a) Emissions On-Board Diagnostics (OBD) — MANDATED, but that's the *emissions* layer, not
UDS.** In the US, **CARB mandated OBD-II from model year 1996** (California), and OBD-II is
required for all US passenger cars and light trucks. In the EU, emission-related OBD is
mandated via the Euro 5/6 type-approval framework (**Commission Regulation (EU) 2017/1151**,
supplementing Reg 715/2007; heavy-duty via UNECE R49; earlier UNECE R83 for light vehicles).
What these mandate is: a **standardized connector (SAE J1962)** and access to *emission-related*
diagnostic data. The legislated emissions services historically ride **ISO 15031 / SAE J1979**
over **ISO 15765-4** (OBD-on-CAN). EU 2017/1151 does *reference* ISO 14229 (UDS) as **one
permitted data-link option** for emissions diagnostics — so UDS has a regulatory foothold, but
as an *allowed option*, not a blanket mandate. *Binding: mandated-for-type-approval (the
emissions OBD interface); UDS itself appears as an option. Confidence: high.*

**(b) Full ECU diagnostics + ECU reflashing (the interesting 90%) — DE-FACTO only.** Security
access, routine control, and the reflash sequence **0x34 RequestDownload / 0x36 TransferData /
0x37 RequestTransferExit** live in **UDS ISO 14229** and are **not required by any law**. They
are simply what every workshop tester and every Tier-1 ECU implements. AUTOSAR's own SOVD
explainer confirms the market reality: *"As of today (year 2023) the prevailing Diagnostic
protocol of the automotive industry is UDS. UDS was initially standardized in 2006 as
ISO 14229…"* (AUTOSAR_AP_EXP_SOVD, R25-11). *Binding: de-facto. Confidence: high.*

**(c) Periodic Technical Inspection (roadworthiness) — MANDATED electronic-interface access,
not UDS specifically.** **Directive 2014/45/EU** requires EU inspection stations to have,
from **20 May 2023**, "a device to connect to the electronic vehicle interface, such as an
on-board diagnostics (OBD) scan tool" (Annex III). Electronic PTI (ePTI) is standardised in
**EN ISO 20730** (which builds on UDS/OBD access). So the *inspection port and electronic
read-out* are a mandated contract — but the law names the interface capability and ISO 20730,
not "UDS" as such. *Binding: mandated (inspection regime). Confidence: high.*

**(d) DoIP (ISO 13400) — DE-FACTO transport, not mandated.** DoIP is the standardized way to
carry UDS over IP / Automotive Ethernet. ISO's own scope notes it is "usable for legislated
diagnostic communication as well as manufacturer-specific use cases," but **no regulation
mandates DoIP** — it is the de-facto IP diagnostic transport, chosen for bandwidth as
architectures move to Ethernet. *Binding: de-facto. Confidence: high.*

**(e) For EVs specifically — the emissions-OBD mandate largely falls away.** Emissions OBD
regulations target *tailpipe/emission-related* systems; **battery-electric vehicles have no
tailpipe emissions**, so the emissions-OBD legal hook mostly does not bind a pure BEV. That
leaves EV diagnostics resting on **de-facto UDS/DoIP** plus the powertrain-agnostic PTI
electronic-interface requirement (safety components). CARB has been *developing* EV-specific
diagnostic/serviceability requirements (reported ~2026), but that is emerging, not an
established UDS mandate. *Binding: de-facto for EV diagnostics (emissions-OBD mandate mostly
n/a to BEVs); EV-specific mandate = emerging. Confidence: medium-high.*

**Net UDS/DoIP verdict:** the *emissions* OBD interface and the *PTI* electronic interface are
mandated slices of diagnostic access; the **full diagnostic + reflash protocol stack that
firmware engineers actually work with (UDS ISO 14229 over DoIP ISO 13400) is de-facto, not
de-jure.** It survives any middleware choice because the entire aftermarket/service ecosystem
is built on it — not because a statute names it.

Sources: ISO 14229-1:2020 (`https://www.iso.org/standard/72439.html`);
ISO 13400-2:2019 (`https://www.iso.org/standard/74785.html`);
CARB OBD-II fact sheet
(`https://ww2.arb.ca.gov/resources/fact-sheets/board-diagnostic-ii-obd-ii-systems-fact-sheet`);
EU 2017/1151 (`https://www.legislation.gov.uk/eur/2017/1151` / UNECE mirror
`https://unece.org/fileadmin/DAM/trans/doc/2018/wp29other/EU_2017_1151.pdf`);
Dir 2014/45/EU (`https://www.legislation.gov.uk/eudr/2014/45`);
`repo:autosar/specs/R25-11/AP/AUTOSAR_AP_EXP_SOVD.pdf`.

---

## 4. SOVD (ISO 17978) — the HPC-era diagnostic API

**Origin & standardization.** SOVD (Service-Oriented Vehicle Diagnostics) began as an **ASAM**
standard (first version 2022) and has now been taken into ISO as **ISO 17978**:
- **ISO 17978-1:2026** — General information, definitions, rules and basic principles
  (`https://www.iso.org/standard/85133.html`).
- **ISO 17978-2:2026** — Use cases definition (`https://www.iso.org/standard/86586.html`).
- **ISO 17978-3:2026** — Application programming interface (API)
  (`https://www.iso.org/standard/86587.html`).

All three parts carry **2026** publication dates (ISO 17978-1 close-of-voting recorded
2026-04-17). *Confidence: high that -1/-2/-3 are published as :2026; the ISO catalog pages
themselves are Cloudflare-gated in this sandbox — confirmed via iTeh/ANSI catalog mirrors and
ISO title metadata.*

**What it standardizes.** A **service-oriented, self-describing diagnostic API using current
IT technologies (HTTP/HTTPS, REST, JSON)** for diagnosing **high-performance computers (HPCs)
and legacy ECUs** in an extended vehicle — with no dependency on ODX data files (unlike UDS).
Primary characterization from the local AUTOSAR spec:
- *"the SOVD protocol is specified on vehicle level"* and the *"SOVD Gateway acts as HTTP
  reverse proxy"* using **HTTPS / REST / JSON** (AUTOSAR_AP_EXP_SOVD, R25-11).
- SOVD *"is a 'State-of-the-Art diagnostic API using current information technologies'"* and is
  *"self-explaining, meaning it does not rely and has no dependency to an external ODX data
  description"* (same doc, quoting ASAM). UDS is incorporated *within* the SOVD API for
  microcontrollers.

**Adoption signals.** AUTOSAR Adaptive natively realises SOVD (functional cluster `ara::diag`
+ a SOVD Gateway); the Eclipse **OpenSOVD** project is an open-source implementation
(ISO 17978-aligned, per the repo's adaptive-open-source note). Tooling vendors (DSA, Vector,
etc.) advertise SOVD support. *Binding: de-facto (emerging) — the industry's chosen HPC-era
diagnostic API, not a legal mandate. Confidence: high.*

Sources: ISO 17978-1/-2/-3:2026 pages above; DSA SOVD page
(`https://www.dsa.de/en/competences/sovd.html`);
`repo:autosar/specs/R25-11/AP/AUTOSAR_AP_EXP_SOVD.pdf`;
`repo:autosar/research/adaptive-open-source-2026-07.md` (OpenSOVD).

---

## 5. eCall (EU 2015/758) — a mandated connectivity function, middleware-independent

**Regulation (EU) 2015/758** made the 112-based eCall in-vehicle system a **type-approval
requirement**. From **31 March 2018**, national authorities may grant EC type-approval only to
new **types** of vehicles fitted with a 112-based eCall system. It applies to **category M1
(passenger cars) and N1 (light commercial vehicles ≤ 3.5 t)**. Function: on a severe crash the
system **automatically dials 112** over the cellular network and transmits a Minimum Set of
Data (incl. GPS location), then opens a voice channel.

This is the cleanest example of the thesis: a **mandated vehicle↔outside-world connectivity
function** specified entirely at the *function/interface* level. The regulation says nothing
about the in-vehicle middleware, bus, or software stack that implements it — AUTOSAR, a
proprietary TCU stack, anything. *Binding: mandated-for-type-approval (EU, new M1/N1 types from
2018-03-31). Confidence: high.*

Sources: EUR-Lex Reg (EU) 2015/758 (`https://eur-lex.europa.eu/eli/reg/2015/758/oj/eng`);
EU Parliament press "Saving lives: eCall mandatory in new car models from this week"
(`https://www.europarl.europa.eu/news/en/press-room/20180326IPR00510/saving-lives-ecall-mandatory-in-new-car-models-from-this-week`);
EUR-Lex summary "eCall in-vehicle system — type-approval".

---

## 6. ISO 15118 (Plug & Charge) — de-facto EV charging contract

**ISO 15118** defines EV↔charging-station communication. **ISO 15118-2** introduced **Plug &
Charge** (automatic certificate-based authentication + billing — plug in, charge, no app/RFID);
**ISO 15118-20** is the 2nd-generation protocol adding **bidirectional power transfer (V2G)** and
wireless charging. It is **CharIN's preferred** EV↔charger protocol and is adopted by major OEMs
and charge-point operators for high-power DC charging.

**Binding nuance:** on the *vehicle* side, ISO 15118 / Plug & Charge is **de-facto** (no law
forces a given car to implement it). But there is a regulatory push on the *infrastructure*
side — the EU **AFIR** (Alternative Fuels Infrastructure Regulation) drives ISO 15118 support
on public charge-points, with **ISO 15118-20 support becoming mandatory in the EU from ~2027**,
which makes vehicle-side support effectively unavoidable for interoperability. *Binding:
de-facto for the vehicle (regulation-pushed on charge-points). Confidence: high on de-facto
status; medium on the exact 2027 AFIR detail.*

Sources: CharIN Plug & Charge (`https://www.charin.global/technology/plug-charge/`);
ISO 15118 overviews (Monta, EVB 2026 guide).

---

## 7. AUTOSAR-side check (LOCAL R25-11 mirror) — the punchline

**Question:** does AUTOSAR R25-11 standardize ANY vehicle↔cloud/backend protocol? **Answer: No.
AUTOSAR standardizes the interfaces *inside* the vehicle and explicitly leaves the
vehicle↔backend connection to the OEM. Standardization stops at the vehicle boundary.** Two
independent, verbatim spec quotes from the local mirror prove it:

**(a) OTA / software-update backend — V-UCM (Doc 1090, AP R25-11).** The Vehicle Update &
Configuration Management spec routes all backend traffic through an "OTA Client" adaptive
application, and states plainly:

> "The communication between Backend and OTA Client is abstracted and details like protocol
> are out of scope for this specification document."

> "…OTA Client should be able to accommodate any proprietary communication protocol used
> between OTA Client and Backend and convert it into ara::com transport protocol."
> — `AUTOSAR_AP_SWS_VehicleUpdateAndConfigurationManagement`, §7.7.1, R25-11.

So AUTOSAR standardizes the *in-vehicle* side (V-UCM APIs over **ara::com**, UCM package
handling) and treats the backend protocol as OEM-proprietary and out of scope.

**(b) Diagnostics backend — SOVD explainer (Doc 1064, AP R25-11).** SOVD standardizes
*proximity* and *in-vehicle* access (via mDNS); remote/backend access is deliberately left open:

> "Standardizing remote access is rather difficult since many dependencies towards the backend
> infrastructure exist. This degree of freedom is kept open by AUTOSAR."
> — `AUTOSAR_AP_EXP_SOVD`, §2.4 "Backend Connectivity", R25-11.

**(c) No "Vehicle API" backend concept.** A grep for "Vehicle API" across all 14 AP R25-11 SWS/
EXP/TPS PDFs in the mirror returns **zero hits** — AUTOSAR defines no vehicle↔cloud "Vehicle
API." (The COVESA "Vehicle Signal Specification / Vehicle API" world is a separate, non-AUTOSAR
effort.)

**Punchline for the slide:** *AUTOSAR's standardization boundary is the vehicle itself.* Inside
the car it standardizes middleware, service discovery (SOME/IP), diagnostics (UDS via DCM/
`ara::diag`, SOVD API) and the diagnostic edge node; at the **diagnostic port / vehicle edge
node** it hands off to DoIP and SOVD; and for the **cloud/backend link it defines nothing** —
that protocol is explicitly the OEM's own. Which is exactly why the contracts in §§1–6 (R155,
R156, eCall, OBD, UDS/DoIP, SOVD, ISO 15118) survive *any* middleware choice: they are set at
or beyond the boundary where AUTOSAR intentionally stops.

*Binding: n/a (scope fact about the AUTOSAR standard). Confidence: high — direct spec quotes
from the pinned R25-11 mirror.*

Sources: `repo:autosar/specs/R25-11/AP/AUTOSAR_AP_SWS_VehicleUpdateAndConfigurationManagement.pdf`;
`repo:autosar/specs/R25-11/AP/AUTOSAR_AP_EXP_SOVD.pdf`.

---

## One-line synthesis for the deck

> The middleware inside the car (AUTOSAR or not) is a private implementation choice. What a
> car owes the outside world is fixed at the vehicle boundary by **regulation** (R155 CSMS,
> R156 SUMS, eCall, emissions-OBD, PTI) and by **de-facto industry standards** (UDS/DoIP,
> SOVD, ISO 15118) — and AUTOSAR's own specs explicitly stop at that boundary, leaving the
> vehicle↔backend protocol to the OEM.
