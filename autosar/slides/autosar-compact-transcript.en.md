# English presenter transcript — AUTOSAR in 30 minutes (Classic vs Adaptive)

This file is a read-aloud script for the 30-minute AUTOSAR deck "AUTOSAR in 30 minutes — Classic vs Adaptive". It has one section for each of the 28 slides, in deck order. Each section gives a target time, the words to say in short timed blocks, a line to move to the next slide, and a short tip where it truly helps. The spoken parts add up to about 31 and a half minutes, which is 1898 seconds, so keep a steady pace and trim a little if you want time for questions. All numbers, dates, names and honest warnings match the deck, and every technical term, module name and API name is kept in English for the engineers.

---

## Slide 1 — AUTOSAR in 30 minutes

**Target time: about 40 seconds.** This is the opening slide. Ask one question and tell people they already have the mental model.

**Open, ask the question (~15 sec):**
"Hello everyone. Thirty minutes, and only one question. Which AUTOSAR software runs on which chip. That is the whole story today. One organization, two platforms, and they sit in one car."

**The version stamp (~12 sec):**
"Everything in this deck is stamped to release R25-11. That release was published on the 27th of November, 2025. The outside claims all have a URL as their source, and the full deck keeps all the references."

**Reassure the audience (~13 sec):**
"You already know MCUs, which are small control chips. You know CAN, the car's main wiring bus. You know an RTOS, a small real-time operating system. And you know how to reflash bare-metal. So you already have the mental model. Today we just give it the automotive names. CP means Classic Platform, and AP means Adaptive Platform. Those two names come back all day."

**Transition:**
"Before the technical part, we answer one thing first. Why does AUTOSAR even exist?"

**Presentation tip:** Say "R25-11" as "R twenty-five eleven". Speak slowly here. This is the slide where people settle into their seats.

---

## Slide 2 — Why AUTOSAR exists

**Target time: about 75 seconds.** This slide plants a business rule that comes back at the end of the deck. Say it clearly.

**Open, what it really is (~18 sec):**
"First, clear up one misunderstanding. AUTOSAR is a worldwide development partnership. It is not a product. The founding talks happened in 2002. The Development Agreement was signed in July 2003. Today there are about 340 partners, exactly 339 at the end of 2025, across the whole industry. The specs are free to read. But you need a license to build a product from them."

**The model in one line (~22 sec):**
"The whole model fits in one founding-era phrase, from Heinecke and others in 2006. Cooperate on standards, compete on implementation. There is one shared spec and one XML schema. Then many vendors sell their own conformant stacks, all built from that one spec."

**The rule that predicts adoption (~25 sec):**
"And here is the business rule that predicts who uses AUTOSAR. Its value grows with how many organizational boundaries your software has to cross. Tier-1 suppliers, the companies that build an ECU, a control computer, for the carmaker, implement AUTOSAR to win the OEM's RFQ, which is the request for quotation. But a vertically-integrated OEM, a carmaker that builds everything itself, such as Rivian, just skips it and builds its own. That comes from the Sonatus interview."

**Close (~10 sec):**
"Remember this rule. It comes back on the silicon decision table and on the decision tree at the end."

**Transition:**
"Now into a real car. One vehicle, two platforms, and what runs where."

**Presentation tip:** If someone asks "340 or 339?", say: about 340 today, and the closing number for 2025 was 339. Tier-1 is the supplier that builds the ECU for the OEM. OEM is the carmaker. RFQ is the request for quotation.

---

## Slide 3 — One vehicle, two platforms

**Target time: about 55 seconds.** This is a frame slide. Build the two-platform worldview, but do not go deep yet.

**Open, two platforms (~20 sec):**
"One car, two platforms. Classic runs on the deeply-embedded MCUs, the small control chips that handle the fast control tasks. Adaptive runs on the HPC SoCs, the high-performance-compute chips, the big all-in-one chips that do the heavy computing."

**The core idea, not competitors (~20 sec):**
"The most important point on this slide is simple. These two are not competitors. They live together in one 2026 car. Adaptive does not replace Classic. And Adaptive does not try to do Classic's job."

**Close, how they connect (~15 sec):**
"They connect through Ethernet and through gateways. For the whole talk, keep this picture in your head. Two platforms, side by side, in one car."

**Transition:**
"Let us start with the side that is familiar to firmware people. Classic in one slide."

**Presentation tip:** Say "HPC" as "H P C" and "SoC" as "S O C". This is a short bridge slide. Do not linger.

---

## Slide 4 — Classic in one slide

**Target time: about 70 seconds.** Three pillars of Classic: everything static, the OS is a static real-time kernel, and the mature ASIL-D path.

**Open, everything is static (~22 sec):**
"Classic in one slide. Rule number one. Everything is static and decided at build time. The task set, the memory map and the communication matrix are all frozen in ARXML, which is the AUTOSAR setup file in XML. Then the tools generate all of that into exactly one binary for one ECU, which is one small control computer in the car."

**The OS is a static real-time kernel (~20 sec):**
"The OS here is a static real-time kernel. It fixes its whole task set at build time. It uses fixed-priority preemptive scheduling, and it has no heap. It is much like a statically configured RTOS you already know, only stricter. It is packaged as Scalability Classes SC1 to SC4. The higher classes add timing protection and memory protection."

**The mature ASIL-D path (~20 sec):**
"And Classic owns the mature ASIL-D path. ASIL is the car safety level from ISO 26262, the road-vehicle safety standard. Its determinism comes from making everything static. The first AUTOSAR implementation certified to ISO 26262 up to ASIL D appeared in 2016. That was Vector MICROSAR Safe, certified by exida."

**Close (~8 sec):**
"Static, a static real-time kernel, and a mature ASIL-D path. Those three pillars are the whole spirit of Classic."

**Transition:**
"On the next slide I will show one trick. This is the idea that is truly new for a bare-metal engineer."

**Presentation tip:** Point at the Classic stack picture when you say "one binary for one ECU". Say "ASIL" as "A-sil". The levels go QM, then A, B, C, D, from ISO 26262.

---

## Slide 5 — The relocation trick

**Target time: about 75 seconds.** This is the "aha" slide for firmware people. Show the problem first, then show how it works.

