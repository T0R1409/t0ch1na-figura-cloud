package dev.t0ch1na.autocloud;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.time.Instant;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Base64;
import java.util.LinkedHashSet;
import java.util.Map;
import java.util.function.LongSupplier;
import java.util.regex.Pattern;

public final class Directory {
    public static final String URL = "https://raw.githubusercontent.com/T0R1409/t0ch1na-figura-cloud/main/cloud.json";
    public static final String API_URL = "https://api.github.com/repos/T0R1409/t0ch1na-figura-cloud/contents/cloud.json";
    public static final String HEADER = "X-T0CH1NA-Addon";
    public static final String VERSION = "1";
    private static final Pattern HOST = Pattern.compile("[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\\.trycloudflare\\.com");
    public enum State { READY, OFFLINE, UNKNOWN }
    public record Result(String host, State state, String message) {}
    public record Response(int status, String body, String date) {}
    @FunctionalInterface public interface Transport {
        Response get(URI uri, Duration timeout, Map<String,String> headers) throws Exception;
    }
    private final Transport transport;
    private final LongSupplier clock;
    private boolean triedApi;
    private long lastApi;
    private String discoveredCache;

    public Directory() {
        HttpClient client = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(5))
                .followRedirects(HttpClient.Redirect.NEVER).build();
        transport = (uri, timeout, headers) -> {
            HttpRequest.Builder builder = HttpRequest.newBuilder(uri).timeout(timeout).GET();
            headers.forEach(builder::header);
            HttpResponse<String> response = client.send(builder.build(), HttpResponse.BodyHandlers.ofString());
            return new Response(response.statusCode(), response.body(), response.headers().firstValue("Date").orElse(null));
        };
        clock = System::nanoTime;
    }
    public Directory(Transport transport, LongSupplier clock) { this.transport = transport; this.clock = clock; }
    public static boolean allowedHost(String host) { return host != null && HOST.matcher(host).matches(); }

    public static String parse(String json, Instant now) {
        if (json.length() > 8192) throw new IllegalArgumentException("Directory too large");
        JsonObject object = JsonParser.parseString(json).getAsJsonObject();
        if (object.get("schema").getAsInt() != 1) throw new IllegalArgumentException("Directory schema");
        Instant expires = Instant.parse(object.get("expiresAt").getAsString());
        if (!expires.isAfter(now) || expires.isAfter(now.plusSeconds(1800)))
            throw new IllegalArgumentException("Directory expired or clock mismatch");
        if (!object.get("online").getAsBoolean()) return null;
        String host = object.get("hostname").getAsString();
        if (!allowedHost(host)) throw new IllegalArgumentException("Invalid cloud hostname");
        return host;
    }
    private Duration budget(long deadline, int capSeconds) {
        long remaining = deadline - clock.getAsLong();
        if (remaining < 1_000_000L) throw new IllegalStateException("Probe time budget exhausted");
        return Duration.ofNanos(Math.min(remaining, capSeconds * 1_000_000_000L));
    }
    private String read(Response response) {
        if (response.status() != 200) throw new IllegalStateException("GitHub HTTP " + response.status());
        String body = response.body();
        if (body.length() > 20000) throw new IllegalArgumentException("Directory response too large");
        JsonObject object = JsonParser.parseString(body).getAsJsonObject();
        if (object.has("encoding") && "base64".equals(object.get("encoding").getAsString()))
            body = new String(Base64.getMimeDecoder().decode(object.get("content").getAsString()), java.nio.charset.StandardCharsets.UTF_8);
        Instant serverTime = Instant.now();
        if (response.date() != null) {
            try { serverTime = ZonedDateTime.parse(response.date(), DateTimeFormatter.RFC_1123_DATE_TIME).toInstant(); }
            catch (Exception ignored) {}
        }
        return parse(body, serverTime);
    }
    private static String problem(Exception e) {
        // No credentials are used in player requests; never include response bodies.
        return e instanceof IllegalStateException || e instanceof IllegalArgumentException
                ? e.getMessage() : e.getClass().getSimpleName();
    }
    public Result probe(String configuredHost, String cachedHost) {
        long deadline = clock.getAsLong() + 15_000_000_000L;
        String discovered = null;
        String detail = "กำลังอ่าน GitHub";
        boolean directoryRead = false;
        boolean declaredOffline = false;
        Map<String,String> headers = Map.of("Cache-Control", "no-cache", "User-Agent", "T0CH1NA-AutoCloud/1");
        try {
            Response response = transport.get(URI.create(URL + "?check=" + Instant.now().getEpochSecond() / 15), budget(deadline, 8), headers);
            discovered = read(response);
            directoryRead = true;
        } catch (Exception e) { detail = "อ่าน GitHub ไม่สำเร็จ: " + problem(e); }
        // Public API fallback is throttled to once per five minutes, avoiding
        // exhaustion of GitHub's unauthenticated API quota on shared IPs.
        if (!directoryRead && (!triedApi || clock.getAsLong() - lastApi >= 300_000_000_000L)) {
            triedApi = true;
            lastApi = clock.getAsLong();
            try {
                Response response = transport.get(URI.create(API_URL), budget(deadline, 4),
                        Map.of("Accept", "application/vnd.github.raw+json", "User-Agent", "T0CH1NA-AutoCloud/1"));
                discovered = read(response);
                directoryRead = true;
            } catch (Exception e) { detail = "อ่าน GitHub ไม่สำเร็จ: " + problem(e); }
        }
        declaredOffline = directoryRead && discovered == null;
        if (allowedHost(discovered)) discoveredCache = discovered;
        LinkedHashSet<String> candidates = new LinkedHashSet<>();
        if (allowedHost(discovered)) candidates.add(discovered);
        if (allowedHost(configuredHost)) candidates.add(configuredHost);
        if (allowedHost(cachedHost)) candidates.add(cachedHost);
        if (allowedHost(discoveredCache)) candidates.add(discoveredCache);
        for (String candidate : candidates) {
            try {
                Response response = transport.get(URI.create("https://" + candidate + "/health"), budget(deadline, 7),
                        Map.of(HEADER, VERSION, "User-Agent", "T0CH1NA-AutoCloud/1"));
                if (response.status() != 200) throw new IllegalStateException("Cloud HTTP " + response.status());
                if (response.body().length() > 4096) throw new IllegalArgumentException("Health response too large");
                JsonObject body = JsonParser.parseString(response.body()).getAsJsonObject();
                if (!"ok".equals(body.get("status").getAsString()) || !"t0ch1na".equals(body.get("cloudId").getAsString())
                        || !body.get("requiresAddon").getAsBoolean()) throw new IllegalArgumentException("Cloud identity mismatch");
                return new Result(candidate, State.READY, "คลาวด์ส่วนตัวพร้อมใช้งาน");
            } catch (Exception e) { detail = "ติดต่อคลาวด์ไม่ได้: " + problem(e); }
        }
        return new Result(null, declaredOffline ? State.OFFLINE : State.UNKNOWN,
                declaredOffline ? "โฮสต์ประกาศว่าคลาวด์ปิด" : detail);
    }
}
