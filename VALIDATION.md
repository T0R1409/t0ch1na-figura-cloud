# Validation — 1.0.0-beta.6 branding

- Six JARs compile successfully for the existing loader/game matrix.
- Fabric JSON and Forge/NeoForge TOML parse successfully.
- Display name, author and description match the user-requested Unicode strings exactly.
- Every JAR contains icon.png identical byte-for-byte to the PNG in the user-uploaded ZIP.
- Cloud MOTD contains exactly the requested credit and no extra explanation.
- Host-only credit updater matches both old and current server.py MOTD shapes; Python syntax remains valid.
- Sorted archive entries and hashes verified.

The startup, discovery, timeout, fallback and authentication behavior is the same as beta 5.
The visual appearance in each Minecraft mod list has not been tested interactively.
