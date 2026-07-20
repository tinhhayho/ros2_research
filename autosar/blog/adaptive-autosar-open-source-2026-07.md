---
title: "Adaptive AUTOSAR in the open: what you can actually clone and read"
date: 2026-07-16
tags:
  - autosar
  - adaptive-platform
  - open-source
  - embedded
---

## The ask: show me real Adaptive AUTOSAR code

A colleague on my team — firmware, CAN, an RTOS, bare-metal reflashing, and
zero automotive-platform-software experience — cornered me after a slide review.
Every diagram of the AUTOSAR Adaptive Platform (AP) looks the same: boxes labelled
`ara::com`, `ara::exec`, Execution Management, functional clusters. "Fine," they said, "but
show me the *code*. What can I actually clone and read?"

That is a fair and surprisingly awkward question, so I spent a research day on it.
Everything below is dated: researched July 2026, all repo states as of 2026-07-16.

The short version: you can read AP-shaped code, you can ship the production transport layer
that runs *underneath* AP, and you can clone the whole software-defined-vehicle (SDV)
middleware belt that surrounds AP — but you cannot get a conformant, complete,
production-grade **open** AP stack. That gap is the whole story.

## The honest landscape — and the CAPI twist

Official AP code exists. AUTOSAR now ships it under the name **CAPI** — Common Adaptive
Platform Implementation — a code-first initiative with quarterly releases of
automotive-grade code, described as certification-ready. So the "there is no official
implementation" folklore is out of date. Here is the twist: CAPI is *"developed
collaboratively by and for AUTOSAR partners."* Its git link, `code.autosar.org/capi/capi`,
redirects straight to a GitLab `users/sign_in` page (verified 2026-07-16). It is
**partner-gated, not open source**. There is no public download of official AP reference
code.

The commercial stacks — Vector MICROSAR Adaptive, Elektrobit, ETAS RTA-VRTE, Apex.AI,
Qorix — are proprietary too. So what is genuinely open? The honest community landscape
sorts into a very short list:

