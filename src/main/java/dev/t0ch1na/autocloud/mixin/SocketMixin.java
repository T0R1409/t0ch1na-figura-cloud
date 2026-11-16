package dev.t0ch1na.autocloud.mixin;
import dev.t0ch1na.autocloud.Bridge;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
@Mixin(targets="org.figuramc.figura.backend2.trust.KeyStoreHelper", remap=false)
public abstract class SocketMixin {
    @Inject(method="websocketWithBackendCertificates", at=@At("RETURN"), remap=false)
    private static void t0ch1na$socket(String token, CallbackInfoReturnable<Object> ci) {
        Bridge.tagSocket(ci.getReturnValue());
    }
}
