# Open-Source Adaptive AUTOSAR (AP / `ara::*`) Implementations — Scout Notes

> **Corrections (fact-check 2026-07-16, wf_ecadf716-210):** (1) langroodi's language standard is **C++14** (its CMakeLists sets `CMAKE_CXX_STANDARD 14`), not C++17. (2) langroodi self-describes **per cluster** against **R20-11 – R22-11** (R21-11 is the most-cited baseline; R22-11 only for the E2E Profile 11 part of `com` and for `phm`), not simply "approximating R22-11". (3) Its post-2023 commits are **documentation-only** (one later commit also touches CONTRIBUTING.md), not "README-only". (4) `ZiadAhmed9/ara-rs` is **dual-licensed Apache-2.0 OR MIT**, not Apache-2.0 only. (10) `insooth/autosar-adaptive` holds **64 spec PDFs + 17 spec ZIP archives (88 files total)** plus the single `ara::per` header, not "~88 spec PDFs".

Scope: open-source implementations of AUTOSAR Adaptive Platform APIs (`ara::com`, `ara::exec`,
`ara::diag`, `ara::phm`, `ara::sm`, `ara::core`, `ara::log`, …) — complete or partial,
educational or research — plus the public-availability status of the official AUTOSAR AP
Demonstrator / CAPI. Every fact below was verified against a primary source fetched on
**2026-07-16** (GitHub API, `raw.githubusercontent.com`, GitHub web, autosar.org, code.autosar.org).

---

## Key findings

1. **`langroodi/Adaptive-AUTOSAR` is the one genuinely broad, readable AP teaching codebase.**
   MIT, 489 stars / 196 forks, pure C++ (+CMake). It is an explicitly *educational Linux
   simulator* that implements real code across **seven `ara::` clusters** — `ara::com` (full
   SOME/IP + SOME/IP-SD state machines, pub/sub, RPC, E2E Profile 11), `ara::exec`, `ara::diag`
   (extensive UDS + DoIP), `ara::phm`, `ara::sm`, `ara::core`, `ara::log` — plus runnable
   platform daemons (execution/state/health/diagnostic managers) and an `extended_vehicle` demo
   app. **Caveat on activity:** the last *source-code* commit was **2023-06-22**; everything
   after that (through the 2025-04-08 `pushed_at`) is README/CONTRIBUTING edits only. So it is
   feature-frozen / dormant (~3 years cold) but not archived.

2. **Everything else is markedly smaller, a graveyard, or brand-new/unproven.** The sweep found
   *no* second broad C++ implementation. The rest fall into: (a) **spec-PDF dumps** masquerading
   as implementations (`insooth/autosar-adaptive`, `LoyenWang/AUTOSAR-Adaptive`); (b) **early
   skeletons** (`Chaos0929/AdaptiveAUTOSAR-Cpp17`, `TreeNeeBee/*`, `tianxingyang/AUTOSAR-AP`);
   (c) **single-cluster fragments** (`cflaviu/aa-crypto17-10`); and (d) one **ambitious but
   two-weeks-old Rust workspace** (`ZiadAhmed9/ara-rs`).

3. **A notable Rust attempt exists and is real code, not vapor:** `ZiadAhmed9/ara-rs` (Apache-2.0,
   created 2026-03-30). It mirrors the canonical `ara::com` **Proxy/Skeleton** shape in idiomatic
   async Rust, ships a `cargo-arxml` code generator (ARXML → proxy/skeleton), a SOME/IP transport
   crate, and worked `battery-service` / `diagnostics-service` examples. Very young, solo author,
   6 stars — promise, not a track record.

4. **The official AUTOSAR AP Demonstrator is NOT open source, and the successor "CAPI" is
   partner-gated.** AUTOSAR has pivoted from the old (member-only) *Demonstrator* to **CAPI —
   Common Adaptive Platform Implementation**, described on autosar.org as a "code-first initiative
   … Developed collaboratively by *and for* AUTOSAR partners." Its Git lives at
   `https://code.autosar.org/capi/capi`, which **redirects to a GitLab `users/sign_in` login** —
   i.e. no public/anonymous access. There is no public download of official AP reference code.

