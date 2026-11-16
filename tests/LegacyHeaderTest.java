import dev.t0ch1na.autocloud.Bridge;
import dev.t0ch1na.autocloud.Directory;
import org.apache.http.client.methods.HttpGet;
import java.lang.reflect.Field;
import java.util.concurrent.atomic.AtomicBoolean;
public class LegacyHeaderTest {
 public static class Socket {
  public String header;
  public java.net.URI getURI(){return java.net.URI.create("wss://private.trycloudflare.com/ws");}
  public void addHeader(String name,String value){header=name+":"+value;}
 }
 public static void main(String[] args)throws Exception{
  Field busy=Bridge.class.getDeclaredField("BUSY");busy.setAccessible(true);((AtomicBoolean)busy.get(null)).set(true);
  org.figuramc.figura.config.Configs.SERVER_IP.value="private.trycloudflare.com";
  org.figuramc.figura.config.Configs.SERVER_IP.tempValue="private.trycloudflare.com";
  Bridge.bootstrap();
  HttpGet request=new HttpGet("https://private.trycloudflare.com/api");Bridge.tagLegacy(request);
  if(!"1".equals(request.getFirstHeader(Directory.HEADER).getValue()))throw new AssertionError("Private header missing");
  HttpGet official=new HttpGet("https://figura.moonlight-devs.org/api");Bridge.tagLegacy(official);
  if(official.containsHeader(Directory.HEADER))throw new AssertionError("Official header leaked");
  Socket socket=new Socket();Bridge.tagSocket(socket);
  if(!(Directory.HEADER+":1").equals(socket.header))throw new AssertionError("Socket header missing");
  System.out.println("Java 8 legacy headers passed: Apache HTTP request and socket tagged, official request isolated");
 }
}