**Open, make the hook (~10 sec):**
"On the last slide I promised a trick. Here it is. You can move a software part from one ECU to another ECU. An ECU is one small control computer in the car. And you do not change the code of that part at all."

**How it works, part one, the VFB (~20 sec):**
"The secret is simple. Software parts never call each other directly. They also never call a bus or a driver. They only talk over one thing. It is called the Virtual Functional Bus. They use three calls: Rte_Write, Rte_Read, and Rte_Call. Their code never says CAN. It never names a driver."

**How it works, part two, the RTE is built per deployment (~30 sec):**
"So who decides where the data really goes? The RTE does. RTE means Runtime Environment. It is the generated glue code. And it is built fresh for each deployment. Look at the picture. On top, two parts talk over the bus. On the bottom, they are placed on real ECUs. If two parts sit on the same ECU, the tool makes the RTE a simple copy in memory. If they sit on two different ECUs, the tool makes the RTE a message on CAN or Ethernet. The code of the part stays the same in both cases."

**Close (~15 sec):**
"So when you move a part, only the generated code changes. Bare-metal has nothing like this."

**Transition:**
"Now let us go one layer down. When a real signal must go on the wire, how does Classic pack it?"

**Presentation tip:** Say this slide slower than the others. It is the base idea for the ara::com part later. If someone asks "is this like a HAL?", say: it is the same spirit, but the tool builds the code at build time for the whole car, so there is no runtime cost.

---

## Slide 6 — CP comms and diagnostics

**Target time: about 75 seconds.** Three even blocks: the comm matrix, the two diagnostic modules, and reflashing.

**Open, the communication matrix (~27 sec):**
"Classic comms and diagnostics in sixty seconds. Communication uses a frozen communication matrix, also called the K-matrix. It is signal-oriented, not service-oriented. It fixes every frame, every signal, every sender and every receiver at build time. The COM module, which is the AUTOSAR signal-packing module, packs the signals into I-PDUs, the packed data frames, and sends them onto CAN, LIN, FlexRay or Ethernet. All of this is statically generated. So you can prove it at integration time."

**The idea people get wrong, DEM computes, DCM formats (~30 sec):**
"Diagnostics split into two modules. And this is the number-one thing people get wrong, so get it right. DEM computes. DEM is the Diagnostic Event Manager, the fault-memory database. It debounces the monitor results and keeps the UDS status byte for each DTC, which is a stored fault code. DCM formats. DCM is the Diagnostic Communication Manager. It is a generated UDS server that reads DEM and talks to the tester. UDS is the standard diagnostic language, from ISO 14229. DCM computes nothing about faults."

**Reflashing you already know (~18 sec):**
"And reflashing is the bootloader you already know. The UDS services 0x34, 0x36 and 0x37, which are RequestDownload, TransferData and RequestTransferExit, flash the whole ECU through the bootloader."

**Transition:**
"That is the end of Classic. The next question is: why do we need a second platform at all?"

**Presentation tip:** Stress the line "DEM computes, DCM formats". People love to ask about it. Say "I-PDU" as "I P D U". If someone asks about FlexRay, say it is the deterministic high-speed bus, now declining.

---

## Slide 7 — Why Adaptive exists

**Target time: about 85 seconds.** This is a hinge slide. Classic's strengths turn into limits, and the sentence that defines Adaptive must be said exactly right.

**Open, strengths turn into limits (~40 sec):**
"Why do we need a second platform. Classic's own strengths turn into limits. It has a static communication matrix, with no service discovery at runtime. It has no dynamic deployment, and only limited over-the-air update of a function. Its BSW, the Basic Software, is C-centric and has no heap. So put all of that together. Classic cannot host large, always-changing C++ code, and it cannot host perception stacks."

**AUTOSAR's answer (~33 sec):**
"AUTOSAR's answer is a second platform, a service platform on POSIX. POSIX is the standard Unix-style OS interface. And this next sentence must be said exactly. Adaptive is middleware and services on top of a POSIX OS. It is not a new OS. The Adaptive Applications are ordinary POSIX processes, written in C++ and linked against ARA, which is the AUTOSAR runtime for Adaptive."

**Close, point at the figure (~12 sec):**
"Look at the Adaptive stack picture. At the bottom is an existing POSIX OS. On top is the ARA layer and the apps. AUTOSAR does not swap the OS. They put a service layer on top of the OS."

**Transition:**
"But not every OS can carry Adaptive. There is a hard line that picks your kernel."

**Presentation tip:** The line "it is not a new OS" is the most misunderstood point about AP, so stress it. Say "ARA" as "A R A". It stands for AUTOSAR Runtime for Adaptive Applications.

---

## Slide 8 — AP runs only on a POSIX OS

**Target time: about 70 seconds.** This slide sorts kernels. Do not read the whole table. State the two spec rules, then split into two groups.

**Open, the two spec rules (~28 sec):**
"This is the hardest architectural line. The spec makes it a hard rule. The apps must program against POSIX PSE51, which is the minimal single-process POSIX profile, plus the C++ Standard Library. That is in AP_SWS_OperatingSystemInterface, Doc 719, requirement RS_OSI_00100, named POSIX PSE51 Compliance. But that is not enough. The platform underneath must also be an MMU multi-process OS. MMU is the chip part that gives each process its own memory. That is the spec's virtual-memory rule, SWS_OSI_01010. It requires every Process to run in its own virtual address space, because Execution Management spawns processes from the manifest."

**Split into two groups, the OSes that can host AP (~22 sec):**
"Those two rules sort every kernel into two groups. On the side that can host AP, the production pair is QNX and Linux. QNX Neutrino is the production default. It has full POSIX, it was certified to PSE52, a larger POSIX profile, around 2008, and its ASIL-D comes through QNX OS for Safety. Linux and AGL are POSIX-conformant but not formally certified, so they are for development and QM builds. The capable-class also has Green Hills INTEGRITY, PikeOS, and VxWorks."

**The OSes that cannot host AP (~15 sec):**
"On the side that cannot host AP is everything with a task model. FreeRTOS, whose own README says a POSIX app cannot be ported using only this wrapper. SAFERTOS, which has no POSIX and ships as one static image. Zephyr and NuttX, which are MCU-class RTOSes. And AUTOSAR OS, which is Classic's own static real-time kernel."

