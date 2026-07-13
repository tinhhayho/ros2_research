# Fleet management with AUTOSAR + UDS — audit of an external draft, and what survived (July 2026)

**What this is.** An externally produced draft report ("Fleet management in AUTOSAR
architectures with UDS on NVIDIA DRIVE Thor", dated 2026-07-13) was submitted for
inclusion in this repo. Per repo policy nothing goes into the deck/blog unaudited, so it
went through the standard workflow first: three parallel fact-check passes with
non-overlapping scopes (UDS/diagnostics standards; AUTOSAR platform claims; NVIDIA
Thor/DriveOS claims) + independent re-verification of every load-bearing or surprising
quote against the primary page. This file records the verdicts; the corrected content —
and only the corrected content — feeds the new fleet/diagnostics section of the deck and
blog. Claim rows in `research/claims-audit-2026-07.md` (F-series).

**Headline result.** The *standards* half of the draft (UDS service IDs, ISO numbers,
DCM/DEM/DM module names) is solid. The *deployment* half is not: its centerpiece
architecture — multiple "virtual Classic AUTOSAR ECU" partitions under Thor's hypervisor
with Thor as a UDS/DoIP fleet gateway — contradicts NVIDIA's own public SDK docs and
Vector's own Thor announcement, and had to be rebuilt from primary sources.

## 1. Verdict table

Status: ✅ confirmed · 🟡 partly (kept with correction) · ❌ refuted (excluded) ·
❓ not documented anywhere (excluded).

| # | Draft claim | Verdict | Correction / evidence |
|---|---|---|---|
| 1 | UDS = ISO 14229, application-layer diagnostic protocol | ✅ | ISO 14229-1:2020, OSI 5–7, transport-independent |
| 2 | Service IDs 0x10/0x22/0x2A/0x19/0x31/0x27 + names | ✅ | all correct per ISO 14229-1 |
| 3 | "0x34–0x37 = RequestDownload/TransferData" (flashing) | 🟡 | four codes, four services: 0x34 RequestDownload, **0x35 RequestUpload** (omitted in draft), 0x36 TransferData, 0x37 RequestTransferExit |
| 4 | DID 0xF190 = VIN | ✅ | standardized DID, read via 0x22 |
| 5 | DoCAN = ISO 15765-2; DoIP = ISO 13400 | ✅ | plus ISO 14229-5 (UDSonIP) |
| 6 | Classic diagnostics = DCM + DEM (+NvM), CanTp transport | ✅ | module names and split correct |
| 7 | Adaptive DM "primarily over DoIP", C++ API | 🟡 | per SWS_Diagnostics, DM supports **only** DoIP as transport (not CAN); API = `ara::diag`; DM also implements ASAM SOVD v1.0.0 |
| 8 | Each Software Cluster has its own diagnostic address | ✅ | DM instantiates one diagnostic server per SoftwareCluster |
| 9 | UCM = "Update Configuration Management" | 🟡 | **Update *and* Configuration Management** (AUTOSAR's own doc title) |
| 10 | UDS 0x34–0x37 is the usual Adaptive FOTA path | 🟡 | one valid channel; the native path is UCM's `ara::com` TransferStart/TransferData/TransferExit fed by an OTA client — not routed through UDS |
| 11 | SOVD = ASAM standard, cloud-native complement to UDS | 🟡 | correct, but dated: SOVD is now **ISO 17978-1/-2/-3:2026** — REST/HTTP(+2 recommended) + JSON + OAuth; complements UDS and can front legacy UDS ECUs |
| 12 | 0x2A periodic reads = fleet telemetry channel to the cloud | ❌ | 0x2A is real and works over DoIP, but is time-polled, session-scoped, DID-space-constrained (0xF2xx); continuous fleet telemetry runs on telematics pipelines (MQTT/proprietary); UDS stays a diagnostic protocol |
| 13 | Cloud talks "DoIP/5G + UDS" directly to the vehicle | ❌ | every real deployment terminates the external link at a TCU/gateway (TLS, certificates) which translates into in-vehicle UDS; raw UDS is not exposed to the internet; SOVD is the intended external-facing API |
| 14 | ODX/DEXT = the "diagnostic database" | 🟡 | ODX = ISO 22901-1 "**Open** Diagnostic data eXchange"; DEXT = AUTOSAR Diagnostic Extract; both are description/exchange *formats* — the packaged file tools load is a **PDX** container |
| 15 | Classic = deeply-embedded hard-RT; Adaptive = HPC/SDV | ✅ | standard framing |
| 16 | Classic OS "= OSEK/VDX" | 🟡 | Classic runs **AUTOSAR OS** — a backward-compatible superset of OSEK OS (memory/timing protection, multicore, SC1–SC4) |
| 17 | Adaptive OS = "POSIX (QNX/Linux)" | 🟡 | requirement is the **PSE51** profile *for Adaptive Applications*; Foundation/Services may use full POSIX; QNX and Linux are indeed the dominant choices |
| 18 | Classic comms = "CAN/DoCAN" vs Adaptive "Ethernet/SOME/IP" | ❌ (as written) | Classic has had a standardized **SOME/IP Transformer since 4.2.1 (2016)** — a year before Adaptive's first release — plus Ethernet, DoIP, LIN, FlexRay; the row implied Classic can't do Ethernet |
| 19 | Classic = full-flash updates; Adaptive = per-cluster via UCM | ✅ | EB: Classic "always required a full update", Adaptive supports differential/per-cluster |
| 20 | Classic = high ASIL, Adaptive = lower (implicit) | 🟡 | outdated ceiling: Vector ships MICROSAR Adaptive Safe at **ASIL-B**, ASIL-D planned; Wind River's Adaptive safety concept assessed ASIL-D-suitable by TÜV SÜD |
| 21 | "Classic on Adaptive" trend (Classic BSW as an Adaptive app) | ❌ | no such pattern under that name; the real pattern is **Classic vECU in a VM under a hypervisor** (EB corbos Hypervisor et al.), used for consolidation/simulation/HIL |
| 22 | ECU consolidation: dozens of ECUs → central+zonal | ✅ | Bosch zone-ECU framing; NXP central compute; reported targets 100+ → under a dozen (vendor figures) |
| 23 | Thor = Blackwell GPU | ✅ | current official page; note the still-live 2022 unveil page says Hopper/Ada — superseded in Mar 2024, a stale-source trap |
| 24 | Thor = "~1000+ TOPS" | 🟡 | official: "more than 1,000 INT8 TOPS (2,000 FP4 TFLOPs)"; don't conflate with Jetson Thor T5000's 2070 sparse-FP4 TFLOPS |
| 25 | "DriveOS is based on QNX + supports Linux" | ❌ | DriveOS = Type-1 hypervisor platform + service VMs; QNX **or** Linux is the guest choice — public SDK 7.0.3: "Multiple Guest OS are not supported. In addition, you can run QNX or Linux, but not both." |
| 26 | Thor hypervisor hosts multiple partitions incl. several "virtual Classic AUTOSAR ECUs" (Body/Gateway, Powertrain) | ❌ | contradicted by the single-guest SDK limit; no NVIDIA/partner doc shows Classic as a Thor hypervisor guest; Classic lives on the **companion MCU (RH850)** — Vector: "Our MICROSAR Classic is used as reference integration for the companion MCU" |
| 27 | FSI is a hypervisor partition | ❌ | FSI is dedicated separate silicon (lockstep Cortex-R52 cluster, own power/clocks) — not a hypervisor-enforced partition |
| 28 | AUTOSAR ecosystem partners: EB, ETAS, Vector, Neusoft | 🟡 | EB and Vector confirmed with NVIDIA ties; **ETAS and Neusoft: no NVIDIA-specific tie found** — dropped |
| 29 | Thor as UDS/DoIP diagnostic gateway for the fleet backend | ❓ | zero documentation; the documented SoC↔MCU link is a proprietary "Common Interface over UDP over Ethernet", not DoIP/UDS; gateway/UDS routing is a gateway-ECU / companion-MCU domain function |
| 30 | Thor targets central compute, robotaxis, trucks | ✅ | NVIDIA/Uber robotaxi; Aurora+Continental trucks (PACCAR Peterbilt, mass production targeted 2027) |

## 2. The corrected picture (what the deck/blog now teach)

1. **UDS is the in-vehicle diagnostic language.** One request format (ISO 14229-1)
   whether the ECU is a Classic body controller reached over CAN (CanTp) or a central
   computer reached over Ethernet (DoIP). `22 F1 90` reads the VIN either way.
2. **Diagnostics has two platform homes.** Classic: DCM (dispatch/sessions/security) +
   DEM (fault memory) as configured BSW modules. Adaptive: the DM functional cluster
   (`ara::diag`), DoIP-only, one diagnostic server per Software Cluster.
3. **The fleet backend never speaks raw UDS to a vehicle.** The TCU terminates the
   4G/5G link (TLS + certificates); a central gateway translates into in-vehicle
   UDS. Continuous telemetry is a telematics pipeline (MQTT/proprietary), not 0x2A
   polling. The standardized external-facing diagnostic API is **SOVD (ISO
   17978:2026)** — REST/HTTP + JSON — which complements UDS and can front legacy ECUs.
4. **OTA:** Classic ECUs reflash whole images via bootloader + UDS 0x34/0x36/0x37;
   Adaptive machines install per Software Cluster via UCM (`ara::ucm`), fed by an OTA
   client from the backend.
5. **On Thor specifically:** one hypervisor, one guest OS (QNX *or* Linux, public SDK),
   NVIDIA service VMs; Adaptive AUTOSAR arrives as Tier-1 middleware inside the guest
   (Vector MICROSAR Adaptive "can be enabled on NVIDIA DRIVE AGX platform"); Classic
   AUTOSAR runs on the **real** companion MCU (RH850) and — per Vector's 2025-08-25
   announcement — MICROSAR Classic "takes an essential role" in the FSI + companion-MCU
   reference integration, "up to ASIL-D". No documented fleet-gateway role for Thor.
6. **Virtual Classic ECUs exist as an industry pattern — elsewhere.** Hypervisor-hosted
   Classic vECUs are documented on EB corbos Hypervisor and (formerly OpenSynergy, now
   Qualcomm-owned since 2024-06-10) COQOS — whose supported-SoC list (Qualcomm, NXP,
   Renesas, TI, Samsung) does **not** include NVIDIA.

## 3. New facts worth keeping (surfaced by this audit)

- **SOVD became ISO 17978 (2026)**: -1 principles, -2 use cases, -3 REST/JSON API
  standardizing diagnosis of "HPCs and legacy ECUs". The ASAM-only framing is dated.
- **Vector × Thor, primary-fetched (2025-08-25)**: reference integration for **both the
  FSI and the companion MCU**; "With our certified MICROSAR Classic solution we enable
  the realization of safety-critical functions in compliance with ISO 26262 up to
  ASIL-D." This sharpens our earlier "FSI runs FSI RTOS" note: Vector positions MICROSAR
  Classic as taking "an essential role" in the tightly integrated FSI. (Addendum added
  to `research/automotive-stack-autosar-2026-07.md`.)
- **Qualcomm acquired OpenSynergy's virtualization assets (COQOS) on 2024-06-10** —
  OpenSynergy's own announcement; OpenSynergy retains Bluetooth/Radio-Tuner products.
  Our earlier COQOS row should be read as Qualcomm-camp IP.
- **Classic SOME/IP predates Adaptive**: SOME/IP Transformer standardized in AUTOSAR
  4.2.1 (2016); AP's first release was R17-10 (2017).
- **Adaptive safety ceiling is moving**: MICROSAR Adaptive Safe ASIL-B shipping, ASIL-D
  planned; Wind River Adaptive safety concept assessed ASIL-D-suitable (TÜV SÜD).
- **AUTOSAR Adaptive DM implements ASAM SOVD v1.0.0** alongside ISO 14229-1 — the
  UDS→SOVD bridge is already inside the platform spec.

## 4. Excluded from publication (refuted/undocumented)

- Multiple DriveOS instances / multiple guest VMs on public-SDK Thor.
- "Virtual Classic AUTOSAR ECU" partitions (Body/Gateway, Powertrain) on Thor.
- FSI as a hypervisor partition.
- Thor as DoIP/UDS fleet diagnostic gateway.
- "Classic on Adaptive" as a named trend.
- 0x2A as the fleet telemetry mechanism; cloud-direct UDS over 5G.
- ETAS and Neusoft as NVIDIA AUTOSAR partners (no source found).

## 4b. Cross-check addendum (2026-07-13, same day): the "one guest vs dual-stack" contradiction resolved

An independent external fact-check pass was run on the specific conflict between the
public-SDK single-guest note and NVIDIA's "multiple OS domains" / dual-stack framing;
its two load-bearing new sources were then re-fetched and verified here. Refinements:

- **The precise rule is "no *mixed* guests", not "only one guest".** DriveOS 6.x (Orin)
  AV PCT docs list exactly three supported configurations: `linux` (Single Linux GOS
  VM), `qnx` (Single QNX GOS VM), and `dual-qnx` (Dual QNX GOS VMs) — verified at the
  6.0.6 avpct page. NVIDIA staff, forum, 2024-04-11 (verified verbatim): "Linux + QNX
  GOS VM is not supported. Single Linux/QNX GOS VM or dual QNX GOS VM configurations
  are supported."
- **Policy is consistent across 6.x (Orin) → 7.x (Thor)** — the same "not both" note
  appears in both generations' docs; the Thor limit is not a regression (retracts the
  "possible generational tightening" speculation from the first pass).
- **"Multiple OS domains" reconciles as guest OS(es) + NVIDIA service VMs** (BPMP,
  Security Engine, Display, GPU sharing, Storage, Debug servers) — the hypervisor
  genuinely runs many VMs; what it never publicly runs is QNX *and* Linux as
  concurrent full guests.
- **No OEM/public source documents concurrent QNX+Linux full guests on one Thor**
  either; MB.OS-style dual-stack descriptions are platform-level and consistent with
  multi-SoC / companion-MCU partitioning.
- Consequence for our own material: the `driveos-dualstack` figure and the two
  deck/blog passages using the "QNX VM + Linux VM on one Thor" framing carry a caveat
  (manifest rows A2/F12 updated; deck slide + blog §6.2 footnoted).

## 5. Verification notes

- autosar.org PDFs and iso.org pages intermittently blocked in-sandbox (TLS/403); where
  the primary PDF could not be fetched, the quote is corroborated by ≥2 independent
  secondary excerpts and flagged in the F-series manifest rows.
- Web-search **summaries** twice synthesized unsupported claims ("Classic AUTOSAR can
  run as a guest OS", "Linux, QNX and Android simultaneously" on DRIVE) that traced to
  generic third-party material (QNX Hypervisor marketing), not NVIDIA sources — every
  cited quote here was re-fetched from the actual page before use.
- The 2022 Thor unveil press release (Hopper/Ada/Grace, "2,000 teraflops FP8") is still
  live and unedited — do not cite it for current Thor specs.

## Sources

- iso.org: 14229-1:2020 · 15765-2 (DoCAN) · 13400 (DoIP) · 14229-5 (UDSonIP) ·
  17978-1/-2/-3:2026 (SOVD) · 22901-1 (ODX)
- autosar.org: SWS_Diagnostics (AP) · SWS_UpdateAndConfigurationManagement ·
  RS_OperatingSystemInterface (PSE51) · SWS_OS (Classic) · SOME/IP Transformer 4.2.1
- asam.net: SOVD standard page ("developed… not to replace… UDS but to coexist")
- developer.nvidia.com: DriveOS 7.0.3 Foundation Services ("Multiple Guest OS are not
  supported…") · SoC-to-MCU Communication (Common Interface over UDP) · DriveOS 7.0.3
  virtualization docs
- nvidia.com in-vehicle-computing (Blackwell; ">1,000 INT8 TOPS (2,000 FP4 TFLOPs)")
- vector.com: news 2025-08-25 "On the fast track…" (FSI + companion-MCU reference
  integration, MICROSAR Classic up to ASIL-D, MICROSAR Adaptive on DRIVE AGX) —
  full-page fetch this audit · MICROSAR Adaptive product page · MICROSAR Adaptive Safe
  ASIL-B news
- elektrobit.com: EB corbos AdaptiveCore/Hypervisor · OTA-with-Adaptive blog ·
  virtualization-of-a-Classic-ECU-platform tech corner
- opensynergy.com: "Qualcomm Acquires OpenSynergy's Virtualization Assets" (2024-06-10)
- windriver.com press (Adaptive ASIL-D concept, TÜV SÜD) · eenewseurope.com
- bosch-mobility.com zone-ECU · nxp.com central compute
- nvidianews.nvidia.com: Uber robotaxi · Thor unveil 2022 (stale-spec caveat) ·
  ir.aurora.tech (Aurora/Continental/NVIDIA trucks)
