# Validation — 1.0.0-beta.2

Passed:
- All six addon JARs compile against real Fabric/Forge/NeoForge loader APIs (Java 17; modern NeoForge Java 21).
- Method/field descriptors used by mixins and reflection verified in all five official Figura 0.1.6 JARs; legacy NeoForge 1.20.1 uses the Forge Figura build.
- Java policy tests: initial official fallback, transient failure tolerance, offline fallback,
  recovery to private cloud, changed URL, directory expiry, host restrictions,
  private header attachment and header isolation from official/stale hosts.
- Nine Python integration/unit tests: addon gate for API and WebSocket, authenticated upload/download,
  avatar persistence after restart, limits/boundary, ownership, allowlist, delete/equip,
  WebSocket auth/event/ping, GitHub publisher document and secret isolation.
- Python host scripts parse successfully.
- Combined Docker Compose configuration validates.

Not performed:
- Interactive Minecraft client launch for the six loader/game combinations.
- Real Minecraft account/Mojang session verification.
- End-to-end publication from the user's Windows machine with their fine-grained GitHub token.

The GitHub directory starts offline. Automatic private selection starts only after the host
upgrade is installed and its publisher can update cloud.json.

NeoForge metadata, loader entrypoints, Java class versions and mixin compatibility levels verified for both versions.
NeoForge 1.20.1 legacy relies on Forge compatibility; no dedicated official Figura NeoForge 1.20.1 artifact exists.