**Close, one test (~5 sec):**
"The test is one question. Does this OS speak PSE51 and run MMU-isolated processes? If both are yes, it can host AP."

**Transition:**
"On top of that POSIX OS, AP builds its functional clusters. Let us look straight at the spec."

**Presentation tip:** Do not read every table row. The audience can read it. Just name the QNX and Linux pair and the one test. If someone asks why NuttX does not count, say it has an optional MMU kernel build but no fork or exec, so it is still MCU-class.

---

## Slide 9 — The functional clusters

**Target time: about 70 seconds.** This is a map slide. Read it as a map, not a checklist. Land on four clusters.

**Open, read it as a map (~20 sec):**
"This is the Adaptive platform taken straight from the spec. It is an unmodified figure. The source is AP_EXP_PlatformDesign, R25-11, Figure 4.1. Read it as a map, not as a checklist. R25-11 defines 20 functional clusters. Do not try to read all twenty."

**The four clusters that carry the talk (~40 sec):**
"You only need to point at four. Communication Management, which is ara::com, the Adaptive communication API, handles the talking between apps. Execution Management, which is ara::exec, starts the processes and manages their life cycle. Diagnostic Management, which is ara::diag, handles diagnostics. And Update and Config Management, which is ara::ucm, handles updates. Those four clusters carry the rest of the talk. The other sixteen or so clusters are out of scope for today."

**Close (~10 sec):**
"So when you look at this map, your eyes only need four boxes. com, exec, diag, and ucm."

**Transition:**
"Let us start with the most important one, and the one middleware people know best. ara::com."

**Presentation tip:** Really point at the four boxes when you name them. Keep "functional cluster" in English. Say "ara::com" as "a-ra com".

---

## Slide 10 — ara::com bindings

**Target time: about 80 seconds.** This is the core AP API slide. The takeaway is: the API does not depend on the protocol, and the binding is swappable underneath.

**Open, one proxy and skeleton API (~24 sec):**
"ara::com is one single API that does not depend on any protocol. It is built on a proxy and skeleton model. The app only writes code against that API. The integrator is the one who picks the wire binding, and they pick it in the manifest, not in the code."

**Three standardized bindings (~28 sec):**
"There are three standardized bindings. SOME/IP, which is a service network protocol over IP. Signal-Based. And DDS, which is a data-sharing middleware. DDS has been present since release R18-03. Look at the picture. The same API is on top, and swappable bindings are below it. Besides those three standardized ones, Local IPC is the reality inside one machine. But Local IPC is at the implementation level. It is not a standardized protocol between vendors."

**The transferable idea (~20 sec):**
"Here is the idea to take home. The API does not depend on the protocol, and the binding is swappable underneath. It is exactly like ROS 2's rmw over DDS. rmw is ROS 2's middleware wrapper layer. Anyone who has done ROS 2 will feel at home right away."

**Close (~8 sec):**
"One API, many bindings, chosen at integration time, not at code time. That is the whole spirit of ara::com."

**Transition:**
"Enough theory. Now let us open three real repositories, starting with a Classic stack written in C."

**Presentation tip:** If the audience has a ROS 2 background, the rmw comparison lands well. If not, you can drop it. Say "SOME/IP" as "some-eye-pee" and "DDS" as "D D S".

---

## Slide 11 — Inside repo 1 of 3, Fang717 arccore-core-21

**Target time: about 65 seconds.** The first repo slide. Introduce the structure, then say the honest provenance warning plainly.

**Open, what it is (~14 sec):**
"This is the first of three repositories worth reading, a Classic Platform stack in C. It is Arctic Core, a full vendor Basic Software stack. Its own README describes it: 'Arctic Core is an open-source implementation of the AUTOSAR (Automotive Open System Architecture) standard, designed for the development of automotive Electronic Control Units (ECUs).'"

**The directory tree (~26 sec):**
"Look at the tree. The core/communication folder holds the communication chain: Com, PduR the PDU router, CanIf the CAN interface, CanTp the transport protocol, and SoAd, plus a bundled lightweight TCP/IP stack, lwip-2.0.3. The core/system folder holds the static real-time OS kernel and the system services EcuM, BswM and SchM. The core/diagnostic folder holds the three UDS modules Dem, Dcm and Det. The modules stamp themselves as AUTOSAR 4.0.3 in a release macro. For example, Com.h sets COM_AR_RELEASE to 4, 0, 3. Hardware support is broad, and the MCU ports live under core/mcal/arch."

**The honest part, provenance warning (~22 sec):**
"Now the honest part, and you must say it plainly. This is an anonymous re-upload, by a GitHub user named Fang717, of a commercial-era vendor snapshot, Arctic Core version 21.0.0. It has no real development history. All 8,481 source files were added in one single 'Initial commit' in June 2024, and no later commit touches the code. The README says GPL-2.0, but there is no top-level LICENSE file, the GitHub API reports no license, and the per-file headers carry a dual notice instead, either a commercial ArcCore licence or GPL version 2. The code itself is old. The per-file copyright reads 2013 and 2014. So despite the 21.0.0 label and the 2024 upload, this is AUTOSAR 4.0.3-era code."

**Close (~3 sec):**
"Read it to see the shape of a real Classic stack. Do not read it for production."

**Transition:**
"Now let us open two functions in this stack and see what Classic C code looks like."

**Presentation tip:** The commit for this repo is 7874929. The provenance warning is required. Do not skip it. If someone asks "can we use it?", say: good for learning the architecture, not for a product.

---

## Slide 12 — The code 1 of 3, Classic in C

**Target time: about 65 seconds.** This is a code slide. Follow the "What to notice" order and name the identifiers exactly.

**Open, the Com_SendSignal function (~30 sec):**
"These are two real functions from the Arctic Core stack. The first is Com_SendSignal. It is the COM service a task calls to publish an application signal, which COM later packs into an I-PDU on the bus. Notice this. It returns a uint8 that the vendor typedef'd, and it takes a Com_SignalIdType, not a bare C type. So the module behaves the same on every MCU. Before it does any work, it checks that COM was initialized, with the test COM_INIT is not equal to Com_GetStatus. If not, it reports a development-time error through the DET, using DET_REPORTERROR, and returns the code COM_SERVICE_NOT_AVAILABLE, instead of touching uninitialized config. The comment tagged @req COM334 links this exact line to a numbered clause in the AUTOSAR COM spec. And that requirement-to-code traceability runs through the whole stack."

