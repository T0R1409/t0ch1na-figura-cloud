# Validation — 1.0.0-beta.1

Passed:
- All four Java 17-bytecode addon JARs compile against their real Fabric/Forge loader APIs.
- Method/field descriptors used by mixins and reflection verified in all four official Figura 0.1.6 JARs.
- Java policy tests: initial official fallback, transient failure tolerance, offline fallback,
  recovery to private cloud, changed URL, directory expiry, host restrictions,
  private header attachment and header isolation from official/stale hosts.
- Nine Python integration/unit tests: addon gate for API and WebSocket, authenticated upload/download,
  avatar persistence after restart, limits/boundary, ownership, allowlist, delete/equip,
  WebSocket auth/event/ping, GitHub publisher document and secret isolation.
- Python host scripts parse successfully.
- Combined Docker Compose configuration validates.

Not performed:
- Interactive Minecraft client launch for the four loader/game combinations.
- Real Minecraft account/Mojang session verification.
- End-to-end publication from the user's Windows machine with their fine-grained GitHub token.

The GitHub directory starts offline. Automatic private selection starts only after the host
upgrade is installed and its publisher can update cloud.json.
