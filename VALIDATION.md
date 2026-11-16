# Validation — 1.0.0-beta.5

Passed:
- All six loader/game JARs compile with their real loader APIs.
- Startup config hook, cancellable AuthHandler.auth(boolean), toast overload, and all other
  mixin/reflection targets verified in five real official Figura 0.1.6 JARs.
- Selection policy: no first choice until evidence or deadline; early READY/OFFLINE; UNKNOWN
  remains pending; exact 15s timeout to official; later recovery; conservative runtime fallback;
  old results cannot clobber a manual edit; official requests never receive private addon header.
- Directory transport fixtures: raw endpoint success, public API fallback, cooldown and cached
  discovered hostname, HTTP server time validation, offline versus network errors, rejection of
  invalid/expired documents, and a total 15s probe budget across raw/API/health requests.
- Mock Figura controller: startup auth gate, failed lookup does not immediately authenticate,
  timeout starts official auth, later result starts private auth, stale manual-edit result ignored.
- Six release JAR metadata and sorted ZIP payload hashes checked.

Not performed:
- Interactive Minecraft launch for six loader/game combinations.
- Actual toast display in Minecraft.
- An end-to-end test from the friend's computer or that computer's network.

The mock controller invokes startup/bootstrap directly; real Mixin target descriptors are
checked separately. Host/backend/publisher code is unchanged from the deployed host version.
