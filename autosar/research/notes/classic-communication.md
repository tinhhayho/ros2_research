# AUTOSAR Classic Platform — Signal-Based Communication Stack

> Research notes for embedded/firmware engineers new to automotive software platforms.
> Audience already knows MCUs, CAN framing, RTOS, bare-metal C. Focus: how CP moves a
> signal end-to-end, and where its static, signal-oriented model differs from a
> service-oriented runtime. Latest release verified: **AUTOSAR R25-11** (released
> 2025-11-27, minor release, supersedes R24-11) [1]. Today: 2026-07-15.

## Executive summary

AUTOSAR Classic Platform (CP) communication is **signal-oriented and frozen at build
time**. Application software reads/writes *signals* through the RTE; the COM module packs
signals into I-PDUs on a fixed byte layout; PduR routes PDUs; bus interface modules
(CanIf/LinIf/FrIf/SoAd) hand frames to drivers. There is no runtime discovery of who
talks to whom on classic buses — the entire mapping (the **communication matrix**) is
generated from ARXML (historically K-matrix/DBC/FIBEX) and compiled in. On top of this
core, CP layers optional services: **CanTp** and friends for segmenting PDUs larger than
one frame; **E2E** profiles (CRC + counter + Data ID) to detect corruption/loss/reordering
across ECU and even bus boundaries per ISO 26262; **SecOC** to add a truncated CMAC/AES-128
MAC plus a freshness value for authenticity and replay protection (but *not* confidentiality);
and **Network Management** (CanNm/FrNm/UdpNm) for synchronized sleep/wakeup and **partial
networking**. CP can also do **SOME/IP** over Ethernet (SomeIpXf + SoAd + Service Discovery),
but its "services" are still statically configured, so it lacks the true dynamic
service-orientation of the Adaptive Platform. FlexRay is in decline; CAN FD is now
mainstream, with CAN XL and zonal/Ethernet backbones the growth direction.

## 1. Signal → PDU → frame: the module chain (TX and RX)

The core insight for a firmware engineer: the CP stack is a **layered pipeline of BSW
modules**, each doing one abstraction step, wired by a build-time configuration.

**TX (application → wire), CAN example:**
1. **SW-C / RTE** — application writes a value; RTE calls `Com_SendSignal`.
2. **COM** — packs the signal (bit position, length, endianness, scaling already resolved
   at build time) into an **I-PDU** (a byte array). Applies TX modes (periodic/on-change),
   minimum delay, and can invoke the E2E/SOME/IP **transformer chain** here.
3. **PduR (PDU Router)** — a configurable routing table forwards the I-PDU to the correct
   lower module. For a normal CAN signal PDU it goes to CanIf; for a large PDU it goes to
   CanTp first. PduR is also where **gateway routing** (bus-to-bus forwarding) happens.
4. **(CanTp)** — only if the PDU is larger than one frame's payload: segments it into
   First Frame / Consecutive Frames with flow control (ISO 15765-2 style).
5. **CanIf (CAN Interface)** — ECU-abstraction layer: maps the abstract PDU to a hardware
   transmit handle/mailbox, manages controller mode and PDU mode, calls the driver [2][7].
6. **CanDrv (MCAL CAN driver)** — writes the CAN/CAN FD frame to the controller. Transmit
   confirmation propagates back up (CanIf → PduR → COM → RTE).

**RX (wire → application)** is the mirror image: CanDrv ISR → **CanIf** reception
indication → **PduR** → (**CanTp** reassembly if segmented) → **COM** unpacks the byte
layout back into signals, runs reception deadline monitoring / signal invalidation → **RTE**
delivers to the SW-C [2][7]. Related helper modules: **IpduM** (I-PDU Multiplexer) packs
several alternative "sub-PDUs" into one PDU on the wire (dynamic multiplexing) and handles
**container/contained** PDUs; **LdCom** is a thin large-data path that bypasses signal
packing. The same skeleton holds for other buses by swapping the interface/driver:
LIN → **LinIf/LinTp/LinDrv**, FlexRay → **FrIf/FrTp/FrDrv**, Ethernet → **SoAd/TcpIp/EthIf**.

## 2. The communication matrix — why it is frozen at build time

The **communication matrix (K-matrix)** is the master description of *all* network
communication in the vehicle: every frame/PDU, every signal, which ECU sends it, which
ECUs receive it, byte layout, timing (cycle time, min-delay), and value encoding
(scaling, offset, physical units) [3][8].

