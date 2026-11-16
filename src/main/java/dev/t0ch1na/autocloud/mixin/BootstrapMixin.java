package dev.t0ch1na.autocloud.mixin;
import dev.t0ch1na.autocloud.Bridge;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
@Mixin(targets="org.figuramc.figura.config.ConfigManager", remap=false)
public abstract class BootstrapMixin {
    @Inject(method="loadConfig", at=@At("RETURN"), remap=false)
    private static void t0ch1na$startup(CallbackInfo ci) { Bridge.bootstrap(); }
}
