package dev.t0ch1na.autocloud.mixin;
import dev.t0ch1na.autocloud.Bridge;
import java.net.http.HttpRequest;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyVariable;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
@Mixin(targets="org.figuramc.figura.backend2.AuthHandler", remap=false)
public abstract class AuthMixin {
    @Inject(method="auth", at=@At("HEAD"), cancellable=true, remap=false)
    private static void t0ch1na$waitForSelection(boolean reAuth, CallbackInfo ci) {
        if (Bridge.deferAuthentication()) ci.cancel();
    }
    @ModifyVariable(method="request", at=@At("HEAD"), argsOnly=true, ordinal=0, remap=false)
    private static HttpRequest t0ch1na$auth(HttpRequest request) { return Bridge.tag(request); }
}
