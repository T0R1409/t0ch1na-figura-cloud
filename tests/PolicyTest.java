import dev.t0ch1na.autocloud.*;
import java.net.URI;
import java.net.http.HttpRequest;
public final class PolicyTest {
 static void eq(Object e,Object a){if(!java.util.Objects.equals(e,a))throw new AssertionError(e+" != "+a);}
 static Directory.Result ready(String host){return new Directory.Result(host,Directory.State.READY,"ready");}
 static Directory.Result unknown(){return new Directory.Result(null,Directory.State.UNKNOWN,"network");}
 public static void main(String[] args)throws Exception{
  Selection startup=new Selection(Selection.OFFICIAL,0);
  eq(true,startup.waiting());eq(Selection.OFFICIAL,startup.tick(14999));eq(true,startup.waiting());
  startup.update(unknown(),1000,0);eq(true,startup.waiting());
  eq(Selection.OFFICIAL,startup.tick(15000));eq(false,startup.waiting());
  eq("late.trycloudflare.com",startup.update(ready("late.trycloudflare.com"),20000,0));
  Selection fast=new Selection(Selection.OFFICIAL,0);
  eq("fast.trycloudflare.com",fast.update(ready("fast.trycloudflare.com"),2000,0));eq(false,fast.waiting());
  Selection offline=new Selection("saved.trycloudflare.com",0);
  eq(Selection.OFFICIAL,offline.update(new Directory.Result(null,Directory.State.OFFLINE,"offline"),1000,0));eq(false,offline.waiting());
  fast.update(unknown(),10000,0);fast.update(unknown(),25000,0);fast.update(unknown(),40000,0);
  eq("fast.trycloudflare.com",fast.selected());
  eq(Selection.OFFICIAL,fast.update(unknown(),70000,0));
  eq("new.trycloudflare.com",fast.update(ready("new.trycloudflare.com"),71000,0));
  long old=fast.revision();fast.adopt("manual.trycloudflare.com",72000);
  eq("manual.trycloudflare.com",fast.update(ready("old.trycloudflare.com"),73000,old));
  HttpRequest request=HttpRequest.newBuilder(URI.create("https://"+Selection.OFFICIAL+"/api")).build();
  eq(false,Bridge.tag(request).headers().firstValue(Directory.HEADER).isPresent());
  System.out.println("Policy passed: bounded 15s first decision, early readiness/offline, unknown distinction, late recovery, confirmed failover, stale results and official header isolation");
 }
}
