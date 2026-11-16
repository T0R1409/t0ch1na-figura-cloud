package dev.t0ch1na.autocloud;
import net.fabricmc.api.ClientModInitializer;
public final class FabricEntrypoint implements ClientModInitializer {
    @Override public void onInitializeClient() {
        System.getLogger("T0CH1NA AutoCloud").log(System.Logger.Level.INFO, "AutoCloud loaded (Fabric)");
    }
}
