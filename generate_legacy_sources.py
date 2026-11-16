"""Generate the Java 8 HTTP adapter from the shared, tested controller/policy."""
from pathlib import Path


def generate(root, target):
    package=target/'dev/t0ch1na/autocloud';package.mkdir(parents=True,exist_ok=True)
    src=root/'src/main/java/dev/t0ch1na/autocloud'
    s=(src/'Directory.java').read_text()
    s=s.replace('import java.net.http.HttpClient;\n','').replace('import java.net.http.HttpRequest;\n','').replace('import java.net.http.HttpResponse;\n','')
    s=s.replace('    public record Result(String host, State state, String message) {}','''    public static final class Result {
        private final String host,message; private final State state;
        public Result(String host,State state,String message){this.host=host;this.state=state;this.message=message;}
        public String host(){return host;} public State state(){return state;} public String message(){return message;}
    }''')
    s=s.replace('    public record Response(int status, String body, String date) {}','''    public static final class Response {
        private final int status; private final String body,date;
        public Response(int status,String body,String date){this.status=status;this.body=body;this.date=date;}
        public int status(){return status;} public String body(){return body;} public String date(){return date;}
    }''')
    a=s.index('    public Directory() {');b=s.index('    public Directory(Transport transport',a)
    s=s[:a]+'''    public Directory() {
        transport = (uri,timeout,headers) -> {
            java.net.HttpURLConnection connection=(java.net.HttpURLConnection)uri.toURL().openConnection();
            long deadline=System.nanoTime()+timeout.toNanos();
            int ms=(int)Math.max(1,timeout.toMillis());
            connection.setConnectTimeout(Math.min(5000,ms));connection.setReadTimeout(ms);
            connection.setInstanceFollowRedirects(false);
            headers.forEach(connection::setRequestProperty);
            try {
                int status=connection.getResponseCode();
                java.io.InputStream input=status>=400?connection.getErrorStream():connection.getInputStream();
                java.io.ByteArrayOutputStream output=new java.io.ByteArrayOutputStream();
                if(input!=null)try(java.io.InputStream stream=input){
                    byte[] buffer=new byte[4096];int size;
                    while(true){
                        long left=deadline-System.nanoTime();
                        if(left<=0)throw new java.net.SocketTimeoutException("Request time budget exhausted");
                        connection.setReadTimeout((int)Math.max(1,java.util.concurrent.TimeUnit.NANOSECONDS.toMillis(left)));
                        size=stream.read(buffer);if(size<0)break;
                        output.write(buffer,0,size);if(output.size()>65536)throw new IllegalArgumentException("Response too large");
                    }
                }
                return new Response(status,new String(output.toByteArray(),java.nio.charset.StandardCharsets.UTF_8),connection.getHeaderField("Date"));
            } finally {connection.disconnect();}
        };
        clock=System::nanoTime;
    }
    private static Map<String,String> headers(String... values){
        Map<String,String> result=new java.util.LinkedHashMap<String,String>();
        for(int i=0;i<values.length;i+=2)result.put(values[i],values[i+1]);return result;
    }
'''+s[b:]
    s=s.replace('Map.of(', 'headers(').replace('JsonParser.parseString(', 'new JsonParser().parse(')
    (package/'Directory.java').write_text(s)
    s=(src/'Bridge.java').read_text().replace('import java.net.http.HttpRequest;\n','')
    s=s.replace('System.Logger','CompatLog').replace('System.getLogger','CompatLog.getLogger')
    s=s.replace('    private record ProbeResult(long revision, Directory.Result result) {}','''    private static final class ProbeResult {
        private final long revision; private final Directory.Result result;
        ProbeResult(long revision,Directory.Result result){this.revision=revision;this.result=result;}
        long revision(){return revision;} Directory.Result result(){return result;}
    }''')
    a=s.index('    public static HttpRequest tag(');b=s.index('    public static void tagSocket',a)
    s=s[:a]+'''    public static void tagLegacy(Object request) {
        try {
            java.net.URI uri=(java.net.URI)request.getClass().getMethod("getURI").invoke(request);
            if(privateHost(uri.getHost()))request.getClass().getMethod("setHeader",String.class,String.class)
                    .invoke(request,Directory.HEADER,Directory.VERSION);
        } catch(Exception e){LOG.log(CompatLog.Level.ERROR,"Unable to tag legacy Figura HTTP request",e);}
    }

'''+s[b:]
    (package/'Bridge.java').write_text(s)
    (package/'Selection.java').write_bytes((src/'Selection.java').read_bytes())
    (package/'CompatLog.java').write_text('''package dev.t0ch1na.autocloud;
public final class CompatLog {
 public enum Level {DEBUG,INFO,WARNING,ERROR}
 private final java.util.logging.Logger logger;
 private CompatLog(String name){logger=java.util.logging.Logger.getLogger(name);}
 public static CompatLog getLogger(String name){return new CompatLog(name);}
 private java.util.logging.Level level(Level value){return value==Level.ERROR?java.util.logging.Level.SEVERE:value==Level.WARNING?java.util.logging.Level.WARNING:value==Level.DEBUG?java.util.logging.Level.FINE:java.util.logging.Level.INFO;}
 public void log(Level value,String text){logger.log(level(value),text);}
 public void log(Level value,String text,Throwable error){logger.log(level(value),text,error);}
}
''')
    mixins=package/'mixin';mixins.mkdir(exist_ok=True)
    for name in ['BootstrapMixin','NetworkMixin','SocketMixin']:
        (mixins/(name+'.java')).write_bytes((src/'mixin'/(name+'.java')).read_bytes())
    (mixins/'AuthMixin.java').write_text('''package dev.t0ch1na.autocloud.mixin;
import dev.t0ch1na.autocloud.Bridge;
import org.apache.http.client.methods.HttpUriRequest;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.*;
@Mixin(targets="org.figuramc.figura.backend2.AuthHandler",remap=false)
public abstract class AuthMixin {
 @Inject(method="auth",at=@At("HEAD"),cancellable=true,remap=false)
 private static void waitForSelection(boolean reAuth,CallbackInfo ci){if(Bridge.deferAuthentication())ci.cancel();}
 @Inject(method="request",at=@At("HEAD"),remap=false)
 private static void tag(HttpUriRequest request,CallbackInfoReturnable<String> ci){Bridge.tagLegacy(request);}
}
''')
    (mixins/'HttpMixin.java').write_text('''package dev.t0ch1na.autocloud.mixin;
import dev.t0ch1na.autocloud.Bridge;
import org.apache.http.client.methods.HttpRequestBase;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.*;
@Mixin(targets="org.figuramc.figura.backend2.HttpAPI",remap=false)
public abstract class HttpMixin {
 @Inject(method="header(Ljava/lang/String;Ljava/lang/String;)Lorg/apache/http/client/methods/HttpRequestBase;",at=@At("RETURN"),remap=false)
 private void tag(String path,String type,CallbackInfoReturnable<HttpRequestBase> ci){Bridge.tagLegacy(ci.getReturnValue());}
}
''')
    for loader in ['fabric','forge']:
        p=target/loader/'dev/t0ch1na/autocloud';p.mkdir(parents=True,exist_ok=True)
        name='FabricEntrypoint' if loader=='fabric' else 'ForgeEntrypoint'
        text=(root/f'src/{loader}/java/dev/t0ch1na/autocloud/{name}.java').read_text()
        text=text.replace('System.getLogger','CompatLog.getLogger').replace('System.Logger.Level','CompatLog.Level')
        (p/(name+'.java')).write_text(text)
    return package
