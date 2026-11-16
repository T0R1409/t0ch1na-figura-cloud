package dev.t0ch1na.autocloud.mixin;
import dev.t0ch1na.autocloud.Bridge;
import java.net.http.HttpRequest;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyVariable;
@Mixin(targets="org.figuramc.figura.backend2.AuthHandler", remap=false)
public abstract class AuthMixin {
    @ModifyVariable(method="request", at=@At("HEAD"), argsOnly=true, ordinal=0, remap=false)
    private static HttpRequest t0ch1na$auth(HttpRequest request) { return Bridge.tag(request); }
}