**The component talks only through the RTE (~35 sec):**
"The second snippet is an application software component. It never calls the Basic Software directly. It only uses the generated Rte_ functions. Rte_IRead and Rte_IWrite move port data. Here, Rte_IWrite_SwcWriterRunnable_SenderPort_data1 writes out, and Rte_IRead_SwcWriterRunnable_InputPort_data1 reads in. And Rte_Call invokes a client-server operation, here Rte_Call_Blinker_Write. So the component stays fully independent of the hardware and the bus. Even asking the network to wake up is done through the RTE. The SwcWriterInit function requests full communication from the ComM module, using Rte_IWrite_Init_ComMControl_requestedMode with the value COMM_FULL_COMMUNICATION. Those long Rte_ names are produced by the RTE generator from the ECU config. Nobody types them by hand. That is the heart of the config-driven Classic style."

**Transition:**
"The same idea now, but in a different Classic stack, rewritten from scratch by one person."

**Presentation tip:** Say "@req COM334" as "req COM three three four". This is a code slide, so point along the lines as you name the functions. If someone asks why the Rte_ names are so long, say the generator joins the runnable name, the port name and the data element name into one.

---

## Slide 13 — ArcCore and Arctic Core history

**Target time: about 50 seconds.** A short history slide. Say the company, the acquisition, and where the code is today.

**Open, the ArcCore company (~18 sec):**
"A quick history. A Swedish company, ArcCore AB, also written ARCCORE, was founded in 2006 in Gothenburg, Sweden. From 2009 it focused on the AUTOSAR standard. Its product was Arctic Core, an open-source Classic AUTOSAR Basic Software stack written in C. It was sold next to Arctic Studio, the commercial configuration toolchain that generates the RTE. The licensing was open-core, which means a GPL-2.0 core plus commercial licences. The source lived in a Mercurial repository at my.arccore.com."

**The Vector acquisition (~14 sec):**
"In 2018, Vector Informatik, based in Stuttgart, Germany, acquired ARCCORE, effective the 11th of July, 2018. At that time ARCCORE had about 80 employees, and its chief executive and co-founder was Michael Svenstam."

**Where the code is today (~18 sec):**
"Today the original ARCCORE servers are offline, checked on the 20th of July, 2026. The open-source code survives only as dormant community mirrors on GitHub. The largest is openAUTOSAR/classic-platform, which is GPL-2.0, has 664 stars, and had its last code push in August 2024. This deck reads Fang717/arccore-core-21, the 2024 re-upload of the version 21.0.0 snapshot, which is mostly 4.0.3-era, mixed-vintage code with no real development history."

**Transition:**
"So if your team wants to reuse this tree, what does it give you, and what stays your job?"

**Presentation tip:** Say "Michael Svenstam" clearly, and read the dates out in full. Open-core just means an open-source core sold next to paid commercial licences.

---

## Slide 14 — Reading repo 1 of 3

**Target time: about 60 seconds.** A practical slide for a chip or ECU team. Read the tree as two lists: what you reuse, and what stays your job.

**Open, two lists (~8 sec):**
"Now the practical question, read straight off the tree. Read it as two lists. The directories you can reuse as they are, and the work that stays yours."

**The reuse side (~26 sec):**
"On the reuse side. The communication, system and diagnostic folders are the hardware-independent upper Basic Software. They sit above the MCAL line, which is the lowest driver layer. So they are portable, and they give you a working reference on any silicon. The mcal and mcal/arch folders are driver skeletons. If your part is a listed family, such as mpc5xxx, rh850_x, stm32 or tms570, you reuse them directly. If it is not, they are the exact contract your own driver must meet. The generic Linux sim target lets you run the upper stack on a PC for early bring-up, before any silicon driver exists. And the boards and examples folders are integration templates, from config to build to run."

**The build side (~26 sec):**
"On the build side, the work that stays yours. You still write the MCAL for your own silicon when it is not a listed family: Mcu, Port, Dio, Can, Adc, Spi, Pwm, Wdg and Gpt against your registers. You write your board and ECU config in ARXML, the clock tree, the pin multiplexing, the memory map and the ECU extract, which is not in this tree. You do the RTE and BSW generation and integration, an Arctic Studio equivalent, because the tree is source, not a generated system. You port it forward from this 4.0.3-era snapshot to a current release, such as R21-11, R22-11 or R24-11. And you own the functional-safety case plus the licence and IP clearance, because this code is GPL, uncertified and anonymously sourced. Reaching ASIL-D means a certified stack, or carrying the whole ISO 26262 case yourself."

**Transition:**
"Now the second repository, a very different Classic stack."

**Presentation tip:** Frame it as reuse versus build. The key honest line is the last one: the safety case, the GPL copyleft, the missing LICENSE file and the unknown source are all yours to resolve.

---

## Slide 15 — Inside repo 2 of 3, autoas/as

**Target time: about 65 seconds.** The second repo slide. A stack written from scratch by one person, with a warning about the inconsistent licence.

**Open, how it differs (~16 sec):**
"The second repository is autoas/as, a very different Classic stack. Where Arctic Core is an anonymous re-upload of a commercial snapshot, this one is written from scratch by one person. It is a Classic AUTOSAR 4.4 Basic Software stack, mostly in C, with the modules under infras. The author's README says it plainly: 'This project is only free to be used for evaluation and study purpose, all of the BSWs are developed by me alone according to AUTOSAR 4.4.'"

