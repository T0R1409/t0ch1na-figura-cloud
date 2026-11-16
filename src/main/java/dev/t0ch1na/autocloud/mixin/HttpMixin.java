package dev.t0ch1na.autocloud.mixin;
import dev.t0ch1na.autocloud.Bridge;
import java.net.http.HttpRequest;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
@Mixin(targets="org.figuramc.figura.backend2.HttpAPI", remap=false)
public abstract class HttpMixin {
    @Inject(method="header", at=@At("RETURN"), remap=false)
    private void t0ch1na$header(String path, CallbackInfoReturnable<HttpRequest.Builder> ci) {
        Bridge.tag(ci.getReturnValue());
    }
}
