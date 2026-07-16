---
marp: true
paginate: true
theme: default
style: |
  section { font-size: 26px; }
  h1 { color: #1b2b4a; }
  h2 { color: #2E5FAC; }
  table { font-size: 22px; }
  code { background: #eef2f8; }
  section.lead h1 { font-size: 50px; }
  section.lead h2 { color: #5b7bb0; font-weight: 500; }
  section.diagram { display: flex; align-items: center; justify-content: center; padding: 14px; }
  section.diagram img { height: 650px; width: auto; max-width: 100%; }
  .cmd { display:inline-block; background:#11233f; color:#e8eefc; padding:8px 16px;
         border-radius:8px; font-family:monospace; font-size:22px; margin:4px 0; }
  .ok { color:#2e7d32; font-weight:bold; }
  .bad { color:#c62828; font-weight:bold; }
  .gloss { font-size:17px; color:#66708a; border-top:1px solid #dde3ee;
           margin-top:16px; padding-top:6px; }
---

<!-- _class: lead -->

# AUTOSAR for firmware engineers — 2026

## one organization · two platforms · one vehicle

A field guide for embedded engineers who know MCUs, CAN, an RTOS and bare-metal
reflashing — and are new to automotive software platforms. Release-stamped to
**AUTOSAR R25-11** (published 2025-11-27). External claims are URL-sourced —
**references at the end.**

---

## Agenda

1. **One org, three standards** — history, governance, the FO / CP / AP split, the release timeline
2. **Classic Platform** — the statically-configured RTOS stack you half-know: RTE/VFB, AUTOSAR OS, ARXML, the signal path, E2E/SecOC, DCM/DEM, NvM/WdgM, functional safety
3. **Adaptive Platform** — the POSIX/C++ service platform on the "big chip": function clusters, EM/SM, `ara::com`, SOME/IP vs DDS, UCM OTA, DM/SOVD, PHM, vendors & ASIL reality
4. **Head-to-head & coexistence** — one vehicle running both, the R25-11 convergence, where ROS 2 sits, what it means for our team

<div class="gloss">AUTOSAR = AUTomotive Open System ARchitecture · FO = Foundation · CP = Classic Platform · AP = Adaptive Platform · RTE = Runtime Environment · VFB = Virtual Functional Bus · UDS = Unified Diagnostic Services (ISO 14229) · SOVD = Service-Oriented Vehicle Diagnostics · full expansions on the glossary slide near the end</div>

---

<!-- _class: lead -->

# Part 0
## one organization, three standards

---

<!-- _class: diagram -->

<img alt="autosar-timeline" src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA5NjAgNjIwIiB3aWR0aD0iOTYwIiBoZWlnaHQ9IjYyMCIgZm9udC1mYW1pbHk9IkhlbHZldGljYSwgQXJpYWwsIHNhbnMtc2VyaWYiPgogIDxyZWN0IHg9IjAiIHk9IjAiIHdpZHRoPSI5NjAiIGhlaWdodD0iNjIwIiBmaWxsPSIjZmZmZmZmIi8+CgogIDxkZWZzPgogICAgPG1hcmtlciBpZD0iYXJyIiBtYXJrZXJXaWR0aD0iMTAiIG1hcmtlckhlaWdodD0iMTAiIHJlZlg9IjgiIHJlZlk9IjMiIG9yaWVudD0iYXV0byIgbWFya2VyVW5pdHM9InN0cm9rZVdpZHRoIj4KICAgICAgPHBhdGggZD0iTTAsMCBMOSwzIEwwLDYgeiIgZmlsbD0iIzQ0NCIvPgogICAgPC9tYXJrZXI+CiAgPC9kZWZzPgoKICA8IS0tIFRpdGxlIC0tPgogIDx0ZXh0IHg9IjQ4MCIgeT0iMzgiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMjYiIGZvbnQtd2VpZ2h0PSI3MDAiIGZpbGw9IiMxYjJiNGEiPkFVVE9TQVIgYXQgYSBnbGFuY2Ug4oCUIHRocmVlIHJlbGVhc2UgbGluZXMgdGhhdCBtZXJnZWQgaW50byBvbmU8L3RleHQ+CgogIDwhLS0gPT09PT09PT09PT09PT09PT09PT09IEZvdW5kaW5nIGNvbHVtbiAobGVmdCkgPT09PT09PT09PT09PT09PT09PT09IC0tPgogIDx0ZXh0IHg9IjEwNCIgeT0iNjIiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTEiIGZvbnQtd2VpZ2h0PSI3MDAiIGZpbGw9IiM0NDQiPkZvdW5kaW5nIDIwMDLigJMyMDAzPC90ZXh0PgoKICA8cmVjdCB4PSIxMCIgeT0iNjgiIHdpZHRoPSIxODgiIGhlaWdodD0iNjgiIHJ4PSI2IiBmaWxsPSIjRUNFQ0VDIiBzdHJva2U9IiNCMEIwQjAiIHN0cm9rZS13aWR0aD0iMS4yIi8+CiAgPHRleHQgeD0iMTA0IiB5PSI4MyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSI4LjUiIGZvbnQtd2VpZ2h0PSI3MDAiIGZpbGw9IiMzMzMiPjIwMDIg4oCUIGZvdW5kaW5nIGRpc2N1c3Npb25zPC90ZXh0PgogIDx0ZXh0IHg9IjEwNCIgeT0iOTUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iOC41IiBmaWxsPSIjMzMzIj4mYW1wOyBraWNrLW9mZiB3b3Jrc2hvcDwvdGV4dD4KICA8dGV4dCB4PSIxMDQiIHk9IjEwOCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSI3LjUiIGZpbGw9IiMzMzMiPkJNVyDCtyBCb3NjaCDCtyBDb250aW5lbnRhbCDCtzwvdGV4dD4KICA8dGV4dCB4PSIxMDQiIHk9IjExOCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSI3LjUiIGZpbGw9IiMzMzMiPkRhaW1sZXJDaHJ5c2xlciDCtyBWVzs8L3RleHQ+CiAgPHRleHQgeD0iMTA0IiB5PSIxMjgiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iNy41IiBmaWxsPSIjMzMzIj5TaWVtZW5zIFZETyBzb29uIGFmdGVyPC90ZXh0PgoKICA8cmVjdCB4PSIxMCIgeT0iMTQyIiB3aWR0aD0iMTg4IiBoZWlnaHQ9IjM2IiByeD0iNiIgZmlsbD0iI0VDRUNFQyIgc3Ryb2tlPSIjQjBCMEIwIiBzdHJva2Utd2lkdGg9IjEuMiIvPgogIDx0ZXh0IHg9IjEwNCIgeT0iMTU4IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjgiIGZpbGw9IiMzMzMiPkp1bCAyMDAzIOKAlCBJbml0aWFsIERldmVsb3BtZW50PC90ZXh0PgogIDx0ZXh0IHg9IjEwNCIgeT0iMTcwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjgiIGZpbGw9IiMzMzMiPkFncmVlbWVudCBzaWduZWQ8L3RleHQ+CgogIDxyZWN0IHg9IjEwIiB5PSIxODQiIHdpZHRoPSIxODgiIGhlaWdodD0iMzYiIHJ4PSI2IiBmaWxsPSIjRUNFQ0VDIiBzdHJva2U9IiNCMEIwQjAiIHN0cm9rZS13aWR0aD0iMS4yIi8+CiAgPHRleHQgeD0iMTA0IiB5PSIyMDAiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iOCIgZmlsbD0iIzMzMyI+U2VwIDIwMDMg4oCUIHB1YmxpYyBkZWJ1dCwgVkRJPC90ZXh0PgogIDx0ZXh0IHg9IjEwNCIgeT0iMjEyIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjgiIGZpbGw9IiMzMzMiPkNvbmZlcmVuY2UsIEJhZGVuLUJhZGVuPC90ZXh0PgoKICA8IS0tID09PT09PT09PT09PT09PT09PT09PSBTd2ltbGFuZTogQ2xhc3NpYyA9PT09PT09PT09PT09PT09PT09PT0gLS0+CiAgPHJlY3QgeD0iMjAwIiB5PSI3MCIgd2lkdGg9IjQ0MCIgaGVpZ2h0PSI2NCIgcng9IjgiIGZpbGw9IiNFQUYxRkIiIHN0cm9rZT0iIzlCQkNFMCIgc3Ryb2tlLXdpZHRoPSIxLjUiLz4KICA8cmVjdCB4PSIyMDQiIHk9Ijc0IiB3aWR0aD0iOTIiIGhlaWdodD0iNTYiIHJ4PSI2IiBmaWxsPSIjN2Y5ZGM5IiBzdHJva2U9IiM1ZjgyYjgiIHN0cm9rZS13aWR0aD0iMS4yIi8+CiAgPHRleHQgeD0iMjUwIiB5PSI5NiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMiIgZm9udC13ZWlnaHQ9IjcwMCIgZmlsbD0iI2ZmZmZmZiI+Q2xhc3NpYzwvdGV4dD4KICA8dGV4dCB4PSIyNTAiIHk9IjExMCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSI5LjUiIGZpbGw9IiNmZmZmZmYiPlBsYXRmb3JtIChDUCk8L3RleHQ+CiAgPHRleHQgeD0iMjUwIiB5PSIxMjQiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iOC41IiBmb250LXN0eWxlPSJpdGFsaWMiIGZpbGw9IiNlZWY0ZmIiPmZyb20gMjAwNTwvdGV4dD4KCiAgPHJlY3QgeD0iMzA0IiB5PSI4MCIgd2lkdGg9Ijc2IiBoZWlnaHQ9IjQ4IiByeD0iNSIgZmlsbD0iI2ZmZmZmZiIgc3Ryb2tlPSIjN2Y5ZGM5IiBzdHJva2Utd2lkdGg9IjEuMiIvPgogIDx0ZXh0IHg9IjM0MiIgeT0iOTciIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTIiIGZvbnQtd2VpZ2h0PSI3MDAiIGZpbGw9IiMyMjMzNDQiPjEuMDwvdGV4dD4KICA8dGV4dCB4PSIzNDIiIHk9IjExMSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSI5IiBmaWxsPSIjMjIzMzQ0Ij5NYXkgMjAwNTwvdGV4dD4KICA8dGV4dCB4PSIzNDIiIHk9IjEyMyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSI3LjUiIGZpbGw9IiMyMjMzNDQiPmZpcnN0IENQIHJlbGVhc2U8L3RleHQ+CgogIDxyZWN0IHg9IjM4OCIgeT0iODAiIHdpZHRoPSI3NiIgaGVpZ2h0PSI0OCIgcng9IjUiIGZpbGw9IiNmZmZmZmYiIHN0cm9rZT0iIzdmOWRjOSIgc3Ryb2tlLXdpZHRoPSIxLjIiLz4KICA8dGV4dCB4PSI0MjYiIHk9IjEwMiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMiIgZm9udC13ZWlnaHQ9IjcwMCIgZmlsbD0iIzIyMzM0NCI+NC4wPC90ZXh0PgogIDx0ZXh0IHg9IjQyNiIgeT0iMTE2IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjkiIGZpbGw9IiMyMjMzNDQiPkRlYyAyMDA5PC90ZXh0PgoKICA8cmVjdCB4PSI0NzIiIHk9IjgwIiB3aWR0aD0iNzYiIGhlaWdodD0iNDgiIHJ4PSI1IiBmaWxsPSIjZmZmZmZmIiBzdHJva2U9IiM3ZjlkYzkiIHN0cm9rZS13aWR0aD0iMS4yIi8+CiAgPHRleHQgeD0iNTEwIiB5PSI5NyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMiIgZm9udC13ZWlnaHQ9IjcwMCIgZmlsbD0iIzIyMzM0NCI+NC4yLjE8L3RleHQ+CiAgPHRleHQgeD0iNTEwIiB5PSIxMTEiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iOSIgZmlsbD0iIzIyMzM0NCI+T2N0IDIwMTQ8L3RleHQ+CiAgPHRleHQgeD0iNTEwIiB5PSIxMjMiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iNyIgZmlsbD0iIzIyMzM0NCI+U09NRS9JUCBYZiBzdGQuPC90ZXh0PgoKICA8cmVjdCB4PSI1NTYiIHk9IjgwIiB3aWR0aD0iNzYiIGhlaWdodD0iNDgiIHJ4PSI1IiBmaWxsPSIjZmZmZmZmIiBzdHJva2U9IiM3ZjlkYzkiIHN0cm9rZS13aWR0aD0iMS4yIi8+CiAgPHRleHQgeD0iNTk0IiB5PSI5NyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMiIgZm9udC13ZWlnaHQ9IjcwMCIgZmlsbD0iIzIyMzM0NCI+NC40LjA8L3RleHQ+CiAgPHRleHQgeD0iNTk0IiB5PSIxMTEiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iOSIgZmlsbD0iIzIyMzM0NCI+T2N0IDIwMTg8L3RleHQ+CiAgPHRleHQgeD0iNTk0IiB5PSIxMjMiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iNyIgZmlsbD0iIzIyMzM0NCI+bGFzdCBzdGFuZGFsb25lIENQPC90ZXh0PgoKICA8IS0tID09PT09PT09PT09PT09PT09PT09PSBTd2ltbGFuZTogRm91bmRhdGlvbiA9PT09PT09PT09PT09PT09PT09PT0gLS0+CiAgPHJlY3QgeD0iMjAwIiB5PSIxNDIiIHdpZHRoPSI0NDAiIGhlaWdodD0iNTgiIHJ4PSI4IiBmaWxsPSIjRUNGNkVDIiBzdHJva2U9IiM4RkJGOEYiIHN0cm9rZS13aWR0aD0iMS41Ii8+CiAgPHJlY3QgeD0iMjA0IiB5PSIxNDYiIHdpZHRoPSI5MiIgaGVpZ2h0PSI1MCIgcng9IjYiIGZpbGw9IiM4RkJGOEYiIHN0cm9rZT0iIzZmYTA2ZiIgc3Ryb2tlLXdpZHRoPSIxLjIiLz4KICA8dGV4dCB4PSIyNTAiIHk9IjE2NiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMiIgZm9udC13ZWlnaHQ9IjcwMCIgZmlsbD0iIzFmM2QxZiI+Rm91bmRhdGlvbjwvdGV4dD4KICA8dGV4dCB4PSIyNTAiIHk9IjE4MCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSI5LjUiIGZpbGw9IiMxZjNkMWYiPihGTyk8L3RleHQ+CiAgPHRleHQgeD0iMjUwIiB5PSIxOTIiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iOC41IiBmb250LXN0eWxlPSJpdGFsaWMiIGZpbGw9IiMyNzRhMjciPmZyb20gMjAxNjwvdGV4dD4KCiAgPHJlY3QgeD0iMzkwIiB5PSIxNTAiIHdpZHRoPSIxMTgiIGhlaWdodD0iNDQiIHJ4PSI1IiBmaWxsPSIjZmZmZmZmIiBzdHJva2U9IiM4RkJGOEYiIHN0cm9rZS13aWR0aD0iMS4yIi8+CiAgPHRleHQgeD0iNDQ5IiB5PSIxNjciIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTAuNSIgZm9udC13ZWlnaHQ9IjcwMCIgZmlsbD0iIzJkNWEyZCI+UjEuMC4wIOKAlCBPY3QgMjAxNjwvdGV4dD4KICA8dGV4dCB4PSI0NDkiIHk9IjE4MCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSI4IiBmaWxsPSIjMmQ1YTJkIj5maXJzdCBGb3VuZGF0aW9uOzwvdGV4dD4KICA8dGV4dCB4PSI0NDkiIHk9IjE5MCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSI3LjUiIGZpbGw9IiMyZDVhMmQiPmNhcnJpZXMgc2hhcmVkIG1ldGEtbW9kZWwvc2NoZW1hPC90ZXh0PgoKICA8cmVjdCB4PSI1MTYiIHk9IjE1MCIgd2lkdGg9IjExOCIgaGVpZ2h0PSI0NCIgcng9IjUiIGZpbGw9IiNmZmZmZmYiIHN0cm9rZT0iIzhGQkY4RiIgc3Ryb2tlLXdpZHRoPSIxLjIiLz4KICA8dGV4dCB4PSI1NzUiIHk9IjE2OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMC41IiBmb250LXdlaWdodD0iNzAwIiBmaWxsPSIjMmQ1YTJkIj4xLjUuMSDigJQgTWFyIDIwMTk8L3RleHQ+CiAgPHRleHQgeD0iNTc1IiB5PSIxODQiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iOC41IiBmaWxsPSIjMmQ1YTJkIj5sYXN0IHN0YW5kYWxvbmUgRk88L3RleHQ+CgogIDwhLS0gPT09PT09PT09PT09PT09PT09PT09IFN3aW1sYW5lOiBBZGFwdGl2ZSA9PT09PT09PT09PT09PT09PT09PT0gLS0+CiAgPHJlY3QgeD0iMjAwIiB5PSIyMDgiIHdpZHRoPSI0NDAiIGhlaWdodD0iNjQiIHJ4PSI4IiBmaWxsPSIjRkRGMUU2IiBzdHJva2U9IiNFMEE5NkQiIHN0cm9rZS13aWR0aD0iMS41Ii8+CiAgPHJlY3QgeD0iMjA0IiB5PSIyMTIiIHdpZHRoPSI5MiIgaGVpZ2h0PSI1NiIgcng9IjYiIGZpbGw9IiNFMEE5NkQiIHN0cm9rZT0iI2M5OGE0ZiIgc3Ryb2tlLXdpZHRoPSIxLjIiLz4KICA8dGV4dCB4PSIyNTAiIHk9IjIzNCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMiIgZm9udC13ZWlnaHQ9IjcwMCIgZmlsbD0iIzVhM2QyMiI+QWRhcHRpdmU8L3RleHQ+CiAgPHRleHQgeD0iMjUwIiB5PSIyNDgiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iOS41IiBmaWxsPSIjNWEzZDIyIj5QbGF0Zm9ybSAoQVApPC90ZXh0PgogIDx0ZXh0IHg9IjI1MCIgeT0iMjYyIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjguNSIgZm9udC1zdHlsZT0iaXRhbGljIiBmaWxsPSIjNWEzZDIyIj5mcm9tIDIwMTc8L3RleHQ+CgogIDxyZWN0IHg9IjMwNiIgeT0iMjE0IiB3aWR0aD0iMTAyIiBoZWlnaHQ9IjUwIiByeD0iNSIgZmlsbD0iI2ZmZmZmZiIgc3Ryb2tlPSIjRTBBOTZEIiBzdHJva2Utd2lkdGg9IjEuMiIvPgogIDx0ZXh0IHg9IjM1NyIgeT0iMjM0IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjEwLjUiIGZvbnQtd2VpZ2h0PSI3MDAiIGZpbGw9IiM2QjRBMkIiPjE3LTAzIOKAlCBNYXIgMjAxNzwvdGV4dD4KICA8dGV4dCB4PSIzNTciIHk9IjI0OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSI4LjUiIGZpbGw9IiM2QjRBMkIiPmZpcnN0IEFQIHJlbGVhc2U8L3RleHQ+CgogIDxyZWN0IHg9IjQxNiIgeT0iMjE0IiB3aWR0aD0iMTAyIiBoZWlnaHQ9IjUwIiByeD0iNSIgZmlsbD0iI2ZmZmZmZiIgc3Ryb2tlPSIjRTBBOTZEIiBzdHJva2Utd2lkdGg9IjEuMiIvPgogIDx0ZXh0IHg9IjQ2NyIgeT0iMjMyIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjEwLjUiIGZvbnQtd2VpZ2h0PSI3MDAiIGZpbGw9IiM2QjRBMkIiPjE4LTAzIOKAlCBNYXIgMjAxODwvdGV4dD4KICA8dGV4dCB4PSI0NjciIHk9IjI0NiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSI4IiBmaWxsPSIjNkI0QTJCIj5ERFMgbmV0d29yayBiaW5kaW5nPC90ZXh0PgogIDx0ZXh0IHg9IjQ2NyIgeT0iMjU3IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjcuNSIgZm9udC1zdHlsZT0iaXRhbGljIiBmaWxsPSIjNkI0QTJCIj4obm90IDE4LTEwKTwvdGV4dD4KCiAgPHJlY3QgeD0iNTI2IiB5PSIyMTQiIHdpZHRoPSIxMDIiIGhlaWdodD0iNTAiIHJ4PSI1IiBmaWxsPSIjZmZmZmZmIiBzdHJva2U9IiNFMEE5NkQiIHN0cm9rZS13aWR0aD0iMS4yIi8+CiAgPHRleHQgeD0iNTc3IiB5PSIyMzQiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTAuNSIgZm9udC13ZWlnaHQ9IjcwMCIgZmlsbD0iIzZCNEEyQiI+MTktMDMg4oCUIE1hciAyMDE5PC90ZXh0PgogIDx0ZXh0IHg9IjU3NyIgeT0iMjQ5IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjguNSIgZmlsbD0iIzZCNEEyQiI+bGFzdCBzdGFuZGFsb25lIEFQPC90ZXh0PgoKICA8IS0tID09PT09PT09PT09PT09PT09PT09PSBDb252ZXJnZW5jZSBmdW5uZWwgdG8gUjE5LTExID09PT09PT09PT09PT09PT09PT09PSAtLT4KICA8bGluZSB4MT0iNjQwIiB5MT0iMTAyIiB4Mj0iNjcyIiB5Mj0iMTUwIiBzdHJva2U9IiM0NDQiIHN0cm9rZS13aWR0aD0iMS44IiBtYXJrZXItZW5kPSJ1cmwoI2FycikiLz4KICA8bGluZSB4MT0iNjQwIiB5MT0iMTcxIiB4Mj0iNjcyIiB5Mj0iMTc0IiBzdHJva2U9IiM0NDQiIHN0cm9rZS13aWR0aD0iMS44IiBtYXJrZXItZW5kPSJ1cmwoI2FycikiLz4KICA8bGluZSB4MT0iNjQwIiB5MT0iMjQwIiB4Mj0iNjcyIiB5Mj0iMjAwIiBzdHJva2U9IiM0NDQiIHN0cm9rZS13aWR0aD0iMS44IiBtYXJrZXItZW5kPSJ1cmwoI2FycikiLz4KCiAgPHJlY3QgeD0iNjc0IiB5PSIxMTYiIHdpZHRoPSIyMzgiIGhlaWdodD0iMTE2IiByeD0iMTAiIGZpbGw9IiNFNEU0RUUiIHN0cm9rZT0iIzZiNmY4ZiIgc3Ryb2tlLXdpZHRoPSIyIi8+CiAgPHRleHQgeD0iNzkzIiB5PSIxNDAiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTQiIGZvbnQtd2VpZ2h0PSI3MDAiIGZpbGw9IiMyYjJmNTUiPlIxOS0xMSDigJQgTm92IDIwMTk8L3RleHQ+CiAgPHRleHQgeD0iNzkzIiB5PSIxNjAiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTIiIGZvbnQtd2VpZ2h0PSI3MDAiIGZpbGw9IiM1YjNhOGEiPlVOSUZJQ0FUSU9OPC90ZXh0PgogIDx0ZXh0IHg9Ijc5MyIgeT0iMTc5IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjkuNSIgZmlsbD0iIzJiMmY1NSI+b25lIG5hbWluZyBSe3l5fS0xMSDCtyBvbmU8L3RleHQ+CiAgPHRleHQgeD0iNzkzIiB5PSIxOTIiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iOS41IiBmaWxsPSIjMmIyZjU1Ij5Ob3ZlbWJlciBjYWRlbmNlIMK3IG9uZTwvdGV4dD4KICA8dGV4dCB4PSI3OTMiIHk9IjIwNSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSI5LjUiIGZpbGw9IiMyYjJmNTUiPkFVVE9TQVJfMDAwbm4gc2NoZW1hPC90ZXh0PgogIDx0ZXh0IHg9Ijc5MyIgeT0iMjE4IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjkuNSIgZmlsbD0iIzJiMmY1NSI+YWNyb3NzIENQICsgQVA8L3RleHQ+CgogIDx0ZXh0IHg9Ijc5MyIgeT0iMjUwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjguNSIgZm9udC1zdHlsZT0iaXRhbGljIiBmaWxsPSIjNTU1Ij5DUCBpbnRlcm5hbCB2ZXJzaW9uIG5ldmVyIHJlc2V0IOKAlCBSMjUtMTEgaXMgaW50ZXJuYWxseSBSNC4xMS4wLDwvdGV4dD4KICA8dGV4dCB4PSI3OTMiIHk9IjI2MiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSI4LjUiIGZvbnQtc3R5bGU9Iml0YWxpYyIgZmlsbD0iIzU1NSI+c28gIkFVVE9TQVIgNC54IiBpcyBzdGlsbCBhbGl2ZTwvdGV4dD4KCiAgPCEtLSA9PT09PT09PT09PT09PT09PT09PT0gRWxib3cgY29ubmVjdG9yIHRvIHVuaWZpZWQgdHJhY2sgPT09PT09PT09PT09PT09PT09PT09IC0tPgogIDxwb2x5bGluZSBwb2ludHM9Ijg4MCwyMzIgODgwLDI5MCA2MCwyOTAgNjAsMzM4IiBmaWxsPSJub25lIiBzdHJva2U9IiM2YjZmOGYiIHN0cm9rZS13aWR0aD0iMS42IiBtYXJrZXItZW5kPSJ1cmwoI2FycikiLz4KICA8dGV4dCB4PSI0NDAiIHk9IjI4NCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSI4LjUiIGZvbnQtc3R5bGU9Iml0YWxpYyIgZmlsbD0iIzY2NiI+dGhlIHNpbmdsZSBtZXJnZWQgcmVsZWFzZSBsaW5lIOKAlCBjb250aW51ZXMgZXZlcnkgTm92ZW1iZXIg4oaTPC90ZXh0PgoKICA8IS0tID09PT09PT09PT09PT09PT09PT09PSBVbmlmaWVkIGJvdHRvbSB0cmFjayA9PT09PT09PT09PT09PT09PT09PT0gLS0+CiAgPHJlY3QgeD0iNDgiIHk9IjM0MCIgd2lkdGg9Ijg1MiIgaGVpZ2h0PSI1NCIgcng9IjEwIiBmaWxsPSIjRTJFMkVBIiBzdHJva2U9IiM5YTlmYjAiIHN0cm9rZS13aWR0aD0iMS41Ii8+CiAgPHRleHQgeD0iNjYiIHk9IjM2MiIgdGV4dC1hbmNob3I9InN0YXJ0IiBmb250LXNpemU9IjEwIiBmb250LXdlaWdodD0iNzAwIiBmaWxsPSIjMzMzIj51bmlmaWVkIFJ7eXl9LTExIGxpbmUg4oCUPC90ZXh0PgogIDx0ZXh0IHg9IjY2IiB5PSIzNzgiIHRleHQtYW5jaG9yPSJzdGFydCIgZm9udC1zaXplPSI4LjUiIGZpbGw9IiMzMzMiPm9uZSByZWxlYXNlICsgb25lIHNjaGVtYSwgZXZlcnkgTm92ZW1iZXI8L3RleHQ+CgogIDx0ZXh0IHg9IjM1NiIgeT0iMzcxIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjguNSIgZmlsbD0iIzMzMyI+UjIwLTExPC90ZXh0PgogIDx0ZXh0IHg9IjQxNiIgeT0iMzcxIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjguNSIgZmlsbD0iIzMzMyI+UjIxLTExPC90ZXh0PgogIDx0ZXh0IHg9IjQ3NiIgeT0iMzcxIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjguNSIgZmlsbD0iIzMzMyI+UjIyLTExPC90ZXh0PgogIDx0ZXh0IHg9IjUzNiIgeT0iMzcxIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjguNSIgZmlsbD0iIzMzMyI+UjIzLTExPC90ZXh0PgogIDx0ZXh0IHg9IjU5NiIgeT0iMzcxIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjguNSIgZmlsbD0iIzMzMyI+UjI0LTExPC90ZXh0PgogIDx0ZXh0IHg9IjY0NiIgeT0iMzcxIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjEyIiBmb250LXdlaWdodD0iNzAwIiBmaWxsPSIjMzMzIj7igKY8L3RleHQ+CgogIDwhLS0gUjI1LTExIGVuZCBub2RlIC0tPgogIDxyZWN0IHg9IjY4NCIgeT0iMzI2IiB3aWR0aD0iMjQyIiBoZWlnaHQ9Ijc4IiByeD0iMTAiIGZpbGw9IiNERkYwRDgiIHN0cm9rZT0iIzhGQkY4RiIgc3Ryb2tlLXdpZHRoPSIyIi8+CiAgPHRleHQgeD0iODA1IiB5PSIzNTIiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTUiIGZvbnQtd2VpZ2h0PSI3MDAiIGZpbGw9IiMyZDVhMmQiPlIyNS0xMTwvdGV4dD4KICA8dGV4dCB4PSI4MDUiIHk9IjM2OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSI5LjUiIGZpbGw9IiMyZDVhMmQiPjIwMjUtMTEtMjcgwrcgaW50ZXJuYWwgUjQuMTEuMDwvdGV4dD4KICA8dGV4dCB4PSI4MDUiIHk9IjM4NSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMCIgZm9udC13ZWlnaHQ9IjcwMCIgZmlsbD0iIzJkNWEyZCI+Y3VycmVudCByZWxlYXNlPC90ZXh0PgoKICA8IS0tIENhbGxvdXQgdGFncyAtLT4KICA8bGluZSB4MT0iNzYwIiB5MT0iNDA0IiB4Mj0iNzEyIiB5Mj0iNDE0IiBzdHJva2U9IiM4RkJGOEYiIHN0cm9rZS13aWR0aD0iMS4yIi8+CiAgPHJlY3QgeD0iNDk4IiB5PSI0MTQiIHdpZHRoPSI0MjgiIGhlaWdodD0iNDAiIHJ4PSI2IiBmaWxsPSIjREZGMEQ4IiBzdHJva2U9IiM4RkJGOEYiIHN0cm9rZS13aWR0aD0iMS4yIi8+CiAgPHRleHQgeD0iNzEyIiB5PSI0MzEiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iOS41IiBmb250LXdlaWdodD0iNzAwIiBmaWxsPSIjMmQ1YTJkIj5ORVc6IEREUyBUcmFuc2Zvcm1lciBvbiBDbGFzc2ljPC90ZXh0PgogIDx0ZXh0IHg9IjcxMiIgeT0iNDQ2IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjguNSIgZm9udC1zdHlsZT0iaXRhbGljIiBmaWxsPSIjMmQ1YTJkIj5zdGFuZGFyZC1sZXZlbCBjb25jZXB0IGluIFIyNS0xMSDigJQgbm8gc2hpcHBpbmcgdmVuZG9yIGltcGwgeWV0PC90ZXh0PgoKICA8cmVjdCB4PSI0OTgiIHk9IjQ1OCIgd2lkdGg9IjQyOCIgaGVpZ2h0PSI0NCIgcng9IjYiIGZpbGw9IiNGQ0U4RDUiIHN0cm9rZT0iI0UwQTk2RCIgc3Ryb2tlLXdpZHRoPSIxLjIiLz4KICA8dGV4dCB4PSI3MTIiIHk9IjQ3NSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSI5LjUiIGZvbnQtd2VpZ2h0PSI3MDAiIGZpbGw9IiM2QjRBMkIiPkNQIHJlbW92ZWQgRmxzIMK3IEVlcCDCtyBUVENBTiDCtyBMZENvbTwvdGV4dD4KICA8dGV4dCB4PSI3MTIiIHk9IjQ5MCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSI4LjUiIGZpbGw9IiM2QjRBMkIiPkZscy9FZXAg4oaSIE1lbS9NZW1BY2MgwrcgTGRDb20gYWJzb3JiZWQgaW50byBDb208L3RleHQ+CgogIDwhLS0gU2NoZW1hdGljIGhvbmVzdHkgbm90ZSAobG93ZXIgbGVmdCkgLS0+CiAgPHRleHQgeD0iMjAiIHk9IjQzMCIgdGV4dC1hbmNob3I9InN0YXJ0IiBmb250LXNpemU9IjkiIGZvbnQtc3R5bGU9Iml0YWxpYyIgZmlsbD0iIzY2NiI+U2NoZW1hdGljIG92ZXJ2aWV3IOKAlCBtaWxlc3RvbmUgbm9kZXMgYXJlIHNob3duIGluIGNocm9ub2xvZ2ljYWw8L3RleHQ+CiAgPHRleHQgeD0iMjAiIHk9IjQ0MyIgdGV4dC1hbmNob3I9InN0YXJ0IiBmb250LXNpemU9IjkiIGZvbnQtc3R5bGU9Iml0YWxpYyIgZmlsbD0iIzY2NiI+b3JkZXIgd2l0aGluIGVhY2ggdHJhY2ssIG5vdCBvbiBhIGxpbmVhciB0aW1lIHNjYWxlLiBUaGUgZGF0ZWQ8L3RleHQ+CiAgPHRleHQgeD0iMjAiIHk9IjQ1NiIgdGV4dC1hbmNob3I9InN0YXJ0IiBmb250LXNpemU9IjkiIGZvbnQtc3R5bGU9Iml0YWxpYyIgZmlsbD0iIzY2NiI+bGFiZWxzIGFyZSB0aGUgbG9hZC1iZWFyaW5nIGZhY3RzLjwvdGV4dD4KCiAgPCEtLSBGb290bm90ZSAvIGdsb3NzIC0tPgogIDx0ZXh0IHg9IjQ4MCIgeT0iNTU2IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjExIiBmb250LXN0eWxlPSJpdGFsaWMiIGZpbGw9IiM1NTUiPk9uZSBBVVRPU0FSIHN0YW5kYXJkIHNldCwgcHVibGlzaGVkIG9uY2UgYSB5ZWFyIGVhY2ggTm92ZW1iZXIgc2luY2UgUjE5LTExLjwvdGV4dD4KICA8dGV4dCB4PSI0ODAiIHk9IjU3NCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSI5LjUiIGZpbGw9IiM1NTU1NTUiPkNQID0gQ2xhc3NpYyBQbGF0Zm9ybSDCtyBBUCA9IEFkYXB0aXZlIFBsYXRmb3JtIMK3IEZPID0gRm91bmRhdGlvbiDCtyBTT01FL0lQID0gU2NhbGFibGUgc2VydmljZS1PcmllbnRlZCBNaWRkbGV3YXJFIG92ZXIgSVAgwrcgRERTID0gRGF0YSBEaXN0cmlidXRpb24gU2VydmljZSDCtyBYZiA9IFRyYW5zZm9ybWVyPC90ZXh0PgogIDx0ZXh0IHg9IjQ4MCIgeT0iNTkwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjkuNSIgZmlsbD0iIzU1NTU1NSI+U291cmNlczogYXV0b3Nhci5vcmcvYWJvdXQvaGlzdG9yeSDCtyBDUC9BUCBSZWxlYXNlIE92ZXJ2aWV3cyBSMjUtMTEgwrcgRERTIG9uIEFQIHNpbmNlIFIxOC0wMyAocnRpLmNvbSk8L3RleHQ+Cjwvc3ZnPgo=" />

---

## One standard set, three members: FO · CP · AP

- **The org, in one line**: a **worldwide development partnership** (founding talks 2002,
  Development Agreement July 2003), governed top-down by ~10 **Core Partners**; **~360
  partners today, Asia-led** (Jan 2025: Asia 174 > Europe 140 > NA 41). Jan 2026: DENSO, Huawei and
  Vector promoted to Core. Specs are **free to read, license-to-build**
- **Foundation (FO)** — the cross-platform glue: common requirements, the **meta-model and
  single XML schema**, methodology, and shared wire protocols (SOME/IP, time-sync, DoIP, E2E,
  SecOC). FO is what lets a Classic ECU and an Adaptive machine live in one vehicle project
- **Classic Platform (CP)** — statically-configured, real-time, **OSEK-heritage** stack for
  deeply embedded microcontrollers. First released 1.0 in **2005**
- **Adaptive Platform (AP)** — **POSIX**-based, service-oriented, dynamically-deployed stack
  for high-performance compute. First released **17-03 (March 2017)**
- **The naming trap**: the **R19-11 unification** (Nov 2019) merged CP's `4.x.y` and AP's
  `yy-mm` into one annual `R{yy}-11` label, one November release, one schema — **but the CP
  internal version never reset**. R25-11 is internally **R4.11.0**; "AUTOSAR 4.x" is alive
- **Document prefixes** you'll meet: **EXP** (explanatory), **TR** (technical report),
  **RS/SRS** (requirements), **SWS** (the detailed testable module spec), **TPS** (templates),
  **PRS** (wire-protocol requirements)

<div class="gloss">OSEK = the 1990s European automotive RTOS standard CP's OS descends from · POSIX = Portable Operating System Interface (IEEE 1003) · SOME/IP = Scalable service-Oriented MiddlewarE over IP · DoIP = Diagnostics over IP (ISO 13400) · E2E = End-to-End protection · SecOC = Secure Onboard Communication · SWS = Software Specification</div>

---

## The spec landscape — a reading map (every PDF is a free download)

<style scoped>
  section { font-size: 18.5px; padding-top: 28px; }
  h2 { margin-bottom: 4px; }
  p { margin: 5px 0; }
  table { font-size: 15.5px; }
  .gloss { font-size: 13px; margin-top: 8px; }
</style>

All specs live at `autosar.org/fileadmin/standards/R25-11/<FO|CP|AP>/<name>.pdf` — no login, no
membership. **Start with the three EXP intros**, use the TR ReleaseOverviews to stay current,
open an SWS only when you implement. (Every filename below verified live against R25-11.)

| You want… | Read (`AUTOSAR_` prefix omitted) |
|---|---|
| **the big picture, first** | `CP_EXP_LayeredSoftwareArchitecture` · `AP_EXP_PlatformDesign` · `FO_EXP_SWArchitecturalDecisions` (why two platforms exist) |
| CP OS, RTE & the VFB | `CP_SWS_OS` (SC1–SC4) · `CP_SWS_RTE` · `CP_TR_VFB` |
| CP comm stack (our diagram) | `CP_SWS_COM` · `CP_SWS_PDURouter` · `CP_SWS_CANTransportLayer` · `CP_SWS_CANInterface` |
| CP diagnostics & services | `CP_SWS_DiagnosticEventManager` (DEM) · `CP_SWS_DiagnosticCommunicationManager` (DCM) · `CP_SWS_NVRAMManager` · `CP_EXP_ModeManagementGuide` · `CP_SWS_WatchdogManager` |
| CP functional safety | `CP_EXP_FunctionalSafetyMeasures` |
| AP function clusters | one SWS each: `AP_SWS_ExecutionManagement` · `…StateManagement` · `…CommunicationManagement` (`ara::com`, SOME/IP + DDS bindings) · `…Diagnostics` · `…UpdateAndConfigurationManagement` (+ `…VehicleUpdateAndConfigurationManagement`) · `…PlatformHealthManagement` · `…Persistency` · `…OperatingSystemInterface` (PSE51) — plus `AP_TPS_ManifestSpecification` |
| wire protocols (CP + AP share) | `FO_PRS_SOMEIPProtocol` · `FO_PRS_SOMEIPServiceDiscoveryProtocol` · `FO_PRS_E2EProtocol` · `FO_PRS_SecOCProtocol` · `FO_PRS_NetworkManagementProtocol` |
| what changed this year | `CP_TR_ReleaseOverview` · `AP_TR_ReleaseOverview` |

<div class="gloss">EXP = explanatory (read these first) · SWS = software specification (one per module, testable) · PRS = wire-protocol requirements · TPS = template spec (ARXML/manifests) · TR = technical report · reading is free — implementing commercially requires an AUTOSAR partner license · R25-11 renames to note: the VFB doc is now CP_TR_VFB (was CP_EXP_VFB in R24-11) and SecOC is FO_PRS_SecOCProtocol (was …SecOcProtocol)</div>

---

<!-- _class: lead -->

# Part 1
## the Classic Platform — the deeply embedded half

---

## What Classic is, and where it runs

- **A statically-configured software stack for deeply embedded ECUs** — single
  microcontrollers, no MMU-class OS, hard real-time, safety-critical. The OSEK-heritage half
- **Hold onto this one property**: a CP ECU builds to **one statically configured binary** —
  fixed task set, fixed communication matrix, fixed memory map, all decided at design time.
  *"All tasks that will ever execute … are allocated when the executable image is built."*
  No `malloc`, no runtime task creation, no service negotiation
- This is the discipline safety-critical firmware already follows by hand — **CP formalizes it
  and generates the glue**
- **Where it sits in a 2026 vehicle**: CP owns the **edge** — zonal, body/chassis/powertrain
  ECUs, and the **safety MCU** that gates actuators on high-compute boards. On an NVIDIA DRIVE
  board: the big SoC does perception; a small lock-step safety MCU running CP owns the
  fail-safe path and diagnostics
- **Pinned silicon**: Orin-gen safety MCU = **Infineon AURIX TC397X**; Thor-gen companion MCU
  = **Renesas RH850U2A16** (Vector MICROSAR Classic as reference). *Never say Thor uses AURIX*
- Myth this repo already killed: **"Classic = CAN only" is false** — CP has had a standardized
  SOME/IP Transformer since **4.2.1 (Oct 2014)**, years before AP's first release, plus Ethernet,
  DoIP, LIN, FlexRay

<div class="gloss">ECU = Electronic Control Unit · MMU = Memory Management Unit (virtual memory; CP has none) · MCU = microcontroller · SoC = System-on-Chip · lock-step = two cores running identical code compared each cycle for fault detection · MICROSAR = Vector's AUTOSAR product family</div>

---

<!-- _class: diagram -->

<img alt="stack-autosar-classic" src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA5NjAgNjAwIiB3aWR0aD0iOTYwIiBoZWlnaHQ9IjYwMCIgZm9udC1mYW1pbHk9IkhlbHZldGljYSwgQXJpYWwsIHNhbnMtc2VyaWYiPgogIDxyZWN0IHg9IjAiIHk9IjAiIHdpZHRoPSI5NjAiIGhlaWdodD0iNjAwIiBmaWxsPSIjZmZmZmZmIi8+CgogIDxkZWZzPgogICAgPG1hcmtlciBpZD0iYXJyIiBtYXJrZXJXaWR0aD0iMTAiIG1hcmtlckhlaWdodD0iMTAiIHJlZlg9IjgiIHJlZlk9IjMiIG9yaWVudD0iYXV0byIgbWFya2VyVW5pdHM9InN0cm9rZVdpZHRoIj4KICAgICAgPHBhdGggZD0iTTAsMCBMOSwzIEwwLDYgeiIgZmlsbD0iIzQ0NCIvPgogICAgPC9tYXJrZXI+CiAgPC9kZWZzPgoKICA8IS0tIFRpdGxlIC0tPgogIDx0ZXh0IHg9IjQ4MCIgeT0iNDAiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMjYiIGZvbnQtd2VpZ2h0PSI3MDAiIGZpbGw9IiMxYjJiNGEiPkFVVE9TQVIgQ2xhc3NpYyDigJQgdGhlIGxheWVyZWQgc3RhY2sgb24gb25lIGRlZXBseSBlbWJlZGRlZCBFQ1U8L3RleHQ+CgogIDwhLS0gPT09PT09PT09PT09PT09PT09PT09IFJvdyAxOiBBcHBsaWNhdGlvbiBMYXllciA9PT09PT09PT09PT09PT09PT09PT0gLS0+CiAgPHJlY3QgeD0iMTUwIiB5PSI2NCIgd2lkdGg9IjYyMCIgaGVpZ2h0PSI3MiIgcng9IjgiIGZpbGw9IiNGQ0U4RDUiIHN0cm9rZT0iI0UwQTk2RCIgc3Ryb2tlLXdpZHRoPSIxLjUiLz4KICA8dGV4dCB4PSI0NjAiIHk9Ijk1IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjEzLjUiIGZvbnQtd2VpZ2h0PSI3MDAiIGZpbGw9IiM2QjRBMkIiPkFwcGxpY2F0aW9uIExheWVyIOKAlCBTV0NzIChTb2Z0d2FyZSBDb21wb25lbnRzKTwvdGV4dD4KICA8dGV4dCB4PSI0NjAiIHk9IjExNSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMi41IiBmaWxsPSIjNkI0QTJCIj5lLmcuIGRvb3IgY29udHJvbCDCtyB0b3JxdWUgcmVxdWVzdCDCtyBkaWFnbm9zdGljcyBkYXRhIHByb3ZpZGVyczwvdGV4dD4KCiAgPGxpbmUgeDE9IjQ2MCIgeTE9IjEzNiIgeDI9IjQ2MCIgeTI9IjE0OCIgc3Ryb2tlPSIjNDQ0IiBzdHJva2Utd2lkdGg9IjIiIG1hcmtlci1lbmQ9InVybCgjYXJyKSIvPgoKICA8IS0tID09PT09PT09PT09PT09PT09PT09PSBSb3cgMjogUlRFID09PT09PT09PT09PT09PT09PT09PSAtLT4KICA8cmVjdCB4PSIxNTAiIHk9IjE1MCIgd2lkdGg9IjYyMCIgaGVpZ2h0PSI2MCIgcng9IjgiIGZpbGw9IiNEQ0U5RjciIHN0cm9rZT0iIzdmOWRjOSIgc3Ryb2tlLXdpZHRoPSIxLjUiLz4KICA8dGV4dCB4PSI0NjAiIHk9IjE3NiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMyIgZm9udC13ZWlnaHQ9IjcwMCIgZmlsbD0iIzIyMzM0NCI+UlRFIOKAlCBSdW50aW1lIEVudmlyb25tZW50PC90ZXh0PgogIDx0ZXh0IHg9IjQ2MCIgeT0iMTk1IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjExLjUiIGZpbGw9IiMyMjMzNDQiPmdlbmVyYXRlZCBnbHVlOiB0aGUgb25seSBpbnRlcmZhY2UgU1dDcyBldmVyIHNlZSAocG9ydHMsIG5vdCBhZGRyZXNzZXMpPC90ZXh0PgoKICA8bGluZSB4MT0iNDYwIiB5MT0iMjEwIiB4Mj0iNDYwIiB5Mj0iMjIyIiBzdHJva2U9IiM0NDQiIHN0cm9rZS13aWR0aD0iMiIgbWFya2VyLWVuZD0idXJsKCNhcnIpIi8+CgogIDwhLS0gPT09PT09PT09PT09PT09PT09PT09IFJvdyAzOiBCU1cgY29tcG9zaXRlIGJhbmQgPT09PT09PT09PT09PT09PT09PT09IC0tPgogIDxyZWN0IHg9IjE1MCIgeT0iMjI0IiB3aWR0aD0iNjIwIiBoZWlnaHQ9IjIzMCIgcng9IjgiIGZpbGw9IiNFQUYxRkIiIHN0cm9rZT0iIzlCQkNFMCIgc3Ryb2tlLXdpZHRoPSIxLjUiLz4KICA8dGV4dCB4PSI0NjAiIHk9IjI0NiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxNCIgZm9udC13ZWlnaHQ9IjcwMCIgZmlsbD0iIzIyMzM0NCI+QlNXIOKAlCBCYXNpYyBTb2Z0d2FyZTwvdGV4dD4KCiAgPCEtLSBTdWItcm93IDE6IFNlcnZpY2VzIExheWVyIC0tPgogIDxyZWN0IHg9IjE2MCIgeT0iMjU2IiB3aWR0aD0iNjAwIiBoZWlnaHQ9IjYwIiByeD0iNiIgZmlsbD0iI0RDRTlGNyIgc3Ryb2tlPSIjN2Y5ZGM5IiBzdHJva2Utd2lkdGg9IjEuNSIvPgogIDx0ZXh0IHg9IjM4NSIgeT0iMjkwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjEwLjUiIGZpbGw9IiMyMjMzNDQiPlNlcnZpY2VzIExheWVyIOKAlCBBVVRPU0FSIE9TIChPU0VLLWhlcml0YWdlKSDCtyBDT00gwrcgTnZNIMK3IFdkZ008L3RleHQ+CiAgPHJlY3QgeD0iNjEwIiB5PSIyNjYiIHdpZHRoPSIxNDAiIGhlaWdodD0iNDAiIHJ4PSI2IiBmaWxsPSIjREZGMEQ4IiBzdHJva2U9IiM4RkJGOEYiIHN0cm9rZS13aWR0aD0iMS41Ii8+CiAgPHRleHQgeD0iNjgwIiB5PSIyODMiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTEiIGZvbnQtd2VpZ2h0PSI3MDAiIGZpbGw9IiMyZDVhMmQiPkRDTSDCtyBERU08L3RleHQ+CiAgPHRleHQgeD0iNjgwIiB5PSIyOTgiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTAuNSIgZm9udC1zdHlsZT0iaXRhbGljIiBmaWxsPSIjMmQ1YTJkIj5kaWFnbm9zdGljcyAoVURTKTwvdGV4dD4KCiAgPCEtLSBTdWItcm93IDI6IEVDVSBBYnN0cmFjdGlvbiBMYXllciAtLT4KICA8cmVjdCB4PSIxNjAiIHk9IjMyOCIgd2lkdGg9IjYwMCIgaGVpZ2h0PSI0OCIgcng9IjYiIGZpbGw9IiNEQ0U5RjciIHN0cm9rZT0iIzdmOWRjOSIgc3Ryb2tlLXdpZHRoPSIxLjUiLz4KICA8dGV4dCB4PSI0NjAiIHk9IjM1NiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMS41IiBmaWxsPSIjMjIzMzQ0Ij5FQ1UgQWJzdHJhY3Rpb24gTGF5ZXIg4oCUIGFic3RyYWN0cyB0aGUgYm9hcmQgd2lyaW5nPC90ZXh0PgoKICA8IS0tIFN1Yi1yb3cgMzogTUNBTCAtLT4KICA8cmVjdCB4PSIxNjAiIHk9IjM4OCIgd2lkdGg9IjYwMCIgaGVpZ2h0PSI1NCIgcng9IjYiIGZpbGw9IiNEQ0U5RjciIHN0cm9rZT0iIzdmOWRjOSIgc3Ryb2tlLXdpZHRoPSIxLjUiLz4KICA8dGV4dCB4PSI0NjAiIHk9IjQxMCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMS41IiBmaWxsPSIjMjIzMzQ0Ij5NQ0FMIOKAlCBNaWNyb2NvbnRyb2xsZXIgQWJzdHJhY3Rpb24gTGF5ZXI6PC90ZXh0PgogIDx0ZXh0IHg9IjQ2MCIgeT0iNDI4IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjExLjUiIGZpbGw9IiMyMjMzNDQiPkNBTi9MSU4vRVRIIGRyaXZlcnMgwrcgQURDIMK3IFBXTSDCtyB3YXRjaGRvZzwvdGV4dD4KCiAgPCEtLSBDREQg4oCUIGJlc2lkZSB0aGUgY29tcG9zaXRlIGJhbmQsIHNwYW5uaW5nIHRoZSB0aHJlZSBzdWItcm93cyAtLT4KICA8cmVjdCB4PSI3ODAiIHk9IjI1NiIgd2lkdGg9IjEzMCIgaGVpZ2h0PSIxODYiIHJ4PSI2IiBmaWxsPSIjRENFOUY3IiBzdHJva2U9IiM3ZjlkYzkiIHN0cm9rZS13aWR0aD0iMS41IiBzdHJva2UtZGFzaGFycmF5PSI2LDQiLz4KICA8dGV4dCB4PSI4NDUiIHk9IjMyNSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMyIgZm9udC13ZWlnaHQ9IjcwMCIgZmlsbD0iIzIyMzM0NCI+Q0REPC90ZXh0PgogIDx0ZXh0IHg9Ijg0NSIgeT0iMzQzIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjEwLjUiIGZpbGw9IiMyMjMzNDQiPkNvbXBsZXggRGV2aWNlPC90ZXh0PgogIDx0ZXh0IHg9Ijg0NSIgeT0iMzU5IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjEwLjUiIGZpbGw9IiMyMjMzNDQiPkRyaXZlcnM8L3RleHQ+CiAgPHRleHQgeD0iODQ1IiB5PSIzNzciIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTAuNSIgZm9udC1zdHlsZT0iaXRhbGljIiBmaWxsPSIjMjIzMzQ0Ij4oYnlwYXNzIGxhbmUpPC90ZXh0PgoKICA8bGluZSB4MT0iNDYwIiB5MT0iNDU0IiB4Mj0iNDYwIiB5Mj0iNDY2IiBzdHJva2U9IiM0NDQiIHN0cm9rZS13aWR0aD0iMiIgbWFya2VyLWVuZD0idXJsKCNhcnIpIi8+CgogIDwhLS0gPT09PT09PT09PT09PT09PT09PT09IFJvdyA0OiBNaWNyb2NvbnRyb2xsZXIgPT09PT09PT09PT09PT09PT09PT09IC0tPgogIDxyZWN0IHg9IjE1MCIgeT0iNDY4IiB3aWR0aD0iNjIwIiBoZWlnaHQ9IjcyIiByeD0iOCIgZmlsbD0iI0VDRUNFQyIgc3Ryb2tlPSIjQjBCMEIwIiBzdHJva2Utd2lkdGg9IjEuNSIvPgogIDx0ZXh0IHg9IjQ2MCIgeT0iNTA5IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjEyLjUiIGZpbGw9IiMzMzMiPk1pY3JvY29udHJvbGxlciDigJQgZS5nLiBSZW5lc2FzIFJIODUwIMK3IEluZmluZW9uIEFVUklYIMK3IE5YUCBTMzJLPC90ZXh0PgoKICA8IS0tID09PT09PT09PT09PT09PT09PT09PSBMZWZ0LXNpZGUgYW5ub3RhdGlvbnMgPT09PT09PT09PT09PT09PT09PT09IC0tPgogIDx0ZXh0IHg9Ijc1IiB5PSI4OCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMC41IiBmb250LXN0eWxlPSJpdGFsaWMiIGZpbGw9IiMyRTVGQUMiPm9uZSBiaW5hcnksIG9uZSBFQ1UsPC90ZXh0PgogIDx0ZXh0IHg9Ijc1IiB5PSIxMDIiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTAuNSIgZm9udC1zdHlsZT0iaXRhbGljIiBmaWxsPSIjMkU1RkFDIj5oYXJkIHJlYWwtdGltZTwvdGV4dD4KICA8bGluZSB4MT0iNzUiIHkxPSIxMDgiIHgyPSIxNTAiIHkyPSIxMDUiIHN0cm9rZT0iIzJFNUZBQyIgc3Ryb2tlLXdpZHRoPSIxIiBzdHJva2UtZGFzaGFycmF5PSI0LDMiLz4KCiAgPHRleHQgeD0iNzUiIHk9IjI1MiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMC41IiBmb250LXN0eWxlPSJpdGFsaWMiIGZpbGw9IiMyRTVGQUMiPmV2ZXJ5dGhpbmcgc3RhdGljYWxseTwvdGV4dD4KICA8dGV4dCB4PSI3NSIgeT0iMjY2IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjEwLjUiIGZvbnQtc3R5bGU9Iml0YWxpYyIgZmlsbD0iIzJFNUZBQyI+Y29uZmlndXJlZCBhdCBidWlsZDwvdGV4dD4KICA8dGV4dCB4PSI3NSIgeT0iMjgwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjEwLjUiIGZvbnQtc3R5bGU9Iml0YWxpYyIgZmlsbD0iIzJFNUZBQyI+dGltZSAoQVJYTUwpPC90ZXh0PgogIDxsaW5lIHgxPSI3NSIgeTE9IjI4NCIgeDI9IjE1MCIgeTI9IjMzMCIgc3Ryb2tlPSIjMkU1RkFDIiBzdHJva2Utd2lkdGg9IjEiIHN0cm9rZS1kYXNoYXJyYXk9IjQsMyIvPgoKICA8dGV4dCB4PSI3NSIgeT0iMzkyIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjEwLjUiIGZvbnQtc3R5bGU9Iml0YWxpYyIgZmlsbD0iIzJFNUZBQyI+TUNBTCDiiYggdGhlIHZlbmRvciBIQUw8L3RleHQ+CiAgPHRleHQgeD0iNzUiIHk9IjQwNiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMC41IiBmb250LXN0eWxlPSJpdGFsaWMiIGZpbGw9IiMyRTVGQUMiPnlvdSBhbHJlYWR5IGtub3c8L3RleHQ+CiAgPGxpbmUgeDE9Ijc1IiB5MT0iNDEwIiB4Mj0iMTUwIiB5Mj0iNDE0IiBzdHJva2U9IiMyRTVGQUMiIHN0cm9rZS13aWR0aD0iMSIgc3Ryb2tlLWRhc2hhcnJheT0iNCwzIi8+CgogIDwhLS0gRm9vdG5vdGUgLS0+CiAgPHRleHQgeD0iNDgwIiB5PSI1NzYiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTEiIGZvbnQtc3R5bGU9Iml0YWxpYyIgZmlsbD0iIzU1NSI+QVVUT1NBUiBPUyBpcyBhIGJhY2t3YXJkLWNvbXBhdGlibGUgc3VwZXJzZXQgb2YgT1NFSyBPUyDigJQgbWVtb3J5L3RpbWluZyBwcm90ZWN0aW9uLCBtdWx0aWNvcmUsIHNjYWxhYmlsaXR5IGNsYXNzZXMgU0Mx4oCTU0M0PC90ZXh0PgoKICA8IS0tIEFiYnJldmlhdGlvbiBrZXkgLS0+CiAgPHRleHQgeD0iNDgwIiB5PSI1OTIiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTAiIGZpbGw9IiM1NTU1NTUiPkFSWE1MID0gQVVUT1NBUidzIGJ1aWxkLXRpbWUgWE1MIGNvbmZpZ3VyYXRpb24gJiMxODM7IFVEUyA9IHVuaWZpZWQgZGlhZ25vc3RpYyBzZXJ2aWNlcyAoSVNPIDE0MjI5KSAmIzE4MzsgRENNICsgREVNID0gZGlhZ25vc3RpYyBjb21tdW5pY2F0aW9uIG1hbmFnZXIgKyBkaWFnbm9zdGljIGV2ZW50IG1hbmFnZXIgKGZhdWx0IG1lbW9yeSk8L3RleHQ+Cjwvc3ZnPgo=" />

---

## The three layers, and the one escape hatch

- CP has three top-level layers: **Application → Runtime Environment (RTE) → Basic Software
  (BSW)**. The BSW splits into three horizontal layers plus one vertical bypass:

| BSW sub-layer | What it does | Firmware analogy |
|---|---|---|
| **Services** (top) | OS, comms + network mgmt, NVRAM, diagnostics, ECU-state mgmt | your middleware: UDS server, EEPROM mgr, watchdog kicker |
| **ECU Abstraction** | abstracts *board* wiring — which peripheral a signal routes through | your board-support glue |
| **MCAL** (bottom) | register-level access to on-chip peripherals; MCU-specific, silicon-vendor-supplied | **the vendor HAL, made standard** — you *port* it, not rewrite |
| **CDD** (vertical) | sanctioned escape hatch: may touch hardware directly for non-standard / extreme-timing needs | a bare-metal ISR that bypasses your own abstraction |

- Drivers you know by register — Dio, Port, Adc, Pwm, Spi, Can, Wdg, Mcu — live in **MCAL**
  behind a fixed API and generated config

<div class="gloss">RTE = Runtime Environment · BSW = Basic Software · MCAL = Microcontroller Abstraction Layer · NVRAM = non-volatile RAM · CDD = Complex Device Driver · HAL = hardware abstraction layer · ISR = interrupt service routine · the CDD legitimately breaks the layering — the standard sanctions it</div>

---

## The relocation trick — SWCs, the VFB, and why the RTE is generated

- Application logic is packaged as **Software Components (SWCs)** exposing **ports** typed by
  interfaces — mainly **sender-receiver** (data-flow) and **client-server** (operation). Code
  is organized as **runnable entities**, each ultimately *"a C function"* fired by RTE Events
- **SWCs never call each other directly.** They talk over the **Virtual Functional Bus (VFB)**
  — a *logical* concept spanning ECUs. The thing that actually implements the VFB on a real
  ECU is the **RTE**, generated per deployment
- RTE generation has two phases: **contract phase** (emits `Rte_<SWC>.h` so a SWC compiles in
  isolation) and **generation phase** (emits the real code that moves data / dispatches runnables)
- SWC code calls **`Rte_Write()` / `Rte_Read()` / `Rte_Call()`** — and *never knows* whether the
  peer is a runnable on the **same** ECU (a local buffer copy) or a **remote** one (a COM
  message over CAN/Ethernet)
- **This is why the same SWC relocates to a different ECU without code changes** — it
  references only ports and `Rte_*` symbols, never a bus or a driver. Moving it changes only
  what the RTE generator emits. **There is no real bare-metal analogue to this**

<div class="gloss">SWC = Software Component · VFB = Virtual Functional Bus · runnable = the schedulable C-function unit inside a SWC · COM = the AUTOSAR signal-packing communication module · deployment (which SWC runs on which ECU) is a late-binding config decision realized by regenerating the RTE</div>

---

## AUTOSAR OS — OSEK heritage, plus scalability classes

- AUTOSAR OS is a **backward-compatible superset of OSEK/VDX OS (ISO 17356-3)** — *not* "= OSEK".
  It keeps OSEK's core: static tasks, fixed-priority preemptive scheduling, priority-ceiling
  resources, events, alarms, counters, Cat-1 vs Cat-2 ISRs. **Know OSEK → you know ~70% of it**
- What AUTOSAR bundled on top, as **Scalability Classes**:

| Class | = | Adds |
|---|---|---|
| **SC1** | OSEK OS + | **Schedule Tables** (time-triggered, sync to global time), stack monitoring |
| **SC2** | SC1 + | **Timing Protection** (execution / inter-arrival budgets) + global time sync |
| **SC3** | SC1 + | **Memory Protection** + OS-Applications + trusted/non-trusted functions |
| **SC4** | SC2+SC3 | both timing and memory protection |

- **Multicore** arrived in release **4.0 (2009)**: multi-core startup, **spinlocks**, and
  **IOC** (Inter-OS-Application Communication) — a spinlock-protected shared-memory ring for
  data crossing a core/partition boundary

<div class="gloss">OSEK/VDX = the 1990s automotive RTOS standard · ISR = interrupt service routine (Cat-1 = no OS calls, lowest latency; Cat-2 = may call OS services) · SC = Scalability Class · IOC = Inter-OS-Application Communication · exact SC1–SC4 wording is medium-confidence (structure high) — see references</div>

---

## The model-driven workflow — ARXML and the OEM↔supplier handshake

- Everything is exchanged as **ARXML** ("AUTOSAR XML"), a fixed-schema format that is **rarely
  hand-authored** — GUI configuration tools produce and consume it. The classic flow:
  1. **System / VFB Description** (OEM) — all SWCs, ports, topology, signals → System Config
  2. **ECU Extract** — the slice for *one* ECU, handed to the Tier-1 supplier
  3. **ECU Configuration (ECUC)** — supplier configures that ECU's BSW + RTE
  4. **Generation** — tools emit BSW config, the RTE and OS config; compiles with hand-written
     SWC code + vendor MCAL into **one ECU executable**
- **Dominant toolchains**: **Vector DaVinci** (Developer + Configurator), **EB tresos Studio**,
  **ETAS ISOLAR / RTA-CAR**. MCU vendors ship the MCAL matching each toolchain
- **Language rule**: BSW/RTE code is **C** and must be **MISRA C** — 4.2 required C:2004; **4.3
  and later (incl. R25-11) require MISRA C:2012**. (C++14 is an *Adaptive* concern — easy to conflate)
- **What is genuinely new** for a bare-metal + RTOS engineer is not the OS or the HAL — it's the
  **generate-then-compile workflow** and the **ARXML handshake**, an artefact with no firmware-world equivalent

<div class="gloss">ARXML = AUTOSAR XML config format · ECUC = ECU Configuration Description · Tier-1 = the supplier who builds an ECU for the OEM · MISRA C = the automotive safe-C coding-rule set · MCAL = Microcontroller Abstraction Layer</div>

---

<!-- _class: diagram -->

<img alt="cp-signal-path" src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA5NjAgNjIwIiB3aWR0aD0iOTYwIiBoZWlnaHQ9IjYyMCIgZm9udC1mYW1pbHk9IkhlbHZldGljYSwgQXJpYWwsIHNhbnMtc2VyaWYiPgogIDxyZWN0IHg9IjAiIHk9IjAiIHdpZHRoPSI5NjAiIGhlaWdodD0iNjIwIiBmaWxsPSIjZmZmZmZmIi8+CgogIDxkZWZzPgogICAgPG1hcmtlciBpZD0iYXJyIiBtYXJrZXJXaWR0aD0iMTAiIG1hcmtlckhlaWdodD0iMTAiIHJlZlg9IjgiIHJlZlk9IjMiIG9yaWVudD0iYXV0byIgbWFya2VyVW5pdHM9InN0cm9rZVdpZHRoIj4KICAgICAgPHBhdGggZD0iTTAsMCBMOSwzIEwwLDYgeiIgZmlsbD0iIzQ0NCIvPgogICAgPC9tYXJrZXI+CiAgICA8bWFya2VyIGlkPSJhcnJiIiBtYXJrZXJXaWR0aD0iMTAiIG1hcmtlckhlaWdodD0iMTAiIHJlZlg9IjgiIHJlZlk9IjMiIG9yaWVudD0iYXV0byIgbWFya2VyVW5pdHM9InN0cm9rZVdpZHRoIj4KICAgICAgPHBhdGggZD0iTTAsMCBMOSwzIEwwLDYgeiIgZmlsbD0iIzdmOWRjOSIvPgogICAgPC9tYXJrZXI+CiAgPC9kZWZzPgoKICA8IS0tIFRpdGxlIC0tPgogIDx0ZXh0IHg9IjQ4MCIgeT0iMzgiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMjYiIGZvbnQtd2VpZ2h0PSI3MDAiIGZpbGw9IiMxYjJiNGEiPkNsYXNzaWMgUGxhdGZvcm0g4oCUIHNpZ25hbCDihpIgUERVIOKGkiBmcmFtZSwgZnJvemVuIGF0IGJ1aWxkIHRpbWU8L3RleHQ+CgogIDwhLS0gPT09PT09PT09PT09PT09PT09PT09IExlZnQgY2FsbC1vdXQgYmFuZDogSy1tYXRyaXggPT09PT09PT09PT09PT09PT09PT09IC0tPgogIDxyZWN0IHg9IjE0IiB5PSI3MiIgd2lkdGg9IjE1MCIgaGVpZ2h0PSI0MTQiIHJ4PSI4IiBmaWxsPSIjRkNFOEQ1IiBzdHJva2U9IiNFMEE5NkQiIHN0cm9rZS13aWR0aD0iMS41Ii8+CiAgPHRleHQgeD0iODkiIHk9IjkzIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjkuNSIgZm9udC13ZWlnaHQ9IjcwMCIgZmlsbD0iIzZCNEEyQiI+U3RhdGljYWxseSBnZW5lcmF0ZWQ8L3RleHQ+CiAgPHRleHQgeD0iODkiIHk9IjEwNiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSI5LjUiIGZvbnQtd2VpZ2h0PSI3MDAiIGZpbGw9IiM2QjRBMkIiPmZyb20gdGhlIGNvbW11bmljYXRpb248L3RleHQ+CiAgPHRleHQgeD0iODkiIHk9IjExOSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSI5LjUiIGZvbnQtd2VpZ2h0PSI3MDAiIGZpbGw9IiM2QjRBMkIiPm1hdHJpeCAoSy1tYXRyaXgpPC90ZXh0PgogIDx0ZXh0IHg9Ijg5IiB5PSIxNDIiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iOC41IiBmaWxsPSIjNkI0QTJCIj5FdmVyeSBmcmFtZS9QRFUsIHNpZ25hbCw8L3RleHQ+CiAgPHRleHQgeD0iODkiIHk9IjE1NCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSI4LjUiIGZpbGw9IiM2QjRBMkIiPnNlbmRlciwgcmVjZWl2ZXJzLCBieXRlPC90ZXh0PgogIDx0ZXh0IHg9Ijg5IiB5PSIxNjYiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iOC41IiBmaWxsPSIjNkI0QTJCIj5sYXlvdXQsIHRpbWluZyAmYW1wOyBlbmNvZGluZzwvdGV4dD4KICA8dGV4dCB4PSI4OSIgeT0iMTc4IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjguNSIgZmlsbD0iIzZCNEEyQiI+YXJlIGZpeGVkIGF0IEJVSUxEIFRJTUUuPC90ZXh0PgogIDx0ZXh0IHg9Ijg5IiB5PSIyMDIiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iOC41IiBmaWxsPSIjNkI0QTJCIj5JbXBvcnRlZCBmcm9tIERCQyAvIExERiAvPC90ZXh0PgogIDx0ZXh0IHg9Ijg5IiB5PSIyMTQiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iOC41IiBmaWxsPSIjNkI0QTJCIj5GSUJFWCwgY2FycmllZCBhcyBBUlhNTC48L3RleHQ+CiAgPHRleHQgeD0iODkiIHk9IjIzOCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSI4LjUiIGZpbGw9IiM2QjRBMkIiPkEgZ2l2ZW4gRUNVIG9ubHkgZXZlcjwvdGV4dD4KICA8dGV4dCB4PSI4OSIgeT0iMjUwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjguNSIgZmlsbD0iIzZCNEEyQiI+c2VlcyB0aGUgUERVcyBjb25maWd1cmVkPC90ZXh0PgogIDx0ZXh0IHg9Ijg5IiB5PSIyNjIiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iOC41IiBmaWxsPSIjNkI0QTJCIj5mb3IgaXQuPC90ZXh0PgogIDx0ZXh0IHg9Ijg5IiB5PSI0NzAiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iOC41IiBmb250LXN0eWxlPSJpdGFsaWMiIGZpbGw9IiM2QjRBMkIiPuKGkiBjb25maWd1cmVzIGV2ZXJ5IGxheWVyPC90ZXh0PgoKICA8IS0tID09PT09PT09PT09PT09PT09PT09PSBUWCBhcnJvdyAobGVmdCBvZiBjb2x1bW4pID09PT09PT09PT09PT09PT09PT09PSAtLT4KICA8bGluZSB4MT0iMTg2IiB5MT0iODAiIHgyPSIxODYiIHkyPSI0NDAiIHN0cm9rZT0iIzQ0NCIgc3Ryb2tlLXdpZHRoPSIyLjIiIG1hcmtlci1lbmQ9InVybCgjYXJyKSIvPgogIDx0ZXh0IHg9IjE4NiIgeT0iNjYiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTIiIGZvbnQtd2VpZ2h0PSI3MDAiIGZpbGw9IiM0NDQiPlRYPC90ZXh0PgogIDx0ZXh0IHg9IjE3OCIgeT0iMjYwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjkuNSIgZm9udC13ZWlnaHQ9IjcwMCIgZmlsbD0iIzY2NiIgdHJhbnNmb3JtPSJyb3RhdGUoLTkwIDE3OCAyNjApIj5hcHBsaWNhdGlvbiDihpIgQ0FOIHdpcmU8L3RleHQ+CgogIDwhLS0gPT09PT09PT09PT09PT09PT09PT09IFJYIGFycm93IChyaWdodCBvZiBjb2x1bW4pID09PT09PT09PT09PT09PT09PT09PSAtLT4KICA8bGluZSB4MT0iNTg0IiB5MT0iNDQwIiB4Mj0iNTg0IiB5Mj0iODAiIHN0cm9rZT0iIzdmOWRjOSIgc3Ryb2tlLXdpZHRoPSIyLjIiIG1hcmtlci1lbmQ9InVybCgjYXJyYikiLz4KICA8dGV4dCB4PSI1ODQiIHk9IjY2IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjEyIiBmb250LXdlaWdodD0iNzAwIiBmaWxsPSIjNWY4MmI4Ij5SWCAobWlycm9yKTwvdGV4dD4KICA8dGV4dCB4PSI1OTYiIHk9IjI2MCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSI5LjUiIGZvbnQtd2VpZ2h0PSI3MDAiIGZpbGw9IiM3ZjlkYzkiIHRyYW5zZm9ybT0icm90YXRlKC05MCA1OTYgMjYwKSI+Q0FOIHdpcmUg4oaSIGFwcGxpY2F0aW9uPC90ZXh0PgoKICA8IS0tID09PT09PT09PT09PT09PT09PT09PSBNYWluIGNvbHVtbiA9PT09PT09PT09PT09PT09PT09PT0gLS0+CiAgPCEtLSAxLiBTVy1DIC8gUlRFIC0tPgogIDxyZWN0IHg9IjIwNiIgeT0iNzIiIHdpZHRoPSIzNjAiIGhlaWdodD0iNTQiIHJ4PSI4IiBmaWxsPSIjRUFGMUZCIiBzdHJva2U9IiM5QkJDRTAiIHN0cm9rZS13aWR0aD0iMS41Ii8+CiAgPHRleHQgeD0iMzg2IiB5PSI5MyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMyIgZm9udC13ZWlnaHQ9IjcwMCIgZmlsbD0iIzIyMzM0NCI+U1ctQyAvIFJURTwvdGV4dD4KICA8dGV4dCB4PSIzODYiIHk9IjExMiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMC41IiBmaWxsPSIjMjIzMzQ0Ij5hcHBsaWNhdGlvbiB3cml0ZXMgYSB2YWx1ZTsgUlRFIGNhbGxzIENvbV9TZW5kU2lnbmFsKCk8L3RleHQ+CiAgPGxpbmUgeDE9IjM4NiIgeTE9IjEyNiIgeDI9IjM4NiIgeTI9IjEzOCIgc3Ryb2tlPSIjNDQ0IiBzdHJva2Utd2lkdGg9IjIiIG1hcmtlci1lbmQ9InVybCgjYXJyKSIvPgoKICA8IS0tIDIuIENPTSAtLT4KICA8cmVjdCB4PSIyMDYiIHk9IjEzOCIgd2lkdGg9IjM2MCIgaGVpZ2h0PSI3NCIgcng9IjgiIGZpbGw9IiNEQ0U5RjciIHN0cm9rZT0iIzdmOWRjOSIgc3Ryb2tlLXdpZHRoPSIxLjUiLz4KICA8dGV4dCB4PSIzODYiIHk9IjE1OCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMyIgZm9udC13ZWlnaHQ9IjcwMCIgZmlsbD0iIzIyMzM0NCI+Q09NPC90ZXh0PgogIDx0ZXh0IHg9IjM4NiIgeT0iMTc0IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjEwIiBmaWxsPSIjMjIzMzQ0Ij5wYWNrcyB0aGUgc2lnbmFsIGludG8gYW4gSS1QRFUg4oCUIGJpdCBwb3NpdGlvbiwgbGVuZ3RoLDwvdGV4dD4KICA8dGV4dCB4PSIzODYiIHk9IjE4OCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMCIgZmlsbD0iIzIyMzM0NCI+ZW5kaWFubmVzcywgc2lnbiBleHRlbnNpb24gYWxsIHJlc29sdmVkIGF0IEJVSUxEIFRJTUU8L3RleHQ+CiAgPHRleHQgeD0iMzg2IiB5PSIyMDMiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iOS41IiBmaWxsPSIjMjIzMzQ0Ij5hcHBsaWVzIFRYIG1vZGVzIChwZXJpb2RpYyAvIG9uLWNoYW5nZSkgKyBtaW5pbXVtIGRlbGF5PC90ZXh0PgogIDxsaW5lIHgxPSIzODYiIHkxPSIyMTIiIHgyPSIzODYiIHkyPSIyMjQiIHN0cm9rZT0iIzQ0NCIgc3Ryb2tlLXdpZHRoPSIyIiBtYXJrZXItZW5kPSJ1cmwoI2FycikiLz4KCiAgPCEtLSBDT00gdHJhbnNmb3JtZXIgc2lkZSBib3ggLS0+CiAgPGxpbmUgeDE9IjU2NiIgeTE9IjE3NiIgeDI9IjYwNiIgeTI9IjE3NiIgc3Ryb2tlPSIjOEZCRjhGIiBzdHJva2Utd2lkdGg9IjEuNSIgbWFya2VyLWVuZD0idXJsKCNhcnIpIi8+CiAgPHJlY3QgeD0iNjA2IiB5PSIxMzIiIHdpZHRoPSIzNDAiIGhlaWdodD0iODgiIHJ4PSI4IiBmaWxsPSIjREZGMEQ4IiBzdHJva2U9IiM4RkJGOEYiIHN0cm9rZS13aWR0aD0iMS41Ii8+CiAgPHRleHQgeD0iNzc2IiB5PSIxNTAiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTEiIGZvbnQtd2VpZ2h0PSI3MDAiIGZpbGw9IiMyZDVhMmQiPlRyYW5zZm9ybWVyIGNoYWluIChpbnNpZGUgQ09NKTwvdGV4dD4KICA8dGV4dCB4PSI3NzYiIHk9IjE3MCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSI5LjUiIGZpbGw9IiMyZDVhMmQiPkUyRSBwcm90ZWN0aW9uIOKAlCBDUkMgKyBjb3VudGVyICsgRGF0YSBJRDwvdGV4dD4KICA8dGV4dCB4PSI3NzYiIHk9IjE4NiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSI5LjUiIGZpbGw9IiMyZDVhMmQiPlNlY09DIOKAlCBNQUMgKyBmcmVzaG5lc3MgKG5vIGVuY3J5cHRpb24pPC90ZXh0PgogIDx0ZXh0IHg9Ijc3NiIgeT0iMjAyIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjkuNSIgZmlsbD0iIzJkNWEyZCI+U29tZUlwWGYg4oCUIFNPTUUvSVAgc2VyaWFsaXphdGlvbjwvdGV4dD4KCiAgPCEtLSAzLiBQZHVSIC0tPgogIDxyZWN0IHg9IjIwNiIgeT0iMjI0IiB3aWR0aD0iMzYwIiBoZWlnaHQ9IjU4IiByeD0iOCIgZmlsbD0iI0RDRTlGNyIgc3Ryb2tlPSIjN2Y5ZGM5IiBzdHJva2Utd2lkdGg9IjEuNSIvPgogIDx0ZXh0IHg9IjM4NiIgeT0iMjQ0IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjEyLjUiIGZvbnQtd2VpZ2h0PSI3MDAiIGZpbGw9IiMyMjMzNDQiPlBkdVIg4oCUIFBEVSBSb3V0ZXI8L3RleHQ+CiAgPHRleHQgeD0iMzg2IiB5PSIyNjEiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTAiIGZpbGw9IiMyMjMzNDQiPnN0YXRpYyByb3V0aW5nIHRhYmxlIGZvcndhcmRzIHRoZSBJLVBEVSB0byBDYW5JZjwvdGV4dD4KICA8dGV4dCB4PSIzODYiIHk9IjI3NSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSI5LjUiIGZpbGw9IiMyMjMzNDQiPihvciB0byBDYW5UcCBmaXJzdCBpZiBsYXJnZSk7IGFsc28gYnVzLXRvLWJ1cyBnYXRld2F5IHJvdXRpbmc8L3RleHQ+CgogIDwhLS0gQ2FuVHAgY29uZGl0aW9uYWwgc2lkZSBib3ggKGRhc2hlZCkgLS0+CiAgPGxpbmUgeDE9IjU2NiIgeTE9IjI1NCIgeDI9IjYwNiIgeTI9IjI1NCIgc3Ryb2tlPSIjN2Y5ZGM5IiBzdHJva2Utd2lkdGg9IjEuNSIgc3Ryb2tlLWRhc2hhcnJheT0iNiw0IiBtYXJrZXItZW5kPSJ1cmwoI2FycmIpIi8+CiAgPHJlY3QgeD0iNjA2IiB5PSIyMjgiIHdpZHRoPSIzNDAiIGhlaWdodD0iNjQiIHJ4PSI4IiBmaWxsPSIjRUFGMUZCIiBzdHJva2U9IiM5QkJDRTAiIHN0cm9rZS13aWR0aD0iMS41IiBzdHJva2UtZGFzaGFycmF5PSI2LDQiLz4KICA8dGV4dCB4PSI3NzYiIHk9IjI0OCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMSIgZm9udC13ZWlnaHQ9IjcwMCIgZmlsbD0iIzIyMzM0NCI+Q2FuVHAg4oCUIG9ubHkgaWYgUERVICZndDsgb25lIGZyYW1lPC90ZXh0PgogIDx0ZXh0IHg9Ijc3NiIgeT0iMjY1IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjkuNSIgZmlsbD0iIzIyMzM0NCI+c2VnbWVudHMgaW50byBGaXJzdCBGcmFtZSAvIENvbnNlY3V0aXZlIEZyYW1lczwvdGV4dD4KICA8dGV4dCB4PSI3NzYiIHk9IjI4MCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSI5LjUiIGZpbGw9IiMyMjMzNDQiPndpdGggZmxvdyBjb250cm9sIChJU08gMTU3NjUtMik8L3RleHQ+CgogIDxsaW5lIHgxPSIzODYiIHkxPSIyODIiIHgyPSIzODYiIHkyPSIyOTQiIHN0cm9rZT0iIzQ0NCIgc3Ryb2tlLXdpZHRoPSIyIiBtYXJrZXItZW5kPSJ1cmwoI2FycikiLz4KCiAgPCEtLSA0LiBDYW5JZiAtLT4KICA8cmVjdCB4PSIyMDYiIHk9IjI5NiIgd2lkdGg9IjM2MCIgaGVpZ2h0PSI1OCIgcng9IjgiIGZpbGw9IiNEQ0U5RjciIHN0cm9rZT0iIzdmOWRjOSIgc3Ryb2tlLXdpZHRoPSIxLjUiLz4KICA8dGV4dCB4PSIzODYiIHk9IjMxNiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMi41IiBmb250LXdlaWdodD0iNzAwIiBmaWxsPSIjMjIzMzQ0Ij5DYW5JZiDigJQgRUNVIEFic3RyYWN0aW9uPC90ZXh0PgogIDx0ZXh0IHg9IjM4NiIgeT0iMzMzIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjEwIiBmaWxsPSIjMjIzMzQ0Ij5tYXBzIHRoZSBhYnN0cmFjdCBQRFUgdG8gYSBoYXJkd2FyZSB0cmFuc21pdCBoYW5kbGUgLzwvdGV4dD4KICA8dGV4dCB4PSIzODYiIHk9IjM0NyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMCIgZmlsbD0iIzIyMzM0NCI+bWFpbGJveDsgbWFuYWdlcyBjb250cm9sbGVyICZhbXA7IFBEVSBtb2RlPC90ZXh0PgogIDxsaW5lIHgxPSIzODYiIHkxPSIzNTQiIHgyPSIzODYiIHkyPSIzNjYiIHN0cm9rZT0iIzQ0NCIgc3Ryb2tlLXdpZHRoPSIyIiBtYXJrZXItZW5kPSJ1cmwoI2FycikiLz4KCiAgPCEtLSA1LiBDYW5EcnYgLS0+CiAgPHJlY3QgeD0iMjA2IiB5PSIzNjYiIHdpZHRoPSIzNjAiIGhlaWdodD0iNjAiIHJ4PSI4IiBmaWxsPSIjRENFOUY3IiBzdHJva2U9IiM3ZjlkYzkiIHN0cm9rZS13aWR0aD0iMS41Ii8+CiAgPHRleHQgeD0iMzg2IiB5PSIzODYiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTIuNSIgZm9udC13ZWlnaHQ9IjcwMCIgZmlsbD0iIzIyMzM0NCI+Q2FuRHJ2IOKAlCBNQ0FMPC90ZXh0PgogIDx0ZXh0IHg9IjM4NiIgeT0iNDAzIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjEwIiBmaWxsPSIjMjIzMzQ0Ij53cml0ZXMgdGhlIENBTiAvIENBTiBGRCBmcmFtZTsgdHJhbnNtaXQgY29uZmlybWF0aW9uPC90ZXh0PgogIDx0ZXh0IHg9IjM4NiIgeT0iNDE3IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjkuNSIgZmlsbD0iIzIyMzM0NCI+cHJvcGFnYXRlcyBiYWNrIHVwIChDYW5JZiDihpIgUGR1UiDihpIgQ09NIOKGkiBSVEUpPC90ZXh0PgogIDxsaW5lIHgxPSIzODYiIHkxPSI0MjYiIHgyPSIzODYiIHkyPSI0NDQiIHN0cm9rZT0iIzQ0NCIgc3Ryb2tlLXdpZHRoPSIyIiBtYXJrZXItZW5kPSJ1cmwoI2FycikiLz4KCiAgPCEtLSBCdXMgYmFyIC0tPgogIDxyZWN0IHg9IjIwNiIgeT0iNDQ2IiB3aWR0aD0iMzYwIiBoZWlnaHQ9IjQwIiByeD0iOCIgZmlsbD0iI0VDRUNFQyIgc3Ryb2tlPSIjQjBCMEIwIiBzdHJva2Utd2lkdGg9IjEuNSIvPgogIDx0ZXh0IHg9IjM4NiIgeT0iNDcxIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjEyLjUiIGZvbnQtd2VpZ2h0PSI3MDAiIGZpbGw9IiMzMzMiPkNBTiAvIENBTiBGRCBidXM8L3RleHQ+CgogIDwhLS0gPT09PT09PT09PT09PT09PT09PT09IFJYIG5vdGUgPT09PT09PT09PT09PT09PT09PT09IC0tPgogIDxyZWN0IHg9IjYwNiIgeT0iMzIyIiB3aWR0aD0iMzQwIiBoZWlnaHQ9IjExOCIgcng9IjgiIGZpbGw9IiNGNEY0RjQiIHN0cm9rZT0iI0IwQjBCMCIgc3Ryb2tlLXdpZHRoPSIxLjUiLz4KICA8dGV4dCB4PSI3NzYiIHk9IjM0MiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMC41IiBmb250LXdlaWdodD0iNzAwIiBmaWxsPSIjMzMzIj5SWCBtaXJyb3JzIFRYICh3aXJlIOKGkiBhcHBsaWNhdGlvbik8L3RleHQ+CiAgPHRleHQgeD0iNzc2IiB5PSIzNjIiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iOS41IiBmaWxsPSIjMzMzIj5DYW5EcnYgSVNSIOKGkiBDYW5JZiBpbmRpY2F0aW9uIOKGkiBQZHVSIOKGkjwvdGV4dD4KICA8dGV4dCB4PSI3NzYiIHk9IjM3NyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSI5LjUiIGZpbGw9IiMzMzMiPihDYW5UcCByZWFzc2VtYmx5KSDihpIgQ09NIHVucGFja3MgYnl0ZXMgaW50bzwvdGV4dD4KICA8dGV4dCB4PSI3NzYiIHk9IjM5MiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSI5LjUiIGZpbGw9IiMzMzMiPnNpZ25hbHMgKyByZWNlcHRpb24gZGVhZGxpbmUgbW9uaXRvcmluZyDihpI8L3RleHQ+CiAgPHRleHQgeD0iNzc2IiB5PSI0MDciIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iOS41IiBmaWxsPSIjMzMzIj5SVEUgZGVsaXZlcnMgdG8gdGhlIFNXLUM8L3RleHQ+CgogIDwhLS0gPT09PT09PT09PT09PT09PT09PT09IEZvb3Rub3RlIC8gZ2xvc3MgPT09PT09PT09PT09PT09PT09PT09IC0tPgogIDx0ZXh0IHg9IjQ4MCIgeT0iNTU4IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjkuNSIgZmlsbD0iIzU1NTU1NSI+U1ctQyA9IFNvZnR3YXJlIENvbXBvbmVudCDCtyBSVEUgPSBSdW50aW1lIEVudmlyb25tZW50IMK3IENPTSA9IHNpZ25hbC1wYWNraW5nIG1vZHVsZSDCtyBJLVBEVSA9IEludGVyYWN0aW9uLWxheWVyIFByb3RvY29sIERhdGEgVW5pdCDCtyBQZHVSID0gUERVIFJvdXRlciDCtyBDYW5UcCA9IENBTiBUcmFuc3BvcnQgTGF5ZXI8L3RleHQ+CiAgPHRleHQgeD0iNDgwIiB5PSI1NzQiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iOS41IiBmaWxsPSIjNTU1NTU1Ij5DYW5JZiA9IENBTiBJbnRlcmZhY2UgwrcgTUNBTCA9IE1pY3JvY29udHJvbGxlciBBYnN0cmFjdGlvbiBMYXllciDCtyBFMkUgPSBFbmQtdG8tRW5kIHByb3RlY3Rpb24gwrcgU2VjT0MgPSBTZWN1cmUgT25ib2FyZCBDb21tdW5pY2F0aW9uIMK3IFNvbWVJcFhmID0gU09NRS9JUCBUcmFuc2Zvcm1lcjwvdGV4dD4KICA8dGV4dCB4PSI0ODAiIHk9IjU5MiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSI5LjUiIGZvbnQtc3R5bGU9Iml0YWxpYyIgZmlsbD0iIzU1NSI+U3ludGhlc2l6ZWQgZnJvbSB0aGUgQVVUT1NBUiBDUCBTV1MgZG9jdW1lbnRzOiBDT00gwrcgUGR1UiDCtyBDYW5UcCDCtyBDYW5JZjwvdGV4dD4KPC9zdmc+Cg==" />

---

## The frozen communication matrix

- CP communication is **signal-oriented and frozen at build time** — a layered pipeline of BSW
  modules, each doing one abstraction step (see the previous diagram)
- The **communication matrix (K-matrix)** is the master description of *all* network
  communication in the vehicle: every frame/PDU, every signal, sender ECU, receivers, byte
  layout, timing, value encoding. It is frozen because CP targets small-flash, deterministic,
  ASIL ECUs — so COM's packing, PduR's routing and CanIf's handle map are all **statically
  generated** and provable at integration time
- **File-format lineage**: **DBC** (Vector, CAN), **LDF** (LIN), **FIBEX** (ASAM, multi-bus),
  and AUTOSAR's own **ARXML** carrier. It is the CAN message database (DBC) you know — promoted
  to a whole-vehicle, multi-bus, code-generating source of truth
- **Bus landscape 2026**: **CAN FD** mainstream (up to 64-byte payload); classic CAN survives
  for low-cost nodes; **FlexRay in decline** (still specified, not removed); **Automotive
  Ethernet (100/1000BASE-T1, TSN)** is the growth path, carrying SOME/IP and DoIP
- **CAN XL** (ISO 11898-1:2024, up to 2048-byte payloads) is emerging — AUTOSAR support release
  unconfirmed (open question)

<div class="gloss">PDU = Protocol Data Unit (the byte array a signal is packed into) · PduR = PDU Router · CanIf = CAN Interface · ASIL = Automotive Safety Integrity Level (ISO 26262, QM < A < B < C < D) · TSN = Time-Sensitive Networking (IEEE 802.1) · CAN FD = CAN with Flexible Data-rate</div>

---

## E2E and SecOC — protect the data, not the channel

- **E2E (End-to-End) protection** guards safety-relevant data per ISO 26262. It's a
  transformer in the COM chain, so protection travels **with the payload across ECU and bus
  boundaries — including through PduR gateways**: CRC + counter computed at the true sender,
  checked at the true receiver, so a gateway can't silently corrupt safety data
- Fault model: repetition, loss, delay, insertion, masquerade, wrong sequence, corruption…
  Mechanisms: a **CRC**, a **counter**, **timeout monitoring**, and a **Data ID** folded in.
  Profiles range **P1/P2/P11/P22 (8-bit)** · **P5/P6 (16-bit)** · **P4 (32-bit)** · **P7 (64-bit)**
  — 8-bit profiles *cannot* detect a masquerade fault in a single cycle
- **SecOC (Secure Onboard Communication)** adds **authenticity + freshness** — **it does NOT
  encrypt.** The payload stays in the clear. TX builds a **Secured I-PDU** = data +
  **Authenticator (a MAC)** + optional **Freshness Value**, using **CMAC / AES-128** (NIST
  SP 800-38B); the MAC is **truncated** to fit tight CAN payloads (a bandwidth/security tradeoff)
- **Honest guarantee**: a verified MAC proves the message came from a holder of the shared
  symmetric key and is fresh (defeats replay) — it does **not** hide data and gives **no
  non-repudiation**. Keys come from the Crypto stack, out of SecOC's scope

<div class="gloss">E2E = End-to-End · CRC = Cyclic Redundancy Check · Data ID = a per-signal identifier mixed into the CRC · SecOC = Secure Onboard Communication · MAC = Message Authentication Code · CMAC = Cipher-based MAC · "no confidentiality" is inferred from the PRS scope — medium confidence</div>

---

## Diagnostics — DEM computes, DCM formats (get this split right)

- **The #1 conceptual error to avoid**: **DEM is the fault database; DCM is the protocol
  server that reads it and talks to the tester.** DCM computes nothing about faults
- **DEM (Diagnostic Event Manager)** is the fault memory. SWCs report a monitor result
  (Passed/Failed) via `Dem_SetEventStatus`; DEM **debounces** it (counter / time / monitor-
  internal), decides when a fault is mature, maintains the per-DTC **8-bit UDS status byte**
  (bit 0 `testFailed` … bit 3 `confirmedDTC` … bit 7 `warningIndicatorRequested`), and stores
  freeze frames to NvM — it is a *client* of the memory stack, it never touches flash itself
- **DCM (Diagnostic Communication Manager)** is a generated, dumb-but-strict **UDS server**. On
  `0x19 ReadDTCInformation` it calls into DEM and formats the answer. It also runs **OBD
  $01–$0A** (J1979) side by side
- **FiM (Function Inhibition Manager)** is the third leg: DEM informs FiM on status change, and
  FiM **inhibits monitors** that would give false readings — prevents cascade/false DTCs
- **OBD vs UDS**: **UDS (ISO 14229) is contractual**; **OBD $01–$0A is statutory — and only for
  emissions ECUs**. A body/comfort ECU has no OBD duty; it serves only UDS

<div class="gloss">DEM = Diagnostic Event Manager · DCM = Diagnostic Communication Manager · FiM = Function Inhibition Manager · DTC = Diagnostic Trouble Code · DID = Data Identifier · NvM = the non-volatile-memory manager · OBD = On-Board Diagnostics · J1979 = SAE emissions-diagnostic standard · a DID read (0x22) checks the DID exists + session + security, then binds to an RTE port or read callout</div>

---

<!-- _class: diagram -->

<img alt="uds-diag-stack" src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA5NjAgNjAwIiB3aWR0aD0iOTYwIiBoZWlnaHQ9IjYwMCIgZm9udC1mYW1pbHk9IkhlbHZldGljYSwgQXJpYWwsIHNhbnMtc2VyaWYiPgogIDxyZWN0IHg9IjAiIHk9IjAiIHdpZHRoPSI5NjAiIGhlaWdodD0iNjAwIiBmaWxsPSIjZmZmZmZmIi8+CgogIDxkZWZzPgogICAgPG1hcmtlciBpZD0iYXJyIiBtYXJrZXJXaWR0aD0iMTAiIG1hcmtlckhlaWdodD0iMTAiIHJlZlg9IjgiIHJlZlk9IjMiIG9yaWVudD0iYXV0byIgbWFya2VyVW5pdHM9InN0cm9rZVdpZHRoIj4KICAgICAgPHBhdGggZD0iTTAsMCBMOSwzIEwwLDYgeiIgZmlsbD0iIzQ0NCIvPgogICAgPC9tYXJrZXI+CiAgPC9kZWZzPgoKICA8IS0tIFRpdGxlIC0tPgogIDx0ZXh0IHg9IjQ4MCIgeT0iNDAiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMjYiIGZvbnQtd2VpZ2h0PSI3MDAiIGZpbGw9IiMxYjJiNGEiPlVEUyAoSVNPIDE0MjI5KSDigJQgb25lIGRpYWdub3N0aWMgbGFuZ3VhZ2UsIHR3byB0cmFuc3BvcnRzLCB0d28gcGxhdGZvcm1zPC90ZXh0PgoKICA8IS0tID09PT09PT09PT09PT09PT09PT09PSBEaWFnbm9zdGljIGNsaWVudCAodG9wKSA9PT09PT09PT09PT09PT09PT09PT0gLS0+CiAgPHJlY3QgeD0iMjUwIiB5PSI2NCIgd2lkdGg9IjQ2MCIgaGVpZ2h0PSI0NCIgcng9IjgiIGZpbGw9IiNERkYwRDgiIHN0cm9rZT0iIzhGQkY4RiIgc3Ryb2tlLXdpZHRoPSIxLjUiLz4KICA8dGV4dCB4PSI0ODAiIHk9IjkxIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjEzLjUiIGZpbGw9IiMyZDVhMmQiPkRpYWdub3N0aWMgY2xpZW50IOKAlCB3b3Jrc2hvcCB0ZXN0ZXIgwrcgZmxlZXQgYmFja2VuZCAodmlhIGdhdGV3YXkpPC90ZXh0PgoKICA8bGluZSB4MT0iNDgwIiB5MT0iMTA4IiB4Mj0iNDgwIiB5Mj0iMTIwIiBzdHJva2U9IiM0NDQiIHN0cm9rZS13aWR0aD0iMiIgbWFya2VyLWVuZD0idXJsKCNhcnIpIi8+CgogIDwhLS0gPT09PT09PT09PT09PT09PT09PT09IFVEUyBzZXJ2aWNlcyBzdHJpcCA9PT09PT09PT09PT09PT09PT09PT0gLS0+CiAgPHJlY3QgeD0iNjAiIHk9IjEyMiIgd2lkdGg9Ijg0MCIgaGVpZ2h0PSI1NiIgcng9IjgiIGZpbGw9IiNEQ0U5RjciIHN0cm9rZT0iIzdmOWRjOSIgc3Ryb2tlLXdpZHRoPSIxLjUiLz4KICA8dGV4dCB4PSI0ODAiIHk9IjE0MiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxNCIgZm9udC13ZWlnaHQ9IjcwMCIgZmlsbD0iIzIyMzM0NCI+VURTIHNlcnZpY2VzIChJU08gMTQyMjktMSwgYXBwbGljYXRpb24gbGF5ZXIpPC90ZXh0PgogIDx0ZXh0IHg9IjQ4MCIgeT0iMTYyIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjExIiBmaWxsPSIjMjIzMzQ0Ij4weDEwIHNlc3Npb24gwrcgMHgyNyBzZWN1cml0eSDCtyAweDIyIHJlYWQgRElEICgweEYxOTAgPSBWSU4pIMK3IDB4MTkgcmVhZCBEVEMgwrcgMHgzMSByb3V0aW5lIMK3IDB4MzQvMHgzNS8weDM2LzB4MzcgdHJhbnNmZXIgKGZsYXNoKTwvdGV4dD4KCiAgPGxpbmUgeDE9IjI2NSIgeTE9IjE3OCIgeDI9IjI2NSIgeTI9IjE5MiIgc3Ryb2tlPSIjNDQ0IiBzdHJva2Utd2lkdGg9IjIiIG1hcmtlci1lbmQ9InVybCgjYXJyKSIvPgogIDxsaW5lIHgxPSI2OTUiIHkxPSIxNzgiIHgyPSI2OTUiIHkyPSIxOTIiIHN0cm9rZT0iIzQ0NCIgc3Ryb2tlLXdpZHRoPSIyIiBtYXJrZXItZW5kPSJ1cmwoI2FycikiLz4KCiAgPCEtLSA9PT09PT09PT09PT09PT09PT09PT0gVHJhbnNwb3J0IGJveGVzID09PT09PT09PT09PT09PT09PT09PSAtLT4KICA8cmVjdCB4PSI2MCIgeT0iMTkyIiB3aWR0aD0iNDEwIiBoZWlnaHQ9IjU2IiByeD0iOCIgZmlsbD0iI0VBRjFGQiIgc3Ryb2tlPSIjOUJCQ0UwIiBzdHJva2Utd2lkdGg9IjEuNSIvPgogIDx0ZXh0IHg9IjI2NSIgeT0iMjI1IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjEzIiBmaWxsPSIjMjM0Ij5Eb0NBTiDigJQgQ2FuVHAgKElTTyAxNTc2NS0yKSBvdmVyIENBTiAvIENBTiBGRDwvdGV4dD4KCiAgPHJlY3QgeD0iNDkwIiB5PSIxOTIiIHdpZHRoPSI0MTAiIGhlaWdodD0iNTYiIHJ4PSI4IiBmaWxsPSIjRUFGMUZCIiBzdHJva2U9IiM5QkJDRTAiIHN0cm9rZS13aWR0aD0iMS41Ii8+CiAgPHRleHQgeD0iNjk1IiB5PSIyMjUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTMiIGZpbGw9IiMyMzQiPkRvSVAgKElTTyAxMzQwMCkgb3ZlciBhdXRvbW90aXZlIEV0aGVybmV0PC90ZXh0PgoKICA8IS0tID09PT09PT09PT09PT09PT09PT09PSBBcnJvd3MgaW50byBwbGF0Zm9ybSBjb2x1bW5zID09PT09PT09PT09PT09PT09PT09PSAtLT4KICA8bGluZSB4MT0iMjY1IiB5MT0iMjQ4IiB4Mj0iMjY1IiB5Mj0iMzA4IiBzdHJva2U9IiM0NDQiIHN0cm9rZS13aWR0aD0iMiIgbWFya2VyLWVuZD0idXJsKCNhcnIpIi8+CiAgPGxpbmUgeDE9IjY5NSIgeTE9IjI0OCIgeDI9IjY5NSIgeTI9IjMwOCIgc3Ryb2tlPSIjNDQ0IiBzdHJva2Utd2lkdGg9IjIiIG1hcmtlci1lbmQ9InVybCgjYXJyKSIvPgogIDxsaW5lIHgxPSI1MjAiIHkxPSIyNDgiIHgyPSI0NTAiIHkyPSIzMDgiIHN0cm9rZT0iIzJFNUZBQyIgc3Ryb2tlLXdpZHRoPSIxIiBzdHJva2UtZGFzaGFycmF5PSI0LDMiIG1hcmtlci1lbmQ9InVybCgjYXJyKSIvPgogIDx0ZXh0IHg9IjUwMCIgeT0iMjc1IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjEwLjUiIGZvbnQtc3R5bGU9Iml0YWxpYyIgZmlsbD0iIzJFNUZBQyI+YWxzbyBwb3NzaWJsZTwvdGV4dD4KCiAgPCEtLSA9PT09PT09PT09PT09PT09PT09PT0gQ2xhc3NpYyBBVVRPU0FSIEVDVSBjb2x1bW4gPT09PT09PT09PT09PT09PT09PT09IC0tPgogIDxyZWN0IHg9IjYwIiB5PSIzMDgiIHdpZHRoPSI0MTAiIGhlaWdodD0iMjAwIiByeD0iOCIgZmlsbD0iI0ZDRThENSIgc3Ryb2tlPSIjRTBBOTZEIiBzdHJva2Utd2lkdGg9IjEuNSIvPgogIDx0ZXh0IHg9IjI2NSIgeT0iMzMwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjE0IiBmb250LXdlaWdodD0iNzAwIiBmaWxsPSIjNkI0QTJCIj5DbGFzc2ljIEFVVE9TQVIgRUNVPC90ZXh0PgoKICA8cmVjdCB4PSI4MCIgeT0iMzQwIiB3aWR0aD0iMzcwIiBoZWlnaHQ9IjQyIiByeD0iOCIgZmlsbD0iI0VDRUNFQyIgc3Ryb2tlPSIjQjBCMEIwIiBzdHJva2Utd2lkdGg9IjEuNSIvPgogIDx0ZXh0IHg9IjI2NSIgeT0iMzY2IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjEyLjUiIGZpbGw9IiMzMzMiPkRDTSDigJQgc2VydmljZSBkaXNwYXRjaCwgc2Vzc2lvbnMsIHNlY3VyaXR5PC90ZXh0PgogIDxsaW5lIHgxPSIyNjUiIHkxPSIzODIiIHgyPSIyNjUiIHkyPSIzODgiIHN0cm9rZT0iIzQ0NCIgc3Ryb2tlLXdpZHRoPSIyIiBtYXJrZXItZW5kPSJ1cmwoI2FycikiLz4KCiAgPHJlY3QgeD0iODAiIHk9IjM4OCIgd2lkdGg9IjM3MCIgaGVpZ2h0PSI0MiIgcng9IjgiIGZpbGw9IiNFQ0VDRUMiIHN0cm9rZT0iI0IwQjBCMCIgc3Ryb2tlLXdpZHRoPSIxLjUiLz4KICA8dGV4dCB4PSIyNjUiIHk9IjQxNCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMi41IiBmaWxsPSIjMzMzIj5ERU0g4oCUIERUQ3MsIGZyZWV6ZSBmcmFtZXMgKE52TS1iYWNrZWQpPC90ZXh0PgogIDxsaW5lIHgxPSIyNjUiIHkxPSI0MzAiIHgyPSIyNjUiIHkyPSI0MzYiIHN0cm9rZT0iIzQ0NCIgc3Ryb2tlLXdpZHRoPSIyIiBtYXJrZXItZW5kPSJ1cmwoI2FycikiLz4KCiAgPHJlY3QgeD0iODAiIHk9IjQzNiIgd2lkdGg9IjM3MCIgaGVpZ2h0PSI0MiIgcng9IjgiIGZpbGw9IiNFQ0VDRUMiIHN0cm9rZT0iI0IwQjBCMCIgc3Ryb2tlLXdpZHRoPSIxLjUiLz4KICA8dGV4dCB4PSIyNjUiIHk9IjQ2MiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMi41IiBmaWxsPSIjMzMzIj5TV0NzIHByb3ZpZGUgdGhlIGRhdGE8L3RleHQ+CgogIDwhLS0gPT09PT09PT09PT09PT09PT09PT09IEFkYXB0aXZlIEFVVE9TQVIgbWFjaGluZSBjb2x1bW4gPT09PT09PT09PT09PT09PT09PT09IC0tPgogIDxyZWN0IHg9IjQ5MCIgeT0iMzA4IiB3aWR0aD0iNDEwIiBoZWlnaHQ9IjIwMCIgcng9IjgiIGZpbGw9IiNGQ0U4RDUiIHN0cm9rZT0iI0UwQTk2RCIgc3Ryb2tlLXdpZHRoPSIxLjUiLz4KICA8dGV4dCB4PSI2OTUiIHk9IjMzMCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxNCIgZm9udC13ZWlnaHQ9IjcwMCIgZmlsbD0iIzZCNEEyQiI+QWRhcHRpdmUgQVVUT1NBUiBtYWNoaW5lPC90ZXh0PgoKICA8cmVjdCB4PSI1MTAiIHk9IjM0MCIgd2lkdGg9IjM3MCIgaGVpZ2h0PSI0MiIgcng9IjgiIGZpbGw9IiNFQ0VDRUMiIHN0cm9rZT0iI0IwQjBCMCIgc3Ryb2tlLXdpZHRoPSIxLjUiLz4KICA8dGV4dCB4PSI2OTUiIHk9IjM2NiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMi41IiBmaWxsPSIjMzMzIj5ETSAoYXJhOjpkaWFnKSDigJQgRG9JUCBvbmx5PC90ZXh0PgogIDxsaW5lIHgxPSI2OTUiIHkxPSIzODIiIHgyPSI2OTUiIHkyPSIzODgiIHN0cm9rZT0iIzQ0NCIgc3Ryb2tlLXdpZHRoPSIyIiBtYXJrZXItZW5kPSJ1cmwoI2FycikiLz4KCiAgPHJlY3QgeD0iNTEwIiB5PSIzODgiIHdpZHRoPSIzNzAiIGhlaWdodD0iNDIiIHJ4PSI4IiBmaWxsPSIjRUNFQ0VDIiBzdHJva2U9IiNCMEIwQjAiIHN0cm9rZS13aWR0aD0iMS41Ii8+CiAgPHRleHQgeD0iNjk1IiB5PSI0MTQiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTIuNSIgZmlsbD0iIzMzMyI+b25lIGRpYWdub3N0aWMgc2VydmVyIHBlciBTb2Z0d2FyZSBDbHVzdGVyPC90ZXh0PgogIDxsaW5lIHgxPSI2OTUiIHkxPSI0MzAiIHgyPSI2OTUiIHkyPSI0MzYiIHN0cm9rZT0iIzQ0NCIgc3Ryb2tlLXdpZHRoPSIyIiBtYXJrZXItZW5kPSJ1cmwoI2FycikiLz4KCiAgPHJlY3QgeD0iNTEwIiB5PSI0MzYiIHdpZHRoPSIzNzAiIGhlaWdodD0iNDIiIHJ4PSI4IiBmaWxsPSIjRUNFQ0VDIiBzdHJva2U9IiNCMEIwQjAiIHN0cm9rZS13aWR0aD0iMS41Ii8+CiAgPHRleHQgeD0iNjk1IiB5PSI0NjIiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTIuNSIgZmlsbD0iIzMzMyI+QWRhcHRpdmUgYXBwcyBwcm92aWRlIHRoZSBkYXRhPC90ZXh0PgoKICA8IS0tIEZvb3Rub3RlIC0tPgogIDx0ZXh0IHg9IjQ4MCIgeT0iNTQ1IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjExIiBmb250LXN0eWxlPSJpdGFsaWMiIGZpbGw9IiM1NTUiPnNhbWUgcmVxdWVzdCBieXRlcyBlaXRoZXIgd2F5IOKAlCAyMiBGMSA5MCByZWFkcyB0aGUgVklOIG9uIGEgYm9keSBFQ1Ugb3ZlciBDQU4gb3Igb24gYSBjZW50cmFsIGNvbXB1dGVyIG92ZXIgRXRoZXJuZXQ8L3RleHQ+CgogIDwhLS0gQWJicmV2aWF0aW9uIGtleSAtLT4KICA8dGV4dCB4PSI0ODAiIHk9IjU3MiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMCIgZmlsbD0iIzU1NTU1NSI+VURTID0gdW5pZmllZCBkaWFnbm9zdGljIHNlcnZpY2VzIChJU08gMTQyMjkpICYjMTgzOyBESUQgLyBEVEMgPSBkYXRhIGlkZW50aWZpZXIgLyBkaWFnbm9zdGljIHRyb3VibGUgY29kZSAmIzE4MzsgRG9DQU4gLyBEb0lQID0gVURTIG92ZXIgQ0FOIChJU08gMTU3NjUtMikgLyBvdmVyIElQIChJU08gMTM0MDApPC90ZXh0PgogIDx0ZXh0IHg9IjQ4MCIgeT0iNTg4IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjEwIiBmaWxsPSIjNTU1NTU1Ij5DYW5UcCA9IHRoZSBDQU4gdHJhbnNwb3J0LXByb3RvY29sIG1vZHVsZSAmIzE4MzsgRENNICsgREVNID0gQ2xhc3NpYyBBVVRPU0FSJ3MgZGlhZ25vc3RpYyBtb2R1bGVzICYjMTgzOyBETSA9IEFkYXB0aXZlJ3MgZGlhZ25vc3RpYyBtYW5hZ2VyICYjMTgzOyBTV0MgPSBzb2Z0d2FyZSBjb21wb25lbnQ8L3RleHQ+Cjwvc3ZnPgo=" />

---

## Functional safety — FFI, and what timing protection is NOT

- CP's safety story is **freedom from interference (FFI)** on three axes — memory, timing,
  execution — plus E2E for the communication path (AUTOSAR *Functional Safety Measures*, Doc 664)
- **Memory FFI = Memory Partitioning via OS-Applications**, MPU-enforced: untrusted partitions
  run non-privileged, MPU regions reprogrammed on context switch, any out-of-region access
  traps to hardware. **Trusted** vs **Non-Trusted** OS-Applications. *Limit*: partitioning is at
  OS-Application granularity — **it cannot separate two Runnables inside one SWC**
- **The genuine surprise** (easy to get wrong on a slide): *"The AUTOSAR OS does **not** offer
  deadline supervision for timing protection."* Timing Protection enforces three **budgets** —
  **Execution Time**, **Locking Time**, **Inter-Arrival Time** — **not** deadlines.
  **Deadline supervision is a separate WdgM job** — the **Watchdog Manager** does **Alive /
  Deadline / Logical** supervision over checkpoints and services the HW watchdog *only while
  everything is correct* (far beyond a single `IWDG_Refresh()`)
- Determinism comes from being **statically everything**: no heap, static schedule tables, no
  MMU dependence, timing protection as a runtime backstop
- **Certified proof point**: **Vector MICROSAR Classic Safe** — *"the world's first AUTOSAR
  implementation … certified to ISO 26262 up to ASIL D"* (2016), later exida re-cert covering
  multicore FFI and execution-time bounds. So one CP ECU can host mixed-criticality software:
  ASIL-D braking in one partition, QM comfort code in another

<div class="gloss">FFI = Freedom From Interference (ISO 26262 term) · MPU = Memory Protection Unit (region-compare, not virtual memory) · OS-Application = the partition unit that owns tasks/ISRs/resources · WdgM = Watchdog Manager · WCET = Worst-Case Execution Time · QM = Quality Managed (no ASIL) · execution-time enforcement requires MCU timer/MPU hardware</div>

---

## Why Classic persists — structural limits, by design

- CP's strengths invert into hard limits, and AUTOSAR's own R25-11 architecture-decisions doc
  (Doc 1078) frames the CP/AP split around them **on purpose**:
  - **Static communication matrix** — no service discovery of new relationships; adding one
    means re-generate + re-flash. *"If you want software that can be replaced during run time,
    this does not work"*
  - **No dynamic deployment / limited OTA of function** — the ECU image is monolithic and static
  - **C-centric BSW, no dynamic memory** — determinism *requires* no heap, which forbids the
    C++/STL ecosystem AUTOSAR itself calls *"essentially indispensable"* for Adaptive. CP cannot
    host large evolving perception/AI stacks
  - **Scaling pain on HPCs** — built for single-digit-core MCUs with kB–MB memory
- **This is exactly why CP persists at the edge**: its static determinism and ASIL-D cert are
  what a **safety island** needs, and its inflexibility doesn't matter there
- The 2026 pattern is a **designed hierarchy, not legacy baggage** — the most advanced AV
  compute still delegates the certified fail-safe path to a small lock-step MCU running Vector
  *Classic* (Orin → AURIX TC397X; Thor → Renesas RH850U2A16). *Not* a hypervisor guest on Thor;
  *not* a documented Thor fleet gateway

<div class="gloss">OTA = Over-The-Air (software update) · STL = C++ Standard Template Library · HPC = High-Performance Computer/Computing · safety island = the small certified MCU that gates actuators for a powerful-but-less-certifiable SoC · AV = Autonomous Vehicle</div>

---

<!-- _class: lead -->

# Part 2
## the Adaptive Platform — the service platform on the big chip

---

## Why the Adaptive Platform exists

<style scoped>
  section { font-size: 22px; }
</style>

- CP cannot serve the new tier of automotive compute — **high-performance computer (HPC)** ECUs
  driving Ethernet backbones, many-core/GPU/FPGA silicon, service-oriented ADAS/connectivity,
  and **OTA**. AUTOSAR says so plainly: *"the needs of ECUs described above cannot be fulfilled
  [by CP]. Therefore, AUTOSAR specifies a second software platform, the Adaptive Platform …
  offers flexible software configuration, e.g. to support software update over-the-air"*
- Two named drivers: **Ethernet** (switched, high-bandwidth — CP *"cannot fully utilise"* it)
  and **processors** (*"manycore … tens to hundreds of cores, GPGPU … FPGA"*)
- **The one-line orientation, say it precisely**: *"The Adaptive Platform does **not** specify a
  new Operating System … it defines an execution context and Operating System Interface."*
  **AP is middleware + services on top of a POSIX OS — not a new OS.** If your CP instinct is
  "AUTOSAR = the RTOS on my MCU," that instinct is wrong for AP
- **Not "CP is obsolete"** — the two coexist in every real vehicle, usually CP on a companion
  safety MCU and AP on the application SoC
- **The four design traits**: **C++**, **SOA** (a peer is addressed the same whether local
  process or remote machine), **updateability/OTA**, and **agile** deploy-then-update development
- **The dynamic-memory culture shock**: every MISRA-C engineer carries a "no `malloc` in safety
  code" reflex — AUTOSAR says the *opposite* for AP (dynamic allocation is *"allowed and
  assumed"*), answering the non-determinism cost not by banning the heap but with **deterministic
  allocators**. Still, "dynamic" means **deploy-time flexibility + OTA**, *not* free-running
  runtime allocation: the process set per state is fixed in manifests, only discovery is runtime

<div class="gloss">HPC = High-Performance Computer · ADAS = Advanced Driver-Assistance Systems · FPGA = Field-Programmable Gate Array · GPGPU = General-Purpose GPU computing · SOA = Service-Oriented Architecture · POSIX = the standard OS API family (Linux/QNX/PikeOS) AP builds on · deterministic allocator = a fixed-time, fragmentation-bounded replacement for `malloc`/`free`</div>

---

<!-- _class: diagram -->

<img alt="stack-autosar-adaptive" src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA5NjAgNjAwIiB3aWR0aD0iOTYwIiBoZWlnaHQ9IjYwMCIgZm9udC1mYW1pbHk9IkhlbHZldGljYSwgQXJpYWwsIHNhbnMtc2VyaWYiPgogIDxyZWN0IHg9IjAiIHk9IjAiIHdpZHRoPSI5NjAiIGhlaWdodD0iNjAwIiBmaWxsPSIjZmZmZmZmIi8+CgogIDxkZWZzPgogICAgPG1hcmtlciBpZD0iYXJyIiBtYXJrZXJXaWR0aD0iMTAiIG1hcmtlckhlaWdodD0iMTAiIHJlZlg9IjgiIHJlZlk9IjMiIG9yaWVudD0iYXV0byIgbWFya2VyVW5pdHM9InN0cm9rZVdpZHRoIj4KICAgICAgPHBhdGggZD0iTTAsMCBMOSwzIEwwLDYgeiIgZmlsbD0iIzQ0NCIvPgogICAgPC9tYXJrZXI+CiAgPC9kZWZzPgoKICA8IS0tIFRpdGxlIC0tPgogIDx0ZXh0IHg9IjQ4MCIgeT0iNDAiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMjYiIGZvbnQtd2VpZ2h0PSI3MDAiIGZpbGw9IiMxYjJiNGEiPkFVVE9TQVIgQWRhcHRpdmUg4oCUIGEgUE9TSVggc2VydmljZS1vcmllbnRlZCBwbGF0Zm9ybSwgbm90IGFuIE9TPC90ZXh0PgoKICA8IS0tID09PT09PT09PT09PT09PT09PT09PSBSb3cgMTogQWRhcHRpdmUgQXBwbGljYXRpb25zID09PT09PT09PT09PT09PT09PT09PSAtLT4KICA8cmVjdCB4PSIxNTAiIHk9IjY0IiB3aWR0aD0iNjIwIiBoZWlnaHQ9Ijc4IiByeD0iOCIgZmlsbD0iI0ZDRThENSIgc3Ryb2tlPSIjRTBBOTZEIiBzdHJva2Utd2lkdGg9IjEuNSIvPgogIDx0ZXh0IHg9IjQ2MCIgeT0iOTciIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTMuNSIgZm9udC13ZWlnaHQ9IjcwMCIgZmlsbD0iIzZCNEEyQiI+QWRhcHRpdmUgQXBwbGljYXRpb25zIOKAlCBDKysxNCBwcm9jZXNzZXM8L3RleHQ+CiAgPHRleHQgeD0iNDYwIiB5PSIxMTgiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTIuNSIgZmlsbD0iIzZCNEEyQiI+ZWFjaCBiZWxvbmdzIHRvIGEgU29mdHdhcmUgQ2x1c3RlcjogdGhlIHVuaXQgb2YgdXBkYXRlIGFuZCBkaWFnbm9zaXM8L3RleHQ+CgogIDxsaW5lIHgxPSI0NjAiIHkxPSIxNDIiIHgyPSI0NjAiIHkyPSIxNTQiIHN0cm9rZT0iIzQ0NCIgc3Ryb2tlLXdpZHRoPSIyIiBtYXJrZXItZW5kPSJ1cmwoI2FycikiLz4KCiAgPCEtLSA9PT09PT09PT09PT09PT09PT09PT0gUm93IDI6IEFSQSAodGFsbGVyLCA2IHN1Yi1ib3hlcykgPT09PT09PT09PT09PT09PT09PT09IC0tPgogIDxyZWN0IHg9IjE1MCIgeT0iMTU2IiB3aWR0aD0iNjIwIiBoZWlnaHQ9IjIxNCIgcng9IjgiIGZpbGw9IiNEQ0U5RjciIHN0cm9rZT0iIzdmOWRjOSIgc3Ryb2tlLXdpZHRoPSIxLjUiLz4KICA8dGV4dCB4PSI0NjAiIHk9IjE3OCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxNCIgZm9udC13ZWlnaHQ9IjcwMCIgZmlsbD0iIzIyMzM0NCI+QVJBIOKAlCBBVVRPU0FSIFJ1bnRpbWUgZm9yIEFkYXB0aXZlPC90ZXh0PgoKICA8IS0tIGFyYTo6Y29tIC0tPgogIDxyZWN0IHg9IjE2MCIgeT0iMTkwIiB3aWR0aD0iMTgwIiBoZWlnaHQ9IjcwIiByeD0iNiIgZmlsbD0iI0RDRTlGNyIgc3Ryb2tlPSIjN2Y5ZGM5IiBzdHJva2Utd2lkdGg9IjEuNSIvPgogIDx0ZXh0IHg9IjI1MCIgeT0iMjIxIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjEwLjUiIGZpbGw9IiMyMjMzNDQiPmFyYTo6Y29tIOKAlDwvdGV4dD4KICA8dGV4dCB4PSIyNTAiIHk9IjIzNyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMC41IiBmaWxsPSIjMjIzMzQ0Ij5TT01FL0lQIMK3IEREUyBiaW5kaW5nPC90ZXh0PgoKICA8IS0tIGFyYTo6ZGlhZyAoaGlnaGxpZ2h0ZWQpIC0tPgogIDxyZWN0IHg9IjM2MCIgeT0iMTkwIiB3aWR0aD0iMTgwIiBoZWlnaHQ9IjcwIiByeD0iNiIgZmlsbD0iI0RGRjBEOCIgc3Ryb2tlPSIjOEZCRjhGIiBzdHJva2Utd2lkdGg9IjEuNSIvPgogIDx0ZXh0IHg9IjQ1MCIgeT0iMjIxIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjEwLjUiIGZpbGw9IiMyZDVhMmQiPmFyYTo6ZGlhZyDigJQ8L3RleHQ+CiAgPHRleHQgeD0iNDUwIiB5PSIyMzciIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTAuNSIgZmlsbD0iIzJkNWEyZCI+RE0gKFVEUyBvdmVyIERvSVApPC90ZXh0PgoKICA8IS0tIGFyYTo6dWNtIChoaWdobGlnaHRlZCkgLS0+CiAgPHJlY3QgeD0iNTYwIiB5PSIxOTAiIHdpZHRoPSIxODAiIGhlaWdodD0iNzAiIHJ4PSI2IiBmaWxsPSIjREZGMEQ4IiBzdHJva2U9IiM4RkJGOEYiIHN0cm9rZS13aWR0aD0iMS41Ii8+CiAgPHRleHQgeD0iNjUwIiB5PSIyMjEiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTAuNSIgZmlsbD0iIzJkNWEyZCI+YXJhOjp1Y20g4oCUPC90ZXh0PgogIDx0ZXh0IHg9IjY1MCIgeT0iMjM3IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjEwLjUiIGZpbGw9IiMyZDVhMmQiPlVDTSB1cGRhdGVzPC90ZXh0PgoKICA8IS0tIGFyYTo6ZXhlYyAtLT4KICA8cmVjdCB4PSIxNjAiIHk9IjI3NCIgd2lkdGg9IjE4MCIgaGVpZ2h0PSI3MCIgcng9IjYiIGZpbGw9IiNEQ0U5RjciIHN0cm9rZT0iIzdmOWRjOSIgc3Ryb2tlLXdpZHRoPSIxLjUiLz4KICA8dGV4dCB4PSIyNTAiIHk9IjMwNSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMC41IiBmaWxsPSIjMjIzMzQ0Ij5hcmE6OmV4ZWMg4oCUPC90ZXh0PgogIDx0ZXh0IHg9IjI1MCIgeT0iMzIxIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjEwLjUiIGZpbGw9IiMyMjMzNDQiPmxpZmVjeWNsZTwvdGV4dD4KCiAgPCEtLSBhcmE6OnBlciAtLT4KICA8cmVjdCB4PSIzNjAiIHk9IjI3NCIgd2lkdGg9IjE4MCIgaGVpZ2h0PSI3MCIgcng9IjYiIGZpbGw9IiNEQ0U5RjciIHN0cm9rZT0iIzdmOWRjOSIgc3Ryb2tlLXdpZHRoPSIxLjUiLz4KICA8dGV4dCB4PSI0NTAiIHk9IjMwNSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMC41IiBmaWxsPSIjMjIzMzQ0Ij5hcmE6OnBlciDigJQ8L3RleHQ+CiAgPHRleHQgeD0iNDUwIiB5PSIzMjEiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTAuNSIgZmlsbD0iIzIyMzM0NCI+cGVyc2lzdGVuY3k8L3RleHQ+CgogIDwhLS0gYXJhOjpsb2cgLS0+CiAgPHJlY3QgeD0iNTYwIiB5PSIyNzQiIHdpZHRoPSIxODAiIGhlaWdodD0iNzAiIHJ4PSI2IiBmaWxsPSIjRENFOUY3IiBzdHJva2U9IiM3ZjlkYzkiIHN0cm9rZS13aWR0aD0iMS41Ii8+CiAgPHRleHQgeD0iNjUwIiB5PSIzMTMiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTAuNSIgZmlsbD0iIzIyMzM0NCI+YXJhOjpsb2c8L3RleHQ+CgogIDxsaW5lIHgxPSI0NjAiIHkxPSIzNzAiIHgyPSI0NjAiIHkyPSIzODIiIHN0cm9rZT0iIzQ0NCIgc3Ryb2tlLXdpZHRoPSIyIiBtYXJrZXItZW5kPSJ1cmwoI2FycikiLz4KCiAgPCEtLSA9PT09PT09PT09PT09PT09PT09PT0gUm93IDM6IFBPU0lYIE9TID09PT09PT09PT09PT09PT09PT09PSAtLT4KICA8cmVjdCB4PSIxNTAiIHk9IjM4NCIgd2lkdGg9IjYyMCIgaGVpZ2h0PSI3NiIgcng9IjgiIGZpbGw9IiNFQUYxRkIiIHN0cm9rZT0iIzlCQkNFMCIgc3Ryb2tlLXdpZHRoPSIxLjUiLz4KICA8dGV4dCB4PSI0NjAiIHk9IjQxNiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMyIgZm9udC13ZWlnaHQ9IjcwMCIgZmlsbD0iIzIyMzM0NCI+UE9TSVggT1Mg4oCUIFFOWCBvciBMaW51eDwvdGV4dD4KICA8dGV4dCB4PSI0NjAiIHk9IjQzNyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMS41IiBmaWxsPSIjMjIzMzQ0Ij5hcHBzIHNlZSB0aGUgUFNFNTEgcHJvZmlsZTsgcGxhdGZvcm0gc2VydmljZXMgbWF5IHVzZSBmdWxsIFBPU0lYPC90ZXh0PgoKICA8bGluZSB4MT0iNDYwIiB5MT0iNDYwIiB4Mj0iNDYwIiB5Mj0iNDcyIiBzdHJva2U9IiM0NDQiIHN0cm9rZS13aWR0aD0iMiIgbWFya2VyLWVuZD0idXJsKCNhcnIpIi8+CgogIDwhLS0gPT09PT09PT09PT09PT09PT09PT09IFJvdyA0OiBIaWdoLXBlcmZvcm1hbmNlIFNvQyA9PT09PT09PT09PT09PT09PT09PT0gLS0+CiAgPHJlY3QgeD0iMTUwIiB5PSI0NzQiIHdpZHRoPSI2MjAiIGhlaWdodD0iNjYiIHJ4PSI4IiBmaWxsPSIjRUNFQ0VDIiBzdHJva2U9IiNCMEIwQjAiIHN0cm9rZS13aWR0aD0iMS41Ii8+CiAgPHRleHQgeD0iNDYwIiB5PSI1MTIiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTMiIGZpbGw9IiMzMzMiPkhpZ2gtcGVyZm9ybWFuY2UgU29DIOKAlCBUaG9yLWNsYXNzIGNlbnRyYWwgY29tcHV0ZXJzLCBkb21haW4vem9uYWwgSFBDczwvdGV4dD4KCiAgPCEtLSA9PT09PT09PT09PT09PT09PT09PT0gUmlnaHQtc2lkZSBkYXNoZWQgY2FsbG91dCA9PT09PT09PT09PT09PT09PT09PT0gLS0+CiAgPHJlY3QgeD0iNzc1IiB5PSIxODAiIHdpZHRoPSIxNzUiIGhlaWdodD0iMjAwIiByeD0iOCIgZmlsbD0iI2ZmZmZmZiIgc3Ryb2tlPSIjMkU1RkFDIiBzdHJva2Utd2lkdGg9IjEuNSIgc3Ryb2tlLWRhc2hhcnJheT0iNiw0Ii8+CiAgPHRleHQgeD0iODYyIiB5PSIyMzYiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTAiIGZpbGw9IiMyRTVGQUMiPnNlcnZpY2Utb3JpZW50ZWQ6IGFwcHM8L3RleHQ+CiAgPHRleHQgeD0iODYyIiB5PSIyNTAiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTAiIGZpbGw9IiMyRTVGQUMiPmZpbmQgc2VydmljZXMgYXQgcnVudGltZTwvdGV4dD4KICA8dGV4dCB4PSI4NjIiIHk9IjI2NCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMCIgZmlsbD0iIzJFNUZBQyI+KGRpc2NvdmVyeSkg4oCUPC90ZXh0PgogIDx0ZXh0IHg9Ijg2MiIgeT0iMjgyIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjEwIiBmaWxsPSIjMkU1RkFDIj5idXQgcHJvZHVjdGlvbiBidWlsZHM8L3RleHQ+CiAgPHRleHQgeD0iODYyIiB5PSIyOTYiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTAiIGZpbGw9IiMyRTVGQUMiPnBpbiBkaXNjb3ZlcnkgZG93biBhbmQ8L3RleHQ+CiAgPHRleHQgeD0iODYyIiB5PSIzMTAiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTAiIGZpbGw9IiMyRTVGQUMiPnJlc3RyaWN0IGR5bmFtaWMgbWVtb3J5PC90ZXh0PgogIDx0ZXh0IHg9Ijg2MiIgeT0iMzI0IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjEwIiBmaWxsPSIjMkU1RkFDIj50byBzdGFydHVwPC90ZXh0PgoKICA8IS0tID09PT09PT09PT09PT09PT09PT09PSBMZWZ0LXNpZGUgYW5ub3RhdGlvbiA9PT09PT09PT09PT09PT09PT09PT0gLS0+CiAgPHRleHQgeD0iNzUiIHk9IjI0NiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMC41IiBmb250LXN0eWxlPSJpdGFsaWMiIGZpbGw9IiMyRTVGQUMiPm1pZGRsZXdhcmUgT04gYW4gT1Mg4oCUPC90ZXh0PgogIDx0ZXh0IHg9Ijc1IiB5PSIyNjAiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTAuNSIgZm9udC1zdHlsZT0iaXRhbGljIiBmaWxsPSIjMkU1RkFDIj5BZGFwdGl2ZSBpcyBub3QgaXRzZWxmPC90ZXh0PgogIDx0ZXh0IHg9Ijc1IiB5PSIyNzQiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTAuNSIgZm9udC1zdHlsZT0iaXRhbGljIiBmaWxsPSIjMkU1RkFDIj5hbiBvcGVyYXRpbmcgc3lzdGVtPC90ZXh0PgogIDxsaW5lIHgxPSI3NSIgeTE9IjI3OCIgeDI9IjE1MCIgeTI9IjMwMCIgc3Ryb2tlPSIjMkU1RkFDIiBzdHJva2Utd2lkdGg9IjEiIHN0cm9rZS1kYXNoYXJyYXk9IjQsMyIvPgoKICA8IS0tIEZvb3Rub3RlIC0tPgogIDx0ZXh0IHg9IjQ4MCIgeT0iNTcyIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjExIiBmb250LXN0eWxlPSJpdGFsaWMiIGZpbGw9IiM1NTUiPnVwZGF0ZXMgcGVyIFNvZnR3YXJlIENsdXN0ZXIgdmlhIFVDTSAoVXBkYXRlIGFuZCBDb25maWd1cmF0aW9uIE1hbmFnZW1lbnQpIOKAlCBub3QgZnVsbC1FQ1UgcmVmbGFzaCDCtzwvdGV4dD4KICA8dGV4dCB4PSI0ODAiIHk9IjU4OCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMSIgZm9udC1zdHlsZT0iaXRhbGljIiBmaWxsPSIjNTU1Ij5zYWZldHk6IEFTSUwtQiBzaGlwcGluZywgQVNJTC1EIHByb2dyYW1zIHVuZGVyd2F5PC90ZXh0PgoKICA8IS0tIEFiYnJldmlhdGlvbiBrZXkgLS0+CiAgPHRleHQgeD0iNDgwIiB5PSI1OTgiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iOSIgZmlsbD0iIzU1NTU1NSI+RE0gPSBkaWFnbm9zdGljIG1hbmFnZXIgKFVEUyBvdmVyIERvSVApICYjMTgzOyBVQ00gPSB1cGRhdGUgJmFtcDsgY29uZmlndXJhdGlvbiBtYW5hZ2VtZW50ICYjMTgzOyBTT01FL0lQID0gYXV0b21vdGl2ZSBzZXJ2aWNlIG1pZGRsZXdhcmUgJiMxODM7IFBTRTUxID0gdGhlIG1pbmltYWwgcmVhbC10aW1lIFBPU0lYIHByb2ZpbGU8L3RleHQ+Cjwvc3ZnPgo=" />

---

## Adaptive Applications are POSIX processes on ARA

- An **Adaptive Application (AA)** is an ordinary **POSIX process** written in **C++**, linked
  against **ARA** (AUTOSAR Runtime for Adaptive Applications)
- Crucially an AA is restricted "by definition" to the **POSIX PSE51** profile — a
  *single-process* profile (IEEE 1003.13). PSE51 gives threads, mutexes, RT scheduling, timers —
  but **excludes `fork`/`exec`** (no multi-process, no `posix_spawn`) — POSIX shared-memory objects it keeps. Consequences: **one process = one
  address space, multiple threads**; you cannot spawn children (that's Execution Management's
  job); isolation comes from OS process boundaries. Note the OS *itself* must be **multi-process
  POSIX** — only the *AAs* are held to PSE51
- The Machine may be *"a real physical machine, a fully-virtualized machine, a para-virtualized
  OS, an OS-level container or any other virtualized"* environment — AP presents a consistent view
- AAs code against the **`ara::` C++ namespaces** — `ara::com`, `ara::exec`, `ara::core`,
  `ara::log`, `ara::crypto`, `ara::diag`, `ara::per`, `ara::phm`
- The building-block view groups the function clusters into **seven technical categories** —
  Runtime, Communication, Storage, Security, Safety, Configuration, Diagnostics

<div class="gloss">AA = Adaptive Application · ARA = AUTOSAR Runtime for Adaptive Applications (the `ara::` C++ API surface) · PSE51 = IEEE 1003.13's minimal single-process real-time POSIX profile · `fork`/`exec` = the POSIX process-creation calls PSE51 omits</div>

---

## The R25-11 function-cluster inventory (this list changes)

- R25-11 defines **20 function clusters across seven categories** — each its own SWS document.
  **A "canonical list" must always be release-stamped:**

| Category | Function clusters (R25-11) |
|---|---|
| **Runtime (5)** | Execution Mgmt · State Mgmt · Log & Trace · Core · OS Interface (PSE51) |
| **Communication (5)** | Communication Mgmt (`ara::com`) · Raw Data Stream · Network Mgmt · Time Sync · Automotive API Gateway *(R24-11)* |
| **Storage (2)** | Persistency (`ara::per`) · **Remote Persistency** *(new R25-11)* |
| **Security (3)** | Cryptography · Intrusion Detection Mgr *(R21-11)* · Firewall *(R22-11)* |
| **Safety (2)** | Platform Health Mgmt (`ara::phm`) · **Safe HW Acceleration** *(new R25-11)* |
| **Configuration (2)** | Update & Configuration Mgmt (UCM) · Vehicle UCM *(R23-11)* |
| **Diagnostics (1)** | Diagnostic Mgmt (`ara::diag`) |

- **Do not present as current**: **IAM** (Identity & Access Mgmt, removed R23-11) and **RESTful
  Communication** (removed R21-11). R25-11 also added **Suspend-to-RAM** in State Management

<div class="gloss">SWS = Software Specification (one per cluster) · UCM = Update and Configuration Management · IAM = Identity and Access Management (removed) · "daemon-based" = the reference design runs the cluster as a separate daemon process · the inventory is not static across releases</div>

---

## Execution Mgmt vs State Mgmt — EM enforces, SM decides

- **The single most-misunderstood pair.** **Execution Management (EM)** *"starts, configures,
  and stops Processes as configured in Function Group States using interfaces of the OS"* — it's
  the entry point the OS launches at boot. **But EM does not decide *which* apps run or *when***:
  *"a special FC, called State Management (SM), is the controller, commanding EM."* **SM owns the
  policy; EM only enforces the mechanism**
- The unit of composition is the **Function Group** — a named set of processes with states,
  where *"a Function Group State defines a set of active Applications for any certain situation."*
  Elegant unification: a **"Machine State" is just the Function Group State of a reserved group
  `MachineFG`** in the one `PLATFORM_CORE` cluster
- **"EM ≈ systemd" breaks in five ways**: (a) policy is externalized to a safety cluster (SM),
  not unit files; (b) the unit is a whole machine mode, not a service target; (c) EM enforces
  **resource groups** + **authenticated startup**; (d) config is **ARXML Manifests**, not
  `.service` files; (e) EM is a **certified entry point** under an ISO 26262 argument
- **Five manifest kinds**: **Execution** (per-executable), **Service Instance** (service→transport
  mapping), **Machine** (the machine with no apps), **Raw Data Stream**, **Software Distribution**

<div class="gloss">EM = Execution Management · SM = State Management · FC = Function Cluster · Function Group = a named set of processes with states · Manifest = ARXML authored at integration time, read at startup · systemd = the Linux service manager (the tempting-but-wrong analogy)</div>

---

## `ara::com` — one API, several bindings

- AP exposes **one** application communication API, `ara::com`, on a **proxy/skeleton** model:
  the **proxy** is the local representative of a possibly-remote service; the **skeleton**
  connects the service implementation to the transport. **The app codes against `ara::com`; the
  integrator chooses the wire binding in the manifest**
- A subtlety: **serialization runs in the AA's own execution context** (the binding is compiled
  into the app binary, not a separate broker). The API supports event/callback *and* polling,
  sync + async methods (`std::future`/`std::promise`), and **zero-copy** capabilities
- **Four service elements**: an **event** (a notification carrying data, to subscribers only); a
  **trigger** (the same, *without* payload — a data-less "something happened"); a **method**
  (client/server request/response, or fire-and-forget); a **field** (a value with up to three
  accessors — notifier, getter, setter)
- **R25-11 currency**: the big `ara::com` cuts actually landed at **R23-11** — **Raw Data Streaming
  removed** and **Communication Groups marked OBSOLETE** (Comm Groups ran R20-11 → R23-11; Raw Data
  Streaming had been in `ara::com` since R19-11). R25-11 itself just **reworked the `ara::com` C++
  API** against generated headers and deleted the leftover obsolete text. Listing those as current is stale

<div class="gloss">`ara::com` = the Adaptive communication-management API · proxy = client-side stub · skeleton = server-side stub · event / trigger / method / field = the four service-element kinds · zero-copy = passing data by pointer in shared memory, no serialization copy</div>

---

## Binding choice: SOME/IP vs DDS vs local IPC

- **SOME/IP** — the automotive-native option: compact serialization + **SOME/IP-SD** service
  discovery. Connection- and ID-oriented (Service ID / Instance ID / Event ID / Eventgroup) —
  familiar from CAN/UDS thinking. Subscription granularity is the **eventgroup**; SD runs **over
  UDP multicast only**
- **DDS binding — present since R18-03** (published 23 Apr 2018; *not* R18-10, a folklore
  correction this repo already made). **Data-centric**: publish to a Topic, matched by type +
  QoS + name, no explicit peer connection. Mapping: events/triggers → **Topic + DataWriter**;
  methods & field get/set → **DDS Service (DDS-RPC)**; field notifiers → a Topic. **QoS is
  manifest-driven** (`qosProfile`), not fixed by the spec
- **Local IPC / zero-copy** — the local wire is **implementation-specific**, *not* a
  standardized inter-vendor protocol (unlike SOME/IP and RTPS). The dominant realization is
  **Eclipse iceoryx** — a low-level zero-copy shared-memory IPC ("plumbing") that higher layers wrap:
  it sits *under* both ROS 2 (via `rmw_iceoryx`) and some `ara::com` implementations, not either API itself
- **The single most transferable idea**: **the application API is protocol-agnostic; DDS/SOME-IP
  is a swappable binding underneath** — exactly like ROS 2's `rmw`/DDS layering

<div class="gloss">SOME/IP = Scalable service-Oriented MiddlewarE over IP · SD = Service Discovery · DDS = Data Distribution Service (OMG) · QoS = Quality of Service · RTPS = the DDS wire protocol · IPC = Inter-Process Communication · iceoryx = the shared-memory zero-copy IPC shared with ROS 2 · `rmw` = ROS 2's middleware-abstraction layer</div>

---

## UCM — OTA the automotive way

- The unit of update is the **Software Cluster**: AP can be extended *"with new software packages
  without re-flashing the entire ECU."* The per-machine **UCM** (`ara::ucm::PackageManagement`)
  runs the workflow **Transfer → Process → Activate → (Verify/Finish or Rollback)**:
  1. **Transfer** — stream the package (`TransferStart → TransferData → TransferExit`)
  2. **Process** — `ProcessSwPackage` unpacks, validates, writes the cluster
  3. **Activate** — *UCM asks State Management for an update session*, SM stops the outdated
     clusters' processes, UCM makes the new ones available; `VerifyUpdate` → `Finish` commits
- **Rollback is best-effort, NOT guaranteed** — the spec documents a *failing* rollback
  (`UCM ROLLBACK FAILED`). For an MCU engineer: the A/B-bank reflash idea, but per-cluster and
  coordinated with a state machine, not a bootloader
- **Vehicle-wide OTA = V-UCM (Vehicle UCM)** — formerly "UCM Master," now its **own spec since
  R23-11**. It coordinates the campaign: **backend** (authenticate the Vehicle Package, resolve
  inter-cluster dependencies), **Vehicle State Manager** (apply safety conditions), and
  **driver consent**. Chain: **OEM backend → V-UCM → subordinate per-machine UCM instances**

<div class="gloss">UCM = Update and Configuration Management (per machine) · V-UCM = Vehicle UCM (vehicle-wide campaign coordinator) · Software Cluster = AP's unit of deployment/update · Vehicle Package = the signed bundle V-UCM authenticates · A/B bank = the dual-slot reflash pattern from MCU bootloaders</div>

---

## Diagnostics on AP — one cluster does DCM + DEM's jobs

- *"The DM is a diagnostic server … that realizes a UDS server instance according to
  ISO 14229-1 and SOVD according to ASAM."* Since R19-03 the interface is C++ (`ara::diag`),
  configured from the **Diagnostic Extract Template (DEXT)**. Where CP splits diagnostics into
  **DCM + DEM** BSW modules, **AP merges both roles into one cluster** — one `ara::diag` API
- **One Diagnostic Server Instance per Software Cluster**, and all instances *"share a single
  TransportLayer instance (e.g. DoIP on TCP/IP port 13400)"*
- **Transport phrasing — get it exactly right**: **DoIP (ISO 13400-2:2019) is the only
  *standardized* UDS transport for the AP DM; the SWS explicitly permits a custom transport.**
  Verbatim: *"the DoIP protocol … or a custom implementation of a transport protocol can be
  used."* **Do not repeat the refuted web claim "R24-11 added CAN transport" — a hallucination**;
  DoIP-only-as-standard is confirmed against the R24-11 **and R25-11** SWS texts (this research
  re-read both; earlier releases not re-checked)
- **SOVD is realized *inside* the DM + a SOVD Gateway — there is no separate "SOVD cluster."**
  It's a modern API over **HTTP/REST + JSON + OAuth**, self-describing, *"UDS as a subset,"* and
  can front legacy ECUs via **SOVD→UDS translation**. *ISO transition mid-flight*: R25-11 cites
  ISO 17978-3:2025/2026 & ASAM SOVD 1.1, but warns 1.1 is *"not yet (fully) supported"*

<div class="gloss">DM = Diagnostic Management (`ara::diag`) · DEXT = Diagnostic Extract Template · DoIP = Diagnostics over IP (ISO 13400) · SOVD = Service-Oriented Vehicle Diagnostics · OAuth = the token-based authorization framework · SOVD adds OAuth, proximity challenge, data-lists, bulk data — no UDS equivalent</div>

---

## PHM and Persistency — supervision and stored state

- **Platform Health Management (`ara::phm`)** is AP's analogue of CP's WdgM, required by
  ISO 26262. Three supervisions — **Alive**, **Deadline**, **Logical** — over **Checkpoints**
  apps report via `ReportCheckpoint`, aggregated into a **Global Supervision Status** per
  Function Group
- On failure, **PHM notifies State Management** (which decides + triggers recovery — e.g. restart
  a Function Group); *"if no response … is received in time, the PHM will do its own
  countermeasures"* via the **hardware watchdog**
- *Release-stamped*: **Health Channels are obsolete** (set obsolete R21-11, "Removed" R24-11) —
  material presenting them as a live PHM input is out of date
- **Persistency (`ara::per`)** provides **Key-Value Storage** and **File Storage**, with
  **redundancy** *"configured to use replication of stored data, CRCs, or Hashes"* and defined
  **Install / Update / Finalize / Roll-Back of persistent data** across Software-Cluster updates.
  The guarantee is *defined install/update/finalize semantics with a rollback path* — **not
  transparent automatic migration**
- **Log & Trace** exposes `ara::log` over the **DLT** protocol (note SOVD logging is *not*
  standardized through `ara::log`)

<div class="gloss">PHM = Platform Health Management · WdgM = CP's Watchdog Manager (the analogue) · Checkpoint = the point an app reports it reached · `ara::per` = the persistency cluster · KVS = Key-Value Storage · DLT = Diagnostic Log and Trace protocol</div>

---

## The mid-2026 reality — OSes, vendors, and the ASIL hedge

- **The OS underneath is a separate procurement + certification decision.** **QNX** is the
  de-facto safety OS — QNX OS for Safety is ISO 26262 **ASIL-D** certified (~35–38% of the
  *overall* automotive-OS market by analyst estimates — an OS-type share, not a safety-only figure).
  **Linux** carries most non-safety/ADAS compute but
  can't itself certify above ~ASIL-B (reached via a **certified hypervisor** or safety companion).
  **PikeOS, INTEGRITY, VxWorks** also appear
- **The exact hedge to keep — "ASIL-B shipping, ASIL-D programs underway":**

| Vendor / product | Stated safety (mid-2026) |
|---|---|
| **Vector MICROSAR Adaptive (Safe)** | ASIL-B in first series projects; Vector's own **ASIL-D target 2026**; a *separate* Vector–QNX deal (Jun 2024) targets ASIL-D on QNX OS, no date |
| **ETAS RTA-VRTE** | **ISO 26262 ASIL-B certified, TÜV SÜD, March 2025** |
| **Qorix** (KPIT+ZF JV, Qualcomm shareholder) | **TÜV SÜD ASIL-B certified, Aug 2025** |
| **Elektrobit EB corbos AdaptiveCore** | hypervisor **ASIL-B certified** (TÜV SÜD, 2024); AdaptiveCore itself makes no ASIL-D claim — it pairs with a separately ASIL-D-certified OS |
| **Wind River** AUTOSAR Adaptive | ASIL-D **program** (2019; shipped certificate unverified) |

- **Separate "developed to ASIL-x" (a process claim) from "certified by TÜV SÜD at ASIL-x."**
  **No fully-certified end-to-end ASIL-D AP middleware ships as of mid-2026** — ASIL-D lives in
  the **OS (QNX) + hypervisor + vendor safety case**
- **The 2025–26 ecosystem shift**: **Eclipse S-CORE** (launched 2025-06-12, dual-language C++/Rust,
  Apache-licensed, built by the *same* AUTOSAR members — hedging, not defecting, and cooperating
  with AUTOSAR) and **SOAFEE** (Arm-led SIG defining a **cloud-native architecture** — containers,
  hypervisors, K8s, CI/CD — for mixed-criticality SDV workloads; running an AP stack as a container
  is a *demonstrated pattern*, not SOAFEE's definition). Teach SOAFEE as the environment, AP as one payload it can host

<div class="gloss">ASIL = Automotive Safety Integrity Level (QM < A < B < C < D) · TÜV SÜD = a German technical-certification body · JV = joint venture · SEooC = Safety Element out of Context · S-CORE = Eclipse Safe Open Vehicle Core · SOAFEE = Scalable Open Architecture For the Embedded Edge · SIG = Special Interest Group · K8s = Kubernetes · CI/CD = continuous integration/delivery · Silicon targets: NVIDIA Orin/Thor · NXP S32G · Qualcomm Snapdragon Ride · TI TDA4x</div>

---

## CP vs AP — the platform split (1/2)

<style scoped>
  section { font-size: 21px; padding-top: 38px; }
  table { font-size: 16.5px; }
  table td, table th { padding: 4px 10px; }
  .gloss { font-size: 13.5px; margin-top: 8px; }
  h2 { margin-bottom: 6px; }
</style>

| Dimension | **Classic Platform (CP)** | **Adaptive Platform (AP)** |
|---|---|---|
| **OS / kernel** | AUTOSAR OS — OSEK superset (SC1–SC4, no MMU) | not a new OS: an **OS Interface** on POSIX **PSE51** over Linux/QNX/PikeOS |
| **Language & API** | C; RTE-generated `Rte_Read/Write/Call` | C++14 (C++17 via MISRA C++:2023 merge); `ara::*` |
| **Config time** | fully **static** — fixed pre-build (ECUC) → one binary | **dynamic** — manifests bound late; discovery + start/stop at runtime |
| **Communication** | **signal**-oriented — COM packs signals→I-PDUs on CAN/LIN/FlexRay/Ethernet | **service**-oriented — `ara::com` proxy/skeleton over **SOME/IP or DDS** |
| **Scheduling** | static priority table; hard RT by construction | POSIX `SCHED_FIFO`/`RR`, optional `SCHED_DEADLINE`; determinism *engineered* |
| **Memory** | static allocation; MPU partitions; **no heap in safety paths** | **dynamic allocation allowed and assumed** (C++/STL); deterministic allocators |

<div class="gloss">SC = Scalability Class · MMU = Memory Management Unit · PSE51 = minimal single-process POSIX profile · ECUC = ECU Configuration · I-PDU = Interaction-layer PDU · `SCHED_DEADLINE` = Linux EDF scheduler · every row is sourced in the references</div>

---

## CP vs AP — the platform split (2/2)

<style scoped>
  section { font-size: 21px; padding-top: 38px; }
  table { font-size: 16.5px; }
  table td, table th { padding: 4px 10px; }
  .gloss { font-size: 13.5px; margin-top: 8px; }
  h2 { margin-bottom: 6px; }
</style>

| Dimension | **Classic Platform (CP)** | **Adaptive Platform (AP)** |
|---|---|---|
| **Safety** | mature ISO 26262 **up to ASIL D** (first ASIL-D AUTOSAR impl certified 2016) | documented "up to ASIL D," harder in practice; **ASIL-B shipping, ASIL-D underway** |
| **Update** | reflash the **whole ECU** via bootloader/UDS (0x34/0x36/0x37) | **UCM** — install/update individual Software Clusters; OTA-native |
| **Diagnostics** | **DCM + DEM** — UDS over DoCAN/DoIP | **DM** (`ara::diag`) — UDS server *and* SOVD; DoIP only standardized transport (custom permitted) |
| **Tooling** | Vector MICROSAR / EB tresos / ETAS RTA-CAR; DaVinci | Vector MICROSAR Adaptive / EB corbos / ETAS RTA-VRTE / Qorix |
| **Silicon** | MCUs: Infineon AURIX, NXP S32K, Renesas RH850 | SoCs: NVIDIA Orin/Thor, Qualcomm, NXP S32G, Renesas R-Car |
| **Typical use** | brakes, EPS, body, powertrain — ASIL B–D actuators | ADAS/AD, HPC gateways, infotainment — often mixed-criticality with a CP safety island |

- **The "up to ASIL D" trap**: on paper both are "up to ASIL D." In practice AP's ASIL-D is
  achieved via mixed-criticality partitioning + a CP/lockstep companion — **not** the Linux/QNX
  host alone. **Do not call AP "low-ASIL," but do not call it "ASIL-D certified" either**

<div class="gloss">DCM/DEM = CP's diagnostic modules · DM = AP's Diagnostic Manager · UCM = Update and Configuration Management · DoCAN = Diagnostics over CAN (ISO 15765-2) · EPS = Electric Power Steering · AD = Autonomous Driving</div>

---

## Coexistence in one 2026 vehicle

- A modern SDV runs **both platforms at once**: **CP for the reflex nervous system, AP for the
  brain, Ethernet + gateways for the spine.** Zonal/actuator ECUs run Classic on CAN/LIN/FlexRay;
  central HPCs run Adaptive on Linux/QNX over automotive Ethernet
- **The signal↔service (S2S) gateway** is the key coexistence mechanism: it subscribes to
  Classic COM **signals**, repackages them, and offers them as SOME/IP **services** (and
  vice-versa) — *"acting like a remote SOME/IP node."* Shipped by **Vector MICROSAR** (S2S
  add-on), **Elektrobit** (EB tresos + EB corbos), **ETAS** (RTA-CAR + RTA-VRTE)
- **Diagnostics routing across the split — two distinct boxes**: the **TCU** terminates the
  external 4G/5G link (TLS + certificates); a separate **central gateway** (DoIP router +
  **firewall** — the security chokepoint) routes **DoIP** on the backbone and re-transports it
  to **DoCAN** on CAN branches — **raw UDS is never exposed to the internet; SOVD is the external API**
- **The OEM "wrap" pattern**: AUTOSAR adopted *selectively* inside a proprietary base layer.
  **Mercedes MB.OS** Base Layer was co-developed with Vector, *"based on AUTOSAR Adaptive and
  Classic and the AUTOSAR Runtime Environment"* — AUTOSAR is an **ingredient, not the platform**.
  VW's **E³** (E3 1.1 MEB / E3 1.2 PPE, CARIAD software) is **domain-controller-based today** (ICAS1–3 / five HPCs); its zonal + central-AP shape is the announced next step (**SSP / E3 2.0**)

<div class="gloss">SDV = Software-Defined Vehicle · S2S = Signal-to-Service gateway · TCU = Telematics Control Unit (modem + cloud endpoint) · MB.OS = Mercedes-Benz Operating System · MEB = VW's Modular Electric Drive Matrix · PPE = Premium Platform Electric · CARIAD = VW Group's software subsidiary · ICAS = In-Car Application Server · SSP = Scalable Systems Platform · migrating a function CP→AP is a re-architecting (new interface, rewrite in `ara::com`, manifests + UCM packaging, S2S gateway, re-done safety case) — not a recompile</div>

---

## Fleet ↔ a CP+AP vehicle — one request, end to end

<style scoped>
  section { font-size: 19.5px; padding-top: 28px; }
  h2 { margin-bottom: 4px; }
  p { margin: 5px 0; }
  ol { margin: 4px 0; }
  .gloss { font-size: 13px; margin-top: 8px; }
</style>

**Read a fault code from a zonal brake ECU, starting in the cloud:**

1. The backend speaks **SOVD (REST/JSON over HTTPS)** and collects **MQTT telemetry** — **never raw UDS**; the vehicle's entry point is the **TCU**
2. The **central gateway** (DoIP router + firewall) is the security chokepoint for everything below it
3. Target lives on **AP** → the **DM** (`ara::diag`) on the HPC answers: UDS-over-DoIP, or SOVD natively
4. Target lives on **CP** → the gateway **re-transports DoIP → DoCAN**; the ECU's **DCM+DEM** answer. **Same UDS bytes, different transport** — the Classic ECU just sees "a tester"

**Push an update:** **V-UCM** on the HPC orchestrates the whole vehicle — AP **Software Clusters** go through UCM (transfer → process → activate, with rollback); CP ECUs are **reflashed over UDS 0x34–0x37** through the gateway, exactly like a workshop flash session

**Real vehicles shaped like this:** **Mercedes MB.OS** — CP + AP coexisting under one Vector-built base layer (the named production example) · **Rivian Gen 2** — the zonal topology shipped for real: **3 zone ECUs (West / East / South) + dual NVIDIA DRIVE Orin** as central compute — cited for the *shape*; Rivian's software stack is its own, not an AUTOSAR deployment

<div class="gloss">SOVD = Service-Oriented Vehicle Diagnostics (ISO 17978) · TCU = Telematics Control Unit · DoIP / DoCAN = UDS transports (ISO 13400 / ISO 15765-2) · DM = Diagnostic Manager (AP — one diagnostic server per Software Cluster) · DCM + DEM = Diagnostic Communication / Event Manager (CP) · V-UCM = Vehicle Update & Configuration Management · the punchline: one diagnostic language (UDS, ISO 14229), two transports, two server implementations</div>

---

<!-- _class: diagram -->

<img alt="fleet-uds-flow" src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA5NjAgNjAwIiB3aWR0aD0iOTYwIiBoZWlnaHQ9IjYwMCIgZm9udC1mYW1pbHk9IkhlbHZldGljYSwgQXJpYWwsIHNhbnMtc2VyaWYiPgogIDxyZWN0IHg9IjAiIHk9IjAiIHdpZHRoPSI5NjAiIGhlaWdodD0iNjAwIiBmaWxsPSIjZmZmZmZmIi8+CgogIDxkZWZzPgogICAgPG1hcmtlciBpZD0iYXJyIiBtYXJrZXJXaWR0aD0iMTAiIG1hcmtlckhlaWdodD0iMTAiIHJlZlg9IjgiIHJlZlk9IjMiIG9yaWVudD0iYXV0byIgbWFya2VyVW5pdHM9InN0cm9rZVdpZHRoIj4KICAgICAgPHBhdGggZD0iTTAsMCBMOSwzIEwwLDYgeiIgZmlsbD0iIzQ0NCIvPgogICAgPC9tYXJrZXI+CiAgICA8bWFya2VyIGlkPSJhcnJiIiBtYXJrZXJXaWR0aD0iMTAiIG1hcmtlckhlaWdodD0iMTAiIHJlZlg9IjgiIHJlZlk9IjMiIG9yaWVudD0iYXV0byIgbWFya2VyVW5pdHM9InN0cm9rZVdpZHRoIj4KICAgICAgPHBhdGggZD0iTTAsMCBMOSwzIEwwLDYgeiIgZmlsbD0iIzJFNUZBQyIvPgogICAgPC9tYXJrZXI+CiAgPC9kZWZzPgoKICA8IS0tIFRpdGxlIC0tPgogIDx0ZXh0IHg9IjQ4MCIgeT0iNDAiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMjYiIGZvbnQtd2VpZ2h0PSI3MDAiIGZpbGw9IiMxYjJiNGEiPkZsZWV0IGRpYWdub3N0aWNzIGVuZC10by1lbmQg4oCUIHdoZXJlIFVEUyByZWFsbHkgbGl2ZXMgKDIwMjYpPC90ZXh0PgoKICA8IS0tID09PT09PT09PT09PT09PT09PT09PSBGbGVldCBiYWNrZW5kICh0b3ApID09PT09PT09PT09PT09PT09PT09PSAtLT4KICA8cmVjdCB4PSIyMzAiIHk9IjU4IiB3aWR0aD0iNTAwIiBoZWlnaHQ9IjQyIiByeD0iOCIgZmlsbD0iI0RGRjBEOCIgc3Ryb2tlPSIjOEZCRjhGIiBzdHJva2Utd2lkdGg9IjEuNSIvPgogIDx0ZXh0IHg9IjQ4MCIgeT0iODQiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTMuNSIgZmlsbD0iIzJkNWEyZCI+RmxlZXQgYmFja2VuZCDigJQgdGVsZW1ldHJ5IERCIMK3IHByZWRpY3RpdmUgbWFpbnRlbmFuY2UgwrcgT1RBIGNhbXBhaWduczwvdGV4dD4KCiAgPCEtLSA9PT09PT09PT09PT09PT09PT09PT0gV2lyZWxlc3MgbGluayB6b25lID09PT09PT09PT09PT09PT09PT09PSAtLT4KICA8bGluZSB4MT0iMjQ4IiB5MT0iMTA0IiB4Mj0iMjQ4IiB5Mj0iMTk2IiBzdHJva2U9IiMyRTVGQUMiIHN0cm9rZS13aWR0aD0iMS41IiBzdHJva2UtZGFzaGFycmF5PSI2LDQiIG1hcmtlci1lbmQ9InVybCgjYXJyYikiLz4KICA8bGluZSB4MT0iNzEyIiB5MT0iMTA0IiB4Mj0iNzEyIiB5Mj0iMTk2IiBzdHJva2U9IiMyRTVGQUMiIHN0cm9rZS13aWR0aD0iMS41IiBzdHJva2UtZGFzaGFycmF5PSI2LDQiIG1hcmtlci1lbmQ9InVybCgjYXJyYikiLz4KICA8dGV4dCB4PSIyNTgiIHk9IjEyNiIgdGV4dC1hbmNob3I9InN0YXJ0IiBmb250LXNpemU9IjExIiBmaWxsPSIjMjIzMzQ0Ij50ZWxlbWV0cnk6IE1RVFQgLyBwcm9wcmlldGFyeSB0ZWxlbWF0aWNzIChjb250aW51b3VzIGRhdGEpPC90ZXh0PgogIDx0ZXh0IHg9IjcwMiIgeT0iMTQ4IiB0ZXh0LWFuY2hvcj0iZW5kIiBmb250LXNpemU9IjExIiBmaWxsPSIjMjIzMzQ0Ij5kaWFnbm9zdGljczogU09WRCDigJQgUkVTVC9IVFRQICsgSlNPTiAoSVNPIDE3OTc4OjIwMjYpPC90ZXh0PgogIDx0ZXh0IHg9IjQ4MCIgeT0iMTcyIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjExIiBmb250LXN0eWxlPSJpdGFsaWMiIGZpbGw9IiNiMDRhNGEiPnJhdyBVRFMgaXMgTk9UIGV4cG9zZWQgdG8gdGhlIGludGVybmV0PC90ZXh0PgoKICA8IS0tID09PT09PT09PT09PT09PT09PT09PSBWZWhpY2xlIGJvdW5kYXJ5ID09PT09PT09PT09PT09PT09PT09PSAtLT4KICA8cmVjdCB4PSI2MCIgeT0iMjAwIiB3aWR0aD0iODQwIiBoZWlnaHQ9IjM0MCIgcng9IjgiIGZpbGw9IiNFQUYxRkIiIHN0cm9rZT0iIzJFNUZBQyIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtZGFzaGFycmF5PSI3LDUiLz4KICA8dGV4dCB4PSI5MCIgeT0iMjIzIiBmb250LXNpemU9IjEyIiBmb250LXdlaWdodD0iNzAwIiBmb250LXN0eWxlPSJpdGFsaWMiIGZpbGw9IiMyRTVGQUMiPnZlaGljbGU8L3RleHQ+CgogIDwhLS0gVENVIC0tPgogIDxyZWN0IHg9IjI4MCIgeT0iMjMyIiB3aWR0aD0iNDAwIiBoZWlnaHQ9IjQ0IiByeD0iOCIgZmlsbD0iI0RDRTlGNyIgc3Ryb2tlPSIjN2Y5ZGM5IiBzdHJva2Utd2lkdGg9IjEuNSIvPgogIDx0ZXh0IHg9IjQ4MCIgeT0iMjU5IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjEzIiBmaWxsPSIjMjIzMzQ0Ij5UQ1Ug4oCUIHRlbGVtYXRpY3MgdW5pdCAoNEcvNUcgbW9kZW0sIFRMUyArIGNlcnRpZmljYXRlcyk8L3RleHQ+CgogIDxsaW5lIHgxPSI0ODAiIHkxPSIyNzYiIHgyPSI0ODAiIHkyPSIyOTIiIHN0cm9rZT0iIzQ0NCIgc3Ryb2tlLXdpZHRoPSIyIiBtYXJrZXItZW5kPSJ1cmwoI2FycikiLz4KCiAgPCEtLSBDZW50cmFsIGdhdGV3YXkgLS0+CiAgPHJlY3QgeD0iMTEwIiB5PSIyOTQiIHdpZHRoPSI3NDAiIGhlaWdodD0iNDgiIHJ4PSI4IiBmaWxsPSIjRENFOUY3IiBzdHJva2U9IiM3ZjlkYzkiIHN0cm9rZS13aWR0aD0iMS41Ii8+CiAgPHRleHQgeD0iNDgwIiB5PSIzMjMiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTIuNSIgZmlsbD0iIzIyMzM0NCI+Y2VudHJhbCBnYXRld2F5IOKAlCBEb0lQIGdhdGV3YXkgKyBmaXJld2FsbDogdGhlIHNlY3VyaXR5IGNob2tlcG9pbnQ7IHRyYW5zbGF0ZXMgZXh0ZXJuYWwgcmVxdWVzdHMgaW50byBpbi12ZWhpY2xlIFVEUzwvdGV4dD4KCiAgPGxpbmUgeDE9IjI5MCIgeTE9IjM0MiIgeDI9IjI5MCIgeTI9IjM3MiIgc3Ryb2tlPSIjNDQ0IiBzdHJva2Utd2lkdGg9IjIiIG1hcmtlci1lbmQ9InVybCgjYXJyKSIvPgogIDxsaW5lIHgxPSI2NzAiIHkxPSIzNDIiIHgyPSI2NzAiIHkyPSIzNzIiIHN0cm9rZT0iIzQ0NCIgc3Ryb2tlLXdpZHRoPSIyIiBtYXJrZXItZW5kPSJ1cmwoI2FycikiLz4KCiAgPCEtLSBOZXR3b3JrIGJyYW5jaGVzIC0tPgogIDxyZWN0IHg9IjExMCIgeT0iMzc0IiB3aWR0aD0iMzYwIiBoZWlnaHQ9IjQ0IiByeD0iOCIgZmlsbD0iI0VBRjFGQiIgc3Ryb2tlPSIjOUJCQ0UwIiBzdHJva2Utd2lkdGg9IjEuNSIvPgogIDx0ZXh0IHg9IjI5MCIgeT0iNDAxIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjEyLjUiIGZpbGw9IiMyMzQiPkV0aGVybmV0IGJhY2tib25lIOKAlCBEb0lQL1VEUyArIFNPTUUvSVA8L3RleHQ+CgogIDxyZWN0IHg9IjQ5MCIgeT0iMzc0IiB3aWR0aD0iMzYwIiBoZWlnaHQ9IjQ0IiByeD0iOCIgZmlsbD0iI0VBRjFGQiIgc3Ryb2tlPSIjOUJCQ0UwIiBzdHJva2Utd2lkdGg9IjEuNSIvPgogIDx0ZXh0IHg9IjY3MCIgeT0iNDAxIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjEyLjUiIGZpbGw9IiMyMzQiPkNBTiAvIENBTi1GRCBicmFuY2hlcyDigJQgQ2FuVHAvVURTPC90ZXh0PgoKICA8bGluZSB4MT0iMjkwIiB5MT0iNDE4IiB4Mj0iMjAwIiB5Mj0iNDQ2IiBzdHJva2U9IiM0NDQiIHN0cm9rZS13aWR0aD0iMiIgbWFya2VyLWVuZD0idXJsKCNhcnIpIi8+CiAgPGxpbmUgeDE9IjY3MCIgeTE9IjQxOCIgeDI9IjQ4MCIgeTI9IjQ0NiIgc3Ryb2tlPSIjNDQ0IiBzdHJva2Utd2lkdGg9IjIiIG1hcmtlci1lbmQ9InVybCgjYXJyKSIvPgogIDxsaW5lIHgxPSI2NzAiIHkxPSI0MTgiIHgyPSI3NjAiIHkyPSI0NDYiIHN0cm9rZT0iIzQ0NCIgc3Ryb2tlLXdpZHRoPSIyIiBtYXJrZXItZW5kPSJ1cmwoI2FycikiLz4KCiAgPCEtLSBCb3R0b20gY29tcHV0ZSByb3cgLS0+CiAgPHJlY3QgeD0iNzAiIHk9IjQ0NiIgd2lkdGg9IjI2MCIgaGVpZ2h0PSI2NCIgcng9IjgiIGZpbGw9IiNGQ0U4RDUiIHN0cm9rZT0iI0UwQTk2RCIgc3Ryb2tlLXdpZHRoPSIxLjUiLz4KICA8dGV4dCB4PSIyMDAiIHk9IjQ2NSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMS41IiBmaWxsPSIjNkI0QTJCIj5IUEMgLyBjZW50cmFsIGNvbXB1dGVyIOKAlDwvdGV4dD4KICA8dGV4dCB4PSIyMDAiIHk9IjQ4MiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMS41IiBmaWxsPSIjNkI0QTJCIj5BZGFwdGl2ZSBETSAoYXJhOjpkaWFnKSw8L3RleHQ+CiAgPHRleHQgeD0iMjAwIiB5PSI0OTkiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTEuNSIgZmlsbD0iIzZCNEEyQiI+VUNNIGZvciBPVEEgaW5zdGFsbDwvdGV4dD4KCiAgPHJlY3QgeD0iMzUwIiB5PSI0NDYiIHdpZHRoPSIyNjAiIGhlaWdodD0iNjQiIHJ4PSI4IiBmaWxsPSIjRkNFOEQ1IiBzdHJva2U9IiNFMEE5NkQiIHN0cm9rZS13aWR0aD0iMS41Ii8+CiAgPHRleHQgeD0iNDgwIiB5PSI0ODIiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTEuNSIgZmlsbD0iIzZCNEEyQiI+em9uYWwvZG9tYWluIEVDVXMg4oCUIENsYXNzaWMgRENNICsgREVNPC90ZXh0PgoKICA8cmVjdCB4PSI2MzAiIHk9IjQ0NiIgd2lkdGg9IjI2MCIgaGVpZ2h0PSI2NCIgcng9IjgiIGZpbGw9IiNGQ0U4RDUiIHN0cm9rZT0iI0UwQTk2RCIgc3Ryb2tlLXdpZHRoPSIxLjUiLz4KICA8dGV4dCB4PSI3NjAiIHk9IjQ4MiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMS41IiBmaWxsPSIjNkI0QTJCIj5sZWdhY3kgRUNVcyDigJQgQ2xhc3NpYyBEQ00gKyBERU08L3RleHQ+CgogIDwhLS0gRm9vdG5vdGUgLS0+CiAgPHRleHQgeD0iNDgwIiB5PSI1NzUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTEiIGZvbnQtc3R5bGU9Iml0YWxpYyIgZmlsbD0iIzU1NSI+VURTIDB4MkEgcGVyaW9kaWMgcmVhZHMgZXhpc3QsIGJ1dCBjb250aW51b3VzIGZsZWV0IHRlbGVtZXRyeSBydW5zIG9uIHRlbGVtYXRpY3MgcGlwZWxpbmVzIOKAlCBVRFMgc3RheXMgYSBkaWFnbm9zdGljIHByb3RvY29sPC90ZXh0PgoKICA8IS0tIEFiYnJldmlhdGlvbiBrZXkgLS0+CiAgPHRleHQgeD0iNDgwIiB5PSI1OTIiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iOS41IiBmaWxsPSIjNTU1NTU1Ij5TT1ZEID0gUkVTVC9KU09OIGRpYWdub3N0aWMgQVBJIChJU08gMTc5NzgpICYjMTgzOyBVRFMgPSB1bmlmaWVkIGRpYWdub3N0aWMgc2VydmljZXMgKElTTyAxNDIyOSkgJiMxODM7IERvSVAgLyBDYW5UcCA9IFVEUyBvdmVyIElQIC8gb3ZlciBDQU4gJiMxODM7IERNK1VDTSAvIERDTStERU0gPSBBZGFwdGl2ZSAvIENsYXNzaWMgZGlhZ25vc3RpYyAmYW1wOyB1cGRhdGUgbW9kdWxlczwvdGV4dD4KPC9zdmc+Cg==" />

---

<!-- _class: diagram -->

<img alt="fleet-on-thor" src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA5NjAgNjAwIiB3aWR0aD0iOTYwIiBoZWlnaHQ9IjYwMCIgZm9udC1mYW1pbHk9IkhlbHZldGljYSwgQXJpYWwsIHNhbnMtc2VyaWYiPgogIDxyZWN0IHg9IjAiIHk9IjAiIHdpZHRoPSI5NjAiIGhlaWdodD0iNjAwIiBmaWxsPSIjZmZmZmZmIi8+CgogIDxkZWZzPgogICAgPG1hcmtlciBpZD0iYXJyIiBtYXJrZXJXaWR0aD0iMTAiIG1hcmtlckhlaWdodD0iMTAiIHJlZlg9IjgiIHJlZlk9IjMiIG9yaWVudD0iYXV0byIgbWFya2VyVW5pdHM9InN0cm9rZVdpZHRoIj4KICAgICAgPHBhdGggZD0iTTAsMCBMOSwzIEwwLDYgeiIgZmlsbD0iIzQ0NCIvPgogICAgPC9tYXJrZXI+CiAgPC9kZWZzPgoKICA8IS0tIFRpdGxlIC0tPgogIDx0ZXh0IHg9IjQ4MCIgeT0iNDAiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMjYiIGZvbnQtd2VpZ2h0PSI3MDAiIGZpbGw9IiMxYjJiNGEiPkZsZWV0IG1hbmFnZW1lbnQgb24gRFJJVkUgVGhvciDigJQgd2hhdCdzIGFjdHVhbGx5IGRvY3VtZW50ZWQgKDIwMjYpPC90ZXh0PgoKICA8IS0tID09PT09PT09PT09PT09PT09PT09PSBGbGVldCBiYWNrZW5kICh0b3ApID09PT09PT09PT09PT09PT09PT09PSAtLT4KICA8cmVjdCB4PSIyMDAiIHk9IjU4IiB3aWR0aD0iNTYwIiBoZWlnaHQ9IjQwIiByeD0iOCIgZmlsbD0iI0RGRjBEOCIgc3Ryb2tlPSIjOEZCRjhGIiBzdHJva2Utd2lkdGg9IjEuNSIvPgogIDx0ZXh0IHg9IjQ4MCIgeT0iODMiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTMuNSIgZmlsbD0iIzJkNWEyZCI+RmxlZXQgYmFja2VuZCDigJQgT1RBIGNhbXBhaWducyDCtyB0ZWxlbWV0cnkgwrcgU09WRC90ZWxlbWF0aWNzIEFQSXM8L3RleHQ+CgogIDxsaW5lIHgxPSI0ODAiIHkxPSI5OCIgeDI9IjQ4MCIgeTI9IjExMCIgc3Ryb2tlPSIjNDQ0IiBzdHJva2Utd2lkdGg9IjIiIG1hcmtlci1lbmQ9InVybCgjYXJyKSIvPgoKICA8IS0tID09PT09PT09PT09PT09PT09PT09PSBUQ1UgKyBjZW50cmFsIGdhdGV3YXkgPT09PT09PT09PT09PT09PT09PT09IC0tPgogIDxyZWN0IHg9IjE3MCIgeT0iMTEyIiB3aWR0aD0iNTYwIiBoZWlnaHQ9IjQ0IiByeD0iOCIgZmlsbD0iI0RDRTlGNyIgc3Ryb2tlPSIjN2Y5ZGM5IiBzdHJva2Utd2lkdGg9IjEuNSIvPgogIDx0ZXh0IHg9IjQ1MCIgeT0iMTM5IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjEyLjUiIGZpbGw9IiMyMjMzNDQiPlRDVSArIGNlbnRyYWwgZ2F0ZXdheSDigJQgc2VwYXJhdGUgRUNVczogdGVybWluYXRlIHRoZSBjbG91ZCBsaW5rLCBzcGVhayBVRFMgaW50byB0aGUgdmVoaWNsZTwvdGV4dD4KICA8dGV4dCB4PSI4NDUiIHk9IjEyOCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMC41IiBmb250LXN0eWxlPSJpdGFsaWMiIGZpbGw9IiMyRTVGQUMiPlRob3IgaGFzIG5vIGRvY3VtZW50ZWQ8L3RleHQ+CiAgPHRleHQgeD0iODQ1IiB5PSIxNDMiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTAuNSIgZm9udC1zdHlsZT0iaXRhbGljIiBmaWxsPSIjMkU1RkFDIj5mbGVldC1nYXRld2F5IHJvbGU8L3RleHQ+CgogIDwhLS0gQXJyb3dzIGZyb20gZ2F0ZXdheSBpbnRvIHRoZSBib2FyZCAtLT4KICA8bGluZSB4MT0iNDkwIiB5MT0iMTU2IiB4Mj0iNDkwIiB5Mj0iMjU3IiBzdHJva2U9IiM0NDQiIHN0cm9rZS13aWR0aD0iMiIgbWFya2VyLWVuZD0idXJsKCNhcnIpIi8+CiAgPHRleHQgeD0iNTAwIiB5PSIxODIiIHRleHQtYW5jaG9yPSJzdGFydCIgZm9udC1zaXplPSIxMSIgZmlsbD0iIzIyMzM0NCI+RG9JUCAvIFVEUzwvdGV4dD4KCiAgPHBhdGggZD0iTTcwMCwxNTYgTDcwMCwxNzggTDkyNSwxNzggTDkyNSw0OTAgTDg5MCw0OTAiIGZpbGw9Im5vbmUiIHN0cm9rZT0iIzQ0NCIgc3Ryb2tlLXdpZHRoPSIyIiBtYXJrZXItZW5kPSJ1cmwoI2FycikiLz4KICA8dGV4dCB4PSI5NDEiIHk9IjMzNCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMSIgZmlsbD0iIzIyMzM0NCIgdHJhbnNmb3JtPSJyb3RhdGUoLTkwIDk0MSAzMzQpIj5pbi12ZWhpY2xlIG5ldHdvcms8L3RleHQ+CgogIDwhLS0gPT09PT09PT09PT09PT09PT09PT09IERSSVZFIEFHWCBUaG9yIGJvYXJkID09PT09PT09PT09PT09PT09PT09PSAtLT4KICA8cmVjdCB4PSI2MCIgeT0iMjAwIiB3aWR0aD0iODQwIiBoZWlnaHQ9IjM0MCIgcng9IjgiIGZpbGw9IiNFQUYxRkIiIHN0cm9rZT0iIzJFNUZBQyIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtZGFzaGFycmF5PSI3LDUiLz4KICA8dGV4dCB4PSI4MiIgeT0iMjIxIiBmb250LXNpemU9IjEyIiBmb250LXdlaWdodD0iNzAwIiBmb250LXN0eWxlPSJpdGFsaWMiIGZpbGw9IiMyRTVGQUMiPkRSSVZFIEFHWCBUaG9yIGJvYXJkPC90ZXh0PgoKICA8IS0tIFRob3IgU29DIC0tPgogIDxyZWN0IHg9IjgwIiB5PSIyMjgiIHdpZHRoPSI3NDAiIGhlaWdodD0iMjEwIiByeD0iOCIgZmlsbD0iI0VDRUNFQyIgc3Ryb2tlPSIjQjBCMEIwIiBzdHJva2Utd2lkdGg9IjEuNSIvPgogIDx0ZXh0IHg9IjEwMCIgeT0iMjUwIiBmb250LXNpemU9IjEzLjUiIGZvbnQtd2VpZ2h0PSI3MDAiIGZpbGw9IiMzMzMiPlRob3IgU29DPC90ZXh0PgoKICA8IS0tIEd1ZXN0IE9TIFZNIC0tPgogIDxyZWN0IHg9Ijk1IiB5PSIyNjAiIHdpZHRoPSI1NzUiIGhlaWdodD0iMTIwIiByeD0iOCIgZmlsbD0iI0RDRTlGNyIgc3Ryb2tlPSIjN2Y5ZGM5IiBzdHJva2Utd2lkdGg9IjEuNSIvPgogIDx0ZXh0IHg9IjM4MiIgeT0iMjgwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjEyLjUiIGZpbGw9IiMyMjMzNDQiPkd1ZXN0IE9TIFZNIOKAlCBRTlggb3IgTGludXggKHB1YmxpYyBTREs6IG9uZSBndWVzdCwgbm90IGJvdGgpPC90ZXh0PgoKICA8cmVjdCB4PSIxMTAiIHk9IjI5MiIgd2lkdGg9IjE3NSIgaGVpZ2h0PSI3MiIgcng9IjgiIGZpbGw9IiNGQ0U4RDUiIHN0cm9rZT0iI0UwQTk2RCIgc3Ryb2tlLXdpZHRoPSIxLjUiLz4KICA8dGV4dCB4PSIxOTciIHk9IjMzMiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMS41IiBmaWxsPSIjNkI0QTJCIj5PRU0gQVYgc3RhY2sgwrcgRHJpdmVXb3JrczwvdGV4dD4KCiAgPHJlY3QgeD0iMzAwIiB5PSIyOTIiIHdpZHRoPSIzNTUiIGhlaWdodD0iNzIiIHJ4PSI4IiBmaWxsPSIjREZGMEQ4IiBzdHJva2U9IiM4RkJGOEYiIHN0cm9rZS13aWR0aD0iMS41Ii8+CiAgPHRleHQgeD0iNDc4IiB5PSIzMTAiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTEiIGZvbnQtd2VpZ2h0PSI3MDAiIGZpbGw9IiMyZDVhMmQiPkFVVE9TQVIgQWRhcHRpdmUg4oCUIFRpZXItMTogVmVjdG9yIE1JQ1JPU0FSLCBFQiBjb3Jib3M8L3RleHQ+CiAgPHRleHQgeD0iNDc4IiB5PSIzMzAiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTAuNSIgZmlsbD0iIzJkNWEyZCI+RE0gKGFyYTo6ZGlhZykg4oCUIFVEUyBvdmVyIERvSVAsIG9uZSBzZXJ2ZXIgcGVyIFNvZnR3YXJlIENsdXN0ZXI8L3RleHQ+CiAgPHRleHQgeD0iNDc4IiB5PSIzNDciIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTAuNSIgZmlsbD0iIzJkNWEyZCI+VUNNIOKAlCBPVEEgaW5zdGFsbCBwZXIgU29mdHdhcmUgQ2x1c3RlcjwvdGV4dD4KCiAgPCEtLSBEcml2ZU9TIHN0cmlwIC0tPgogIDxyZWN0IHg9Ijk1IiB5PSIzOTIiIHdpZHRoPSI1NzUiIGhlaWdodD0iMzQiIHJ4PSI4IiBmaWxsPSIjRENFOUY3IiBzdHJva2U9IiM3ZjlkYzkiIHN0cm9rZS13aWR0aD0iMS41Ii8+CiAgPHRleHQgeD0iMzgyIiB5PSI0MTMiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTIiIGZpbGw9IiMyMjMzNDQiPkRyaXZlT1MgNyDigJQgVHlwZS0xIGh5cGVydmlzb3IgKyBOVklESUEgc2VydmljZSBWTXMgKHN0b3JhZ2UgwrcgZGlzcGxheSDCtyBHUFUgc2hhcmluZyk8L3RleHQ+CgogIDwhLS0gRlNJIC0tPgogIDxyZWN0IHg9IjY4NSIgeT0iMjYwIiB3aWR0aD0iMTIwIiBoZWlnaHQ9IjE2NiIgcng9IjgiIGZpbGw9IiNFQUYxRkIiIHN0cm9rZT0iIzlCQkNFMCIgc3Ryb2tlLXdpZHRoPSIxLjUiLz4KICA8dGV4dCB4PSI3NDUiIHk9IjI5MCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMC41IiBmaWxsPSIjMjM0Ij5GU0kg4oCUIGxvY2tzdGVwPC90ZXh0PgogIDx0ZXh0IHg9Ijc0NSIgeT0iMzA1IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjEwLjUiIGZpbGw9IiMyMzQiPkNvcnRleC1SNTIsPC90ZXh0PgogIDx0ZXh0IHg9Ijc0NSIgeT0iMzIwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjEwLjUiIGZpbGw9IiMyMzQiPnNlcGFyYXRlIHNpbGljb248L3RleHQ+CiAgPHRleHQgeD0iNzQ1IiB5PSIzNTAiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTAuNSIgZmlsbD0iIzIzNCI+VmVjdG9yIE1JQ1JPU0FSPC90ZXh0PgogIDx0ZXh0IHg9Ijc0NSIgeT0iMzY1IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjEwLjUiIGZpbGw9IiMyMzQiPkNsYXNzaWMgaW4gdGhlPC90ZXh0PgogIDx0ZXh0IHg9Ijc0NSIgeT0iMzgwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjEwLjUiIGZpbGw9IiMyMzQiPnJlZmVyZW5jZSBpbnRlZ3JhdGlvbjwvdGV4dD4KCiAgPCEtLSBjb21wYW5pb24gTUNVIC0tPgogIDxyZWN0IHg9IjU2MCIgeT0iNDUyIiB3aWR0aD0iMzI1IiBoZWlnaHQ9Ijc2IiByeD0iOCIgZmlsbD0iI0ZDRThENSIgc3Ryb2tlPSIjRTBBOTZEIiBzdHJva2Utd2lkdGg9IjEuNSIvPgogIDx0ZXh0IHg9IjcyMiIgeT0iNDc1IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjEyLjUiIGZvbnQtd2VpZ2h0PSI3MDAiIGZpbGw9IiM2QjRBMkIiPmNvbXBhbmlvbiBNQ1Ug4oCUIFJlbmVzYXMgUkg4NTA8L3RleHQ+CiAgPHRleHQgeD0iNzIyIiB5PSI0OTQiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTEiIGZpbGw9IiM2QjRBMkIiPk1JQ1JPU0FSIENsYXNzaWMgKEFGVyk6IERDTSArIERFTTwvdGV4dD4KICA8dGV4dCB4PSI3MjIiIHk9IjUxMSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMSIgZmlsbD0iIzZCNEEyQiI+Q2xhc3NpYyBBVVRPU0FSIGxhbmQg4oCUIGEgcmVhbCBFQ1UsIG5vdCBhIFZNPC90ZXh0PgoKICA8IS0tIENvbm5lY3RvciBTb0MgPC0+IGNvbXBhbmlvbiBNQ1UgLS0+CiAgPHBhdGggZD0iTTIwMCw0MzggTDIwMCw0OTAgTDU2MCw0OTAiIGZpbGw9Im5vbmUiIHN0cm9rZT0iIzQ0NCIgc3Ryb2tlLXdpZHRoPSIxLjUiLz4KICA8dGV4dCB4PSIzNzUiIHk9IjQ4MyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMC41IiBmb250LXN0eWxlPSJpdGFsaWMiIGZpbGw9IiM1NTUiPnByb3ByaWV0YXJ5IENvbW1vbiBJbnRlcmZhY2UgKFVEUCBvdmVyIEV0aGVybmV0KSDigJQgbm90IERvSVA8L3RleHQ+CgogIDwhLS0gRm9vdG5vdGUgLS0+CiAgPHRleHQgeD0iNDgwIiB5PSI1NjAiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTEiIGZvbnQtc3R5bGU9Iml0YWxpYyIgZmlsbD0iIzU1NSI+ZG9jdW1lbnRlZDogRE0gKyBVQ00gaW5zaWRlIHRoZSBndWVzdCwgQ2xhc3NpYyBvbiB0aGUgY29tcGFuaW9uIE1DVSAmIzgyMTI7IG5vIGZsZWV0LWdhdGV3YXkgcm9sZSwgbm8gdmlydHVhbCBDbGFzc2ljLUVDVSBwYXJ0aXRpb25zPC90ZXh0PgoKICA8IS0tIEFiYnJldmlhdGlvbiBrZXkgLS0+CiAgPHRleHQgeD0iNDgwIiB5PSI1NzgiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTAiIGZpbGw9IiM1NTU1NTUiPlRDVSA9IHRlbGVtYXRpY3MgY29udHJvbCB1bml0ICYjMTgzOyBVRFMgPSB1bmlmaWVkIGRpYWdub3N0aWMgc2VydmljZXMgJiMxODM7IERvSVAgPSBkaWFnbm9zdGljcyBvdmVyIElQICYjMTgzOyBETSAvIFVDTSA9IEFkYXB0aXZlIEFVVE9TQVIgZGlhZ25vc3RpY3MgLyB1cGRhdGUgJmFtcDsgY29uZmlnIG1hbmFnZW1lbnQ8L3RleHQ+CiAgPHRleHQgeD0iNDgwIiB5PSI1OTMiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTAiIGZpbGw9IiM1NTU1NTUiPkRDTSArIERFTSA9IENsYXNzaWMgQVVUT1NBUiBkaWFnbm9zdGljIG1vZHVsZXMgJiMxODM7IEZTSSA9IGZ1bmN0aW9uYWwgc2FmZXR5IGlzbGFuZCAmIzE4MzsgQUZXID0gVmVjdG9yJ3MgQVVUT1NBUiBmaXJtd2FyZSAmIzE4MzsgU09WRCA9IHRoZSBSRVNUIGRpYWdub3N0aWMgQVBJIChJU08gMTc5NzgpPC90ZXh0Pgo8L3N2Zz4K" />

---

## Convergence — the two worlds are moving together

- The old dichotomy *"signals = Classic, services = Adaptive; CAN = Classic, Ethernet = Adaptive"*
  is **outdated at the standard level.** R25-11-era moves close the gap:
- **DDS on the Classic Platform (new in R25-11 — the headline).** The CP Release Overview §2.1.1.5
  states management of *"Events, Methods, and Fields, previously available through SOME/IP, are
  now extended to DDS"* with a *"new BSW module **DDS Transformer**,"* *"full support of
  ClientServerInterface,"* and integration of the OMG **SPDP/SEDP** discovery protocols plus AP's
  Service Discovery. **Hedge to preserve: this is a *standard-level concept new in R25-11* — no
  shipping vendor implementation was verified; adoption timelines unconfirmed.** In principle a CP
  ECU can join the same DDS databus AP and ROS 2 already use
- **Dynamic memory, blessed on purpose** — the heap is permitted on the compute side, provided
  determinism is engineered back in (a philosophical convergence with the C++ application world)
- **MISRA C++:2023 merge** — the AUTOSAR C++14 guidelines folded into one industry standard
  targeting C++17 (formal ARA C++17 move stays open)
- **SOVD as the external-facing diagnostic API** (ISO 17978-3, REST/JSON/OAuth) and **Eclipse
  S-CORE** (open, dual-language C++/Rust, built by AUTOSAR's own members) are the other convergence signals

<div class="gloss">DDS = Data Distribution Service · SPDP/SEDP = the OMG Simple Participant / Endpoint Discovery Protocols · BSW = Basic Software · the CP DDS Transformer is R25-11 standard-level only — never present it as shipping</div>

---

<!-- _class: diagram -->

<img alt="dds-scope" src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA5NjAgNjAwIiB3aWR0aD0iOTYwIiBoZWlnaHQ9IjYwMCIgZm9udC1mYW1pbHk9IkhlbHZldGljYSwgQXJpYWwsIHNhbnMtc2VyaWYiPgogIDxyZWN0IHg9IjAiIHk9IjAiIHdpZHRoPSI5NjAiIGhlaWdodD0iNjAwIiBmaWxsPSIjZmZmZmZmIi8+CgogIDxkZWZzPgogICAgPG1hcmtlciBpZD0iYXJyIiBtYXJrZXJXaWR0aD0iMTAiIG1hcmtlckhlaWdodD0iMTAiIHJlZlg9IjgiIHJlZlk9IjMiIG9yaWVudD0iYXV0byIgbWFya2VyVW5pdHM9InN0cm9rZVdpZHRoIj4KICAgICAgPHBhdGggZD0iTTAsMCBMOSwzIEwwLDYgeiIgZmlsbD0iIzQ0NCIvPgogICAgPC9tYXJrZXI+CiAgPC9kZWZzPgoKICA8IS0tIFRpdGxlIC0tPgogIDx0ZXh0IHg9IjQ4MCIgeT0iNDAiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMjYiIGZvbnQtd2VpZ2h0PSI3MDAiIGZpbGw9IiMxYjJiNGEiPldoYXQgRERTIGFjdHVhbGx5IGNvbm5lY3RzIOKAlCBhbmQgd2hlcmUgaXQgc3RvcHM8L3RleHQ+CgogIDwhLS0gPT09PT09PT09PT09PT09PT09PT09IFRvcCByb3c6IHRocmVlIGdyZWVuIGJveGVzID09PT09PT09PT09PT09PT09PT09PSAtLT4KICA8cmVjdCB4PSI0MCIgeT0iNjQiIHdpZHRoPSIyODAiIGhlaWdodD0iODgiIHJ4PSI4IiBmaWxsPSIjREZGMEQ4IiBzdHJva2U9IiM4RkJGOEYiIHN0cm9rZS13aWR0aD0iMS41Ii8+CiAgPHRleHQgeD0iMTgwIiB5PSI5MiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMyIgZm9udC13ZWlnaHQ9IjcwMCIgZmlsbD0iIzJkNWEyZCI+c2FtZSBwcm9jZXNzPC90ZXh0PgogIDx0ZXh0IHg9IjE4MCIgeT0iMTE0IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjExIiBmaWxsPSIjMmQ1YTJkIj5ub2RlIEEg4oaUIG5vZGUgQjwvdGV4dD4KICA8dGV4dCB4PSIxODAiIHk9IjEzMiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMSIgZmlsbD0iIzJkNWEyZCI+aW50cmEtcHJvY2VzcyAob3B0LWluKTogcG9pbnRlcnMsIEREUyBieXBhc3NlZDwvdGV4dD4KCiAgPHJlY3QgeD0iMzQwIiB5PSI2NCIgd2lkdGg9IjI4MCIgaGVpZ2h0PSI4OCIgcng9IjgiIGZpbGw9IiNERkYwRDgiIHN0cm9rZT0iIzhGQkY4RiIgc3Ryb2tlLXdpZHRoPSIxLjUiLz4KICA8dGV4dCB4PSI0ODAiIHk9IjkyIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjEzIiBmb250LXdlaWdodD0iNzAwIiBmaWxsPSIjMmQ1YTJkIj5zYW1lIG1hY2hpbmU8L3RleHQ+CiAgPHRleHQgeD0iNDgwIiB5PSIxMTQiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTEiIGZpbGw9IiMyZDVhMmQiPnByb2Nlc3Mg4oaUIHByb2Nlc3M8L3RleHQ+CiAgPHRleHQgeD0iNDgwIiB5PSIxMzIiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTEiIGZpbGw9IiMyZDVhMmQiPnNoYXJlZCBtZW1vcnkgLyBsb29wYmFjayBVRFA8L3RleHQ+CgogIDxyZWN0IHg9IjY0MCIgeT0iNjQiIHdpZHRoPSIyODAiIGhlaWdodD0iODgiIHJ4PSI4IiBmaWxsPSIjREZGMEQ4IiBzdHJva2U9IiM4RkJGOEYiIHN0cm9rZS13aWR0aD0iMS41Ii8+CiAgPHRleHQgeD0iNzgwIiB5PSI5MiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMyIgZm9udC13ZWlnaHQ9IjcwMCIgZmlsbD0iIzJkNWEyZCI+YWNyb3NzIG1hY2hpbmVzPC90ZXh0PgogIDx0ZXh0IHg9Ijc4MCIgeT0iMTE0IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjExIiBmaWxsPSIjMmQ1YTJkIj5yb2JvdCDihpQgbGFwdG9wIOKGlCByb2JvdDwvdGV4dD4KICA8dGV4dCB4PSI3ODAiIHk9IjEzMiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMSIgZmlsbD0iIzJkNWEyZCI+RXRoZXJuZXQg4oCUIG11bHRpY2FzdCBkaXNjb3Zlcnk8L3RleHQ+CgogIDwhLS0gPT09PT09PT09PT09PT09PT09PT09IExvY2F0aW9uIHRyYW5zcGFyZW5jeSBzdHJpcCA9PT09PT09PT09PT09PT09PT09PT0gLS0+CiAgPHJlY3QgeD0iNDAiIHk9IjE3MCIgd2lkdGg9Ijg4MCIgaGVpZ2h0PSI0MCIgcng9IjgiIGZpbGw9IiNEQ0U5RjciIHN0cm9rZT0iIzdmOWRjOSIgc3Ryb2tlLXdpZHRoPSIxLjUiLz4KICA8dGV4dCB4PSI0ODAiIHk9IjE5NSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMi41IiBmaWxsPSIjMjIzMzQ0Ij5sb2NhdGlvbiB0cmFuc3BhcmVuY3kg4oCUIGlkZW50aWNhbCBwdWIvc3ViIEFQSSBpbiBhbGwgdGhyZWUgY2FzZXM7IHBhcnRpY2lwYW50cyBhcmUgT1MgcHJvY2Vzc2VzIHdpdGggYW4gSVAgc3RhY2s8L3RleHQ+CgogIDwhLS0gPT09PT09PT09PT09PT09PT09PT09IEJvdW5kYXJ5IGxpbmUgPT09PT09PT09PT09PT09PT09PT09IC0tPgogIDx0ZXh0IHg9IjY0IiB5PSIyNTQiIHRleHQtYW5jaG9yPSJzdGFydCIgZm9udC1zaXplPSIxMS41IiBmb250LXdlaWdodD0iNzAwIiBmb250LXN0eWxlPSJpdGFsaWMiIGZpbGw9IiMyRTVGQUMiPmJlbG93IHRoaXMgbGluZTogbm8gRERTPC90ZXh0PgogIDxsaW5lIHgxPSI2MCIgeTE9IjI2MiIgeDI9IjkwMCIgeTI9IjI2MiIgc3Ryb2tlPSIjMkU1RkFDIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1kYXNoYXJyYXk9IjcsNSIvPgoKICA8IS0tID09PT09PT09PT09PT09PT09PT09PSBCb3R0b20tbGVmdDogTUNVIC8gZmllbGRidXMgbGFuZCA9PT09PT09PT09PT09PT09PT09PT0gLS0+CiAgPHJlY3QgeD0iNjAiIHk9IjMzMCIgd2lkdGg9IjQyMCIgaGVpZ2h0PSIxNjAiIHJ4PSI4IiBmaWxsPSIjRkNFOEQ1IiBzdHJva2U9IiNFMEE5NkQiIHN0cm9rZS13aWR0aD0iMS41Ii8+CiAgPHRleHQgeD0iMjcwIiB5PSIzODgiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTIuNSIgZm9udC13ZWlnaHQ9IjcwMCIgZmlsbD0iIzZCNEEyQiI+TUNVIC8gZmllbGRidXMgbGFuZCDigJQgRk9DICZhbXA7IHNhZmV0eSBsb29wczwvdGV4dD4KICA8dGV4dCB4PSIyNzAiIHk9IjQxMSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMSIgZmlsbD0iIzZCNEEyQiI+RXRoZXJDQVQgwrcgQ0FOLUZEOiBzdGF0aWMgZnJhbWVzLCBubyBJUCBzdGFjazwvdGV4dD4KICA8dGV4dCB4PSIyNzAiIHk9IjQzMiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMC41IiBmaWxsPSIjNkI0QTJCIj4oY2Fyczogem9uYWwvYm9keSBFQ1VzIOKAlCBDQU4sIHNpZ25hbC1iYXNlZCBDbGFzc2ljIEFVVE9TQVIpPC90ZXh0PgoKICA8IS0tID09PT09PT09PT09PT09PT09PT09PSBCb3R0b20tcmlnaHQ6IHRoZSBicmlkZ2UgPT09PT09PT09PT09PT09PT09PT09IC0tPgogIDxyZWN0IHg9IjUwMCIgeT0iMzMwIiB3aWR0aD0iNDIwIiBoZWlnaHQ9IjE2MCIgcng9IjgiIGZpbGw9IiNFQUYxRkIiIHN0cm9rZT0iIzlCQkNFMCIgc3Ryb2tlLXdpZHRoPSIxLjUiLz4KICA8dGV4dCB4PSI3MTAiIHk9IjM3MiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMi41IiBmb250LXdlaWdodD0iNzAwIiBmaWxsPSIjMjIzMzQ0Ij50aGUgYnJpZGdlOiBtaWNyby1ST1M8L3RleHQ+CiAgPHRleHQgeD0iNzEwIiB5PSIzOTMiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTAuNSIgZmlsbD0iIzIyMzM0NCI+cmNsYyArIFhSQ0UtRERTIGNsaWVudCDigJQgYSBMSUJSQVJZIGxpbmtlZCBpbnRvPC90ZXh0PgogIDx0ZXh0IHg9IjcxMCIgeT0iNDEwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjEwLjUiIGZpbGw9IiMyMjMzNDQiPnlvdXIgZmlybXdhcmUsIGEgdGFzayBvbiBZT1VSIFJUT1M8L3RleHQ+CiAgPHRleHQgeD0iNzEwIiB5PSI0MjgiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTAuNSIgZmlsbD0iIzIyMzM0NCI+dGFsa3MgWFJDRSAobm90IEREUykgdG8gYW4gQWdlbnQgb24gdGhlIGJpZyBjb21wdXRlcjwvdGV4dD4KICA8dGV4dCB4PSI3MTAiIHk9IjQ0NiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMC41IiBmaWxsPSIjMjIzMzQ0Ij50aGUgQWdlbnQgam9pbnMgdGhlIGdyYXBoIG9uIHRoZSBNQ1UncyBiZWhhbGY8L3RleHQ+CgogIDwhLS0gQWdlbnQgYXJyb3cgYWNyb3NzIHRoZSBib3VuZGFyeSAtLT4KICA8bGluZSB4MT0iNzEwIiB5MT0iMzMwIiB4Mj0iNzEwIiB5Mj0iMjEyIiBzdHJva2U9IiM0NDQiIHN0cm9rZS13aWR0aD0iMiIgbWFya2VyLWVuZD0idXJsKCNhcnIpIi8+CiAgPHRleHQgeD0iNzIwIiB5PSIyNzgiIHRleHQtYW5jaG9yPSJzdGFydCIgZm9udC1zaXplPSIxMSIgZmlsbD0iIzIyMzM0NCI+QWdlbnQ8L3RleHQ+CgogIDwhLS0gRm9vdG5vdGUgLS0+CiAgPHRleHQgeD0iNDgwIiB5PSI1NTYiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTEiIGZvbnQtc3R5bGU9Iml0YWxpYyIgZmlsbD0iIzU1NSI+YXV0b21vdGl2ZSBtaXJyb3I6IG9uIFRob3IgdGhlIHNhbWUgcm9sZSBpcyBwbGF5ZWQgYnkgaW4tZ3Vlc3QgbWlkZGxld2FyZSAoTnZTdHJlYW1zIMK3IGFyYTo6Y29tIOKAlCBTT01FL0lQIG9yIEREUyBiaW5kaW5nKTs8L3RleHQ+CiAgPHRleHQgeD0iNDgwIiB5PSI1NzQiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTEiIGZvbnQtc3R5bGU9Iml0YWxpYyIgZmlsbD0iIzU1NSI+dGhlIEREUyB3aXJlIGZhbWlseSBpcyB3aGF0IEFVVE9TQVIgQWRhcHRpdmUgc2hhcmVzIHdpdGggUk9TIDIgKGJpbmRpbmcgc2luY2UgUjE4LTAzKTwvdGV4dD4KICA8dGV4dCB4PSI0ODAiIHk9IjU5MSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSI5LjUiIGZpbGw9IiM1NTU1NTUiPkREUyA9IGRhdGEgZGlzdHJpYnV0aW9uIHNlcnZpY2UgKFJPUyAyJ3MgcHViL3N1YiBtaWRkbGV3YXJlKSAmIzE4MzsgWFJDRS1ERFMgPSBERFMgZm9yIGV4dHJlbWVseSByZXNvdXJjZS1jb25zdHJhaW5lZCBlbnZpcm9ubWVudHMgKG1pY3JvLVJPUykgJiMxODM7IFNPTUUvSVAgPSBhdXRvbW90aXZlIHNlcnZpY2UgbWlkZGxld2FyZTwvdGV4dD4KPC9zdmc+Cg==" />

---

## Where ROS 2 sits — next to, not inside, AUTOSAR

- ROS 2 and AP **share the DDS wire family** (ROS 2's default RMW is DDS; AP has a DDS binding
  since R18-03) — **but they are NOT plug-compatible.** Blockers to naive DDS-to-DDS: ROS 2
  mangles topic names (`rt/…`, `rq/…`, `rr/…`) while AP-DDS uses `"ara.com://services/…"`
  partitions; type construction differs; AP's USER_DATA discovery mode isn't in ROS 2. **Interop
  goes through a bridge/gateway** (SOME/IP-DDS, ROS2-SOME/IP) — an active 2024–2026 research area
- **Positioning — prototyping/R&D vs production**: Apex.AI frames it as *"ROS 2 … code-first …
  as easy as possible to develop"* vs *"AUTOSAR … interoperability between suppliers and OEMs."*
  A 2026 arXiv comparison finds ROS 2 *"lacks several concepts essential for series-production"*
  (operation modes, allocation control, watchdog supervision) — **which is why AP exists alongside
  ROS 2 rather than replacing it**
- **The safe-C++ playbook converges**: the production ROS 2 derivative **Apex.Grace** is
  *"certified by TÜV Nord as a Safety Element out of Context (SEooC) up to ASIL D."* It enforces
  static memory pools and eliminates runtime allocation — mirroring AP's deterministic-allocator
  discipline. One genuinely shared building block: **iceoryx** — the low-level zero-copy IPC that sits *under* both stacks via separate bindings

<div class="gloss">ROS 2 = Robot Operating System 2 · RMW = ROS Middleware abstraction · DDS/RTPS = the shared wire family · SEooC = Safety Element out of Context · Apex.Grace = the ASIL-D-certified ROS 2 derivative (formerly Apex.OS) · Autoware = the flagship open AD stack on ROS 2</div>

---

## What this means for our embedded team

- **Classic is the world you already half-know.** Static config, no heap in safety paths,
  MPU partitions, E2E/SecOC, windowed watchdogs — **it is the same functional-safety mindset you
  use on MCUs, formalized and code-generated.** Learn CP to understand *why* automotive safety
  code looks the way it does
- **Adaptive is where the "big chip" is going.** Service-oriented, manifest-driven, OTA-updatable,
  C++ on POSIX — and its **DDS binding is the bridge to the ROS 2 knowledge this repo already
  teaches.** Learn AP (and ROS 2) to understand where the compute side is heading
- **Carry the corrected mental models, not the folklore:**
  - **DEM computes fault status; DCM only formats** — the #1 conceptual error to avoid
  - **SecOC = authenticity + freshness, NOT encryption**
  - **OS Timing Protection = budgets, NOT deadline supervision** (that's WdgM)
  - **Thor safety MCU = Renesas RH850U2A16, NOT AURIX** (Orin = AURIX TC397X)
  - **"DoIP-only" only with "standardized" attached**; **CP is not CAN-only**; **AP is not low-ASIL**
- **The hands-on next step**: contrast `github.com/langroodi/Adaptive-AUTOSAR` (MIT Linux AP
  simulator) with our `rclcpp`/DDS work — the natural bridge from ROS 2 into the AUTOSAR world

<div class="gloss">DEM/DCM = Diagnostic Event / Communication Manager · SecOC = Secure Onboard Communication · WdgM = Watchdog Manager · DoIP = Diagnostics over IP · every corrected model here is drawn from the three research docs behind this deck</div>

---

## Glossary — Adaptive Platform additions

<style scoped>
  section { font-size: 12.5px; padding-top: 28px; padding-bottom: 18px; line-height: 1.38; }
  ul { columns: 2; column-gap: 30px; margin-top: 4px; }
  li { margin-bottom: 1px; break-inside: avoid; }
  h2 { margin-bottom: 4px; font-size: 28px; }
  p { margin: 2px 0 2px 0; font-size: 13.5px; }
</style>

*(Extends the main deck's three-slide glossary — SWC/RTE/BSW/MCAL/CDD/ARXML/OSEK/AUTOSAR-OS/ARA/POSIX/PSE51/UDS/DoCAN/DoIP/DCM/DEM/UCM/SOVD are defined there.)*

- **FO / CP / AP** — Foundation / Classic Platform / Adaptive Platform: the three members of one AUTOSAR standard set
- **VFB** — Virtual Functional Bus: the logical bus SWCs talk over; the RTE implements it per ECU
- **COM / PduR / CanIf** — Classic signal packing / PDU router / CAN interface — the build-time-frozen TX/RX chain
- **E2E / SecOC** — End-to-End protection (CRC+counter, ISO 26262) / Secure Onboard Communication (MAC + freshness, no encryption)
- **NM / PN** — Network Management (synchronized wake/sleep) / Partial Networking (a subset sleeps)
- **EcuM / BswM** — ECU State Manager (lifecycle edges) / BSW Mode Manager (steady-state rule engine)
- **WdgM / StbM** — Watchdog Manager (Alive/Deadline/Logical supervision) / Synchronized Time-Base Manager
- **FFI** — Freedom From Interference: ISO 26262 spatial/temporal isolation between mixed-ASIL software
- **AA** — Adaptive Application: a POSIX process (C++, PSE51) linked against ARA
- **EM / SM** — Execution Management (starts/stops processes — the enforcer) / State Management (decides which run — the brain)
- **Function Group / Function Cluster** — AP's unit of composition (a set of processes with states) / a platform building block (`ara::…`)
- **Manifest** — ARXML deployment config (Execution / Service-Instance / Machine / Raw-Data-Stream / Software-Distribution)
- **`ara::com`** — the one AP communication API (proxy/skeleton), bound to SOME/IP or DDS in the manifest
- **event / trigger / method / field** — the four `ara::com` service-element kinds (trigger = a data-less event)
- **SOME/IP / DDS** — the two standardized `ara::com` wire bindings (DDS present since R18-03)
- **DM / V-UCM** — Diagnostic Management (`ara::diag`, merges DCM+DEM) / Vehicle UCM (vehicle-wide OTA campaign coordinator)
- **PHM / `ara::per`** — Platform Health Management (AP's WdgM analogue) / Persistency (KVS + File Storage)
- **iceoryx** — low-level zero-copy shared-memory IPC that sits under both AP and ROS 2 via separate bindings
- **S-CORE / SOAFEE** — Eclipse open dual-language (C++/Rust) SDV core stack / Arm-led cloud-native SDV architecture (containers, K8s, CI/CD)
- **S2S gateway** — Signal-to-Service gateway bridging Classic COM signals ⇄ SOME/IP services

---

## References 1/2 — AUTOSAR primary sources

<style scoped>
  section { font-size: 15px; padding-top: 28px; line-height: 1.32; }
  ul { margin-top: 4px; }
  li { margin-bottom: 2px; }
  h2 { margin-bottom: 6px; }
</style>

- **Release / structure**: [autosar.org/news-events/release-event](https://www.autosar.org/news-events/release-event) · [.../detail/release-r25-11-is-now-available](https://www.autosar.org/news-events/detail/release-r25-11-is-now-available) · [CP_TR_ReleaseOverview](https://www.autosar.org/fileadmin/standards/R25-11/CP/AUTOSAR_CP_TR_ReleaseOverview.pdf) (R25-11, DDS-on-CP, removed specs, schema) · [autosar.org/about/history](https://www.autosar.org/about/history)
- **Classic architecture**: [CP_EXP_LayeredSoftwareArchitecture](https://www.autosar.org/fileadmin/standards/R25-11/CP/AUTOSAR_CP_EXP_LayeredSoftwareArchitecture.pdf) (R25-11) · [FO_EXP_SWArchitecturalDecisions](https://www.autosar.org/fileadmin/standards/R25-11/FO/AUTOSAR_FO_EXP_SWArchitecturalDecisions.pdf) (R25-11, Doc 1078, dynamic memory) · [TR_Methodology](https://www.autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_TR_Methodology.pdf) (R22-11) · RTE/VFB: [hpi.de Naumann RTE_VFB](https://hpi.de/fileadmin/user_upload/fachgebiete/giese/Ausarbeitungen_AUTOSAR0809/NicoNaumann_RTE_VFB.pdf) · embetronicx.com RTE tutorial · [mxhelp.danlawinc.com](https://mxhelp.danlawinc.com/autosar_reference.htm)
- **Classic OS / comms**: [Vector AUTOSAR_Task_Scheduling](https://cdn.vector.com/cms/content/know-how/_technical-articles/AUTOSAR/AUTOSAR_Task_Scheduling_VU_201507_PressArticle_EN.pdf) (SC1–SC4) · [osek-vdx.org OS 2.2.3](https://www.osek-vdx.org/mirror/os223.pdf) · [SWS_ServiceDiscovery](https://www.autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_SWS_ServiceDiscovery.pdf) (R22-11) · [PRS_E2EProtocol](https://www.autosar.org/fileadmin/standards/R19-03/FO/AUTOSAR_PRS_E2EProtocol.pdf) (R19-03) · [FO_PRS_SecOcProtocol](https://www.autosar.org/fileadmin/standards/R24-11/FO/AUTOSAR_FO_PRS_SecOcProtocol.pdf) (R24-11) · [PRS_NetworkManagementProtocol](https://www.autosar.org/fileadmin/standards/R22-11/FO/AUTOSAR_PRS_NetworkManagementProtocol.pdf) (R22-11) · [eenews CAN-FD-vs-FlexRay](https://www.eenewseurope.com/en/infineon-can-fd-success-goes-at-the-expense-of-flexray/)
- **Classic services / safety**: [CP_SWS_DiagnosticEventManager](https://www.autosar.org/fileadmin/standards/R24-11/CP/AUTOSAR_CP_SWS_DiagnosticEventManager.pdf) (R24-11) · [CP_SWS_DiagnosticCommunicationManager](https://www.autosar.org/fileadmin/standards/R24-11/CP/AUTOSAR_CP_SWS_DiagnosticCommunicationManager.pdf) (R24-11) · [SWS_NVRAMManager](https://www.autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_SWS_NVRAMManager.pdf) (R22-11) · [EXP_ModeManagementGuide](https://www.autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_EXP_ModeManagementGuide.pdf) (R22-11) · [CP_SWS_WatchdogManager](https://www.autosar.org/fileadmin/standards/R23-11/CP/AUTOSAR_CP_SWS_WatchdogManager.pdf) (R23-11) · [SWS_SynchronizedTimeBaseManager](https://www.autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_SWS_SynchronizedTimeBaseManager.pdf) (R22-11) · [EXP_FunctionalSafetyMeasures](https://www.autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_EXP_FunctionalSafetyMeasures.pdf) (R22-11, Doc 664)
- **Vendors / silicon**: [vector.com MICROSAR Classic Safe ASIL-D recert](https://www.vector.com/us/en/news/news/vector-autosar-basic-software-successfully-re-certified-additional-modules-available-in-asil-d-2/) (exida) · [developer.nvidia.com DRIVE safety-MCU](https://developer.nvidia.com/docs/drive/drive-os/6.0.9/public/drive-os-linux-sdk/common/topics/mcu_setup_usage/mcu_setup_and_usage1.html) (Orin=AURIX TC397X / Thor=RH850U2A16, repo-verified) · [btc-embedded.com Classic vs Adaptive](https://www.btc-embedded.com/autosar-classic-vs-adaptive)

<div class="gloss">Full URLs, confidence levels and per-claim sourcing live in the three research docs behind this deck: autosar/research/autosar-classic-2026-07.md · autosar-adaptive-2026-07.md · classic-vs-adaptive-2026-07.md</div>

---

## References 2/2 — Adaptive, comparison & open efforts

<style scoped>
  section { font-size: 15px; padding-top: 28px; line-height: 1.32; }
  ul { margin-top: 4px; }
  li { margin-bottom: 2px; }
  h2 { margin-bottom: 6px; }
</style>

- **Adaptive architecture**: [AP_EXP_PlatformDesign](https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_EXP_PlatformDesign.pdf) (R25-11, Doc 706) · [AP_EXP_SWArchitecture](https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_EXP_SWArchitecture.pdf) (R25-11, Doc 982) · [AP_SWS_ExecutionManagement](https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_SWS_ExecutionManagement.pdf) (R25-11, Doc 721) · [AP_TPS_ManifestSpecification](https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_TPS_ManifestSpecification.pdf) (R25-11) · [AP_SWS_OperatingSystemInterface](https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_SWS_OperatingSystemInterface.pdf) (R25-11, PSE51)
- **Adaptive comms**: [AP_SWS_CommunicationManagement](https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_SWS_CommunicationManagement.pdf) (R25-11, Doc 717) · [rti.com AP 18.03 now-with-DDS](https://www.rti.com/blog/autosar-adaptive-platform-18.03-now-with-dds) + [status-of-DDS-in-AUTOSAR](https://www.rti.com/blog/status-of-dds-in-autosar) · [PRS_SOMEIPServiceDiscovery](https://www.autosar.org/fileadmin/standards/R19-03/FO/AUTOSAR_PRS_SOMEIPServiceDiscoveryProtocol.pdf) (R19-03) · [omg.org DDS-RPC 1.0](https://www.omg.org/spec/DDS-RPC/1.0) · [apex.ai iceoryx-speeds-up-AUTOSAR-and-ROS-2](https://www.apex.ai/post/eclipse-iceoryx-blueberry-speeds-up-autosar-and-ros-2)
- **Adaptive lifecycle / diag**: [AP_SWS_UpdateAndConfigurationManagement](https://www.autosar.org/fileadmin/standards/R24-11/AP/AUTOSAR_AP_SWS_UpdateAndConfigurationManagement.pdf) (R24-11, Doc 888) · [AP_SWS_VehicleUpdateAndConfigurationManagement](https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_SWS_VehicleUpdateAndConfigurationManagement.pdf) (R25-11, Doc 1090) · [AP_SWS_Diagnostics](https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_SWS_Diagnostics.pdf) (R25-11) · [AP_EXP_SOVD](https://www.autosar.org/fileadmin/standards/R24-11/AP/AUTOSAR_AP_EXP_SOVD.pdf) (R24-11, Doc 1064) · [AP_SWS_PlatformHealthManagement](https://www.autosar.org/fileadmin/standards/R24-11/AP/AUTOSAR_AP_SWS_PlatformHealthManagement.pdf) (R24-11) · [AP_SWS_Persistency](https://www.autosar.org/fileadmin/standards/R24-11/AP/AUTOSAR_AP_SWS_Persistency.pdf) (R24-11) · [asam.net SOVD](https://www.asam.net/standards/detail/sovd/) · [iso.org 17978-1](https://www.iso.org/standard/85133.html)
- **C++ / vendors / certs**: [autosar.org MISRA-integration announcement](https://www.autosar.org/news-events/detail/misra-consortium-announce-integration-of-autosar-c-coding-guidelines-into-updated-industry-standard) · [perforce.com MISRA-C++:2023](https://www.perforce.com/blog/qac/misra-cpp-2023-intro) · [vector.com Adaptive-Safe ASIL-B](https://www.vector.com/int/en/news/news/safe-asil-b-autosar-adaptive-software-for-high-performance-control-units-hpc-available/) · [etas.com ASIL-B TÜV SÜD](https://www.etas.com/ww/en/about-etas/newsroom/overview/strengthening-automotive-safety-compliance/) (March 2025) · qorix.ai TÜV-certified (Aug 2025) · [elektrobit.com EB-corbos-AdaptiveCore](https://www.elektrobit.com/products/ecu/eb-corbos/adaptivecore/) · [automotiveworld.com Wind-River ASIL-D program](https://www.automotiveworld.com/news-releases/wind-river-autosar-adaptive-automotive-software-ready-for-iso-26262-asil-d-certification-program/) · [vvdntech.com Vehicle-OS-Wars](https://www.vvdntech.com/en-us/blog/vehicle-os-wars-android-automotive-vs-qnx-vs-autosar-adaptive-vs-linux/) (QNX share)
- **Comparison / open**: [arxiv.org/pdf/2109.00099](https://arxiv.org/pdf/2109.00099) (AUTOSAR platforms) · [doi.org/10.3390/electronics14183635](https://doi.org/10.3390/electronics14183635) (AP↔ROS2 bridge) · [arxiv.org 2604.22576](https://arxiv.org/pdf/2604.22576) (ROS 2 vs AP, 2026) · [arxiv.org 2511.17540](https://arxiv.org/pdf/2511.17540) (AP↔ROS2 framework, 2025-11) · [apex.ai apexgrace](https://www.apex.ai/apexgrace) + [autosar-and-ros-2-for-SDV](https://www.apex.ai/post/autosar-and-ros-2-for-software-defined-vehicle) · [eclipse S-CORE launch](https://www.globenewswire.com/news-release/2025/06/12/3098131/0/en/the-eclipse-foundation-launches-the-s-core-project-the-automotive-industry-s-first-open-source-core-stack-for-software-defined-vehicles.html) · [covesa SOAFEE blueprint](https://covesa.global/wp-content/uploads/2024/05/SDV-Alliance-Integration-Blueprint-20240109.pdf) · [github.com/langroodi/Adaptive-AUTOSAR](https://github.com/langroodi/Adaptive-AUTOSAR) (MIT AP simulator)

<div class="gloss">Med/low-confidence items and open questions (CAN XL release · C++17 ARA move · SecOC "no confidentiality" wording · exact SC1–SC4 phrasing · S2S-gateway and arXiv rows · ASIL-D field evidence) are flagged as such in the research docs — not asserted here as settled fact.</div>