**Scope and tooling (~33 sec):**
"The scope is broad. The communication chain has Com, PduR, CanIf, CanTp, and also SomeIp and Sd, which is service discovery, plus LinIf. The diagnostics have Dcm, Dem and Det. The memory services have NvM, Fee and Ea. Crypto is Csm. The MCAL drivers include Can, Dio, Fls, Lin and Port. And there is a static, fixed-priority real-time OS kernel with tasks, alarms, counters and resources, under infras/system/kernel/os. Unlike a bare stack, this one also has desktop tooling. tools/generator is a per-module Python config generator, like Com.py, Dcm.py, CanTp.py and about forty more. tools/asone is a QT graphical tool for Com, Dcm and the flash loader. It also has a bootloader and CAN or LIN bus simulators over IP sockets. The whole tree builds with SCons."

**The honest part, inconsistent licence (~16 sec):**
"Now the part you must say plainly. This is one person's project. The history shows a single maintainer, and the README says the modules were developed by the author alone. The AUTOSAR 4.4 label is the author's claim, not a verified or certified result. So treat it as AUTOSAR-style, not compliant. The licence is also internally inconsistent. The LICENSE file declares a dual GPLv3-or-commercial grant, while the README restricts use to evaluation and study only, and GitHub reports the licence as 'Other'. Some paths are still works in progress."

**Transition:**
"Let us open the code: the same Com_SendSignal, but rewritten independently, plus a slice inside the OS kernel."

**Presentation tip:** The commit is bfe1805. The licence inconsistency is a required point, so do not skip it. If someone asks whether it runs on a real car, say no, it is academic, so read it as AUTOSAR-style.

---

## Slide 16 — The code 2 of 3, autoas/as

**Target time: about 65 seconds.** A code slide. The COM function rewritten independently, and the priority-ceiling slice inside GetResource.

**Open, same function, different author (~30 sec):**
"The same idea now, in the from-scratch stack. The first function is Com_SendSignal again, but written independently. Because it is a public AUTOSAR service, it returns Std_ReturnType, the standard E_OK or E_NOT_OK contract. And it sets the variable ret to failure first, to E_NOT_OK, so the caller sees an error unless the send really succeeds. The three DET_VALIDATE lines are the Classic development-error guards, all tagged with COM's service id 0x0A. They reject an uninitialized module, with the test NULL is not equal to COM_CONFIG returning COM_E_UNINIT. They reject an out-of-range signal id, with SignalId less than COM_CONFIG->numOfSignals returning COM_E_PARAM. And they reject a NULL data pointer, returning COM_E_PARAM_POINTER. If any check fails, it returns early. Then the signal is fetched by index from a generated, read-only config table, COM_CONFIG->SignalConfigs. That is the config-driven pattern again."

**The priority-ceiling slice inside GetResource (~35 sec):**
"The second snippet is a slice from inside the GetResource function in the OS kernel. It is the priority-ceiling protocol. When a task takes a resource, its running priority is raised up to that resource's statically configured ceiling. If RunningVar->priority is less than ResourceConstArray[ResID].ceilPrio, then priority is set to ceilPrio. This is how the kernel prevents priority inversion and deadlock without ever blocking at runtime. The previous priority and the previously held resource are saved first, in prevPrio and prevRes, so nested resource pairs unwind like a stack, strictly last-in first-out. The whole update runs inside EnterCritical and ExitCritical with interrupts masked, because it changes shared scheduler state. And it only applies in task context, with the test TCL_TASK equals CallLevel, not inside an interrupt handler."

**Transition:**
"That is the end of the Classic side. Now the third repository, an Adaptive teaching codebase."

**Presentation tip:** Say "0x0A" as "zero x zero A". Keep "priority ceiling" in English. If someone asks why it does not block, say the ceiling is computed statically ahead of time, so raising the priority is enough to stop inversion.

---

## Slide 17 — Inside repo 3 of 3, langroodi Adaptive-AUTOSAR

**Target time: about 65 seconds.** The Adaptive repo slide. A teaching codebase. Show the reading path, and two honest limits.

**Open, start with the README (~18 sec):**
"This is the third repository worth your time, langroodi/Adaptive-AUTOSAR, and it is a teaching codebase. The README states the goal: 'The goal of this project is to implement the interfaces defined by the standard for educational purposes.' Start with the README. It says in one paragraph what the project is, and it lists the exact build, test and run commands."

**The reading path (~29 sec):**
"Then open main.cpp. It is only about fifty-five lines. It builds Execution Management, spins a polling loop, and passes in the manifests. The header to study is execution_client.h. It shows an app reporting its state to Execution Management. And its private members reveal that the call is really a SOME/IP RPC, which is a remote procedure call, not a generated ara::com proxy. CMakeLists.txt pins C++14, fetches GoogleTest, and defines the executable plus two test targets. Under src/ara there are seven AP interface clusters: com, core, diag, exec, plus log, phm and sm. To run it: configure and build with CMake using GCC or Clang, run the unit tests with ctest, then launch by passing in four .arxml manifest files."

**Two honest limits (~18 sec):**
"Two limits you must say plainly. One, the demo is not offline. It needs a Volvo API key, an OAuth 2.0 token, which is a standard access token, and live network access to call the Volvo Extended Vehicle REST API. Two, the code stops at the SOME/IP transport level, with no generated ara::com Proxy/Skeleton facade. And it is dormant, with its last source commit on the 22nd of June, 2023. The license is MIT. Read it for the shape, not for production."

**Transition:**
"Let us open two C++ snippets in this repo and see how the Adaptive platform layer is wired together."

**Presentation tip:** The commit is 866d158. Say "OAuth" as "oh-auth". If someone asks why the demo needs Volvo, say it demonstrates calling out to a real vehicle backend, not a pure simulation.

---

## Slide 18 — The code 3 of 3, Adaptive C++

**Target time: about 65 seconds.** A C++ code slide. The shape of the RpcClient class, then how Execution Management is composed.

**Open, the RpcClient class (~30 sec):**
"Now the same platform layer, in the Adaptive teaching repo. The first snippet is the shape of a class. RpcClient is the abstract SOME/IP request-and-response client that all the wiring is built on. Its public HandlerType is just a std::function that takes a decoded message, of type SomeIpRpcMessage. Its private state is two maps, keyed by a service and method id packed into a uint32_t. One map, mSessionIds, tracks the session id per method. The other map, mHandlers, holds the registered response handlers. The class is deliberately transport-agnostic, so a concrete subclass, such as SocketRpcClient, supplies the real send."

