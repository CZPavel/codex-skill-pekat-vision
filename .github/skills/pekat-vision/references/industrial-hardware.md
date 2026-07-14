# Industrial hardware safety and routing

## Universal rules

1. Match the exact article/order code, firmware, manual, and IODD revision.
2. Read identity before decoding data.
3. Mock payloads and failures before a read-only isolated-device test.
4. Default generated operations to `dry_run=True`.
5. Require explicit approval, backup, exact map, isolated target, and rollback before writes.

Never invent IODD offsets, PLC DB layouts, camera features, ports, commands, or pinouts. Source index: `[hardware-supplemental-source-index-v1]`.

## IFM and IO-Link

For `ifm-00060B-20241119-IODD1.1.xml` only, identity is vendor ID `310`, device ID `1547`, product `O1D110`. The declared 64-bit PDIn contains signed 16-bit items at offsets 48 and 16, a 4-bit unsigned status at offset 4, and booleans at offsets 1 and 0. Preserve the IODD special-value meanings; do not reuse this map for another O1D variant.

Signal-light and parameter writes can affect equipment. Separate read/decode from write commands and expose writes only through an explicit mutation flag.

## PLC and Snap7

- Default to read-only with `192.0.2.10` placeholders.
- Require explicit rack/slot/DB/offset and strict buffer length/type checks.
- Separate transport, reconnect, and decode errors.
- Mock timeout, unreachable PLC, short buffer, bad datatype, and reconnect.
- Diagnostics write a dedicated status key and do not silently change PEKAT `result`.

## MX-G2000

Manual-derived evidence describes controlled airflow, at least 38.1 mm top/side clearance, reliable grounding, and a plant-contained network. The cited processor supports up to eight camera connections; I/O can be configured NPN or PNP. Verify the exact hardware/manual revision before installation or configuration. Never execute restoration/reset instructions automatically.

## Baumer VAX-50C.I.NVX

The dated datasheet for article `11702239` identifies a color Sony IMX250 global-shutter sensor, 2448x2048 resolution, 3.45 um pixels, NVIDIA Jetson Xavier NX, and GigE/USB 3.0/RS232. Do not infer exposure, pixel format, connector, power, environmental, or bandwidth limits from another VAX model. Enumerate identity/features read-only and preserve original configuration before changes.
