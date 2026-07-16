# Spec-figure provenance manifest

Each `spec-*.png` under this directory is a **pixel-faithful, unmodified excerpt** of a
figure in an AUTOSAR R25-11 specification PDF (local mirror: `../../specs/R25-11/`),
reproduced for informational purposes per the R25-11 Disclaimer — © AUTOSAR.
Mined + adopted 2026-07-16; sha256 below is the shipped file, byte-identical to the crop
as extracted (verified at apply time). Verify anytime: crop the named page of the local
PDF and compare content, or `sha256sum -c` against this table.

| file | source document (local path) | figure | PDF page | sha256 |
|---|---|---|---|---|
| `spec-aap-external-systems.png` | `specs/R25-11/AP/AUTOSAR_AP_EXP_SWArchitecture.pdf` | Figure 7.2 | 23 | `1a8a013a37f7ce6814cc60c1ac8458ac483337c6b80f17684baea94e07985323` |
| `spec-ap-architecture-logical-view.png` | `specs/R25-11/AP/AUTOSAR_AP_EXP_PlatformDesign.pdf` | Figure 4.1 | 19 | `308f7ac1e60785bda31d77bdb757c3ccc77ef537993586b8393f97bdb33265a8` |
| `spec-ap-cp-interactions.png` | `specs/R25-11/AP/AUTOSAR_AP_EXP_PlatformDesign.pdf` | Figure 3.2 | 18 | `f191e2bb5b62553336b21e9315c816665e60ed831d9a8185f8cd229d13568870` |
| `spec-cm-service-oriented-communication.png` | `specs/R25-11/AP/AUTOSAR_AP_SWS_CommunicationManagement.pdf` | Figure 7.2 | 67 | `f04190f36598bb6e7741d5af5bd44882e96010d32179b0201d1386c6eef1234e` |
| `spec-cm-technical-architecture.png` | `specs/R25-11/AP/AUTOSAR_AP_SWS_CommunicationManagement.pdf` | Figure 7.1 | 64 | `a419e975df48a321ab61c00960d5dc673a25bcf8a289dca8a784e3b5eff314e2` |
| `spec-e2e-overview.png` | `specs/R25-11/FO/AUTOSAR_FO_PRS_E2EProtocol.pdf` | Figure 1.1 | 13 | `cc3754adf911fa7bab8cec1af4114d315e9aa8b8ad7ec27b2d1c378f0f49e184` |
| `spec-lsa-detailed-view.png` | `specs/R25-11/CP/AUTOSAR_CP_EXP_LayeredSoftwareArchitecture.pdf` | "Overview of Software Layers — detailed view" (no figure numbers in this doc) | 14 | `58e2e91e63171a373a19e1f10e680c8d98109389bce29079ce398f1d7791be07` |
| `spec-memory-partitioning-modes.png` | `specs/R25-11/CP/AUTOSAR_CP_EXP_FunctionalSafetyMeasures.pdf` | Figure 2.8 | 18 | `a6ae9be367d46e05d5a5599eed429e33853c8d2cd67b690b2c39432fa9a73b68` |
| `spec-secured-ipdu-layout.png` | `specs/R25-11/FO/AUTOSAR_FO_PRS_SecOCProtocol.pdf` | Figure 5.1 | 12 | `de2409ba406e4fb2bc040b2cdb6f85a23b910b86b97476f67d5cab700d23bf61` |
| `spec-someip-message-header.png` | `specs/R25-11/FO/AUTOSAR_FO_PRS_SOMEIPProtocol.pdf` | Figure 5.11 | 59 | `30ab5009c59848f995e08114ec12ec0708293995c5c727c95d87c23dea9909f7` |
| `spec-vfb-concept.png` | `specs/R25-11/CP/AUTOSAR_CP_TR_VFB.pdf` | Figure 2.2 | 13 | `72229f65fd155a6008e8f152431d16ae634875e4790aedb08fe33e489567b2d4` |
