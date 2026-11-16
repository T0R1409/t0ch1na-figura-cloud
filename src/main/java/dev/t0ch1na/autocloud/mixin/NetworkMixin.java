package dev.t0ch1na.autocloud.mixin;
import dev.t0ch1na.autocloud.Bridge;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
@Mixin(targets="org.figuramc.figura.backend2.NetworkStuff", remap=false)
public abstract class NetworkMixin {
    @Inject(method="tick", at=@At("HEAD"), remap=false)
    private static void t0ch1na$tick(CallbackInfo ci) { Bridge.tick(); }
}
