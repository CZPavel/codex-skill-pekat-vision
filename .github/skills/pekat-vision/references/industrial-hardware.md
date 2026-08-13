# PEKAT hardware integration routing

## Universal boundary

1. Identify exact PEKAT version, device model/revision, connection path and owner.
2. Separate PEKAT integration from device commissioning.
3. Read identity/capability/current values before proposing a write.
4. Use exact manuals/IODD/node maps; never invent register, bit, pin, PLC, or camera-node mappings.
5. Default examples to read-only or `dry_run=True`. Writes require explicit approval, backup, exact source mapping, isolated target, readback and rollback.

## Router

| Target | PEKAT skill owns | Route deep detail to |
|---|---|---|
| Basler ace 2 area scan or racer 2 S line scan | acquisition architecture, image contract into PEKAT, FLOW/REST/SDK boundary | `basler-cameras` for exact model, pylon/pypylon, GigE/USB, trigger/encoder, bandwidth and lens work |
| IFM AL1304/AL1306 with O1D110, DV2131 or OPD101 | Code/Context/FLOW ownership, bounded HTTP client, failure behavior | `ifm-io-link` for IODD, PDIn/PDOut, ISDU, exact bytes/bits and device writes |
| MX-G2000 | decide standalone/PEKAT-integrated role, image/result/I/O boundary | exact revision manual and PEKAT/MX evidence; do not treat variants as interchangeable |
| Baumer VAX/PV50 | PEKAT project/flow integration and commissioning boundary | exact model/BSP/vendor documentation |
| Allied Vision Alecs | correct identity (not deprecated ADLINK alias), PEKAT install/support evidence boundary | exact Allied Vision/PEKAT model documentation |
| PLC/Snap7 | PEKAT Output/bridge architecture, payload ownership and timeout | exact PLC DB contract and current python-snap7/vendor docs |

If a specialized skill is unavailable, use current primary vendor documents and retain these safety rules; do not block basic PEKAT architecture work.

## Basler integration choices

Choose one explicit owner:

1. PEKAT native camera/provider path;
2. external pypylon application sends encoded/raw images to running PEKAT REST/SDK;
3. Projects Manager owns lifecycle while an external acquisition app owns frames;
4. controlled file/provider handoff for offline work.

Define dtype, dimensions, channels/pixel format, stride/packing, Bayer conversion, trigger/frame identity and timeout. For line scan also define encoder/LineStart mode, line rate, frame assembly and loss handling. Do not optimize FLOW before FOV, exposure/motion and bandwidth budgets are feasible.

## IFM / IO-Link minimum

Discover master firmware/ports/device identity first. Match IODD by exact device ID/revision. Preserve raw PDIn plus decoded engineering value and quality status. Treat PDOut/ISDU as writes even when exposed over HTTP. Poll/cache only when rate and latency justify it; otherwise keep the simple bounded read.

For an O1D110 through AL1306, a good PEKAT answer must name the port/identity discovery, exact process-data layout source, byte/bit order, validity/error fields, unit/scaling, timeout/failure key, and whether the value gates Context or writes GlobalData. Never copy an AL1304/AL1306 endpoint or O1D mapping from memory.

## Smart-camera and MX boundary

Decide whether training/configuration, acquisition, evaluation and PLC I/O live on the smart camera/appliance or on the PC PEKAT project. Avoid dual ownership. Keep recovery/persistent configuration changes manual and backed up unless explicitly authorized.

Physical acquisition, I/O and production acceptance remain open until performed on the exact hardware and version.

Legacy public routing IDs retained for regression: `industrial-hardware`, `hardware-supplemental-source-index-v1`.
