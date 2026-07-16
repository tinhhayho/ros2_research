# Open-source building blocks under / next to commercial Adaptive AUTOSAR (AP)

> **Corrections (fact-check 2026-07-16, wf_ecadf716-210):** (6) vsomeip **never mentions `ara::com`**, but AUTOSAR does appear around its E2E support (changelog "Support AutoSAR E2E Profile 4", E2E test docs citing the AUTOSAR E2E/CRC specs, and two source files citing AUTOSAR FO R22-11) — not "no AUTOSAR or ara::com mention". (7) iceoryx's "Where is iceoryx used" table labels **RTA-VRTE (ETAS)** and **AVIN AGNOSAR** as AUTOSAR Adaptive Platform products, while **Apex.Ida is listed as safe/certified middleware without the AP label**. (8) iceoryx2's README/FAQ describe safety-critical ambitions ("designed to operate in safety-critical systems") but make **no AUTOSAR / ISO 26262 / ASIL certification claim** — not merely "safety/automotive on the roadmap". (9) DDS is **one of the three standardized `ara::com` network bindings (SOME/IP · Signal-Based · DDS)**, not "the other" of two.

Scope: production-grade open-source components that **move the actual bytes** beneath or beside
commercial Adaptive AUTOSAR stacks — SOME/IP transport, DDS transport, zero-copy shared-memory
IPC, and the IDL/proxy-stub tooling whose shape mirrors `ara::com`. All facts below were fetched
and verified on **2026-07-16** (July 2026). Every load-bearing claim is tied to a primary source
in the Sources list; anything I could not confirm from a primary source is called out explicitly.

---

## Key findings

1. **vsomeip (COVESA) is the reference open-source SOME/IP stack, and it is alive and shipping.**
   License **MPL-2.0** (verified from `LICENSE`), latest release **3.7.4 on 2026-07-06** (repo
   pushed the same day). It implements the SOME/IP wire protocol + Service Discovery + E2E, but it
   is deliberately **not** an `ara::com` API. The relationship is: SOME/IP is one of the two
   standardized *network bindings* of `ara::com`; a commercial AP stack maps `ara::com`
   proxy/skeleton calls down onto a SOME/IP stack like vsomeip. The vsomeip repo itself contains
   **no mention of AUTOSAR or ara::com** (verified) — it is a standalone middleware.

2. **CommonAPI C++ + CommonAPI-SomeIP (COVESA) are the closest open-source analogue to the
   `ara::com` *programming model*, but they are a separate, older lineage — and they are dormant.**
   MPL-2.0, BMW/COVESA. They generate C++ **proxy/stub** classes from **Franca IDL**, which
   parallels the AP `ara::com` **proxy/skeleton** pattern in *shape* (build a typed proxy, wait for
   availability, call methods, get/subscribe attributes). They are **not AUTOSAR** and not
   API-compatible with `ara::com`. Important activity finding: the whole CommonAPI stack
   (core-runtime, someip-runtime, core-tools) last released **3.2.4 / 3.2.15 on 2024-10-09** and
   has had **no pushes since** — effectively dormant as of July 2026.

3. **Eclipse iceoryx (C++, Apache-2.0) is the zero-copy shared-memory IPC that AP stacks name
   explicitly; iceoryx2 (Rust core, Apache-2.0 OR MIT) is its successor.** iceoryx's own README
   (main branch) lists AUTOSAR-Adaptive users and ships a dedicated
   **`iceoryx-automotive-soa`** binding described as "*Binding for automotive frameworks like
   AUTOSAR Adaptive ara::com*". That is the honest, current (2026) statement — **not** the stale
   2019 "fully compatible with ara::com" marketing line. iceoryx2 is younger (pre-1.0, v0.9.3),
   very active, with safety/automotive on its **roadmap** but **no AUTOSAR/ISO-26262/ASIL claim in
   its README**.

4. **CORRECTION on Eclipse S-CORE: its `ara::com` communication does NOT run on iceoryx/iceoryx2 —
   it has its own module called "LoLa".** The `eclipse-score/communication` repo README describes
   LoLa as "*A high-performance, safety-critical communication middleware implementation based on
   the Adaptive AUTOSAR Communication Management specification*" and "*Partial implementation of
   Adaptive AUTOSAR Communication Management (ara::com)*" using "*Zero-copy, shared-memory based
   data exchange*". Its `MODULE.bazel` depends on **`boost.interprocess`** for the shared memory,
   **not** iceoryx. A GitHub code search for `iceoryx` across the entire `eclipse-score` org
   returned nothing. So: S-CORE = dual-language C++/Rust (pinned fact, upheld), and its ara::com IPC
   is home-grown LoLa, not iceoryx2. Do not claim S-CORE uses iceoryx.