**Composing Execution Management (~28 sec):**
"The second snippet is the Execution Management entry point. A concrete SocketRpcServer is built from the parsed RPC config: the ipAddress, the portNumber and the protocolVersion. Then that server is handed by pointer into an ara::exec::ExecutionServer. So the execution server talks to clients only through the abstract SOME/IP RPC layer. The last lines load the function-group states and the initial state from the ARXML model, using the fillStates function. That config-driven, model-first style runs through the whole codebase."

**Close (~7 sec):**
"Notice the common point. The config comes from ARXML, and the communication goes through an abstract RPC layer that is swappable underneath. It is exactly the spirit of ara::com from the earlier slide."

**Transition:**
"One more piece. Where is the surface that the spec itself names, and what is the honest boundary of this whole code tour?"

**Presentation tip:** Say "RPC" as "R P C". If someone asks why it uses a pointer, say it lets the execution server not depend on the transport type, and only see the abstract interface.

---

## Slide 19 — The shape of the code

**Target time: about 58 seconds.** This closes the code part. The spec-named surface, how AP reports errors, and the honest boundary about CAPI.

**Open, the standardized surface (~16 sec):**
"This is the shape of real ara:: code from a public repo. Start with the standardized surface. The spec names the ara::com event-send API: Send of a sample-derived type, and Send of an ara::com::SampleAllocateePtr. That is in AP_SWS_CommunicationManagement, R25-11, section 8.4.2.2.2. It is the contract vendors have to implement."

**How AP reports errors (~22 sec):**
"Now look at the code. The ReportExecutionState function returns an ara::core::Result of void, not a thrown exception. Adaptive signals errors as a returned value, not as a thrown exception. And it is the contract every Adaptive Application implements, so Execution Management knows it reached the kRunning state. On the ara::com side, the skeleton's offer lifecycle is also spec-named: OfferService and StopOfferService on the ServiceSkeleton class, from SWS_CM_00101 and SWS_CM_00111, in the same document. One educational caveat. This C++ repo has been dormant since the 22nd of June, 2023, so inactive for 3 years. Read it for the shape, not for production."

**The honest boundary (~20 sec):**
"And here is the honest boundary for the whole code tour. The building blocks and the teaching code are open. But a complete, conformant, open AP stack does not exist. The one complete official implementation, named CAPI, which is the Common Adaptive Platform Implementation, is gated to AUTOSAR partners only."

**Transition:**
"Enough code. Now let us put Classic and Adaptive side by side in one table, seven rows."

**Presentation tip:** Say "CAPI" as "cap-ee". It stands for Common Adaptive Platform Implementation. The line "a complete, open AP stack does not exist" is the honest closing point, so say it clearly.

---

## Slide 20 — CP vs AP, the split that matters

**Target time: about 75 seconds.** A seven-row table. Read it as matching pairs, keep the rhythm, do not get stuck on one row.

**Open, the first three rows (~28 sec):**
"This is the most important split, with seven rows. Target row: on one side, deeply-embedded MCUs such as Infineon AURIX, NXP S32K and Renesas RH850. On the other side, HPC SoCs such as NVIDIA Orin and Thor, Qualcomm, NXP S32G and Renesas R-Car. OS row: on one side, AUTOSAR OS, a static real-time kernel, classes SC1 to SC4, no MMU. On the other side, not a new OS, but an OS Interface on POSIX PSE51, over Linux, QNX or PikeOS. Model row: on one side, fully static, C, the generated Rte_Read, Write and Call, one binary. On the other side, dynamic, C++14, the ara:: namespaces, manifests bound late, with discovery and start-stop at runtime."

**The last four rows (~35 sec):**
"Comms row: on one side, signal-oriented, COM packs signals into I-PDUs on CAN, LIN, FlexRay or Ethernet. On the other side, service-oriented, ara::com proxy and skeleton over SOME/IP or DDS. Diagnostics row: on one side, DCM plus DEM, UDS over DoCAN, which is diagnostics over CAN, or DoIP, which is diagnostics over Ethernet. On the other side, one DM cluster, which is ara::diag, both a UDS server and SOVD, which is Service-Oriented Vehicle Diagnostics, and DoIP is the only standardized transport, though a custom one is permitted. Updates row: on one side, reflash the whole ECU through the bootloader and UDS, that is 0x34, 0x36 and 0x37. On the other side, UCM, install or update individual Software Clusters, OTA-native. Safety row: on one side, mature ISO 26262 up to ASIL D, first certified in 2016. On the other side, 'up to ASIL D' on paper, harder in practice, with ASIL-B shipping and ASIL-D underway."

**Close, Classic is not CAN-only (~12 sec):**
"One point people get wrong. Classic is not CAN-only. A standardized SOME/IP Transformer has shipped since release 4.2.1, in October 2014, years before Adaptive's first release."

**Transition:**
"The table shows the difference. The next slide shows why the two still have to live together."

**Presentation tip:** Keep an even rhythm, one breath per row. Say "SOVD" as "S O V D", which is Service-Oriented Vehicle Diagnostics. If someone asks about AP's ASIL-D, say: no fully-certified end-to-end ASIL-D AP middleware ships as of mid-2026. ASIL-D lives in the OS, such as QNX, plus a hypervisor, plus the vendor's safety case.

---

## Slide 21 — Coexistence

**Target time: about 75 seconds.** A spec figure slide. Point at the two regions and the bypass arrows. Close with the spec sentence.

**Open, Region A (~22 sec):**
"Coexistence, straight from the spec. One figure, two platforms. The source is AP_EXP_PlatformDesign, R25-11, Figure 3.2. Region A, the blue tag, is the Adaptive Platform on the high-performance computer. This is the high-level compute side. It perceives the environment, the driver and the vehicle state. It fuses them into one environment and state model. Then it runs the maneuver and trajectory planning, which is planning the moves and the path."

**Region C (~20 sec):**
"Region C, the boxes on the left and along the bottom, with the teal tag, is the Classic Platform side. This is the fast control side. It groups the sensor-input boxes: camera, radar and lidar, then inertial, odometry and GPS, then C2C and C2I, which are car-to-car and car-to-infrastructure. It also holds the trajectory-control box with its safety function at the bottom."