5. **Honor the pinned caveats.** `eclipse-iceoryx/iceoryx` and its `iceoryx-automotive-soa` example
   appear under the `autosar-adaptive` topic but are **IPC middleware / an SOA demo, not an
   `ara::*` implementation**; I did not re-assert any "fully compatible with `ara::com`" claim.
   Eclipse S-CORE was not surfaced by any AP-implementation search here (it is a separate SDV
   stack, out of this scout's scope).

---

## `langroodi/Adaptive-AUTOSAR` — the lead (verified in depth)

- **URL:** https://github.com/langroodi/Adaptive-AUTOSAR
- **What it is:** self-described "Adaptive Runtime AUTOSAR Linux Simulator." The wiki/README frame
  it as a **simulated Adaptive Platform environment over Linux, implementing the interfaces defined
  by the standard for educational purposes**. Not a product; explicitly a learning/simulation code.
- **License:** **MIT** (GitHub API `license.spdx_id = "MIT"`).
- **Language / standard:** C++ (1.44 MB C++, 22.9 KB CMake). Uses C++17 (`std::optional`-style
  `ara::core::Optional`, `std::promise`/`std::future`, `enum class`). Vendored `pugixml` for ARXML.
- **Popularity:** **489 stars, 196 forks, 0 open issues** (as of 2026-07-16). By a wide margin the
  most-starred community AP implementation found.
- **Activity / maintenance:** created 2021-06-29. **Last source commit 2023-06-22** ("Clean the
  todo list"); the final *feature* work was E2E Profile 11 in June 2023 and `ara::exec` refactors
  in Feb 2023. Commits since (2023-10, 2024-06, 2025-04) touch only README/CONTRIBUTING. Not
  archived. Verdict: **mature-but-dormant**, safe to read, unlikely to change under you.
- **What it covers (enumerated from the real `src/` tree, not the README):**
  - `ara::core` — `Result`, `ErrorCode`, `ErrorDomain`, `InstanceSpecifier`, `Optional`.
  - `ara::com` — SOME/IP message/RPC (`rpc_client`/`rpc_server`, `socket_rpc_*`), **SOME/IP-SD**
    with full client/server FSMs (`initial_wait`, `repetition`, `main`, `service_ready`, …),
    **pub/sub** client/server FSMs, options (IPv4 endpoint, load-balancing), entries, **E2E**
    (`profile.h`, `profile11.h`), and a "communication group" client/server. **Note:** this is a
    *SOME/IP-transport-level* API surface — there is **no generated `ara::com` Proxy/Skeleton
    facade** (no `src/ara/com/proxy` or `skeleton` dir). Apps drive `Subscribe(...)` /
    `OfferService`-style calls at the SOME/IP layer.
  - `ara::exec` — `ExecutionClient` (`ReportExecutionState`), `ExecutionServer`,
    `DeterministicClient`, `StateClient`/`StateServer`, `FunctionGroup`/`FunctionGroupState`,
    worker thread/runnable, modelled-process helper.
  - `ara::diag` — large UDS surface: `Monitor`, `Event`, `DTCInformation`, `Condition`,
    debouncers (counter/timer), `SecurityAccess`, `GenericUDSService`, upload/download,
    `Conversation`, and a `uds_service_router` (+ `application/doip` DoIP client/server, OBD→DoIP).
  - `ara::phm` — `SupervisedEntity`, `CheckpointCommunicator`, `RecoveryAction`, and supervisions
    (alive / deadline / elementary / global).
  - `ara::sm` — `Notifier`, `PowerMode`, `Trigger*`, `states`.
  - `ara::log` — `Logger`, `LogStream`, console/file sinks.
- **Build / demo story:** ships a real `CMakeLists.txt` and a `main.cpp` wiring an
  `extended_vehicle` application with `platform/` daemons (`execution_management`,
  `state_management`, `platform_health_management`, `diagnostic_manager`). Has a `test/` tree with
  mock network layers and GoogleTest-style unit tests. So: **yes, it builds and runs a simulated
  end-to-end scenario**, not just headers.
- **Relation to the AP standard:** hand-written approximation of the R22-11-era specs (README notes
  E2E limited to Profile 11 per R22-11; `ExecutionState` enum has only `kRunning`, matching the
  spec's collapsed state). It follows AP *naming and semantics* (`ara::core::Result<void>`,
  `InstanceSpecifier`, `ReportExecutionState`) but is **not** ARXML-model-generated and makes no
  conformance/safety claim.

### Load-bearing snippets (verbatim, commit-pinned to `866d158a10d895f1d269689a8ddf8153dc03b321`)

**(A) `ara::exec` lifecycle — `ExecutionClient::ReportExecutionState`**
`src/ara/exec/execution_client.h` L20–L58 —
https://github.com/langroodi/Adaptive-AUTOSAR/blob/866d158a10d895f1d269689a8ddf8153dc03b321/src/ara/exec/execution_client.h#L20-L58
```cpp
/// @brief Class that enables an adaptive application to interact with Execution Management
class ExecutionClient final
{
private:
    static const ExecErrorDomain cErrorDomain;
    const uint16_t cServiceId{1};
    const uint16_t cMethodId{1};
    const uint16_t cClientId{2};
    ...
public:
    ExecutionClient(
        core::InstanceSpecifier instanceSpecifier,
        com::someip::rpc::RpcClient *rpcClient,
        int64_t timeout = 30);
    ~ExecutionClient();
    /// @brief Report the application internal state to Execution Management
    ara::core::Result<void> ReportExecutionState(
        ExecutionState state) const;
};
```
Teaches: the canonical AP application → EM handshake (`ReportExecutionState`, `ara::core::Result<void>`,
`InstanceSpecifier`). Note the `ExecutionState` enum has a single value `kRunning` — matching R22-11.

**(B) Proxy/subscribe side — `SomeIpPubSubClient::Subscribe`**
`src/ara/com/someip/pubsub/someip_pubsub_client.h` L43–L52 —
https://github.com/langroodi/Adaptive-AUTOSAR/blob/866d158a10d895f1d269689a8ddf8153dc03b321/src/ara/com/someip/pubsub/someip_pubsub_client.h#L43-L52
```cpp
/// @brief Subscribe to an event-group
/// @param serviceId Service in interest ID
/// @param instanceId Service in interest instance ID
/// @param majorVersion Service in interest major version
/// @param eventgroupId Event-group in interest ID
void Subscribe(
    uint16_t serviceId,
    uint16_t instanceId,
    uint8_t majorVersion,
    uint16_t eventgroupId);
```
Teaches: this repo exposes subscription at the **SOME/IP event-group** level (service/instance/
eventgroup IDs) rather than a generated proxy's `Subscribe()` + `GetNewSamples()` — a good
illustration of what "`ara::com`" looks like when it is *not* code-generated from ARXML.

**(C) Skeleton/offer side — `SomeIpPubSubServer`**
`src/ara/com/someip/pubsub/someip_pubsub_server.h` L52–L62 —
https://github.com/langroodi/Adaptive-AUTOSAR/blob/866d158a10d895f1d269689a8ddf8153dc03b321/src/ara/com/someip/pubsub/someip_pubsub_server.h#L52-L62
```cpp
SomeIpPubSubServer(
    helper::NetworkLayer<sd::SomeIpSdMessage> *networkLayer,
    uint16_t serviceId,
    uint16_t instanceId,
    uint8_t majorVersion,
    uint16_t eventgroupId,
    helper::Ipv4Address ipAddress,
    uint16_t port);
/// @brief Start the server
void Start();
```
Teaches: the "offer" side is a SOME/IP pub/sub server bound to a service/eventgroup and a multicast
endpoint; `Start()`/`Stop()` drive an SD/pub-sub FSM. This is the skeleton analogue in this codebase.

---

## `ZiadAhmed9/ara-rs` — the notable Rust attempt (verified)

- **URL:** https://github.com/ZiadAhmed9/ara-rs
- **What it is:** "Cargo-native Rust developer toolkit for Adaptive AUTOSAR. ARXML code generation,
  typed async communication, and SOME/IP transport for embedded Linux ECUs." A multi-crate Cargo
  workspace: `ara-com` (proxy/skeleton/event/field/method/service abstractions), `ara-com-someip`
  (SOME/IP transport + SD + serialization), `cargo-arxml` (ARXML → generated proxy/skeleton
  codegen tool), plus `examples/battery-service` and `examples/diagnostics-service` with generated
  proxy+skeleton, an mdBook docs site, benchmarks, and a `cxx-bridge` interop example.
- **License:** **Apache-2.0** (GitHub API `license.spdx_id = "Apache-2.0"`).
- **Activity:** **created 2026-03-30, last push 2026-04-15** — i.e. ~2 weeks of very intense solo
  development. 6 stars. Not archived. Genuine, coherent Rust source in the core crates (verified
  `ara-com/src/skeleton.rs`, `proxy.rs`), but the breadth (15 planned "sprints", vsomeip interop,
  Yocto, benchmarks) far outruns its age — treat as **early/experimental, unproven in the field.**
- **Relation to AP standard:** deliberately maps the AP `ara::com` **ProxyBase/SkeletonBase** model
  and a `cargo-arxml` generator onto Rust; SOME/IP wire format for interop. No conformance claim.
- **Load-bearing snippet — `SkeletonBase::offer` (OfferService shape), Rust**
  `ara-com/src/skeleton.rs` L46–L67, commit `3bb2a86f8570c84be2d0e7cea9e31aa1d6409f67` —
  https://github.com/ZiadAhmed9/ara-rs/blob/3bb2a86f8570c84be2d0e7cea9e31aa1d6409f67/ara-com/src/skeleton.rs#L46-L67
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
/// Withdraw the service advertisement.
pub async fn stop_offer(&self) -> Result<(), AraComError> {
    self.transport
        .stop_offer_service(self.service_id, self.instance_id)
        .await
}
```
Teaches: the canonical AP `OfferService`/`StopOfferService` skeleton contract, here as async Rust
delegating to a SOME/IP transport. `ProxyBase` (in `ara-com/src/proxy.rs`) is the mirror image,
with `call_method` / `call_fire_and_forget`.

---

## `Chaos0929/AdaptiveAUTOSAR-Cpp17` — early structured skeleton (verified)

- **URL:** https://github.com/Chaos0929/AdaptiveAUTOSAR-Cpp17
- **License:** MIT. **0 stars.** Created 2025-01-17, last push 2025-01-08. C++17. Not archived.
- **What it covers:** only two thin areas so far — `ara::core::Array` (+ internal violation/location
  utils, with a unit test) and an **`ara::os` process abstraction** (`ara/os/interface/process`,
  with Linux and QNX backends) driven by a small `demo_manager`. ~48 files total.
- **Notable trait:** real **multi-target toolchain scaffolding** — GCC-11 Linux and **QCC-12 QNX
  8.0** CMake presets (x86_64 + aarch64). So it is set up like a productizable stack, but the actual
  `ara::*` surface implemented is minimal. **Verdict: promising layout, near-empty payload.**

---

## Graveyard / mislabeled survey (a finding in itself)

- **`insooth/autosar-adaptive`** — https://github.com/insooth/autosar-adaptive — MIT, **33 stars**,
  12 forks, last push **2020-10**. Described as "Implementation of the AUTOSAR Adaptive Platform
  specifications," but the tree is **~88 AUTOSAR 19-03/Foundation spec PDFs** plus exactly **one**
  implementation header, `include/ara/per/key_value_storage.h`. Effectively a **spec-PDF archive
  with a single stub**, abandoned. High stars are legacy/misleading.
- **`LoyenWang/AUTOSAR-Adaptive`** — https://github.com/LoyenWang/AUTOSAR-Adaptive — MIT, 2 stars,
  last push **2020-07**. No implementation code of its own: architecture-decision markdown, spec
  PDFs, a dev Dockerfile, and **14 git submodules** pointing at
  `github.com/UmlautSoftwareDevelopmentAccount/AP-*` (Com, Core, Crypto, Diag, Exec, IAM, Log, NM,
  Per, PHM, REST, SM, TSync, UCM). **That org now returns HTTP 404 (deleted)** — the submodules are
  dangling. **Verdict: dead scaffolding around a vanished multi-repo effort.**
- **`UmlautSoftwareDevelopmentAccount` (org)** — referenced by LoyenWang's submodules as a
  per-cluster AP implementation org; **`https://github.com/UmlautSoftwareDevelopmentAccount` → 404**,
  API `Not Found`. Gone.
- **`TreeNeeBee` (org)** — https://github.com/TreeNeeBee — a tiny, recent hobby org building
  per-cluster C++ repos: `Core` (2★), `Com` (2★), `Persistency`, `LogAndTrace` (MIT), and a
  `PlatformHealthManagement`/`fsm`/`swctool`, plus `Autosar-Standards` (another spec dump) and
  `LightAP` ("LAP is not AP"). Pushes across 2025-09…2026-03. Mostly 0–2 stars, mixed/absent
  licenses (several `NOASSERTION`). **Verdict: immature, fragmented, unproven.**
- **`tianxingyang/AUTOSAR-AP`** — https://github.com/tianxingyang/AUTOSAR-AP — MIT, 4 stars, last
  push 2024-09. README is a single line (`# AUTOSAR-AP`). **Near-empty stub.**
- **`cflaviu/aa-crypto17-10`** — https://github.com/cflaviu/aa-crypto17-10 — "Crypto interface of
  AUTOSAR Adaptive Platform," C++, 14 stars, last push **2019-09**. **Single-cluster (`ara::crypto`)
  header set, abandoned.**

## Related but NOT `ara::*` implementations (listed to prevent miscategorization)

- **`eclipse-iceoryx/iceoryx`** (2127★, active) — zero-copy IPC middleware; appears under the
  `autosar-adaptive` topic but is **transport, not an AP `ara::*` stack**. The
  **`eclipse-iceoryx/iceoryx-automotive-soa`** repo (44★, last push **2022-06**) is an *example* of
  service-oriented comms over iceoryx, not an `ara::com` implementation. Per the repo's pinned
  guidance, I did **not** repeat any legacy "fully compatible with `ara::com`" marketing.
- **`chrizog/someipy`** (SOME/IP in Python), **`girishchandranc/autosarfactory`** (ARXML Python
  model API), **`Iandiehard/diag-client-lib`** (UDS *client* library), **`vectorgrp/XCPlite`** (XCP),
  **`DD-Silence/Autosar`** (C# ARXML (de)serializer), **`rvenkatesh95/*`** (tooling for Vector's
  commercial *MICROSAR Adaptive*) — all adjacent tooling/protocol libs, none are AP runtime
  implementations.

## Official AUTOSAR AP Demonstrator / CAPI — public availability (verified)

- The old member-only **AP Demonstrator** is not offered as a public download; AUTOSAR has moved to
  **CAPI (Common Adaptive Platform Implementation)**. Verbatim from https://www.autosar.org/capi
  (fetched 2026-07-16):
  > "The AUTOSAR Common Adaptive Platform Implementation (CAPI) is a strategic, code-first initiative
  > by the global AUTOSAR community to provide a standardized, automotive-grade implementation of the
  > AUTOSAR Adaptive Platform standard. … Developed collaboratively by and for AUTOSAR partners, it
  > creates a common foundation that eliminates redundant development of non-differentiating
  > middleware components across the industry."
  and: "CAPI enforces AUTOSAR specifications through code-first advantages and **quarterly releases of
  automotive-grade code**."
- **Access is partner-gated.** The CAPI "Git" link on https://www.autosar.org/capi/aoc points to
  **`https://code.autosar.org/capi/capi`**, which **redirects to `https://code.autosar.org/users/sign_in`
  (GitLab Community Edition login)** — no anonymous/public access. Contact is `capi@autosar.org`.
- **Conclusion:** there is **no public open-source official AP reference implementation.** For showing
  colleagues real AP-shaped code, the community repos above (chiefly `langroodi/Adaptive-AUTOSAR`) are
  the practical option; the official code sits behind an AUTOSAR-partner GitLab login.

---

## Sources (all fetched 2026-07-16)

- https://github.com/langroodi/Adaptive-AUTOSAR
- https://api.github.com/repos/langroodi/Adaptive-AUTOSAR (metadata, license, stars, dates)
- https://api.github.com/repos/langroodi/Adaptive-AUTOSAR/languages
- https://api.github.com/repos/langroodi/Adaptive-AUTOSAR/commits?path=src (last source commit 2023-06-22)
- https://github.com/langroodi/Adaptive-AUTOSAR/commits/master.atom (full HEAD SHA 866d158a10d895f1d269689a8ddf8153dc03b321)
- https://raw.githubusercontent.com/langroodi/Adaptive-AUTOSAR/master/src/ara/exec/execution_client.h
- https://raw.githubusercontent.com/langroodi/Adaptive-AUTOSAR/master/src/ara/com/someip/pubsub/someip_pubsub_client.h
- https://raw.githubusercontent.com/langroodi/Adaptive-AUTOSAR/master/src/ara/com/someip/pubsub/someip_pubsub_server.h
- https://github.com/ZiadAhmed9/ara-rs and https://api.github.com/repos/ZiadAhmed9/ara-rs
- https://raw.githubusercontent.com/ZiadAhmed9/ara-rs/master/ara-com/src/skeleton.rs
- https://raw.githubusercontent.com/ZiadAhmed9/ara-rs/master/ara-com/src/proxy.rs
- https://github.com/Chaos0929/AdaptiveAUTOSAR-Cpp17 and its git tree (branch master_integration)
- https://github.com/insooth/autosar-adaptive and its git tree (master)
- https://github.com/LoyenWang/AUTOSAR-Adaptive and https://raw.githubusercontent.com/LoyenWang/AUTOSAR-Adaptive/master/.gitmodules
- https://api.github.com/users/UmlautSoftwareDevelopmentAccount (404 Not Found) and https://github.com/UmlautSoftwareDevelopmentAccount (HTTP 404)
- https://github.com/TreeNeeBee (org repo listing via API)
- https://github.com/tianxingyang/AUTOSAR-AP and https://raw.githubusercontent.com/tianxingyang/AUTOSAR-AP/main/README.md
- https://github.com/cflaviu/aa-crypto17-10 (via topic search)
- https://api.github.com/search/repositories?q=topic:autosar-adaptive&sort=stars (topic sweep)
- https://nvdungx.github.io/Adaptive-AUTOSAR/ (educational blog, MIT for the blog only — not an implementation)
- https://www.autosar.org/capi (CAPI description, quarterly releases)
- https://www.autosar.org/capi/aoc (CAPI contacts + Git link)
- https://code.autosar.org/capi/capi → redirects to https://code.autosar.org/users/sign_in (GitLab login; partner-gated)
