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
        String official = "figura.moonlight-devs.org";
        Selection fresh = new Selection(official);
        eq(Directory.INITIAL_HOST, fresh.selected());
        for (int i=0; i<1000; i++) eq(Directory.INITIAL_HOST, fresh.update(null, fresh.revision()));
        Selection saved = new Selection("saved.trycloudflare.com");
        eq("saved.trycloudflare.com", saved.selected());
        for (int i=0; i<1000; i++) eq("saved.trycloudflare.com", saved.update(null, saved.revision()));
        eq("latest.trycloudflare.com", saved.update("latest.trycloudflare.com", saved.revision()));
        long old = saved.revision();
        saved.adopt("manual.trycloudflare.com");
        eq("manual.trycloudflare.com", saved.update("stale.trycloudflare.com", old));
        eq("manual.trycloudflare.com", saved.update(null, old));
        eq("manual.trycloudflare.com", saved.update(official, saved.revision()));
        eq("manual.trycloudflare.com", saved.update(null, saved.revision()));
        eq("new.trycloudflare.com", saved.update("new.trycloudflare.com", saved.revision()));
        try { saved.adopt(official); throw new AssertionError("Official cloud accepted"); }
        catch (IllegalArgumentException expected) {}
        Instant now=Instant.parse("2026-11-17T00:00:00Z");
        String json="{\"schema\":1,\"online\":true,\"hostname\":\"current.trycloudflare.com\",\"expiresAt\":\"2026-11-17T00:20:00Z\"}";
        eq("current.trycloudflare.com", Directory.parse(json, now));
        eq(null, Directory.parse(json, now.plusSeconds(1200)));
        eq(null, Directory.parse(json.replace("current.trycloudflare.com", "127.0.0.1"), now));
        eq(null, Directory.parse(json.replace("2026-11-17T00:20:00Z", "2026-11-18T00:20:00Z"), now));
        eq(false, Directory.allowedHost("evil.trycloudflare.com.evil.example"));
        eq(false, Directory.allowedHost("evil.trycloudflare.com:1234"));
        HttpRequest officialRequest=HttpRequest.newBuilder(URI.create("https://"+official+"/api")).build();
        eq(false, Bridge.tag(officialRequest).headers().firstValue(Directory.HEADER).isPresent());
        java.lang.reflect.Field applied=Bridge.class.getDeclaredField("applied");
        applied.setAccessible(true);
        applied.set(null,"latest.trycloudflare.com");
        HttpRequest privateRequest=HttpRequest.newBuilder(URI.create("https://latest.trycloudflare.com/api")).build();
        eq("1",Bridge.tag(privateRequest).headers().firstValue(Directory.HEADER).orElse(null));
        HttpRequest staleRequest=HttpRequest.newBuilder(URI.create("https://stale.trycloudflare.com/api")).build();
        eq(false,Bridge.tag(staleRequest).headers().firstValue(Directory.HEADER).isPresent());
        applied.set(null,official);
        System.out.println("Private-only policy passed: fresh default, saved host, indefinite outage retention, official-host rejection, stale probe rejection, recovery, validation and header isolation");
    }
}
