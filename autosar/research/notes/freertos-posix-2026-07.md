# FreeRTOS + POSIX: live-verification, July 2026

Verification date: 2026-07-16. All facts below were pulled live from primary
sources (GitHub REST API + raw file fetches, freertos.org, aws.github.io,
Espressif docs) on that date. Verbatim quotes are marked with quotation marks.

**Bottom line up front:** The earlier characterization is still essentially
accurate, with one nuance. FreeRTOS+POSIX remains a **FreeRTOS-Labs project**
(`Lab-Project-FreeRTOS-POSIX`), it is **not archived**, and it still receives
occasional small bug-fix PRs (most recently 2026-07-08) — so "dormant" is too
strong; call it **low-activity / maintenance-only**. But it is still the same
**small threading-oriented POSIX subset** (pthread + mutex/cond/barrier,
mqueue, semaphore, sched, clock/time, timer, partial unistd), still tagged only
`v1.0` (2020), and **nothing has graduated out of Labs** into `FreeRTOS-Kernel`
or the main `FreeRTOS/FreeRTOS` distribution, and **no new official POSIX module
shipped in 2024-2026**. No PSE51/PSE52 certification, no MMU multi-process model.

---

## Q1. GitHub: FreeRTOS org repos, Labs POSIX repo, graduation, kernel CHANGELOG

### Org enumeration (POSIX / kernel / labs relevant repos)
Enumerated `https://api.github.com/orgs/FreeRTOS/repos` (pages 1-4). The only
POSIX-application-API repo in the org is:

- `FreeRTOS/Lab-Project-FreeRTOS-POSIX` — archived: **false**; description:
  "This repository contains FreeRTOS+POSIX source code, which could be consumed
  as a submodule."

Other Lab-Project-* repos exist (FreeRTOS-FAT, LoRaWAN, MCUBoot, Cellular-Demo,
Tutorials, etc.) plus `FreeRTOS/FreeRTOS-Labs` (the umbrella Labs distribution).
There is **no** non-Labs repo named `FreeRTOS-POSIX`, and no POSIX API layer
folder inside `FreeRTOS-Kernel`.

### Lab-Project-FreeRTOS-POSIX metadata (GitHub API)
- `archived: false`, `disabled: false`, license MIT, default branch: **main** (only branch)
- `created_at: 2019-11-20`, `pushed_at: 2026-07-08T19:57:37Z`, `updated_at: 2026-07-08`
- Stars 142, forks 81, open issues 4
- **Only release/tag: `v1.0`, published 2020-02-14.** No newer release in 6+ years.

