# Primary Sources

Use these public sources as first-choice references.

## IBM IMS PSB and control blocks

- PSB generation utility:
  - https://www.ibm.com/docs/en/ims/15.4.0?topic=utilities-program-specification-block-psb-generation-utility
  - Confirms PSBGEN input statements (`PSBGEN`, `PCB`, `SENSEG`, `SENFLD`, `END`) and that generated PSBs are placed in `IMS.PSBLIB`.
- PSBGEN examples:
  - https://www.ibm.com/docs/en/ims/15.4.0?topic=utility-examples-psbgen
- Coding PSB source for PSBGEN:
  - https://www.ibm.com/docs/en/ims/15.4.0?topic=uigudid-coding-program-specification-blocks-as-input-psbgen-utility
- ACB Generation and Catalog Populate utility (`DFS3UACB`):
  - https://www.ibm.com/docs/en/ims/15.6.0?topic=utilities-acb-generation-catalog-populate-utility-dfs3uacb
  - Utility action values include `BUILD`, `BUILD_DBD`, `BUILD_PSB`, `DELETE`, and `UPDATE`.

## IBM IMS catalog SQL DDL alternative

- `CREATE PROGRAMVIEW` statement:
  - https://www.ibm.com/docs/ja/ims/15.3.0?topic=statements-create-programview-statement
- `CREATE SENSEGVIEW` statement:
  - https://www.ibm.com/docs/ja/ims/15.3.0?topic=statements-create-sensegview-statement

## IBM IMS connectivity options

- IMS Connect and ODBM:
  - https://www.ibm.com/docs/en/ims/15.6.0?topic=ims-connect
  - https://www.ibm.com/docs/en/ims/15.4.0?topic=support-ims-connect-access-ims-db
- IMS Universal JDBC driver:
  - https://www.ibm.com/docs/en/ims/15.6.0?topic=interfaces-ims-universal-jdbc-drivers
  - DriverManager URL format includes:
    - `jdbc:ims://<hostname>:<port>/<datastoreName>?...`
    - `jdbc:ims://<hostname>:<port>/<dbName>?...`
  - DataSource pattern includes:
    - `jdbc:ims:datastoreName=<IMS_datastore_name>;databaseName=<PSB_name>`
    - `databaseName` is used for PSB name in this mode.
- IMS TM Resource Adapter:
  - https://www.ibm.com/docs/en/ims/15.6.0?topic=adapters-ims-tm-resource-adapter

## z/OS Connect for REST and OpenAPI

- IMS and z/OS Connect REST API solution:
  - https://www.ibm.com/docs/en/ims/15.4.0?topic=fisi1-mobile-rest-api-solution-zos-connect-enterprise-edition
- Call API from IMS z/OS application (consumer pattern):
  - https://www.ibm.com/docs/en/zos-connect/3.0?topic=sor-call-api-from-ims-zos-application

## Automation references

- IBM z/OS IMS Ansible collection `ims_psb_gen`:
  - https://ibm.github.io/z_ansible_collections_doc/ibm_zos_ims/docs/source/modules/ims_psb_gen.html
  - Useful for declarative PSBGEN automation and repeatable CI flows.

## Industrial integration context references

- FIOT and ThingWorx context:
  - https://www.foxon.cz/sluzby/software/fiot
  - https://www.foxon.cz/reseni/procesni-rizeni/iiot-platforma-thingworx
- ThingWorx appKey and session guidance:
  - https://support.ptc.com/help/thingworx/platform/r9.5/en/ThingWorx/Help/Composer/Security/ApplicationKeys/ApplicationKeys.html
  - https://support.ptc.com/help/thingworx/edge_microserver/en/c_sdk/c_ems_wsems_authentication_rest_api.html
- Kepware ThingWorx connectivity:
  - https://support.ptc.com/help/kepware/features/en/kepware/features/THINGWORX_NATIVE_CONNECTIVITY/thingworx_native_connectivity.html

## PEKAT Vision references

- SDK docs:
  - https://pekat-vision.github.io/pekat-vision-sdk-python/
- SDK repo:
  - https://github.com/pekat-vision/pekat-vision-sdk-python
- SDK package:
  - https://pypi.org/project/pekat-vision-sdk/
- Public examples:
  - https://github.com/pekat-vision/pekat-vision-examples
