# Integration Playbook

## 1) Discovery first

Record required values in `project_context.md`:

- Environments:
  - `DEV`, `TEST`, `PROD` hostnames and network boundaries.
- OT sources:
  - Kepware tags, data types, quality flags, timestamp conventions.
- FIOT/ThingWorx:
  - base URL, auth mode (`appKey`), entities (`Thing`, `Property`, `Service`), TLS or mTLS.
- IMS:
  - IMS version, IMSplex, PSB/programview names, DBD names, transactions, catalog usage.
- Governance:
  - change approvals, CAB requirements, rollback owner, support escalation contacts.

## 2) Decide transport

Primary path:
- `ThingWorx/FIOT -> z/OS Connect REST -> IMS`.
- Choose when API governance, OpenAPI contracts, and auditability are priorities.

Alternative path:
- `ThingWorx/FIOT -> IMS Connect + ODBM -> Universal JDBC/DL/I`.
- Choose when direct IMS DB access is required and operations support this model.

Consumer path:
- `IMS -> z/OS Connect -> external REST`.
- Choose for IMS-originated callouts.

## 3) PSB baseline templates

### PSBGEN source template

```text
         PSBGEN  PSBNAME=MYPSB,LANG=COBOL
PCB1     PCB     TYPE=DB,DBDNAME=MYDBD,PROCOPT=G
SEG1     SENSEG  NAME=ROOTSEG,PARENT=0
FLD1     SENFLD  NAME=FIELD1
         END
```

### Minimal JCL pattern for PSBGEN + ACB build

```jcl
//PSBGEN   EXEC PGM=DFSRRC00,PARM='DLI,DFSPBGEN,,,,,,,,,,,N,N'
//STEPLIB  DD  DISP=SHR,DSN=IMS.SDFSRESL
//PSBLIB   DD  DISP=SHR,DSN=IMS.PSBLIB
//SYSIN    DD  *
  ... PSBGEN control statements ...
/*
//ACBGEN   EXEC PGM=DFSUACB0,PARM='AGNP'
//STEPLIB  DD  DISP=SHR,DSN=IMS.SDFSRESL
//DBDLIB   DD  DISP=SHR,DSN=IMS.DBDLIB
//PSBLIB   DD  DISP=SHR,DSN=IMS.PSBLIB
//ACBLIB   DD  DISP=SHR,DSN=IMS.ACBLIB
```

Adjust utility options, datasets, and PROC names per site standard.

## 4) Payload mapping guardrails

Always carry these OT fields through integration:
- `value`
- `quality`
- `timestamp`
- `correlation_id`

Reason: dropping quality or correlation information creates poor auditability and can hide data health issues.

## 5) Security defaults

- Never store app keys, credentials, or private certs in git.
- Keep TLS verification enabled.
- Use request timeouts and bounded retries for every external call.
- Add `x-thingworx-session: false` for ThingWorx application traffic.
- Do not execute production deployment steps without explicit approval.

## 6) PSB troubleshooting checklist

- Program name and PSB name match expected runtime binding.
- `PROCOPT` includes required read or update scope.
- Required `SENSEG` and `SENFLD` definitions exist.
- ACB regenerated after any DBD or PSB change.
- Catalog metadata and driver properties align for Universal JDBC usage.

## 7) Connector smoke test checklist

- Dry-run returns valid mapped IMS request with correlation id.
- Timeout and retry behavior is observable in logs.
- Non-2xx responses are logged with endpoint, status, and attempt count.
- Unit test for retry path passes.
