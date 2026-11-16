package dev.t0ch1na.autocloud;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.time.Instant;
import java.util.regex.Pattern;

public final class Directory {
    private static final System.Logger LOG = System.getLogger("T0CH1NA AutoCloud");
    public static final String INITIAL_HOST = "departments-whole-scripts-aid.trycloudflare.com";
    public static final String URL = "https://raw.githubusercontent.com/T0R1409/t0ch1na-figura-cloud/main/cloud.json";
    public static final String HEADER = "X-T0CH1NA-Addon";
    public static final String VERSION = "1";
    private static final Pattern HOST = Pattern.compile("[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\\.trycloudflare\\.com");
    private final HttpClient client = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(8)).followRedirects(HttpClient.Redirect.NEVER).build();

    public static boolean allowedHost(String host) {
        return host != null && HOST.matcher(host).matches();
    }

    public static String parse(String json, Instant now) {
        if (json.length() > 8192) throw new IllegalArgumentException("Directory too large");
        JsonObject object = JsonParser.parseString(json).getAsJsonObject();
        if (object.get("schema").getAsInt() != 1 || !object.get("online").getAsBoolean()) return null;
        String host = object.get("hostname").getAsString();
        Instant expires = Instant.parse(object.get("expiresAt").getAsString());
        if (!allowedHost(host) || !expires.isAfter(now) || expires.isAfter(now.plusSeconds(1800))) return null;
        return host;
    }

    public String discover() throws Exception {
        // GitHub raw content can have an edge cache of several minutes. The host is
        // always health-checked; a changed nonce also prevents a stale client cache.
        HttpRequest request = HttpRequest.newBuilder(URI.create(URL + "?check=" + Instant.now().getEpochSecond() / 15))
                .timeout(Duration.ofSeconds(12)).header("Cache-Control", "no-cache").GET().build();
        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
        if (response.statusCode() != 200) return null;
        return parse(response.body(), Instant.now());
    }

    public boolean healthy(String host) {
        if (!allowedHost(host)) return false;
        try {
            HttpRequest request = HttpRequest.newBuilder(URI.create("https://" + host + "/health"))
                    .timeout(Duration.ofSeconds(15)).header(HEADER, VERSION).GET().build();
            HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
            if (response.statusCode() != 200 || response.body().length() > 4096) {
                LOG.log(System.Logger.Level.WARNING, "Private cloud health HTTP " + response.statusCode() + " for " + host);
                return false;
            }
            JsonObject body = JsonParser.parseString(response.body()).getAsJsonObject();
            return "ok".equals(body.get("status").getAsString())
                    && "t0ch1na".equals(body.get("cloudId").getAsString())
                    && body.get("requiresAddon").getAsBoolean();
        } catch (Exception e) {
            LOG.log(System.Logger.Level.WARNING, "Private cloud health failed for " + host + ": " + e.getClass().getSimpleName());
            return false;
        }
    }
}
