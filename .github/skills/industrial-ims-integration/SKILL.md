---
name: industrial-ims-integration
description: Design and implement secure integrations between Kepware, FIOT/ThingWorx, PEKAT Vision, and IBM IMS (DB/TM). Use for requests involving IMS PSB/PSBGEN/PCBs/SENSEG/SENFLD, PSBLIB to ACBLIB generation, DFS3UACB, CREATE PROGRAMVIEW, IMS Connect and ODBM, IMS Universal JDBC or DL/I access, z/OS Connect REST and OpenAPI contracts, OTMA or IMS TM Resource Adapter flows, and creation of connector scaffolds with docs, project_context, changelog, src, and tests.
---

# Industrial IMS Integration

## Goal

Build repeatable industrial-to-IMS integration outputs with safe defaults.
Produce architecture, connector skeletons, and operator-friendly documentation without production-side changes.

## Use Workflow

1. Run discovery first and store missing values in `project_context.md`.
2. Choose the primary transport and one fallback:
- Primary: `z/OS Connect` REST/JSON.
- Fallback: `IMS Connect + ODBM + Universal JDBC/DL/I`.
3. Define PSB scope and governance:
- Confirm PSB name to program mapping.
- Confirm PCB + PROCOPT + SENSEG + SENFLD coverage.
- Confirm ACB refresh flow after DBD/PSB updates.
4. Scaffold or update integration code with:
- explicit timeouts,
- bounded retries with backoff,
- correlation id propagation,
- dry-run mode.
5. Sync `docs/TECHNICAL.md`, `docs/USER_GUIDE.md`, `CHANGELOG.md`, and `project_context.md`.
6. Run smoke tests and report any unresolved environment gaps.

## Discovery Contract

Capture these fields before coding:
- OT source: Kepware server/channel/device/tag list, value types, quality model, timestamp format.
- FIOT/ThingWorx: base URL, appKey scope, target Thing/Property/Service, TLS or mTLS requirements.
- IMS runtime: IMS version, IMSplex details, PSB or PROGRAMVIEW names, DBD names, transaction codes.
- Path choice:
  - `A`: Kepware -> ThingWorx/FIOT -> z/OS Connect -> IMS
  - `B`: ThingWorx/FIOT -> IMS Connect/ODBM -> Universal JDBC/DL/I
  - `C`: IMS as consumer calling external REST via z/OS Connect
- Security: appKey/PassTicket/RACF/cert requirements, network constraints, proxy/firewall boundaries.

## Resource Loading

Load resources progressively:
1. Always read `references/primary_sources.md`.
2. Read `references/integration_playbook.md` when designing flow, PSB assets, or troubleshooting.
3. Use `scripts/scaffold_project.py` to generate a baseline implementation.

## Scaffold Command

Run:
`python .github/skills/industrial-ims-integration/scripts/scaffold_project.py --output <target-dir>`

Use `--force` to overwrite existing files.

## PSB and Programview Guidance

- Prefer PSBGEN when operating in classic control block workflows.
- Consider `CREATE PROGRAMVIEW` when IMS catalog SQL DDL governance is required by site standards.
- After PSB or DBD changes, require ACB regeneration/populate workflow before runtime verification.

## Safety Defaults

- Do not deploy to production without explicit approval.
- Do not change firewall rules, user roles, or key rotation without explicit approval.
- Never commit secrets; use `.env` or secret stores.
- Keep TLS verification on by default.
- Every outbound call must define timeout and retry limits.

## Deliverables to Produce

When requested, ensure these paths exist in the target repository:
- `.github/skills/industrial-ims-integration/SKILL.md`
- `docs/TECHNICAL.md`
- `docs/USER_GUIDE.md`
- `project_context.md`
- `CHANGELOG.md`
- `src/`
- `tests/`

## Output Quality Bar

- Keep mapping explicit from OT payload (`value`, `quality`, `timestamp`) to IMS request fields.
- Include a PSB troubleshooting checklist with ACB refresh steps.
- Include at least one runnable smoke test or dry-run test.
