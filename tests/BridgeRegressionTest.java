import dev.t0ch1na.autocloud.Bridge;
import dev.t0ch1na.autocloud.Selection;
import dev.t0ch1na.autocloud.Directory;
import org.figuramc.figura.config.Configs;
import org.figuramc.figura.config.ConfigManager;
import org.figuramc.figura.backend2.NetworkStuff;
import java.lang.reflect.Field;
import java.net.URI;
import java.net.http.HttpRequest;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicReference;

public class BridgeRegressionTest {
 private static void eq(Object expected,Object actual){if(!java.util.Objects.equals(expected,actual))throw new AssertionError(expected+" != "+actual);}
 private static Object field(String name)throws Exception{Field f=Bridge.class.getDeclaredField(name);f.setAccessible(true);return f.get(null);}
 @SuppressWarnings("unchecked")
 private static void result(long revision,String host)throws Exception{
  Class<?> c=Class.forName("dev.t0ch1na.autocloud.Bridge$ProbeResult");
  var constructor=c.getDeclaredConstructor(long.class,String.class);constructor.setAccessible(true);
  ((AtomicReference<Object>)field("PENDING")).set(constructor.newInstance(revision,host));
 }
 public static void main(String[] args)throws Exception{
  // Keep actual HTTP out of this deterministic controller test.
  ((AtomicBoolean)field("BUSY")).set(true);
  Configs.SERVER_IP.value="figura.moonlight-devs.org";
  Configs.SERVER_IP.tempValue=Configs.SERVER_IP.value;
  Bridge.bootstrap();
  eq(Directory.INITIAL_HOST,Configs.SERVER_IP.value);
  eq(0,NetworkStuff.authentications);
  Bridge.tick();
  eq(Directory.INITIAL_HOST,Configs.SERVER_IP.value);
  eq(0,NetworkStuff.disconnects);eq(0,ConfigManager.saves);eq(0,NetworkStuff.authentications);
  Selection selection=(Selection)field("selector");
  long old=selection.revision();
  Configs.SERVER_IP.value="manual.trycloudflare.com";
  Configs.SERVER_IP.tempValue=Configs.SERVER_IP.value;
  // Header tagging works even BEFORE the next tick adopts the Settings edit.
  HttpRequest auth=HttpRequest.newBuilder(URI.create("https://manual.trycloudflare.com/api/auth/id")).build();
  eq("1",Bridge.tag(auth).headers().firstValue(Directory.HEADER).orElse(null));
  result(old,null);Bridge.tick();
  eq("manual.trycloudflare.com",Configs.SERVER_IP.value);
  eq(0,NetworkStuff.disconnects);eq(0,NetworkStuff.authentications);
  // A new failed probe does not interrupt an in-flight Figura login.
  result(selection.revision(),null);Bridge.tick();
  eq("manual.trycloudflare.com",Configs.SERVER_IP.value);eq(2,NetworkStuff.backendStatus);
  eq(0,NetworkStuff.authentications);
  // A valid result recovers to the newest hostname and clears pending requests.
  NetworkStuff.API_REQUESTS.add("pending-upload");
  NetworkStuff.WS_REQUESTS.add("pending-ping");
  UUID local=new UUID(0,1),remote=new UUID(0,2);
  org.figuramc.figura.avatar.AvatarManager.LOADED_USERS.put(local,new Object());
  org.figuramc.figura.avatar.AvatarManager.LOADED_USERS.put(remote,new Object());
  result(selection.revision(),"latest.trycloudflare.com");Bridge.tick();
  eq("latest.trycloudflare.com",Configs.SERVER_IP.value);
  eq(1,NetworkStuff.disconnects);eq(1,NetworkStuff.authentications);eq(1,ConfigManager.saves);
  eq(0,NetworkStuff.API_REQUESTS.size());eq(0,NetworkStuff.WS_REQUESTS.size());
  eq(true,org.figuramc.figura.avatar.AvatarManager.LOADED_USERS.containsKey(local));
  eq(false,org.figuramc.figura.avatar.AvatarManager.LOADED_USERS.containsKey(remote));
  // An arbitrarily long outage never switches to the official cloud.
  for(int i=0;i<100;i++) { result(selection.revision(),null);Bridge.tick(); }
  eq("latest.trycloudflare.com",Configs.SERVER_IP.value);
  eq(1,NetworkStuff.disconnects);eq(1,NetworkStuff.authentications);
  // Even a Settings reset is restored to our private cloud on the next tick.
  Configs.SERVER_IP.value="figura.moonlight-devs.org";
  Configs.SERVER_IP.tempValue=Configs.SERVER_IP.value;
  Bridge.tick();
  eq("latest.trycloudflare.com",Configs.SERVER_IP.value);
  eq(2,NetworkStuff.disconnects);eq(2,NetworkStuff.authentications);
  System.out.println("Bridge private-only regressions passed: forced IP before first tick, private auth header, manual edit, stale results, loading preservation, recovery, queue isolation, local preview, outages and Settings reset");
 }
}
