# Validation — 1.0.0-beta.7 full published matrix

Scope:
- 40 game/loader addon artifacts across 15 Minecraft versions, from 1.16.5 to 1.21.4.
- Figura release inventory read from Modrinth and official GitHub release 0.1.6.
- Three misleading Modrinth game/loader tags excluded because actual Figura metadata requires a newer Minecraft version.
- Five native Quilt 0.1.2 variants; Java 8 adapters for both 1.16.5 loaders.
- Previously distributed NeoForge 1.20.1 preserved as an explicitly experimental Forge-compatible legacy build.

Passed:
- Every selected Figura binary's required method/field names and descriptors checked, adapting
  Apache HTTP descriptors for 1.16.5 and prefixed namespace/WebsocketThingy hook for Quilt.
- Official Figura downloads checked against Modrinth SHA-512 or GitHub SHA-256 digest.
- All 40 JARs compile with eight distinct source/loader/bytecode profiles.
- Metadata parse, exact name/credit, original logo, platform/game/Figura dependency ranges,
  Java class versions, and absence of modern java.net.http/System.Logger references in Java 8 builds.
- Java 8 transport-policy tests executed on actual Temurin 8u512 with Gson 2.8.0.
- Java 8 mock Figura controller tests executed: startup gate, 15s timeout, late private recovery, stale-result rejection.
- Real Apache HttpGet objects tagged and official requests isolated; socket-header reflection fixture passed on Java 8.
- Quilt controller tests executed with prefixed mock Figura classes, including startup gate and failover/recovery.
- Per-version ZIP entries checked against source artifact hashes.

Not performed:
- Interactive Minecraft startup across all 40 game/loader combinations.
- Real Minecraft account login/avatar round trip on every loader/version.
- Actual in-game rendering of every logo/Unicode credit.

These are beta builds with verified binary API contracts and controller/transport tests,
not a claim of complete in-game certification. Source-only branches or unpublished nightlies
are outside the release inventory. Download instructions identify each required Figura build.