- **`langroodi/Adaptive-AUTOSAR`** — the broadest readable AP *teaching* codebase. MIT,
  C++14, 489 stars, seven `ara::` clusters (com, exec, diag, phm, sm, core, log) plus a
  runnable simulated demo. Two caveats travel with it: it exposes **SOME/IP-transport-level
  APIs with no generated `ara::com` Proxy/Skeleton facade**, and it is **dormant** — last
  source commit **2023-06-22** (everything after is documentation-only). It self-describes
  per cluster against R20-11 – R22-11 (R21-11 is the most-cited baseline; R22-11 only for
  `com`'s E2E Profile 11 and `phm`).
- **`ZiadAhmed9/ara-rs`** — a Rust attempt with `ProxyBase`/`SkeletonBase`, a SOME/IP
  transport, `cargo-arxml` ARXML codegen, and worked examples. Apache-2.0 OR MIT
  (dual-licensed). But it was **created 2026-03-30** by a solo author and has 6 stars. Read
  it as **promise, not track record**.
- **A graveyard.** `insooth/autosar-adaptive` is 64 spec PDFs + 17 spec ZIP archives (88
  files total) plus a single `ara::per` header (its 33 stars mislead); `LoyenWang/AUTOSAR-Adaptive` is scaffolding whose 14
  submodules point at a deleted org (404); and several near-empty shells trail back to 2019.

<!-- suggested figure: the honest-landscape table from the "Open-source Adaptive AUTOSAR — an honest landscape" deck slide -->

## The real shape of AP code

Diagrams do not show the one thing a firmware engineer wants: how an app talks to the
platform, and how errors are reported when there is no exception culture. Two snippets
answer that.

First, the **Adaptive Application → Execution Management** state handshake, from `langroodi`
(dormant since 2023-06-22):

```cpp
            /// @brief Report the application internal state to Execution Management
            /// @param state Application current internal state
            /// @returns Void Result if the state reporting was successful, otherwise a Result containing the occurred error
            ara::core::Result<void> ReportExecutionState(
                ExecutionState state) const;
```

[langroodi/Adaptive-AUTOSAR @ 866d158 — src/ara/exec/execution_client.h#L54-L58](https://github.com/langroodi/Adaptive-AUTOSAR/blob/866d158a10d895f1d269689a8ddf8153dc03b321/src/ara/exec/execution_client.h#L54-L58)

Two things to notice. The return type is **`ara::core::Result<void>`**, not `void` plus a
`throw` — AP signals errors as a *returned value*, **not a thrown exception**. That is
exactly the discipline an MCU engineer who has banned exceptions in safety code already
lives by. And `ReportExecutionState` is the **contract every Adaptive Application
implements** so Execution Management (EM) knows the process actually reached its running
state (`kRunning` in this R22-11-era code). EM launches your process; your process reports
back. That single method *is* the EM-to-app protocol.

Second, the service-offer side, in idiomatic async Rust from `ara-rs` (created 2026-03-30):

```rust
    /// Advertise this service instance so that remote proxies can find it.
    pub async fn offer(
        &self,
        major_version: MajorVersion,
        minor_version: MinorVersion,
    ) -> Result<(), AraComError> {
        self.transport
            .offer_service(
                self.service_id,
                self.instance_id,
                major_version,
                minor_version,
            )
            .await
    }
```

[ZiadAhmed9/ara-rs @ 3bb2a86 — ara-com/src/skeleton.rs#L46-L60](https://github.com/ZiadAhmed9/ara-rs/blob/3bb2a86f8570c84be2d0e7cea9e31aa1d6409f67/ara-com/src/skeleton.rs#L46-L60)

Same error idiom — `Result<(), AraComError>`, a returned value, not an exception. And
`offer()`/`stop_offer()` are the **`OfferService`/`StopOfferService` skeleton lifecycle**:
a service skeleton advertises an instance so remote proxies can discover it, then withdraws
it. Underneath, it just delegates to a SOME/IP transport. That is the `ara::com`
service-side contract in miniature.

The caveat rides with the code: the C++ repo is three years cold and the Rust repo is weeks
old. Read them to learn the shape. Neither is conformant or production-grade.

## The LoLa surprise

The most interesting thing I found is not an AP implementation at all — it is close enough
to fool you. Eclipse S-CORE ships a communication module called **LoLa**
(`eclipse-score/communication`). Its README says, verbatim, that it is *"a communication
middleware implementation based on the Adaptive AUTOSAR Communication Management
specification"* and a *"Partial implementation of Adaptive AUTOSAR Communication Management
(ara::com)"*. The README also self-describes it as **ASIL-B qualified**.

So far that reads like open `ara::com`. But look closer. Its API namespace is
**`score::mw::com`, not `ara::com`**. And its zero-copy IPC is built on
**boost.interprocess, not iceoryx**. LoLa is `ara::com`-shaped and `ara::com`-inspired, but
it is S-CORE's own middleware, not the AUTOSAR API. This is the exact trap: *"based on the
`ara::com` specification"* is not the same as *"is `ara::com`."*

## Building blocks you can actually ship

Here is where the open story turns useful. Beneath any commercial AP stack sits a
production transport layer that *is* fully open:

- **vsomeip** (COVESA, BMW-originated). MPL-2.0, release **3.7.4 (2026-07-06)**, actively
  maintained. A standalone **SOME/IP + Service Discovery + E2E** stack — the standardized
  *network binding* under `ara::com`, not an `ara::com` API. Tellingly, the repo **never
  mentions `ara::com`**; AUTOSAR does appear around its E2E support (changelog *"Support
  AutoSAR E2E Profile 4"*, E2E test docs citing the AUTOSAR E2E/CRC specs, and two source
  files citing AUTOSAR FO R22-11). A commercial AP maps its proxy/skeleton calls down
  onto a stack like this.
- **Eclipse iceoryx**. Apache-2.0, **v2.0.8 (2026-05-19)**. Zero-copy shared-memory IPC. It
  ships `iceoryx-automotive-soa`, described in its README as *"a Binding for automotive
  frameworks like AUTOSAR Adaptive `ara::com`,"* and its "Where is iceoryx used" table labels
  RTA-VRTE (ETAS) and AVIN AGNOSAR as AUTOSAR Adaptive Platform products, while Apex.Ida is
  listed as safe/certified middleware without the AP label. (I am deliberately not repeating
  the old "fully compatible with `ara::com`" line — that is not what the project claims today.)
- **Eclipse iceoryx2**. Apache-2.0 OR MIT, **v0.9.3 (2026-07-08)**, pre-1.0 but very active.
  The Rust-core successor. Its README/FAQ describe safety-critical ambitions (*"designed to
  operate in safety-critical systems"*) but make **no AUTOSAR / ISO 26262 / ASIL
  certification claim**.
- **eProsima Fast DDS**. Apache-2.0, **v3.6.2 (2026-07-02)**. Full OMG **DDS/RTPS**. DDS is
  one of the three standardized `ara::com` network bindings (SOME/IP · Signal-Based · DDS),
  so Fast DDS is technically eligible — but it
  is **not** the documented AP Demonstrator binding (that reference work is RTI Connext,
  proprietary). Do not assume Fast DDS equals the AP DDS binding.
- **CommonAPI C++ / -SomeIP** (COVESA). MPL-2.0, **dormant since 2024-10-09**. Franca-IDL
  proxy/stub codegen whose shape *rhymes with* `ara::com` proxies/skeletons — but a separate,
  **non-AUTOSAR** lineage.

The pattern: the **protocol/transport layer of AP is fully available as production open
source; the `ara::` API layer is not.**

<!-- suggested figure: the building-blocks table from the "Building blocks you can actually ship today" deck slide -->

## The ecosystem around AP — and where the line sits

A live Eclipse/consortium belt surrounds AP, all Apache-2.0, all active — and none of it is
AP.

**Eclipse S-CORE** (launched **2025-06-12**; dual-language **C++/Rust** — never Rust-first;
backers BMW Group, Mercedes-Benz, Bosch, ETAS, QNX, Qorix, Accenture) is an open SDV **core
stack**. It is **not an AP implementation** and **makes no AP-compatibility claim** — no
official statement either way; community discussions about a compatibility/mapping layer
exist (eclipse-score GitHub discussions #759, #882) but nothing official. LoLa,
above, lives inside it.

**Eclipse OpenSOVD** (Apache-2.0, mostly Rust, Eclipse **Incubating**, proposed 2025-05-26,
active into July 2026) is the one I would open first if diagnostics is your world. It is an
open implementation of **SOVD (ISO 17978)** that explicitly **bridges AUTOSAR-Adaptive HPCs
and legacy UDS ECUs**, and it complements S-CORE. If you have seen the fleet-diagnostics
story — a backend speaking SOVD to a high-performance computer (HPC) that in turn
re-transports UDS down to Classic ECUs — OpenSOVD is that path in real, readable Rust.

Three more in the same neighbourhood, none of them AP: **Eclipse Ankaios** (workload
orchestration for automotive HPCs; conceptually overlaps AP Execution Management),
**Eclipse Kuksa** (VSS signal databroker, Rust), and **Eclipse uProtocol**
(transport-agnostic messaging; originated as a GM contribution, pairs with COVESA VSS/uServices).

Then the contrast that makes the boundary concrete: Classic AUTOSAR has an open **GPL-2.0**
lineage — Arctic Core, continued as `openAUTOSAR/classic-platform`, 2453 commits. **Adaptive
has no equivalent open conformant stack.** The one complete official AP implementation, CAPI,
is *"developed collaboratively by and for AUTOSAR partners"* — partner-gated, not open
source. That single fact is why the honest line holds: open AP means education plus building
blocks plus surrounding middleware, **not a production AP stack**.

<!-- suggested figure: the S-CORE / OpenSOVD / boundary map from the "The open ecosystem around AP — and where the line sits" deck slide -->

## A reading path for the team

If a colleague has one afternoon, here is the order I would give them:

1. **Open `langroodi/Adaptive-AUTOSAR` first.** It is the only broad, readable AP-shaped
   codebase, and seeing seven `ara::` clusters wired into a runnable simulated demo does more
   for intuition than any diagram. Just remember it is dormant and transport-level, not a
   generated `ara::com` facade.
2. **Then skim `ara-rs`** if your team leans Rust — to see the `ProxyBase`/`SkeletonBase`
   model and `cargo-arxml` codegen expressed in modern async. Treat it as a sketch of a
   possible future, not a dependency.
3. **Clone `vsomeip` to actually build and run SOME/IP.** This is production code you could
   ship under your own service layer today.
4. **Read OpenSOVD's route table** if you care about diagnostics — it maps straight onto the
   SOVD fleet path.
5. **Keep CAPI in mind as the thing you cannot clone** — so nobody burns a day hunting for a
   public mirror that does not exist.

And pin the boundary sentence above the whole exercise: you can learn the shape, ship the
transport, and clone the surroundings — but the conformant AP stack itself stays behind a
partner login.

## Sources

All repositories, releases and dates verified against their GitHub API / project pages on
2026-07-16.

**AP implementations**
- [github.com/langroodi/Adaptive-AUTOSAR](https://github.com/langroodi/Adaptive-AUTOSAR) — MIT · C++ · 7 `ara::` clusters · dormant since 2023-06
- [github.com/ZiadAhmed9/ara-rs](https://github.com/ZiadAhmed9/ara-rs) — Apache-2.0/MIT · Rust proxy/skeleton + `cargo-arxml` · created 2026-03
- [autosar.org/capi](https://www.autosar.org/capi) — CAPI: official, partner-gated, **not** open source

**Protocol / IPC building blocks**
- [github.com/COVESA/vsomeip](https://github.com/COVESA/vsomeip) — MPL-2.0 · SOME/IP
- [github.com/COVESA/capicxx-core-runtime](https://github.com/COVESA/capicxx-core-runtime) — MPL-2.0 · CommonAPI · dormant
- [github.com/eclipse-iceoryx/iceoryx](https://github.com/eclipse-iceoryx/iceoryx) — Apache-2.0 · zero-copy IPC
- [github.com/eclipse-iceoryx/iceoryx2](https://github.com/eclipse-iceoryx/iceoryx2) — Apache-2.0 OR MIT · Rust core
- [github.com/eProsima/Fast-DDS](https://github.com/eProsima/Fast-DDS) — Apache-2.0 · DDS/RTPS

**Open ecosystem around AP**
- [github.com/eclipse-score](https://github.com/eclipse-score) — S-CORE org · Apache-2.0
- [github.com/eclipse-score/communication](https://github.com/eclipse-score/communication) — LoLa: partial `ara::com`, `score::mw::com`
- [github.com/eclipse-opensovd/opensovd-core](https://github.com/eclipse-opensovd/opensovd-core) — Apache-2.0 · SOVD / ISO 17978
- [github.com/eclipse-ankaios/ankaios](https://github.com/eclipse-ankaios/ankaios) · [github.com/eclipse-kuksa/kuksa-databroker](https://github.com/eclipse-kuksa/kuksa-databroker) · [github.com/eclipse-uprotocol/up-spec](https://github.com/eclipse-uprotocol/up-spec) — Apache-2.0 SDV middleware, none are AP
- [autosar.org — SDV Alliance (CES 2024)](https://www.autosar.org/news-events/detail/collaboration-the-key-to-making-the-software-defined-vehicle-a-reality)

**Classic-side contrast**
- [github.com/openAUTOSAR/classic-platform](https://github.com/openAUTOSAR/classic-platform) — GPL-2.0 · Arctic Core lineage — the open Classic fork Adaptive has no equivalent of
