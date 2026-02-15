# Primary Sources

Use these as the default references before adding secondary material.

## Foxon / FIOT context

- Foxon ThingWorx platform page:
  - https://www.foxon.cz/reseni/procesni-rizeni/iiot-platforma-thingworx
  - Confirms Foxon delivers FIOT capabilities on PTC ThingWorx.
  - Mentions real extensions used in customer projects:
    - PROFINET topology rendering in a ThingWorx mashup.
    - SSO extension integration with IBM WebSeal.
    - LDAPWS extension for AD synchronization.
    - Universal HTTP plugin with client certificate support.
  - Mentions alarming and links from visualization to documentation.

- Foxon FIOT page:
  - https://www.foxon.cz/sluzby/software/fiot
  - States FIOT is built on the ThingWorx low-code platform.
  - Describes common outcomes: data integration, digital twins, predictive maintenance, and alarms.

## PTC / ThingWorx auth and session policy

- Application Keys (ThingWorx):
  - https://support.ptc.com/help/thingworx/platform/r9.5/en/ThingWorx/Help/Composer/Security/ApplicationKeys/ApplicationKeys.html
  - Application keys are intended for applications/systems (instead of user session auth).

- EMS and REST session guidance:
  - https://support.ptc.com/help/thingworx/edge_microserver/en/c_sdk/c_ems_wsems_authentication_rest_api.html
  - Recommends not creating sessions for application integrations.
  - Requires `x-thingworx-session: false` in REST calls when avoiding sessions.
  - Shows using `appKey` in headers for requests.

- EMS app key setup:
  - https://support.ptc.com/help/thingworx/edge_microserver/en/c_sdk/c_ems_wsems_authentication_app_keys.html
  - Shows App Key usage for EMS/AlwaysOn authentication.

## Thing model and extension operations

- ThingTemplates:
  - https://support.ptc.com/help/thingworx/platform/r9/en/ThingWorx/Help/Composer/ThingTemplates/ThingTemplates.html
  - Defines shared behavior/structure for Things.

- Things:
  - https://support.ptc.com/help/thingworx/platform/r9/en/ThingWorx/Help/Composer/Things/Things.html
  - Defines concrete modeled entities with properties/services/events.

- Importing extensions:
  - https://support.ptc.com/help/thingworx/platform/r9.6/en/ThingWorx/Help/Composer/Extensions/ImportingExtensions.html
  - Importing extensions is an admin operation and may require restart.

- Disable/enable extension import:
  - https://support.ptc.com/help/thingworx/platform/r9.6/en/ThingWorx/Help/Installation/ConfiguringMongoDBThingWorxConfigurePlatformSettings.html
  - `PlatformSubsystem.importEnabled` controls whether imports are allowed.

## Kepware references

- ThingWorx Native Connectivity from KEPServerEX:
  - https://support.ptc.com/help/kepware/features/en/kepware/features/THINGWORX_NATIVE_CONNECTIVITY/thingworx_native_connectivity.html
  - Covers direct ThingWorx-oriented connectivity options in Kepware.

- KEPServerEX ThingWorx Agent setup:
  - https://support.ptc.com/help/kepware/drivers/en/kepware/drivers/THINGWORX/thingworx_agent_setup.html
  - Documents app key configuration and SSL options in agent settings.

## Note on ExtensionPackageUploader

`ExtensionPackageUploader` is commonly used as the ThingWorx upload mechanism name in API calls and tooling.
Treat endpoint shape/version details as environment-specific and verify in target platform docs/version before deployment.