- **Why frozen:** CP targets deeply embedded ECUs (small flash/RAM, deterministic timing,
  ASIL safety). There is no dynamic memory allocation or runtime service negotiation on the
  classic buses. COM's packing/unpacking code, PduR's routing table, and the CanIf handle
  map are all **statically generated** from the matrix, so timing and memory are known and
  provable at integration time. A given ECU only ever sees the PDUs configured for it.
- **File-format lineage:** the historical exchange formats are **DBC** (Vector, CAN only),
  **LDF** (LIN), and **FIBEX** (ASAM, multi-bus). AUTOSAR's own format is **ARXML** (the
  System Description / System Extract). Tools import DBC/LDF/FIBEX, fill in the
  AUTOSAR-specific parameters per the System Template, and export an **ARXML** system
  extract, from which each ECU's BSW is configured/generated [3][8]. "K-matrix" is the
  colloquial (often Excel/DBC-era) term; ARXML is the formal AUTOSAR carrier.

For an embedded engineer: think of it as the CAN "message database" you already know
(DBC), but promoted to a whole-vehicle, multi-bus, code-generating source of truth.

## 3. Ethernet & SOME/IP on Classic — and its structural limits

CP *can* do service-oriented SOME/IP over automotive Ethernet, split across three modules:
- **SomeIpXf (SOME/IP Transformer)** — a serializer in the COM transformer chain that
  converts VFB data (sender-receiver, client-server, trigger) into the SOME/IP on-wire byte
  format and back [5]. It implements the serialization only.
- **SoAd (Socket Adaptor)** — maps PDUs to TCP/UDP sockets via the TcpIp stack; must be
  initialized before SD [4].
- **SD (Service Discovery, SOME/IP-SD)** — sends **OfferService / FindService** entries and
  handles **SubscribeEventgroup** (incl. multicast eventgroups and TTL), interacting with
  **BswM** and **SoAd** [4][9]. Events can be delivered to multicast endpoints once a
  subscriber count threshold is crossed [9].

**Structural limit vs a true service-oriented runtime:** even though SOME/IP-SD adds
runtime offer/find/subscribe, the *set of services, their IDs, interfaces, and the
transformer/serialization layout are still fixed in ARXML and code-generated*. CP cannot
load new service software or renegotiate interfaces at runtime; there is no POSIX process
model, no `ara::com` proxy/skeleton generated dynamically, no service-instance manifest that
can change without reflashing. So CP SOME/IP is best seen as "static services with dynamic
availability/subscription," whereas the **Adaptive Platform** (sibling agent's scope) offers
dynamically deployable services on POSIX. (Noted here only to mark the structural boundary.)

## 4. E2E protection — profiles and the fault model

E2E ("End-to-End") protection guards **safety-relevant** data against communication faults
per ISO 26262. It is a library/transformer invoked in the COM transformer chain, so
protection travels **with the payload across ECU and bus boundaries** (including through
PduR gateways) — the CRC/counter are computed at the true sender and checked at the true
receiver, independent of the intervening network. The PRS enumerates the fault model it
addresses: **repetition, loss, delay, insertion, masquerade/incorrect addressing, incorrect
sequence, corruption, asymmetric information to multiple receivers, subset reception, and
blocking of the channel** [6]. Mechanisms: a **CRC** (corruption/masquerade), a **counter**
(repetition/loss/insertion/wrong sequence), **timeout monitoring** (loss/delay), and a
**Data ID** folded into the CRC (masquerade/addressing) [6].

Profiles (each tuned to a bus and detection target) [6]:
| Profile | CRC | Typical use |
|---|---|---|
| P1 | 8-bit (CRC-8-SAE J1850), CP-only | legacy CAN |
| P2 | 8-bit, CP-only | legacy CAN (predefined Data ID lists) |
| P4 | **32-bit** (CRC-32P4) | FlexRay/Ethernet, high Hamming distance, long data |
| P5 | **16-bit** (CRC-16 CCITT-FALSE) | CAN/general, sufficient detection |
| P6 | 16-bit | SOME/IP (aligned to SOME/IP layout) |
| P7 | **64-bit** (CRC-64-ECMA) | very large Ethernet data, highest detection |
| P11 | 8-bit | LIN / simplified, P1-like |
| P22 | 8-bit | SOME/IP events, P5-family style |

The newer profiles (4/5/6/7/11/22) share a simpler check design; P1/P2 have a more elaborate
dynamic max-delta-counter and re-sync logic and don't accept NULL pointers [6][10]. Note the
8-bit-CRC profiles cannot detect a masquerading fault in a specific single cycle due to the
short polynomial [6].

## 5. SecOC — what a truncated MAC + freshness actually guarantees

