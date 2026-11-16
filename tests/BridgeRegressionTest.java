import dev.t0ch1na.autocloud.*;
import org.figuramc.figura.config.Configs;
import org.figuramc.figura.backend2.NetworkStuff;
import java.lang.reflect.*;
import java.util.concurrent.atomic.*;
public class BridgeRegressionTest {
 static void eq(Object e,Object a){if(!java.util.Objects.equals(e,a))throw new AssertionError(e+" != "+a);}
 static Object field(String name)throws Exception{Field f=Bridge.class.getDeclaredField(name);f.setAccessible(true);return f.get(null);}
 @SuppressWarnings("unchecked") static void result(long revision,Directory.Result value)throws Exception{
  Class<?> c=Class.forName("dev.t0ch1na.autocloud.Bridge$ProbeResult");
  var ctor=c.getDeclaredConstructor(long.class,Directory.Result.class);ctor.setAccessible(true);
  ((AtomicReference<Object>)field("PENDING")).set(ctor.newInstance(revision,value));
 }
 public static void main(String[] args)throws Exception{
  ((AtomicBoolean)field("BUSY")).set(true);
  Configs.SERVER_IP.value=Selection.OFFICIAL;Configs.SERVER_IP.tempValue=Selection.OFFICIAL;
  Bridge.bootstrap();Bridge.tick();
  eq(true,Bridge.deferAuthentication());eq(0,NetworkStuff.authentications);eq(0,NetworkStuff.disconnects);
  Selection selection=(Selection)field("selector");
  result(selection.revision(),new Directory.Result(null,Directory.State.UNKNOWN,"GitHub timeout"));Bridge.tick();
  eq(true,Bridge.deferAuthentication());eq(0,NetworkStuff.authentications);
  // Advance policy to its deadline without sleeping or blocking the client.
  Field started=Selection.class.getDeclaredField("started");started.setAccessible(true);
  started.setLong(selection,java.util.concurrent.TimeUnit.NANOSECONDS.toMillis(System.nanoTime())-15001);
  Bridge.tick();eq(false,Bridge.deferAuthentication());eq(Selection.OFFICIAL,Configs.SERVER_IP.value);eq(1,NetworkStuff.authentications);
  result(selection.revision(),new Directory.Result("latest.trycloudflare.com",Directory.State.READY,"ready"));Bridge.tick();
  eq("latest.trycloudflare.com",Configs.SERVER_IP.value);eq(2,NetworkStuff.authentications);
  Configs.SERVER_IP.value="manual.trycloudflare.com";Configs.SERVER_IP.tempValue=Configs.SERVER_IP.value;
  long old=selection.revision();result(old,new Directory.Result("stale.trycloudflare.com",Directory.State.READY,"stale"));Bridge.tick();
  eq("manual.trycloudflare.com",Configs.SERVER_IP.value);eq(2,NetworkStuff.authentications);
  System.out.println("Bridge passed: startup auth gate, unknown check retention, deadline fallback authentication, late recovery and stale manual-edit result rejection");
 }
}
