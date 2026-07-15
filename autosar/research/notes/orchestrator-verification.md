# Orchestrator verification addendum — 2026-07-15

Binding constraints for everything drafted from these notes. Where a research note
conflicts with this file or with `repo-constraints.md`, THESE win. Verified directly
against `AUTOSAR_CP_TR_ReleaseOverview.pdf` (R25-11), fetched 2026-07-15 (curl -k due
to the sandbox TLS issue; pdftotext extraction).

## 1. DDS on Classic Platform — CONFIRMED verbatim (high confidence)

R25-11 CP Release Overview §2.1.1.5 "DDS Support on Classic Platform":

> "Management functionalities for Events, Methods, and Fields, previously available
> through SOME/IP, are now extended to DDS, offering increased flexibility thanks to
> its native capability of defining Quality of Service (QoS) parameters at various levels."

> "Introduction of full support of ClientServerInterface and the new BSW module DDS
> Transformer." … "Integration of the OMG SPDP and SEDP discovery protocols, along with
> the Service Discovery protocol already defined in the AUTOSAR Adaptive Platform, thus
> ensuring cross-solution compatibility."

New specs shipped: `CP SWS DataDistributionServiceTransformer`, updates to
`CP SWS DataDistributionService`, `CP RS Transformer` ("Added support of DDS Transformer").
Caveat to preserve on any slide/doc: this is a **standard-level concept new in R25-11**;
no evidence yet of a shipping vendor implementation (adoption timelines unverified).

## 2. R25-11 removed specifications — exact list (§2.2.4, high confidence)

Set to status "removed" in R25-11: **CP SWS/RS FlashDriver (Fls)**, **CP SWS/RS
EEPROMDriver (Eep)**, **CP RS+SWS TTCAN Driver & Interface**, **CP SWS LargeDataCOM
(LdCom)**, plus template/RS housekeeping docs (BSWModuleDescriptionTemplate,
DiagnosticExtractTemplate, ECUConfiguration, ECUResourceTemplate,
SoftwareComponentTemplate, SystemTemplate, Features, TR FrancaIntegration).

Required nuances when presenting this:
- **LdCom was not deleted, it was absorbed**: the COMHandler concept "merges LdCom
  functionality into Com" (§2.1.1.3 area, p.~765-769 of extracted text).
- **Fls/Eep have successors**: R25-11 still ships "Specification of Memory Access"
  (MemAcc) and "Specification of Memory Driver" (Mem) — the generic memory-driver pair
  that replaces part-specific Fls/Eep. The teaching stack NvM → MemIf → {Fee | Ea}
  remains valid; the bottom driver layer is what got modernized. Do NOT write
  "R25-11 removed flash support" or present NvM→Fee→Fls as the current-release wiring
  without this footnote.

## 3. NVIDIA safety-MCU generations — pinned (repo-verified, do not contradict)

- **Orin generation**: safety MCU = Infineon **AURIX TC397X** (B-Step), Vector AFW firmware.
- **Thor generation**: companion/safety MCU = **Renesas RH850U2A16** (DriveOS 7.0.3 flash
  artifact `…AFW-RH850-U2A16-…hex`), Vector MICROSAR Classic as reference integration.
- The classic-safety-limits note's guess "Thor uses an AURIX TC4x" is WRONG — never say
  Thor uses AURIX. Source: `research/automotive-stack-autosar-2026-07.md` (repo-verified).

## 4. AP diagnostic transport phrasing — pinned

Use exactly this framing: **DoIP (ISO 13400-2) is the only *standardized* UDS transport
for the AP Diagnostic Manager; the SWS explicitly permits a custom transport
implementation** (R24-11 and R25-11). The shorthand "DoIP-only" is acceptable on a slide
only with the word "standardized" nearby. This refines (does not contradict) the repo's
existing "DoIP-only confirmed in R24-11" note.

## 5. Other release-stamped facts drafters must keep hedged exactly as noted

- Raw Data Streaming removed from ara::com **at R23-11**, and Communication Groups marked
  **OBSOLETE at R23-11** (Communication Groups introduced R20-11; Raw Data Streaming had been
  in ara::com since R19-11). R25-11 only deleted the leftover obsolete Communication Groups
  text — it is not where either retirement happened. PHM Health Channels obsolete **R21-11**,
  removed R24-11.
- "UCM Master" is now **V-UCM** (own spec since R23-11).
- AUTOSAR C++14 guidelines: standalone doc gone (404 since R23-11), merged into
  MISRA C++:2023 (targets C++17); C++14 remains the historical ARA API baseline —
  whether R25-11 formally moves to C++17 is an OPEN QUESTION, keep it as one.
- ASIL reality mid-2026: ASIL-B AP stacks shipping/certified (Vector MICROSAR Adaptive
  Safe; Qorix TÜV SÜD Aug 2025; ETAS RTA-VRTE TÜV SÜD March 2025); NO fully certified
  ASIL-D AP middleware found — phrase as "ASIL-B shipping, ASIL-D programs underway".

*(§5 corrected after fact-check run wf_4748cedc-22d, 2026-07-15)*