**The key point, the bypass arrows (~23 sec):**
"Now the point that matters most. Watch the arrows leaving the sensor boxes. Some run up to perception in Region A. But some run straight down into the safety function, and they bypass Region A entirely. The safety side keeps its own sensor feed. So the safe path does not depend on the planning path. If the HPC fails, the wheels stay safe."

**Close, the spec sentence (~10 sec):**
"And the spec says it plainly. AP 'will not replace CP'. The two 'interact to form an integrated system', in section 3.4. A modern software-defined vehicle runs both platforms at once, joined by Ethernet and gateways. Coexistence is the designed architecture, not legacy baggage."

**Transition:**
"So which one do you pick for your silicon? There is a procurement table that answers it."

**Presentation tip:** Really point at the bypass arrows. That is the strongest visual idea on the slide. If someone asks whether the safety island is on the figure, say this figure is at the logical level, and the silicon detail is on the next decision table.

---

## Slide 22 — Which stack on which silicon

**Target time: about 85 seconds.** A procurement table, the whole deck in one table. Let the audience find their own silicon row.

**Open, how to use the table (~10 sec):**
"This is the whole deck in one procurement table. It shows what runs where, and who sells it. Your job is simple. Find your own silicon row."

**Walk through the five rows (~55 sec):**
"The A-core SoC row, such as DRIVE Orin and Thor guest, NXP S32G and S32N, or R-Car: it runs QNX or Linux plus an AP stack, or a non-AUTOSAR middleware, the Rivian path. For AP suppliers, there are Vector, Elektrobit with corbos, ETAS RTA-VRTE, and Qorix. The OS underneath is a separate procurement. The safety island on the SoC row, a lockstep Cortex-R52 such as the Thor FSI: it runs vendor safety firmware, plus a Vector FSI reference integration on Thor. The suppliers are NVIDIA FSI firmware and Vector. Note that Vector's MICROSAR Classic up-to-ASIL-D reference targets the companion MCU, not the island. The companion or safety MCU row, such as RH850 in the Thor generation or AURIX in the Orin generation: it runs Classic, and the suppliers are Vector AFW and the NVIDIA reference integration. The zonal or domain MCU row, such as NXP S32Z and S32E, AURIX and RH850: it runs Classic, from Tier-1 Classic stacks, MICROSAR or the EB tresos class. The small edge ECU row, the S32K class: it runs Classic or bare-metal on an RTOS, from Tier-1 stacks or in-house."

**Close, the business rule (~20 sec):**
"Underneath all of it is the business rule from the start. AUTOSAR value scales with how many organizational boundaries your software crosses. Vertically-integrated OEMs such as Rivian skip it. And Tier-1s implement it to win the OEM's RFQ."

**Transition:**
"That is the inside of the car by silicon. Now let us follow the one diagnostic language that both platforms speak."

**Presentation tip:** This is a "screenshot" slide for a manager. Invite the audience to find their row before you read it. Say "FSI" as "F S I", Functional Safety Island. The vendor cells are only examples, not a full market list.

---

## Slide 23 — UDS (ISO 14229)

**Target time: about 70 seconds.** One diagnostic language, two transports, two platform homes. This is the diagnostics deep-dive.

**Open, the UDS language (~24 sec):**
"UDS is the request-and-response diagnostic language. UDS is the standard diagnostic language, defined by ISO 14229-1. Both AUTOSAR platforms speak it. A workshop tester, or a fleet backend reaching in through a gateway, sends the same service bytes to any target. So the language is one, and the target does not change it."

**Two transports (~18 sec):**
"The same service bytes ride two transports. DoCAN, which is diagnostics over CAN, carries them with CanTp, from ISO 15765-2, over CAN or CAN FD. DoIP, which is diagnostics over Ethernet, from ISO 13400, carries them over automotive Ethernet. Same bytes, two roads."

**Two platform homes (~28 sec):**
"Diagnostics have two platform homes. On Classic, the DCM dispatches the services, and the DEM stores the DTCs, the fault codes. On Adaptive, the Diagnostic Manager, which is ara::diag, serves DoIP only, with one diagnostic server per Software Cluster. So the point to remember is this. The bytes 22 F1 90 read the VIN, the Vehicle Identification Number, on a small body ECU over CAN, or on a central computer over Ethernet. The exact same bytes, both times. Here F1 90 is a DID, a Data Identifier, which is a numeric address for one data item."

**Transition:**
"Now let us zoom out and see the whole fleet and diagnostics flow in one picture."

**Presentation tip:** Say "22 F1 90" as "two two, F one ninety". Say "DoIP" as "doh-I-P" and "DoCAN" as "doh-can". If someone wants the full UDS service list, defer to the full 73-slide deck rather than listing them here.

---

## Slide 24 — Fleet and diagnostics in one picture

**Target time: about 75 seconds.** A diagram slide. Outside the car and inside the car, and the boundary that raw UDS never reaches the internet.

**Open, outside the car (~30 sec):**
"Here is fleet and diagnostics in one picture. Look outside the car first. The backend speaks SOVD, which is Service-Oriented Vehicle Diagnostics, that is REST and JSON over HTTPS, plus MQTT telemetry. It never uses raw UDS. The vehicle's entry point is the TCU, the telematics unit that connects the car to the outside network."

**Inside the car (~35 sec):**
"Now look inside the car. The central gateway is a DoIP router and a firewall. It routes DoIP and UDS on the backbone. It re-transports from DoIP down to DoCAN, to reach the Classic branches. And here is the most important boundary on this slide. Raw UDS is never exposed to the internet. The backend only speaks the safe web languages, and the gateway is the place that translates down to UDS inside the car."

**Close (~10 sec):**
"So remember two layers. Outside is SOVD and MQTT on the web. Inside is DoIP down to DoCAN. And a firewall sits in between. UDS stays inside the car."

**Transition:**
"That is diagnostics inside one car. Now let us step back and compare the car world with the robot world you come from."

**Presentation tip:** Say "DoIP" as "doh-I-P" and "DoCAN" as "doh-can". The security point, that raw UDS never reaches the internet, is worth stressing. Managers and security people ask about it.

---

## Slide 25 — Fleet standards, robots vs cars