**SecOC (Secure Onboard Communication)** adds **authenticity and freshness** to PDU-based
communication; it does *not* encrypt — payload stays in the clear (the PRS scope is
authenticity/integrity/freshness, with no confidentiality mechanism) [11].

Mechanics [11]:
- On TX, SecOC builds a **Secured I-PDU** = Authentic I-PDU + **Authenticator** (a MAC) +
  optionally a (truncated) **Freshness Value**. The freshness value is always mixed into the
  MAC even when not transmitted.
- **Algorithm:** "*Using the CMAC algorithm based on AES-128 according to NIST SP 800-38B to
  calculate the MAC*" (SecOC Profile 1 = 24Bit-CMAC-8Bit-FV) [11].
- **Truncation:** to fit tight CAN payloads the MAC is truncated to its most-significant
  bits and the freshness to its least-significant bits. Profile 1: "*use the eight least
  significant bit of the freshness value as truncated freshness value and use the 24 most
  significant bits of the MAC as truncated MAC*" [11]. Truncation lowers the security level,
  so with a full MAC ≥128 bits it is a tradeoff, and length is configurable per Secured
  I-PDU via `SecOCAuthInfoTruncLength` / `SecOCFreshnessValueTruncLength` [11].
- **Freshness** comes from a **Freshness Manager** SW component (monotonic counter or
  timestamp), shared by sender and receiver — this is what defeats **replay** [11].

**Guarantee, honestly stated:** a receiver that verifies the MAC knows the message (1) was
produced by a party holding the shared symmetric key (**data-origin authentication**, which
"*implicitly provides data integrity*"), and (2) is **fresh**, not a replay — *provided* key
distribution and freshness synchronization are sound. It does **not** hide the data
(no confidentiality) and, being symmetric, does not give non-repudiation. Key management
(provisioning, rotation) is **out of SecOC's scope** — SecOC "*relies on the existence of a
software component that provides a freshness*" value and on the Crypto stack (CSM/CryIf/Crypto
driver) for keys [11].

## 6. Network management, partial networking, and the bus landscape in 2026

**Network Management (NM):** "*Main purpose of the NM protocol is to coordinate one or more
groups of ECUs to wake up and shutdown their communication stack synchronously*" [12]. It is
based on **periodic NM messages** in an NM cluster: receiving them means "keep the cluster
awake"; a node that no longer needs the bus stops sending, and once a timer elapses with no
NM messages, all nodes transition together to **Bus-Sleep** (via **Prepare Bus-Sleep**)
[12]. A bus-independent **NM Interface (Nm)** coordinates bus-specific modules **CanNm /
FrNm / UdpNm** [12]. This is how a parked car saves battery without any single master.

**Partial Networking (PN):** lets a **subset** of ECUs on a shared bus sleep while others
stay awake — e.g., keep the door module alive while the powertrain sleeps. Each bit of the
**PN Info Range** in the NM message's **Control Bit Vector (CBV)** represents one **Partial
Network Cluster (PNC)**; a set bit requests that PNC. Dedicated **partial-networking CAN
transceivers** wake the controller only on matching frames. PNC coordinators are top-level
(gateway across channels) or intermediate [12].

**Bus landscape (2026):**
- **CAN FD** is now mainstream in CP (up to 64-byte payload, faster data-phase bitrate);
  Classic CAN remains for low-cost/legacy nodes. Industry commentary: "*CAN FD will eat up
  FlexRay's market share*" [13].
- **FlexRay** is in decline — high cost/complexity, squeezed by CAN FD from below and
  automotive Ethernet from above; it survives mainly in existing high-end chassis/powertrain
  designs and legacy platforms rather than new zonal architectures [13][14]. AUTOSAR still
  specifies FrIf/FrNm/FrTp, so it is supported, not removed.
- **Automotive Ethernet** (100BASE-T1/1000BASE-T1, TSN) is the growth path for zonal/
  service-oriented architectures, carrying SOME/IP and DoIP. **CAN XL** (ISO 11898-1:2024,
  up to 2048-byte payloads, ~10–20 Mbit/s) is emerging as the next CAN generation bridging
  CAN and Ethernet [13] — see open questions on AUTOSAR CAN XL support status.

## Key facts