### Recent commit history (default branch `main`)
```
2026-07-08  f8cc8e3  Restore semaphore value on timed wait failure (#46)
2025-04-04  14ee4b2  Fix detach race condition (#43)
2025-03-31  1bb2a09  pthread_cond: refine prvInitializeStaticCond() (#42)
2025-03-11  f1fe687  Merge pull request #40 from aggarg/build_check
2025-03-10  9fe6bfe  Fix license header
2025-03-10  9c28003  Add CI check
2025-03-10  341a8dc  Add a minimal project which builds all the files
2025-03-10  b4e74b2  timer: add missing ";" (#39)
2025-02-24  4930934  timer: prevent infinite loop on one-shot timer start (#38)
2025-02-21  ae1d3f0  Remove redundant xTimerStart() in timer_settime (#37)
2025-02-03  8339845  Rename xTimerHandle to xTimer (#36)
2025-01-01  21d0639  pthread_cond: Use Task Notifications (#34)
2024-11-10  e6b133f  Update pthread_cond_timedwait to cope with clock failure (#33)
2024-09-25  d761d18  Remove unnecessary NULL check (#31)
2023-07-14  e921c4f  stm32h745 port using GNU Tools for STM32 (#28)
```
Interpretation: every 2024-2026 commit is a **bug fix, CI hygiene, or rename** to
the existing modules (semaphore, pthread_cond, timer). There is **no new API
family** and no expansion toward full POSIX. The 2026-07-08 commit (#46) is a
one-line semaphore correctness fix, not a feature.

### README wording (verbatim, raw main branch)
> "FreeRTOS+POSIX implements *a small subset* of the [POSIX threading] API. This
> subset allows application developers familiar with POSIX API to develop a
> FreeRTOS application using POSIX like threading primitives. FreeRTOS+POSIX does
> not implement more than 80% of the POSIX API. Therefore, an existing POSIX
> compliant application or a POSIX compliant library cannot be ported to run on
> FreeRTOS Kernel using only this wrapper."

> "This repository only contains source code. For demo applications, please visit
> https://github.com/FreeRTOS/FreeRTOS-Labs."

> Notes: "This project is undergoing optimizations or refactorization to improve
> memory usage, modularity, documentation, demo usability, or test coverage."

### API families actually implemented (source tree, `git/trees/main?recursive=1`)
Source `.c` files under `FreeRTOS-Plus-POSIX/source/`:
`clock, mqueue, pthread, pthread_barrier, pthread_cond, pthread_mutex, sched,
semaphore, timer, unistd, utils`.
Public headers under `include/FreeRTOS_POSIX/`:
`errno.h, fcntl.h, mqueue.h, pthread.h, sched.h, semaphore.h, signal.h,
sys/types.h, time.h, unistd.h, utils.h`.
This is exactly the threading/IPC/time subset described earlier — single-process,
no `fork`/`exec`, no full file system, no process model. `signal.h`/`fcntl.h` are
minimal type/stub headers, not full implementations.

### Graduation check
- Main distribution `FreeRTOS/FreeRTOS` → `FreeRTOS-Plus/Source/` contains:
  Application-Protocols, AWS, coreJSON, corePKCS11, FreeRTOS-Cellular-Interface,
  FreeRTOS-Cellular-Modules, FreeRTOS-Plus-CLI, FreeRTOS-Plus-IO,
  FreeRTOS-Plus-TCP, FreeRTOS-Plus-Trace, Reliance-Edge, Utilities.
  **There is NO `FreeRTOS-Plus-POSIX` here.** (The only "posix" strings in the
  main distro are `FreeRTOS/Demo/Posix_GCC` — the Linux simulator demo, i.e.
  direction (b) — and `Reliance-Edge/posix/*`, an unrelated filesystem adapter.)
- `FreeRTOS/FreeRTOS-Labs` still carries `FreeRTOS-Labs/Source/FreeRTOS-Plus-POSIX`
  as a git submodule (type `commit`) plus a
  `FreeRTOS_Plus_POSIX_with_actor_Windows_Simulator` demo. So the app-facing POSIX
  layer lives **only** in Labs, consumed as a submodule — unchanged model.

### FreeRTOS-Kernel releases + CHANGELOG (History.txt) 2024-2026
Kernel releases in window: **V11.1.0 (2024-04-22), V11.2.0 (2025-03-04),
V11.3.0 (2026-03-30)** (latest at verification time).
Every "POSIX" mention in `FreeRTOS-Kernel/History.txt` refers to either:
(1) the **POSIX/Linux simulator PORT** (direction (b)), e.g. line 859 verbatim:
> "Added new POSIX port layer that allows FreeRTOS to run on Linux hosts in..."
and the V11.3.0 entries:
> "Update POSIX port to delete thread key on process exit instead of in
> xPortStartScheduler to ensure proper cleanup of thread-specific memory."
> "Update POSIX port to fix race condition in vPortEndScheduler by moving
> scheduler thread signal after FreeRTOS thread check."
or (2) the kernel config flag `configUSE_POSIX_ERRNO` (line 1006 verbatim):
> "Added configUSE_POSIX_ERRNO to enable per task POSIX style errno"
**No CHANGELOG entry adds or graduates a POSIX application API layer into the
kernel.** The kernel gives you a POSIX-style per-task errno flag and a
Linux-host simulator port; it does not give applications a POSIX API.

---

## Q2. freertos.org docs / 2024-2026 announcements

- The official documentation page for FreeRTOS+POSIX lives at
  `https://www.freertos.org/Documentation/03-Libraries/05-FreeRTOS-labs/03-FreeRTOS-plus-POSIX/00-FreeRTOS-Plus-POSIX`
  — the URL path itself (`05-FreeRTOS-labs`) confirms the site still classifies
  FreeRTOS+POSIX **under FreeRTOS Labs**, not as a core library. (Automated fetch
  of the body was truncated by the tool; the classification is evident from the
  canonical path and from the Labs distribution structure above.)
- The Amazon-FreeRTOS POSIX overview states verbatim:
  > "FreeRTOS+POSIX partially implements IEEE Std 1003.1-2017 Edition The Open
  > Group Technical Standard Base Specifications, Issue 7."
  and lists exactly the headers `errno.h, fcntl.h, mqueue.h, pthread.h, sched.h,
  semaphore.h, signal.h, sys/types.h, time.h, unistd.h` — matching the repo.
- No 2024-2026 freertos.org blog post or announcement was found declaring new or
  expanded official POSIX support. Web search for a 2025-2026 PSE51/new-module
  announcement returned only the existing Labs docs and third-party articles
  (Medium RTOS comparison, Circuit Cellar), no new official release.

---

## Q3. Disambiguation — the two directions (CRITICAL, do not conflate)

- **(a) POSIX API FOR applications running ON FreeRTOS** — what the requester
  asked about. This is **FreeRTOS+POSIX** = `Lab-Project-FreeRTOS-POSIX`, a Labs
  submodule, the small threading subset above. Status: maintenance-only Labs
  project, v1.0/2020, not graduated, not full POSIX.
- **(b) POSIX/Linux simulator PORT running the FreeRTOS kernel ON a POSIX host**
  — this is a *development/simulation* port, the opposite direction. It lives in
  `FreeRTOS-Kernel/portable/ThirdParty/GCC/Posix` and is exercised by
  `FreeRTOS/Demo/Posix_GCC` (`FreeRTOS-simulator-for-Linux.url`). It is **actively
  maintained** (the V11.3.0 / March-2026 CHANGELOG "POSIX port" fixes are this).
  It does NOT give an application a POSIX API; it lets FreeRTOS itself run as a
  Linux process for testing. Reported here only to prevent confusion — it is
  irrelevant to whether apps get POSIX APIs.

---

## Q4. Non-official ecosystem shims on top of FreeRTOS (clearly NOT FreeRTOS-official)

- **ESP-IDF pthread layer (Espressif Systems)** — non-official, actively
  maintained by Espressif. Docs state verbatim:
  > "ESP-IDF is based on FreeRTOS but offers a range of POSIX-compatible APIs
  > that allow easy porting of third-party code."
  Applications use the toolchain's standard `pthread.h` plus `esp_pthread.h`
  extensions. Coverage: pthread create/join/detach/exit/self, thread attributes,
  mutexes, condition variables, unnamed semaphores, read/write locks,
  thread-specific data, `pthread_once`, and POSIX **message queues** (its mqueue
  is based on FreeRTOS-Plus-POSIX). Limitations: no message priorities,
  `pthread_cancel()` returns `ENOSYS`, no named semaphores, `mq_notify()` /
  `mq_setattr()` unimplemented. This is a **vendor SDK layer**, not part of the
  FreeRTOS project, single-process, no MMU.
- **NXP / ST vendor SDKs** — ship FreeRTOS as the RTOS; any POSIX-ish wrappers
  are thin/optional and not a FreeRTOS-official POSIX product. (No official NXP/ST
  "POSIX layer" product was verified in this pass — see unverified.)

None of these shims add a multi-process MMU model or full PSE51 conformance; they
are single-process threading wrappers.

---

## Q5. Impact on the AUTOSAR Adaptive Platform (AP) conclusion

**Nothing found changes the architectural conclusion.** AUTOSAR AP requires a
POSIX **PSE51** (or richer) conformant OS *plus* an MMU-backed multi-process
model (separate ara::* processes / applications with memory isolation, dynamic
loading, process supervision). FreeRTOS+POSIX is:
- a **partial** threading subset ("a small subset", "does not implement more than
  80% of the POSIX API", "an existing POSIX compliant application ... cannot be
  ported ... using only this wrapper") — i.e. not even a complete PSE51,
- **single-process** (no `fork`/`exec`, no process isolation, no MMU multi-process
  model — FreeRTOS is a single-address-space RTOS),
- **not certified** to any PSE profile.

Therefore FreeRTOS-class kernels still **cannot host AUTOSAR AP**. AP continues to
require a POSIX OS such as Linux or a QNX/PikeOS-class RTOS with MMU + PSE51+. The
2024-2026 FreeRTOS activity (a handful of Labs bug fixes and simulator-port
maintenance) does not move this needle.

---

## Sources (fetched live 2026-07-16)
- GitHub API: `https://api.github.com/repos/FreeRTOS/Lab-Project-FreeRTOS-POSIX` (metadata, archived flag, tags, releases, commits)
- Raw README: `https://raw.githubusercontent.com/FreeRTOS/Lab-Project-FreeRTOS-POSIX/main/README.md`
- Source tree: `https://api.github.com/repos/FreeRTOS/Lab-Project-FreeRTOS-POSIX/git/trees/main?recursive=1`
- GitHub API: `https://api.github.com/orgs/FreeRTOS/repos` (org enumeration, pages 1-4)
- GitHub API: `https://api.github.com/repos/FreeRTOS/FreeRTOS-Kernel/releases` and `/tags`
- Raw kernel CHANGELOG: `https://raw.githubusercontent.com/FreeRTOS/FreeRTOS-Kernel/main/History.txt`
- GitHub API: `https://api.github.com/repos/FreeRTOS/FreeRTOS/git/trees/main?recursive=0` (main distro tree; no FreeRTOS-Plus-POSIX)
- GitHub API: `https://api.github.com/repos/FreeRTOS/FreeRTOS-Labs/git/trees/main` (Labs still carries FreeRTOS-Plus-POSIX submodule)
- freertos.org docs path: `https://www.freertos.org/Documentation/03-Libraries/05-FreeRTOS-labs/03-FreeRTOS-plus-POSIX/00-FreeRTOS-Plus-POSIX` (Labs classification; body truncated by fetch tool)
- Amazon-FreeRTOS POSIX overview: `https://aws.github.io/amazon-freertos/202107.00/html2/posix/index.html` ("partially implements IEEE Std 1003.1-2017 ... Issue 7")
- Espressif ESP-IDF pthread docs: `https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/system/pthread.html`

## Unverified
- The freertos.org Labs POSIX page BODY text could not be captured verbatim (fetch
  tool returned "content truncated"); classification inferred from the canonical
  URL path and the Labs repo structure. The README + Amazon-FreeRTOS overview
  provide the verbatim scope wording instead.
- "PSE51" is a community/analytical framing of the subset's *shape* (single-process
  threads + mqueue + semaphore + timer); FreeRTOS's own docs/README do not use the
  literal label "PSE51" (they say "small subset of the POSIX threading API" /
  "partially implements IEEE Std 1003.1-2017 Issue 7"). No FreeRTOS+POSIX PSE51
  certification exists.
- Whether specific NXP MCUXpresso / ST STM32Cube SDK builds ship any POSIX wrapper
  beyond bundling FreeRTOS was not exhaustively verified in this pass; ESP-IDF is
  the one confirmed non-official pthread layer.
- `pushed_at: 2026-07-08` reflects the merge of bug-fix PR #46; no evidence of any
  larger in-flight branch (only branch is `main`; no other branches or newer tags).
