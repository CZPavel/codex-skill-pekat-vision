# Technical Architecture: Industrial IMS Integration

Last updated: 2026-02-15

## 1) Scope

This project bridges industrial OT data into IBM IMS with two integration paths:

1. Primary: REST/JSON via z/OS Connect.
2. Alternative: IMS Connect + ODBM + Universal JDBC or DL/I.

It also supports the reverse path where IMS acts as a consumer and calls external APIs via z/OS Connect.

## 2) Data flow model

- OT acquisition: PLC or machine telemetry enters Kepware.
- IIoT layer: Kepware forwards into ThingWorx/FIOT.
- Enterprise bridge: integration service maps JSON payloads into IMS requests.
- Mainframe boundary:
  - Option A: z/OS Connect API invokes IMS transaction or service provider.
  - Option B: IMS Connect and ODBM path accesses IMS DB through Universal drivers.

## 3) Role of PSB and ACB

- PSB defines program access to IMS resources through PCBs, PROCOPT, and sensitive segment or field definitions.
- PSBGEN writes generated PSBs into `IMS.PSBLIB`.
- Runtime control blocks must be refreshed into `ACBLIB` after PSB or DBD changes.
- SQL DDL `CREATE PROGRAMVIEW` can be used in catalog-driven governance instead of classic PSBGEN flows when site policy allows.

## 4) Connector behavior requirements

- Every outgoing request includes a timeout.
- Retries are bounded and use exponential backoff.
- Correlation id is always propagated.
- Dry-run mode is default for safe first execution.
- Secrets are read from environment variables and never committed.

## 5) OT payload contract

Minimum fields to keep end-to-end:

- `value`
- `quality`
- `timestamp`
- `correlation_id`

Dropping `quality` or `correlation_id` causes poor auditability and can hide upstream data quality defects.

## 6) Security defaults

- Keep TLS verification enabled.
- Keep ThingWorx calls stateless (`x-thingworx-session: false`) when applicable.
- Do not run production deployment steps without explicit approval.
- Do not rotate keys, change firewall policy, or modify IAM/RACF roles without explicit approval.

## 7) Troubleshooting checklist

- Program to PSB binding is correct.
- PCB PROCOPT matches requested read or update action.
- SENSEG and SENFLD definitions cover required data.
- ACB has been regenerated after DBD or PSB changes.
- JDBC metadata uses expected `datastoreName` and PSB `databaseName` values.
- Integration service logs endpoint, status code, latency, and attempts.

## 8) Reference links

- PSBGEN utility:
  - https://www.ibm.com/docs/en/ims/15.4.0?topic=utilities-program-specification-block-psb-generation-utility
- PSBGEN examples:
  - https://www.ibm.com/docs/en/ims/15.4.0?topic=utility-examples-psbgen
- ACB generation utility (`DFS3UACB`):
  - https://www.ibm.com/docs/en/ims/15.6.0?topic=utilities-acb-generation-catalog-populate-utility-dfs3uacb
- IMS Connect:
  - https://www.ibm.com/docs/en/ims/15.6.0?topic=ims-connect
- IMS Connect access to IMS DB:
  - https://www.ibm.com/docs/en/ims/15.4.0?topic=support-ims-connect-access-ims-db
- IMS Universal JDBC drivers:
  - https://www.ibm.com/docs/en/ims/15.6.0?topic=interfaces-ims-universal-jdbc-drivers
- z/OS Connect and IMS:
  - https://www.ibm.com/docs/en/ims/15.4.0?topic=fisi1-mobile-rest-api-solution-zos-connect-enterprise-edition
  - https://www.ibm.com/docs/en/zos-connect/3.0?topic=sor-call-api-from-ims-zos-application
- Ansible `ims_psb_gen`:
  - https://ibm.github.io/z_ansible_collections_doc/ibm_zos_ims/docs/source/modules/ims_psb_gen.html
- ThingWorx/FIOT and Kepware context:
  - https://www.foxon.cz/sluzby/software/fiot
  - https://support.ptc.com/help/kepware/features/en/kepware/features/THINGWORX_NATIVE_CONNECTIVITY/thingworx_native_connectivity.html
  - https://pekat-vision.github.io/pekat-vision-sdk-python/