| # | fact | source URL | exact quote (if load-bearing) | confidence |
|---|------|-----------|-------------------------------|------------|
| 1 | Latest release is R25-11, out 2025-11-27, minor, supersedes R24-11 | https://www.autosar.org/news-events/detail/release-r25-11-is-now-available | — | high |
| 2 | TX path: COM packs signal→I-PDU, PduR routes, CanIf→CAN driver | https://mohamedayman23.medium.com/inside-the-autosar-can-communication-stack-a-layered-architecture-explained-8e92e0f265f9 | COM packs signals into an I-PDU and hands it to PduR, which forwards it to CanIf | high (secondary, matches SWS) |
| 3 | Comm matrix imported as ARXML/FIBEX/DBC/LDF and code-generated | https://eeacom-docs.intrepidcs.com/intro/ | import matrices in ARXML or FIBEX ...; DBC, for CAN ...; LDF, for LIN | high |
| 4 | SoAd must be initialized before SD; SD interacts with BswM/SoAd | https://www.autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_SWS_ServiceDiscovery.pdf | "The SoAd module needs to be initialized before the SD module is initialized." | high (vendor summary of SWS) |
| 5 | SomeIpXf serializes VFB comms; SD/SoAd handle the rest | https://www.autosartoday.com/posts/someipxf_overview_-_messages_and_vfb_serialization_in_autosar | transformer implements some features ... others handled by SD or SoAd | med (secondary) |
| 6 | E2E fault model: repetition, loss, delay, insertion, masquerade, wrong sequence, corruption | https://www.autosar.org/fileadmin/standards/R19-03/FO/AUTOSAR_PRS_E2EProtocol.pdf | "repetition of information; loss of information; delay of information; insertion of information; masquerade or incorrect addressing..." | high (primary) |
| 6b | E2E CRC widths: P1/2/11/22=8b, P5/6=16b, P4=32b, P7=64b | https://www.autosar.org/fileadmin/standards/R19-03/FO/AUTOSAR_PRS_E2EProtocol.pdf | "E2E Profile 4 uses a 32-bit CRC"; "Profile 7 uses a 64-bit CRC"; "Profile 5 uses a 16-bit CRC" | high (primary) |
| 7 | SecOC = authenticity + freshness of PDU comms; MAC + optional FV | https://www.autosar.org/fileadmin/standards/R24-11/FO/AUTOSAR_FO_PRS_SecOcProtocol.pdf | "the authenticity and freshness of PDU based communication between ECUs" | high (primary) |
| 8 | SecOC MAC = CMAC/AES-128 per NIST SP 800-38B | https://www.autosar.org/fileadmin/standards/R24-11/FO/AUTOSAR_FO_PRS_SecOcProtocol.pdf | "Using the CMAC algorithm based on AES-128 according to NIST SP 800-38B to calculate the MAC" | high (primary) |
| 9 | SecOC Profile 1 truncation: 8 LSB of FV, 24 MSB of MAC | https://www.autosar.org/fileadmin/standards/R24-11/FO/AUTOSAR_FO_PRS_SecOcProtocol.pdf | "use the eight least significant bit of the freshness value ... and use the 24 most significant bits of the MAC as truncated MAC" | high (primary) |
| 10 | SecOC provides no confidentiality (integrity/authenticity only) | https://www.autosar.org/fileadmin/standards/R24-11/FO/AUTOSAR_FO_PRS_SecOcProtocol.pdf | "Data origin authentication implicitly provides data integrity" (no encryption mechanism in scope) | med (inferred from scope) |
| 11 | NM coordinates synchronized wake/sleep via periodic NM messages | https://www.autosar.org/fileadmin/standards/R22-11/FO/AUTOSAR_PRS_NetworkManagementProtocol.pdf | "coordinate one or more groups of ECUs to wake up and shutdown their communication stack synchronously" | high (primary) |
| 12 | Partial networking: each PN Info Range bit = one Partial Network | https://www.autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_SWS_NetworkManagementInterface.pdf | "Every bit of the PN Info Range represents one Partial Network..." | high (primary/vendor) |
| 13 | CAN FD displacing FlexRay; FlexRay market share small | https://www.eenewseurope.com/en/infineon-can-fd-success-goes-at-the-expense-of-flexray/ | "CAN FD will eat up FlexRay's market share" | med (industry press) |
| 14 | CanTp segments PDUs > one frame (ISO 15765-2 style) | https://www.embitel.com/blog/embedded-blog/what-is-autosar-communication-stack-comstack/ | CanTp for segmentation | high (secondary, matches SWS) |

## Sources

