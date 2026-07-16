# AUTOSAR R25-11 spec mirror

**Purpose.** This directory is a **local, unmodified mirror of the AUTOSAR R25-11 specification
PDFs referenced by the deck** at `autosar/slides/autosar-deck.md` (reading-map slide + References
slides + slide bodies). It exists so the team can **search the specs offline** — grep, full-text
PDF search, or open them without a network round-trip.

- **Download date:** 2026-07-16
- **Release:** R25-11 (published 2025-11-27)
- **Files:** 35 PDFs (CP + AP + FO)
- **Source URL pattern:** `https://www.autosar.org/fileadmin/standards/R25-11/<AREA>/<NAME>.pdf`
  where `<AREA>` is `CP` (Classic Platform), `AP` (Adaptive Platform), or `FO` (Foundation),
  derived from the `AUTOSAR_CP_` / `AUTOSAR_AP_` / `AUTOSAR_FO_` filename prefix.
- **Fetch command:** `curl -ksL` (the `-k` works around a broken TLS chain in the fetch sandbox;
  files are otherwise byte-for-byte the publisher's originals).
- **Integrity:** see `R25-11/SHA256SUMS` (sha256, paths relative to `R25-11/`). Verify with
  `cd R25-11 && sha256sum -c SHA256SUMS`.

Names are the R25-11 canonical, area-prefixed filenames. Where the deck's References slides cite an
older release under pre-unification naming (e.g. `AUTOSAR_SWS_NVRAMManager`,
`AUTOSAR_FO_PRS_SecOcProtocol`), those deduplicate into the R25-11 name here
(`AUTOSAR_CP_SWS_NVRAMManager`, `AUTOSAR_FO_PRS_SecOCProtocol`).

## Files

| File | Area | Size | Source URL |
|---|---|---|---|
| `AUTOSAR_CP_EXP_FunctionalSafetyMeasures.pdf` | CP | 11.8 MB | https://www.autosar.org/fileadmin/standards/R25-11/CP/AUTOSAR_CP_EXP_FunctionalSafetyMeasures.pdf |
| `AUTOSAR_CP_EXP_LayeredSoftwareArchitecture.pdf` | CP | 2.5 MB | https://www.autosar.org/fileadmin/standards/R25-11/CP/AUTOSAR_CP_EXP_LayeredSoftwareArchitecture.pdf |
| `AUTOSAR_CP_EXP_ModeManagementGuide.pdf` | CP | 0.8 MB | https://www.autosar.org/fileadmin/standards/R25-11/CP/AUTOSAR_CP_EXP_ModeManagementGuide.pdf |
| `AUTOSAR_CP_SWS_CANInterface.pdf` | CP | 1.4 MB | https://www.autosar.org/fileadmin/standards/R25-11/CP/AUTOSAR_CP_SWS_CANInterface.pdf |
| `AUTOSAR_CP_SWS_CANTransportLayer.pdf` | CP | 1.6 MB | https://www.autosar.org/fileadmin/standards/R25-11/CP/AUTOSAR_CP_SWS_CANTransportLayer.pdf |
| `AUTOSAR_CP_SWS_COM.pdf` | CP | 2.8 MB | https://www.autosar.org/fileadmin/standards/R25-11/CP/AUTOSAR_CP_SWS_COM.pdf |
| `AUTOSAR_CP_SWS_DiagnosticCommunicationManager.pdf` | CP | 4.9 MB | https://www.autosar.org/fileadmin/standards/R25-11/CP/AUTOSAR_CP_SWS_DiagnosticCommunicationManager.pdf |
| `AUTOSAR_CP_SWS_DiagnosticEventManager.pdf` | CP | 6.7 MB | https://www.autosar.org/fileadmin/standards/R25-11/CP/AUTOSAR_CP_SWS_DiagnosticEventManager.pdf |
| `AUTOSAR_CP_SWS_NVRAMManager.pdf` | CP | 5.4 MB | https://www.autosar.org/fileadmin/standards/R25-11/CP/AUTOSAR_CP_SWS_NVRAMManager.pdf |
| `AUTOSAR_CP_SWS_OS.pdf` | CP | 4.5 MB | https://www.autosar.org/fileadmin/standards/R25-11/CP/AUTOSAR_CP_SWS_OS.pdf |
| `AUTOSAR_CP_SWS_PDURouter.pdf` | CP | 0.8 MB | https://www.autosar.org/fileadmin/standards/R25-11/CP/AUTOSAR_CP_SWS_PDURouter.pdf |
| `AUTOSAR_CP_SWS_RTE.pdf` | CP | 10.4 MB | https://www.autosar.org/fileadmin/standards/R25-11/CP/AUTOSAR_CP_SWS_RTE.pdf |
| `AUTOSAR_CP_SWS_WatchdogManager.pdf` | CP | 0.9 MB | https://www.autosar.org/fileadmin/standards/R25-11/CP/AUTOSAR_CP_SWS_WatchdogManager.pdf |
| `AUTOSAR_CP_TR_ReleaseOverview.pdf` | CP | 0.3 MB | https://www.autosar.org/fileadmin/standards/R25-11/CP/AUTOSAR_CP_TR_ReleaseOverview.pdf |
| `AUTOSAR_CP_TR_VFB.pdf` | CP | 6.7 MB | https://www.autosar.org/fileadmin/standards/R25-11/CP/AUTOSAR_CP_TR_VFB.pdf |
| `AUTOSAR_AP_EXP_PlatformDesign.pdf` | AP | 4.5 MB | https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_EXP_PlatformDesign.pdf |
| `AUTOSAR_AP_EXP_SOVD.pdf` | AP | 0.3 MB | https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_EXP_SOVD.pdf |
| `AUTOSAR_AP_EXP_SWArchitecture.pdf` | AP | 1.7 MB | https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_EXP_SWArchitecture.pdf |
| `AUTOSAR_AP_SWS_CommunicationManagement.pdf` | AP | 4.4 MB | https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_SWS_CommunicationManagement.pdf |
| `AUTOSAR_AP_SWS_Diagnostics.pdf` | AP | 6.0 MB | https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_SWS_Diagnostics.pdf |
| `AUTOSAR_AP_SWS_ExecutionManagement.pdf` | AP | 1.8 MB | https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_SWS_ExecutionManagement.pdf |
| `AUTOSAR_AP_SWS_OperatingSystemInterface.pdf` | AP | 0.2 MB | https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_SWS_OperatingSystemInterface.pdf |
| `AUTOSAR_AP_SWS_Persistency.pdf` | AP | 1.2 MB | https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_SWS_Persistency.pdf |
| `AUTOSAR_AP_SWS_PlatformHealthManagement.pdf` | AP | 0.7 MB | https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_SWS_PlatformHealthManagement.pdf |
| `AUTOSAR_AP_SWS_StateManagement.pdf` | AP | 3.6 MB | https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_SWS_StateManagement.pdf |
| `AUTOSAR_AP_SWS_UpdateAndConfigurationManagement.pdf` | AP | 1.0 MB | https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_SWS_UpdateAndConfigurationManagement.pdf |
| `AUTOSAR_AP_SWS_VehicleUpdateAndConfigurationManagement.pdf` | AP | 1.1 MB | https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_SWS_VehicleUpdateAndConfigurationManagement.pdf |
| `AUTOSAR_AP_TPS_ManifestSpecification.pdf` | AP | 10.4 MB | https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_TPS_ManifestSpecification.pdf |
| `AUTOSAR_AP_TR_ReleaseOverview.pdf` | AP | 0.2 MB | https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_TR_ReleaseOverview.pdf |
| `AUTOSAR_FO_EXP_SWArchitecturalDecisions.pdf` | FO | 0.2 MB | https://www.autosar.org/fileadmin/standards/R25-11/FO/AUTOSAR_FO_EXP_SWArchitecturalDecisions.pdf |
| `AUTOSAR_FO_PRS_E2EProtocol.pdf` | FO | 3.3 MB | https://www.autosar.org/fileadmin/standards/R25-11/FO/AUTOSAR_FO_PRS_E2EProtocol.pdf |
| `AUTOSAR_FO_PRS_NetworkManagementProtocol.pdf` | FO | 0.2 MB | https://www.autosar.org/fileadmin/standards/R25-11/FO/AUTOSAR_FO_PRS_NetworkManagementProtocol.pdf |
| `AUTOSAR_FO_PRS_SecOCProtocol.pdf` | FO | 0.2 MB | https://www.autosar.org/fileadmin/standards/R25-11/FO/AUTOSAR_FO_PRS_SecOCProtocol.pdf |
| `AUTOSAR_FO_PRS_SOMEIPProtocol.pdf` | FO | 1.5 MB | https://www.autosar.org/fileadmin/standards/R25-11/FO/AUTOSAR_FO_PRS_SOMEIPProtocol.pdf |
| `AUTOSAR_FO_PRS_SOMEIPServiceDiscoveryProtocol.pdf` | FO | 16.7 MB | https://www.autosar.org/fileadmin/standards/R25-11/FO/AUTOSAR_FO_PRS_SOMEIPServiceDiscoveryProtocol.pdf |

## Legal / copyright

From the AUTOSAR R25-11 **Disclaimer** section, quoted as-is:

> This work may be utilized or reproduced without any modification, in any form or by any means,
> for informational purposes only. For any other purpose, no part of the work may be utilized or
> reproduced, in any form or by any means, without permission in writing from the publisher.

The PDFs in this directory are stored unmodified, for informational purposes, copyright AUTOSAR.
