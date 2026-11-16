# Validation — 1.0.0-beta.4

Passed:
- Six JARs compile against Fabric, Forge, modern NeoForge and legacy NeoForge APIs.
- Startup hook ConfigManager.loadConfig()V and every other mixin/reflection target verified in five official Figura JARs.
- Private-only policy: fresh official default selects bundled private host, saved host retained,
  1000 failed probes never select official, newer hostname adopted, stale probe rejected, official hostname rejected.
- Mock Figura controller regression: bootstrap forces IP before first client tick/authentication;
  headers apply before Settings tick; manual edits, stale results, loading-state preservation,
  latest-host recovery, queue clearing, local preview retention and Settings reset restoration.
- Outage controller test retains private hostname through repeated failed probes.
- Earlier host/backend/publisher protocol tests remain applicable; host code is unchanged.

Not performed:
- Interactive Minecraft startup across the six loader/game combinations.
- Real end-to-end test from the friend's computer.

The startup Mixin attaches after Figura finishes loading its configuration, before Figura
starts its normal cloud connection. The mock regression exercises bootstrap directly;
the separate contract check verifies the real released injection method exists.

Bundled bootstrap hostname: departments-whole-scripts-aid.trycloudflare.com
It is a fallback private address, not a stable domain. GitHub access is still required to
learn future hostname changes. No official-cloud fallback exists in this version.