**Target time: about 70 seconds.** This is the bridge back to robotics. Read it as an asymmetry, not a scoreboard.

**Open, robots standardized orchestration (~24 sec):**
"This is the bridge back to the robotics world you come from. Read it as an asymmetry, not a scoreboard. Robots standardized fleet orchestration. VDA 5050 is the wire protocol between a fleet manager and mobile robots, using MQTT and JSON. Open-RMF is the coordinator above it. And MassRobotics covers cross-fleet state sharing. Cars leave that dispatch layer operator-proprietary, with no cross-maker standard."

**Cars standardized diagnostics and updates (~22 sec):**
"Cars standardized the other half. That is diagnostics, updates and the platform itself. UDS from ISO 14229, SOVD from ISO 17978, UCM which is AUTOSAR update management, and AUTOSAR itself all come from the car world. Robots leave those to ROS 2 conventions and vendor tooling. So each side built exactly the standard the other side skipped."

**The shared gap (~24 sec):**
"And here is the gap they share. Neither side has a UDS-DID-style dictionary for semantic capability and sensor discovery. There is no standard way to ask, in a semantic form, what a machine can actually sense and do. Cars have a numeric DID for one data item, but not a full capability dictionary. Robots do not have it either. That gap is open on both sides."

**Transition:**
"Now let us pull all of this into one decision tree: how to pick a stack for a specific ECU."

**Presentation tip:** Say "VDA 5050" as "V D A fifty-fifty". This is the slide that speaks to a ROS 2 audience, so slow down and make the robot-versus-car point clear. AMR means autonomous mobile robot, and AGV means automated guided vehicle.

---

## Slide 26 — Choosing your stack, the decision tree

**Target time: about 95 seconds.** The longest slide. Follow two questions: the MCU branch first, then the HPC branch, then the proof.

**Open, two questions (~12 sec):**
"Two questions pick your stack, and on the MCU side the first fork is safety. Question one: where does this function run? If it is a deeply-embedded MCU, then question two is: what safety level must this ECU carry, and who is the customer?"

**The MCU branch, selling to an OEM (~18 sec):**
"If it carries an ASIL level and you sell it to an OEM, the choice is already made for you. The RFQ demands AUTOSAR plus ASIL evidence. So you buy Classic with a pre-certified base, for example MICROSAR Safe."

**The MCU branch, your own product (~25 sec):**
"If it carries an ASIL level but it is your own product, there are two honest options. One, still buy Classic, to get the certified base, the vendor drivers and the already-solved modules. Two, take a certified non-AUTOSAR RTOS, for example SAFERTOS, and carry the whole ISO 26262 safety case yourself. That is the Rivian path, and it needs a real safety team. And if the ECU is only QM, with no certificate needed, then anything goes."

**The HPC branch (~22 sec):**
"Now the HPC branch. Here the safety story lives in the certified OS, in the hypervisor, in the safety island, and in the companion MCU. And that companion MCU runs Classic. So the only remaining question on the HPC side is about supplier interop. Buy an AP stack if you need the standardized endpoints. Otherwise use S-CORE, or build your own."

**Close, the proof (~18 sec):**
"The orange bar still holds. Every outcome meets the same fleet contracts. And the proof that build-your-own works is real. Tesla fleet-telemetry shows the car as a client, pushing protobuf, a compact binary message format, over a WebSocket, a long-lived web connection, secured with mTLS, where both sides check each other. There is no SOME/IP, no DDS and no DoIP in that path. And Rivian is on record: 'We don't use any of the industry offerings such as AUTOSAR.' Skipping AUTOSAR only forfeits the pre-built in-vehicle endpoints. It never costs you fleet reachability."

**Transition:**
"Let us wrap it up into three takeaways."

**Presentation tip:** This is the densest slide. Keep the rhythm and follow the diagram. Say "S-CORE" as "S core". If someone asks whether Tesla uses AUTOSAR, say: not on the fleet-telemetry path, where they use protobuf over WebSocket and mTLS.

---

## Slide 27 — Three takeaways

**Target time: about 65 seconds.** The closing summary. Three short points, stressed one at a time.

**Open, takeaway one (~22 sec):**
"Three takeaways. One. AUTOSAR is a supply-chain standard. Its value scales with how many organizational boundaries your software crosses. And remember this well. ASIL comes from ISO 26262, not from AUTOSAR."

**Takeaway two (~25 sec):**
"Two. Two platforms, coexisting by design. Classic is static. It has a mature ISO 26262 path up to ASIL D, first certified in 2016. And it runs on MCUs. Adaptive is a service platform on POSIX, and it runs on HPCs. This is a designed hierarchy, not legacy baggage."

**Takeaway three (~15 sec):**
"Three. Find your own silicon row on the decision map. Once you find it, you know the stack, you know the OS question, and you know who sells it."

**Close (~3 sec):**
"Those three sentences are the whole thirty minutes."

**Transition:**
"Last slide: where to dig deeper, and then your questions."

**Presentation tip:** These are three sentences for the audience to write down, so say them slowly and separately. The line "ASIL comes from ISO 26262, not from AUTOSAR" is the most memorable message, so stress it.

---

## Slide 28 — Q&A and where to dig deeper

**Target time: about 35 seconds.** The closing slide. Point to the deeper sources, note the licensing, then open for questions.

**Open, three sources to dig deeper (~20 sec):**
"To go deeper, there are three places. The full 73-slide deck is at autosar/slides/autosar-deck.md. It expands every point from today with the primary-source references. The local spec mirror is at autosar/specs. It holds all 35 R25-11 PDFs, covering Foundation, Classic and Adaptive. And the research docs and blog live under autosar, split into Classic, Adaptive, and Classic-vs-Adaptive."

**Licensing note and open for questions (~15 sec):**
"One note on licensing. The spec figures are reproduced unmodified, copyright AUTOSAR R25-11. The adapted diagrams are redrawn after the cited figures, not copied from the spec artwork. Thank you all. Now let us go to questions."

**Presentation tip:** This is the stop point for questions. The plan leaves about no spare buffer inside the 30-minute frame, so if the talk started late, keep Q&A short. If a question needs deep detail, point the person to the exact slide in the full 73-slide deck instead of answering at length here.
