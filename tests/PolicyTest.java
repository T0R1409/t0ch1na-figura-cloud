import dev.t0ch1na.autocloud.Directory;
import dev.t0ch1na.autocloud.Selection;
import dev.t0ch1na.autocloud.Bridge;
import java.net.URI;
import java.net.http.HttpRequest;
import java.time.Instant;

public final class PolicyTest {
    private static void eq(Object expected, Object actual) {
        if (!java.util.Objects.equals(expected, actual)) throw new AssertionError(expected + " != " + actual);
    }
    public static void main(String[] args) throws Exception {
        Selection state = new Selection();
        eq(Selection.OFFICIAL, state.update(null));
        eq("first.trycloudflare.com", state.update("first.trycloudflare.com"));
        eq("first.trycloudflare.com", state.update(null));
        eq(Selection.OFFICIAL, state.update(null));
        eq("second.trycloudflare.com", state.update("second.trycloudflare.com"));
        eq("third.trycloudflare.com", state.update("third.trycloudflare.com"));
        Instant now=Instant.parse("2026-11-17T00:00:00Z");
        String json="{\"schema\":1,\"online\":true,\"hostname\":\"current.trycloudflare.com\",\"expiresAt\":\"2026-11-17T00:20:00Z\"}";
        eq("current.trycloudflare.com", Directory.parse(json, now));
        eq(null, Directory.parse(json, now.plusSeconds(1200)));
        eq(null, Directory.parse(json.replace("current.trycloudflare.com", "127.0.0.1"), now));
        eq(null, Directory.parse(json.replace("2026-11-17T00:20:00Z", "2026-11-18T00:20:00Z"), now));
        eq(false, Directory.allowedHost("evil.trycloudflare.com.evil.example"));
        eq(false, Directory.allowedHost("evil.trycloudflare.com:1234"));
        HttpRequest official=HttpRequest.newBuilder(URI.create("https://"+Selection.OFFICIAL+"/api")).build();
        eq(false, Bridge.tag(official).headers().firstValue(Directory.HEADER).isPresent());
        java.lang.reflect.Field applied=Bridge.class.getDeclaredField("applied");
        applied.setAccessible(true);
        applied.set(null,"latest.trycloudflare.com");
        HttpRequest privateRequest=HttpRequest.newBuilder(URI.create("https://latest.trycloudflare.com/api")).build();
        eq("1",Bridge.tag(privateRequest).headers().firstValue(Directory.HEADER).orElse(null));
        HttpRequest staleRequest=HttpRequest.newBuilder(URI.create("https://stale.trycloudflare.com/api")).build();
        eq(false,Bridge.tag(staleRequest).headers().firstValue(Directory.HEADER).isPresent());
        applied.set(null,Selection.OFFICIAL);
        System.out.println("Policy tests passed: failover, recovery, URL changes, expiry, host restrictions, official header isolation");
    }
}
