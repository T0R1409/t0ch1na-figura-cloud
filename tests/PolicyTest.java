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
        Selection state = new Selection(Selection.OFFICIAL);
        eq(Selection.OFFICIAL, state.update(null, 0, state.revision()));
        eq("first.trycloudflare.com", state.update("first.trycloudflare.com", 1000, state.revision()));
        eq("first.trycloudflare.com", state.update(null, 2000, state.revision()));
        eq("first.trycloudflare.com", state.update(null, 17000, state.revision()));
        eq("first.trycloudflare.com", state.update(null, 32000, state.revision()));
        eq("first.trycloudflare.com", state.update(null, 61999, state.revision()));
        eq(Selection.OFFICIAL, state.update(null, 62000, state.revision()));
        eq("second.trycloudflare.com", state.update("second.trycloudflare.com", 63000, state.revision()));
        eq("third.trycloudflare.com", state.update("third.trycloudflare.com", 64000, state.revision()));

        // Regression: a saved private cloud remains selected even before a probe.
        Selection startup = new Selection("saved.trycloudflare.com");
        eq("saved.trycloudflare.com", startup.selected());
        eq("saved.trycloudflare.com", startup.update(null, 0, startup.revision()));
        eq("saved.trycloudflare.com", startup.update(null, 15000, startup.revision()));
        eq("saved.trycloudflare.com", startup.update("saved.trycloudflare.com", 30000, startup.revision()));

        // A success resets the grace window after intermittent network failure.
        eq("saved.trycloudflare.com", startup.update(null, 45000, startup.revision()));
        eq("saved.trycloudflare.com", startup.update(null, 60000, startup.revision()));
        eq("saved.trycloudflare.com", startup.update(null, 90000, startup.revision()));
        eq(Selection.OFFICIAL, startup.update(null, 105000, startup.revision()));

        // Regression: a result launched before a manual edit cannot clobber it.
        long oldRevision = startup.revision();
        startup.adopt("manual.trycloudflare.com");
        eq("manual.trycloudflare.com", startup.update(null, 999000, oldRevision));
        eq("manual.trycloudflare.com", startup.update("old.trycloudflare.com", 1000000, oldRevision));
        eq("manual.trycloudflare.com", startup.update(null, 1001000, startup.revision()));
        eq("manual.trycloudflare.com", startup.update(null, 1031000, startup.revision()));
        eq("new.trycloudflare.com", startup.update("new.trycloudflare.com", 1041000, startup.revision()));

        // Fast failures alone are insufficient; elapsed grace alone is insufficient.
        Selection rapid = new Selection("slow.trycloudflare.com");
        for (int i=0;i<20;i++) eq("slow.trycloudflare.com", rapid.update(null, i, rapid.revision()));
        eq(Selection.OFFICIAL, rapid.update(null, 60000, rapid.revision()));
        Selection few = new Selection("slow.trycloudflare.com");
        eq("slow.trycloudflare.com", few.update(null, 0, few.revision()));
        eq("slow.trycloudflare.com", few.update(null, 120000, few.revision()));
        eq(Selection.OFFICIAL, few.update(null, 120001, few.revision()));
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
        System.out.println("Policy regressions passed: startup preservation, slow probes, manual edits, stale results, grace reset, recovery, directory validation and header isolation");
    }
}
