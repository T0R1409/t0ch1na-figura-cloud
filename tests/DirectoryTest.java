import dev.t0ch1na.autocloud.*;
import java.time.Instant;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
public class DirectoryTest {
 static final String DATE="Tue, 17 Nov 2026 00:00:00 GMT";
 static final String DOC="{\"schema\":1,\"online\":true,\"hostname\":\"latest.trycloudflare.com\",\"expiresAt\":\"2026-11-17T00:20:00Z\"}";
 static final String HEALTH="{\"status\":\"ok\",\"cloudId\":\"t0ch1na\",\"requiresAddon\":true}";
 static void eq(Object e,Object a){if(!java.util.Objects.equals(e,a))throw new AssertionError(e+" != "+a);}
 public static void main(String[] args)throws Exception{
  AtomicLong clock=new AtomicLong();
  Directory direct=new Directory((uri,timeout,headers)->new Directory.Response(200,uri.getPath().equals("/health")?HEALTH:DOC,DATE),clock::get);
  // HTTP Date is used, so a wrong local PC date does not reject a valid document.
  eq(Directory.State.READY,direct.probe(Selection.OFFICIAL,null).state());
  AtomicInteger raw=new AtomicInteger(),api=new AtomicInteger();
  Directory fallback=new Directory((uri,timeout,headers)->{
   if(uri.getHost().equals("raw.githubusercontent.com")){raw.incrementAndGet();return new Directory.Response(403,"blocked",DATE);}
   if(uri.getHost().equals("api.github.com")){api.incrementAndGet();return new Directory.Response(200,DOC,DATE);}
   return new Directory.Response(200,HEALTH,DATE);
  },clock::get);
  eq("latest.trycloudflare.com",fallback.probe(Selection.OFFICIAL,null).host());
  eq("latest.trycloudflare.com",fallback.probe(Selection.OFFICIAL,null).host());
  eq(2,raw.get());eq(1,api.get()); // Cooldown plus cached discovery still works.
  Directory unavailable=new Directory((uri,timeout,headers)->{throw new java.net.http.HttpTimeoutException("timeout");},clock::get);
  eq(Directory.State.UNKNOWN,unavailable.probe(Selection.OFFICIAL,null).state());
  Directory offline=new Directory((uri,timeout,headers)->new Directory.Response(200,DOC.replace("\"online\":true","\"online\":false"),DATE),clock::get);
  eq(Directory.State.OFFLINE,offline.probe(Selection.OFFICIAL,null).state());
  AtomicLong deadlineClock=new AtomicLong();
  Directory bounded=new Directory((uri,timeout,headers)->{
   deadlineClock.addAndGet(timeout.toNanos());
   if(uri.getHost().equals("raw.githubusercontent.com"))return new Directory.Response(200,DOC,DATE);
   throw new java.net.http.HttpTimeoutException("slow health");
  },deadlineClock::get);
  eq(Directory.State.UNKNOWN,bounded.probe(Selection.OFFICIAL,null).state());
  eq(15_000_000_000L,deadlineClock.get());
  try{Directory.parse(DOC,Instant.parse("2026-11-17T00:21:00Z"));throw new AssertionError("expired accepted");}catch(IllegalArgumentException expected){}
  try{Directory.parse(DOC.replace("latest.trycloudflare.com","127.0.0.1"),Instant.parse("2026-11-17T00:00:00Z"));throw new AssertionError("invalid accepted");}catch(IllegalArgumentException expected){}
  System.out.println("Directory passed: healthy, raw/API fallback, cooldown, discovered-host cache, server clock, network-vs-offline distinction, stale/invalid rejection and total 15s budget");
 }
}