1. https://www.autosar.org/news-events/detail/release-r25-11-is-now-available — Release R25-11 is Now Available — AUTOSAR — primary
2. https://www.autosar.org/fileadmin/standards/R19-03/FO/AUTOSAR_PRS_E2EProtocol.pdf — E2E Protocol Specification (FO 1.5.1) — AUTOSAR — primary
3. https://www.autosar.org/fileadmin/standards/R24-11/FO/AUTOSAR_FO_PRS_SecOcProtocol.pdf — SecOC Protocol Specification (R24-11) — AUTOSAR — primary
4. https://www.autosar.org/fileadmin/standards/R22-11/FO/AUTOSAR_PRS_NetworkManagementProtocol.pdf — NM Protocol Specification (R22-11) — AUTOSAR — primary
5. https://www.autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_SWS_ServiceDiscovery.pdf — Specification of Service Discovery (R22-11) — AUTOSAR — primary
6. https://www.autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_SWS_NetworkManagementInterface.pdf — Specification of NM Interface (R22-11) — AUTOSAR — primary
7. https://www.autosar.org/fileadmin/standards/R22-11/FO/AUTOSAR_PRS_SOMEIPServiceDiscoveryProtocol.pdf — SOME/IP-SD Protocol Specification (R22-11) — AUTOSAR — primary
8. https://eeacom-docs.intrepidcs.com/intro/ — EEA COM Expert / ARXML tooling docs — Intrepid Control Systems — vendor
9. https://www.autosartoday.com/posts/someipxf_overview_-_messages_and_vfb_serialization_in_autosar — SomeIpXf Overview — AutosarToday — secondary
10. https://www.embitel.com/blog/embedded-blog/what-is-autosar-communication-stack-comstack/ — What is AUTOSAR ComStack — Embitel — secondary
11. https://www.eenewseurope.com/en/infineon-can-fd-success-goes-at-the-expense-of-flexray/ — CAN FD success at expense of FlexRay (Infineon) — eeNews Europe — secondary
12. https://mohamedayman23.medium.com/inside-the-autosar-can-communication-stack-a-layered-architecture-explained-8e92e0f265f9 — Inside the AUTOSAR CAN Communication Stack — Medium — secondary
13. https://en.wikipedia.org/wiki/FlexRay — FlexRay — Wikipedia — secondary

## Surprises

- **CP SOME/IP is "static services, dynamic subscription."** A repo audience might assume
  SOME/IP = service-oriented like the Adaptive Platform. On CP the service set/IDs/layout are
  still code-generated from ARXML; only availability (offer/find) and eventgroup subscription
  are runtime. It is not dynamically deployable software.
- **SecOC does not encrypt.** Despite "Secure Onboard Communication," payload is authenticated
  and made replay-resistant but sent in clear — no confidentiality. Easy to overstate.
- **MACs are heavily truncated** (e.g., 24-bit MAC + 8-bit freshness in Profile 1) to fit CAN
  frames — a deliberate security/bandwidth tradeoff, explicitly acknowledged as a lower
  security level in the spec.
- **E2E travels through gateways**, computed at the real endpoints, so a PduR bus-to-bus
  gateway cannot silently corrupt safety data undetected — protection is genuinely end-to-end,
  not per-hop.
- **8-bit E2E profiles cannot catch a masquerade in a single cycle** (short polynomial) — a
  non-obvious limitation that matters for ASIL decomposition.

## Open questions

- **CAN XL AUTOSAR support status.** ISO 11898-1:2024 defines CAN XL (up to 2048 B, ~10–20
  Mbit/s). I could not confirm from a primary AUTOSAR R25-11 document exactly which release
  first added CanXL driver/CanIf support. *Guess (labeled): CP added CanXL handling around
  R23-11/R24-11; needs verification against the R25-11 CP release overview / SWS CAN Driver.*
- **Exact SecOC "no confidentiality" wording.** The PRS scopes SecOC to authenticity/integrity/
  freshness and lists no encryption mechanism, but I did not find a single sentence literally
  stating "SecOC does not provide confidentiality." Fact #10 is an inference from scope
  (confidence med).
- **R25-11 deltas to the communication stack.** I confirmed R25-11 exists and is a minor
  release but did not enumerate COM/PduR/SecOC/E2E changes vs R24-11 (release overview PDF
  failed TLS in-sandbox; would need direct-fetch verification).
- **Whether P1/P2 remain CP-only in the latest E2E spec.** The R19-03 PRS labels P1/P2
  "only for CP"; I did not re-verify this hasn't changed in a newer FO E2E release.
- **Primary confirmation of the exact TX/RX module order** relied on vendor/secondary summaries
  (Medium/Embitel) that match the SWS; the autosar.org SWS COM/PduR PDFs were not directly
  quoted here because HTML/some PDF fetches hit TLS errors in-sandbox (SecOC/E2E/NM/SD PDFs
  were fetched successfully via curl).