5. **eProsima Fast DDS is the Apache-2.0 open-source DDS side, but I could NOT verify from a
   primary source that Fast DDS was integrated into the *official AUTOSAR AP Demonstrator*.**
   Fast DDS is a full OMG DDS/RTPS implementation (also ROS 2's default RMW), and AP's DDS network
   binding is defined against that same OMG standard — but the documented reference work on the AP
   DDS binding is **RTI's** (RTI Connext, proprietary). The eProsima Fast DDS product page carries
   **no AUTOSAR/Adaptive/ara::com claim** (verified). Treat "Fast DDS = the AP Demonstrator's DDS
   binding" as **unverified**. Separately, the official AP Demonstrator itself is **not a public
   open-source release** — its source is obtained under an AUTOSAR Adaptive license (member/partner
   restricted); numerous *community* AP reimplementations exist on GitHub but are not the official
   demonstrator.

---

## vsomeip (COVESA / BMW-originated)

**What it is.** "*An implementation of Scalable service-Oriented MiddlewarE over IP*" (repo
description). The stack implements the SOME/IP protocol as a set of shared libraries: a core
SOME/IP library, a configuration module, a Service Discovery component, and an E2E protection
module. It is the de-facto open-source SOME/IP reference used across automotive Linux/embedded.

**Repo / License.** https://github.com/COVESA/vsomeip — **MPL-2.0**. Verified directly from
`LICENSE` (header reads "*Mozilla Public License Version 2.0*"); source files carry
"*Copyright (C) 2014-2026 Bayerische Motoren Werke Aktiengesellschaft (BMW AG) ... Mozilla Public
License, v. 2.0*".

**Activity (as of 2026-07-16).** Latest release **3.7.4, published 2026-07-06**; repo `pushed_at`
**2026-07-06**. ~1,263 commits on master. **Actively maintained.**

**How it relates to the AP standard.** SOME/IP is the **standardized network binding** of
`ara::com` (the other being DDS). vsomeip is a **standalone SOME/IP transport**, not an `ara::com`
API — a commercial AP stack's Communication Management maps `ara::com` proxy/skeleton operations
onto a SOME/IP stack of this kind. The vsomeip repository contains **no mention of AUTOSAR or
ara::com** (verified) — it is purely a SOME/IP middleware. So it "moves the bytes" under AP but is
not itself AP.

**Snippet — SOME/IP client (request) API shape.** From `examples/request-sample.cpp`, pinned at
commit `7bcc1e0`. Shows the handler-registration + request-target API a client uses; the client
then calls `app_->request_service(...)` (L86) and `app_->send(request_)` (L127) to drive the
request/response flow.

Permalink: https://github.com/COVESA/vsomeip/blob/7bcc1e06f16a774e70931ed641f475fbba9c8c64/examples/request-sample.cpp#L40-L54

```cpp
        app_->register_state_handler(std::bind(&client_sample::on_state, this, std::placeholders::_1));

        app_->register_message_handler(vsomeip::ANY_SERVICE, SAMPLE_INSTANCE_ID, vsomeip::ANY_METHOD,
                                       std::bind(&client_sample::on_message, this, std::placeholders::_1));

        request_->set_service(SAMPLE_SERVICE_ID);
        request_->set_instance(SAMPLE_INSTANCE_ID);
        request_->set_method(SAMPLE_METHOD_ID);

        std::shared_ptr<vsomeip::payload> its_payload = vsomeip::runtime::get()->create_payload();
        std::vector<vsomeip::byte_t> its_payload_data;
        for (std::size_t i = 0; i < 10; ++i)
            its_payload_data.push_back(vsomeip::byte_t(i % 256));
        its_payload->set_data(its_payload_data);
        request_->set_payload(its_payload);
```

(The server side, `examples/response-sample.cpp`, uses `app_->offer_service(...)`; subscribe/notify
lives in `examples/subscribe-sample.cpp` and `notify-sample.cpp`.)

---

## CommonAPI C++ and CommonAPI-SomeIP (COVESA)

**What they are.** CommonAPI C++ is a middleware-agnostic C++ API generated from **Franca IDL**
interface descriptions, following a **proxy/stub** pattern: the generator emits a typed `...Proxy`
(client) and `...Stub` (service) per interface, and a pluggable *binding* carries the traffic.
- `capicxx-core-runtime` — the binding-independent core runtime.
- `capicxx-someip-runtime` — the SOME/IP binding; it "*requires the CommonAPI Core Runtime library
  and vsomeip library as dependencies*", i.e. it rides on vsomeip for the wire.
- `capicxx-core-tools` — the Franca-based code generator + examples.

**Repos / License.** https://github.com/COVESA/capicxx-core-runtime,
https://github.com/COVESA/capicxx-someip-runtime, https://github.com/COVESA/capicxx-core-tools —
all **MPL-2.0** ("*This Source Code Form is subject to the terms of the Mozilla Public License,
v. 2.0*"). Copyright "*(C) 2016-2023 BMW AG / COVESA*".

**Activity (as of 2026-07-16).** core-runtime **3.2.4 (2024-10-09)**, someip-runtime pushed
**2024-10-09**, core-tools **3.2.15 (2024-10-09)**. No pushes on any of the three since Oct 2024 —
**dormant / maintenance-only** as of July 2026. Worth flagging to colleagues: still widely used in
existing IVI/GENIVI-lineage code, but not actively evolving.

**How the shape parallels `ara::com` (honestly, and clearly non-equivalent).** The generated
CommonAPI proxy usage — `runtime->buildProxy<...Proxy>(domain, instance, connection)`, wait on
`isAvailable()`, then call a method that returns a `CallStatus` — is structurally the same *mental
model* as an AP `ara::com` proxy: find/instantiate a typed service proxy, confirm it is offered,
call methods / get / subscribe events. **But they are different, non-interoperable stacks:**
CommonAPI predates and sits outside AUTOSAR, uses **Franca IDL** (not ARXML), its bindings are
D-Bus / SOME/IP (COVESA), and none of the CommonAPI repos mention AUTOSAR. It is an *analogy for
teaching the proxy/skeleton idea*, not an `ara::com` implementation.

**Snippet — CommonAPI proxy API shape.** From `capicxx-core-tools`
`CommonAPI-Examples/E01HelloWorld/src/E01HelloWorldClient.cpp`, pinned at commit `3ffd442`. After
this window the client calls `myProxy->sayHello(name, callStatus, returnMessage, &info)` (L46) and
checks `callStatus != CommonAPI::CallStatus::SUCCESS` (L47) — the method-call + status shape that
rhymes with an `ara::com` method future/result.

Permalink: https://github.com/COVESA/capicxx-core-tools/blob/3ffd442877b2e3e248c3f90d396fd8691a2dcb82/CommonAPI-Examples/E01HelloWorld/src/E01HelloWorldClient.cpp#L30-L44

```cpp
    std::shared_ptr<E01HelloWorldProxy<>> myProxy = runtime->buildProxy<E01HelloWorldProxy>(domain,
            instance, connection);

    std::cout << "Checking availability!" << std::endl;
    while (!myProxy->isAvailable())
        std::this_thread::sleep_for(std::chrono::microseconds(10));
    std::cout << "Available..." << std::endl;

    const std::string name = "World";
    CommonAPI::CallStatus callStatus;
    std::string returnMessage;

    CommonAPI::CallInfo info(1000);
    info.sender_ = 1234;
```

---

## Eclipse iceoryx (classic, v1 line)

**What it is.** "*Eclipse iceoryx™ — true zero-copy inter-process-communication*". A shared-memory
middleware that transfers data "*from publishers to subscribers without a single copy*". It is the
local, on-host zero-copy transport under DDS/AP stacks (also used by ROS 2, eCAL, Cyclone DDS,
Apex.AI).

**Repo / License / Language.** https://github.com/eclipse-iceoryx/iceoryx — **Apache-2.0**
(verified from `LICENSE`: "*Apache License / Version 2.0, January 2004*", copyright 2019 Robert
Bosch GmbH). Primarily C++.

**Activity (as of 2026-07-16).** Latest release **v2.0.8 (2026-05-19)**; repo pushed
**2026-06-28**. Maintained, but this v1 line is now the mature/maintenance branch with iceoryx2 as
the forward-looking successor.

**Documented AP role TODAY (verified from the README on `main`).** The README explicitly places
iceoryx under AUTOSAR Adaptive stacks:
- Ships a dedicated binding: "*iceoryx-automotive-soa | Binding for automotive frameworks like
  AUTOSAR Adaptive ara::com | C++*" (repo: `eclipse-iceoryx/iceoryx-automotive-soa`).
- "Used by" list includes "*RTA-VRTE | AUTOSAR Adaptive Platform software framework*" (ETAS),
  "*AVIN AGNOSAR Adaptive Platform | AUTOSAR Adaptive Platform Product from AVIN Systems*", and
  "*Apex.Ida from Apex.AI | Safe and certified middleware for autonomous mobility systems*".

**On the stale-marketing warning (upheld).** The correct, *current* statement is the narrow one
above: iceoryx provides a **binding** "*like AUTOSAR Adaptive ara::com*" — i.e. it is a zero-copy
transport that automotive/ara::com frameworks bind to, **not** a drop-in ara::com implementation.
Do not repeat the 2019 "fully compatible with ara::com" phrasing; it is not what the project claims
in 2026.

---

## Eclipse iceoryx2 (Rust core, successor)

**What it is.** Current README tagline: "*Zero-Copy Lock-Free IPC with a Rust Core*" (the repo
description also renders as "*the zero-copy data plane with a Rust core*"). A decentralized (no
central daemon) zero-copy IPC supporting publish-subscribe, request-response, and events, with
consistently low latency independent of payload size.

**Repo / License / Language.** https://github.com/eclipse-iceoryx/iceoryx2 — dual-licensed
**Apache-2.0 OR MIT** (verified: `LICENSE-APACHE` = "*Apache License / Version 2.0, January 2004*").
Rust core (~72%), with completed language bindings for **C, C++, C#, Python** (README table).

**Activity (as of 2026-07-16).** Latest tag **v0.9.3, published 2026-07-08 (marked pre-release)** —
still pre-1.0; repo pushed **2026-07-15**. **Very active.**

**Documented AP/safety role TODAY (honest reading).** iceoryx2's **README does NOT claim** AUTOSAR,
Adaptive Platform, ara::com, S-CORE, ISO 26262, ASIL, or any safety certification (verified). Its
`ROADMAP.md` has a "*Safety & Security*" section and items like "*Zero-copy across hypervisor
partitions*", i.e. safety/automotive are **aspirational roadmap**, not shipped/certified. So:
position iceoryx2 as the actively developed next-gen zero-copy IPC with safety ambitions, **not**
as a certified AP component today.

**Relation to the pinned S-CORE fact.** iceoryx2 does **not** list S-CORE as a user, and S-CORE
does not depend on it (see LoLa section). Do not couple them.

---

## Eclipse S-CORE communication module "LoLa" (context / correction)

**What it is.** `eclipse-score/communication` hosts **LoLa**, described as "*A high-performance,
safety-critical communication middleware implementation based on the Adaptive AUTOSAR Communication
Management specification*" and "*Partial implementation of Adaptive AUTOSAR Communication Management
(ara::com)*", using "*Zero-copy, shared-memory based data exchange*" / "*Zero-copy shared-memory
based inter-process communication (IPC) in embedded systems*".

**Repo / License / Activity.** https://github.com/eclipse-score/communication — part of Eclipse
S-CORE (Apache-2.0 project; S-CORE launched 2025-06-12, dual-language C++/Rust — pinned fact,
upheld). Repo pushed **2026-07-15** — very active.

**The load-bearing correction.** LoLa is S-CORE's **own** ara::com-style IPC. Its `MODULE.bazel`
pulls **`boost.interprocess`** (v1.83) for shared memory and **`rules_rust`** (dual-language), and
has **no iceoryx dependency**; a code search for `iceoryx` across the whole `eclipse-score` org
returned nothing. So the open-source, ara::com-shaped, zero-copy IPC inside S-CORE is **LoLa built
on boost.interprocess**, not iceoryx/iceoryx2. (S-CORE also has an `inc_someip_gateway` incubation
repo for a SOME/IP gateway feature — separate from LoLa's local IPC.)

---

## eProsima Fast DDS (the DDS side, open-source angle only)

**What it is.** "*A C++ implementation of the DDS (Data Distribution Service) standard of the OMG*",
implementing RTPS over UDP etc., exposing both the DDS API and lower-level RTPS. It is also ROS 2's
default RMW (`rmw_fastrtps`).

**Repo / License / Activity.** https://github.com/eProsima/Fast-DDS — **Apache-2.0** (verified from
`LICENSE`: "*Apache License / Version 2.0, January 2004*"). Latest release **v3.6.2 (2026-07-02)**;
repo pushed **2026-07-16**. **Very active.**

**Open-source AP angle (honest, with the gap called out).** DDS is the *other* standardized
`ara::com` network binding (alongside SOME/IP); the AP DDS binding is specified against the **OMG
DDS/RTPS** standard that Fast DDS fully implements, so Fast DDS is a technically-eligible
open-source DDS for a DDS-bound AP deployment. **However:** I found **no primary statement** that
Fast DDS was integrated as the DDS binding of the **official AUTOSAR AP Demonstrator**. The
eProsima Fast DDS product page carries **no AUTOSAR/Adaptive/ara::com claim** (verified). The
publicly documented reference work on the AP DDS network binding is **RTI's** (RTI Connext,
proprietary) — and even RTI's own blog says only "*RTI's reference implementation of the DDS network
binding*" without naming a "Demonstrator". **Do not state Fast DDS is the AP Demonstrator's DDS
binding.** (Deck already covers DDS-binding spec history; this note is strictly the OSS-licensing
angle.)

---

## Other OSS regularly named in/near commercial AP deployments (verified existence)

- **`iceoryx-automotive-soa`** — https://github.com/eclipse-iceoryx/iceoryx-automotive-soa —
  the iceoryx binding "*for automotive frameworks like AUTOSAR Adaptive ara::com*". Named directly
  in iceoryx's README (verified). This is the concrete artifact behind "iceoryx under ara::com".
- **Franca IDL** (behind CommonAPI) — the IDL that CommonAPI generates from; relevant as the
  non-AUTOSAR analogue to ARXML-driven `ara::com` codegen.
- **Community AP reimplementations on GitHub** (education/POC, *not* the official demonstrator, and
  out of this scout's production-grade scope but worth knowing they exist): e.g.
  `langroodi/Adaptive-AUTOSAR` (Linux simulator, educational), `Chaos0929/AdaptiveAUTOSAR-Cpp17`,
  `LoyenWang/AUTOSAR-Adaptive`. Listed here only so the orchestrator can route them to the
  education-focused scout; I did not license-verify each.

---

## Sources (every URL used, fetched 2026-07-16)

Primary repos / raw files:
- https://github.com/COVESA/vsomeip
- https://raw.githubusercontent.com/COVESA/vsomeip/master/LICENSE
- https://raw.githubusercontent.com/COVESA/vsomeip/7bcc1e06f16a774e70931ed641f475fbba9c8c64/examples/request-sample.cpp
- https://api.github.com/repos/COVESA/vsomeip (pushed_at) ; /releases/latest (3.7.4) ; /contents/examples ; /commits/master (SHA 7bcc1e0)
- https://github.com/COVESA/capicxx-core-runtime ; /releases/latest (3.2.4) ; api pushed_at
- https://github.com/COVESA/capicxx-someip-runtime ; api pushed_at
- https://github.com/COVESA/capicxx-core-tools ; /releases/latest (3.2.15) ; /commits/master (SHA 3ffd442)
- https://raw.githubusercontent.com/COVESA/capicxx-core-tools/3ffd442877b2e3e248c3f90d396fd8691a2dcb82/CommonAPI-Examples/E01HelloWorld/src/E01HelloWorldClient.cpp
- https://github.com/eclipse-iceoryx/iceoryx
- https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx/main/README.md
- https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx/main/LICENSE
- https://api.github.com/repos/eclipse-iceoryx/iceoryx (pushed_at) ; /releases/latest (v2.0.8)
- https://github.com/eclipse-iceoryx/iceoryx2
- https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx2/main/README.md
- https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx2/main/ROADMAP.md
- https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx2/main/LICENSE-APACHE
- https://api.github.com/repos/eclipse-iceoryx/iceoryx2 (pushed_at) ; /tags ; /releases (v0.9.3 prerelease)
- https://github.com/eProsima/Fast-DDS
- https://raw.githubusercontent.com/eProsima/Fast-DDS/master/LICENSE
- https://api.github.com/repos/eProsima/Fast-DDS (pushed_at) ; latest release v3.6.2
- https://www.eprosima.com/middleware/fast-dds (no AUTOSAR claim; Apache-2.0)
- https://github.com/eclipse-score/communication
- https://raw.githubusercontent.com/eclipse-score/communication/main/README.md (LoLa)
- https://raw.githubusercontent.com/eclipse-score/communication/main/MODULE.bazel (boost.interprocess, rules_rust; no iceoryx)
- https://api.github.com/orgs/eclipse-score/repos (LoLa = communication module) ; /search/code?q=iceoryx+org:eclipse-score (no hits)

Secondary / corroborating (not used as the basis for any candidate claim):
- https://www.rti.com/blog/integrating-dds-into-the-autosar-adaptive-platform
- https://www.globenewswire.com/news-release/2018/11/15/1652204/0/en/AUTOSAR-Releases-Latest-Version-of-Adaptive-Platform-Featuring-a-Full-Network-Binding-of-the-DDS-Standard.html
- GitHub search results for community AP reimplementations (langroodi/Adaptive-AUTOSAR, etc.)
