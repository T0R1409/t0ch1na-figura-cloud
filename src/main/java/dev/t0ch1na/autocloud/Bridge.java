package dev.t0ch1na.autocloud;

import java.lang.reflect.Field;
import java.net.http.HttpRequest;
import java.util.ArrayList;
import java.util.Map;
import java.util.Queue;
import java.util.LinkedHashSet;
import java.util.UUID;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicReference;

/** All Figura mutations run inside Figura's client tick, never on the worker. */
public final class Bridge {
    private static final System.Logger LOG = System.getLogger("T0CH1NA AutoCloud");
    private static final Directory DIRECTORY = new Directory();
    private static Selection selector;
    private static final AtomicReference<ProbeResult> PENDING = new AtomicReference<>();
    private static final AtomicBoolean BUSY = new AtomicBoolean();
    private static final ExecutorService WORKER = Executors.newSingleThreadExecutor(r -> {
        Thread t = new Thread(r, "t0ch1na-cloud-discovery"); t.setDaemon(true); return t;
    });
    private static String verifiedHost;
    private static volatile String applied;
    private static long lastProbe;
    private static boolean hasProbed;
    private static long lastAuth;
    private static boolean disabled;
    private static final long INTERVAL = 15_000_000_000L;

    private Bridge() {}

    private record ProbeResult(long revision, String reachable) {}

    public static void tick() {
        if (disabled) return;
        try {
            long now = System.nanoTime();
            String current = currentHost();
            if (selector == null) bootstrap();
            current = currentHost();
            if (!Directory.allowedHost(current)) {
                // A Settings reset or manual official IP must never opt out of
                // this private-only mode while the addon is installed.
                switchHost(selector.selected());
                current = selector.selected();
                lastAuth = now;
            } else if (!current.equals(applied)) {
                selector.adopt(current);
                applied = current;
                verifiedHost = current;
                lastAuth = now;
                hasProbed = false;
                LOG.log(System.Logger.Level.INFO, "Checking manually selected cloud: " + current);
            }

            ProbeResult result = PENDING.getAndSet(null);
            if (result != null && result.revision() == selector.revision()) {
                String target = selector.update(result.reachable(), result.revision());
                if (result.reachable() != null) verifiedHost = result.reachable();
                if (!target.equals(current)) {
                    switchHost(target);
                    lastAuth = now;
                    current = target;
                }
            }

            // A slow authentication in state 2 is left alone. Retry only an
            // explicitly disconnected backend, not one that is still loading.
            if (now - lastAuth >= 30_000_000_000L && backendStatus() == 1) {
                figura("backend2.NetworkStuff").getMethod("reAuth").invoke(null);
                lastAuth = now;
            }

            if ((!hasProbed || now - lastProbe >= INTERVAL) && BUSY.compareAndSet(false, true)) {
                lastProbe = now;
                hasProbed = true;
                long revision = selector.revision();
                String configuredHost = current;
                String cachedHost = verifiedHost;
                WORKER.execute(() -> {
                    String reachable = null;
                    try {
                        LinkedHashSet<String> candidates = new LinkedHashSet<>();
                        try {
                            String discovered = DIRECTORY.discover();
                            if (discovered != null) candidates.add(discovered);
                        } catch (Exception e) {
                            LOG.log(System.Logger.Level.DEBUG, "Directory check: " + e.getClass().getSimpleName());
                        }
                        if (Directory.allowedHost(configuredHost)) candidates.add(configuredHost);
                        if (Directory.allowedHost(cachedHost)) candidates.add(cachedHost);
                        for (String candidate : candidates) {
                            if (DIRECTORY.healthy(candidate)) { reachable = candidate; break; }
                        }
                    } catch (Exception e) {
                        LOG.log(System.Logger.Level.WARNING, "Cloud probe failed: " + e.getClass().getSimpleName());
                    } finally {
                        PENDING.set(new ProbeResult(revision, reachable));
                        BUSY.set(false);
                    }
                });
            }
        } catch (Exception e) {
            disabled = true;
            LOG.log(System.Logger.Level.ERROR, "Unsupported Figura API; AutoCloud disabled", e);
        }
    }

    /** Called by ConfigManager.loadConfig before Figura starts cloud authentication. */
    public static void bootstrap() {
        try {
            String saved = currentHost();
            String target = Directory.allowedHost(saved) ? saved : Directory.INITIAL_HOST;
            writeHost(target);
            if (selector == null) selector = new Selection(target);
            else selector.adopt(target);
            applied = target;
            verifiedHost = target;
            hasProbed = false;
            lastAuth = System.nanoTime() - 30_000_000_000L;
            LOG.log(System.Logger.Level.INFO, "Private cloud set during Figura startup: " + target);
        } catch (Exception e) {
            throw new IllegalStateException("Unable to initialize T0CH1NA private cloud", e);
        }
    }

    private static void writeHost(String host) throws Exception {
        Object setting = ipSetting();
        Class<?> type = figura("config.ConfigType");
        type.getField("value").set(setting, host);
        type.getField("tempValue").set(setting, host);
    }

    private static Class<?> figura(String suffix) throws ClassNotFoundException {
        return Class.forName("org.figuramc.figura." + suffix);
    }
    private static Object ipSetting() throws Exception {
        return figura("config.Configs").getField("SERVER_IP").get(null);
    }
    private static String currentHost() throws Exception {
        return String.valueOf(figura("config.ConfigType").getField("value").get(ipSetting()));
    }
    private static int backendStatus() throws Exception {
        return figura("backend2.NetworkStuff").getField("backendStatus").getInt(null);
    }

    private static void switchHost(String host) throws Exception {
        Class<?> network = figura("backend2.NetworkStuff");
        network.getMethod("disconnect", String.class).invoke(null, "AutoCloud switching backend");
        for (String name : new String[]{"API_REQUESTS", "WS_REQUESTS"}) {
            Field field = network.getDeclaredField(name);
            field.setAccessible(true);
            ((Queue<?>) field.get(null)).clear();
        }
        // Clear only remote cached avatars. Keep the user's selected local avatar.
        Class<?> avatars = figura("avatar.AvatarManager");
        Field loaded = avatars.getDeclaredField("LOADED_USERS");
        loaded.setAccessible(true);
        Map<?, ?> users = (Map<?, ?>) loaded.get(null);
        Class<?> mod = figura("FiguraMod");
        for (Object key : new ArrayList<>(users.keySet())) {
            UUID id = (UUID) key;
            if (!(boolean) mod.getMethod("isLocal", UUID.class).invoke(null, id))
                avatars.getMethod("clearAvatars", UUID.class).invoke(null, id);
        }
        writeHost(host);
        figura("config.ConfigManager").getMethod("saveConfig").invoke(null);
        applied = host;
        network.getMethod("reAuth").invoke(null);
        LOG.log(System.Logger.Level.INFO, "Cloud selected: " + host);
    }

    public static boolean privateHost(String host) {
        if (!Directory.allowedHost(host)) return false;
        if (host.equals(applied)) return true;
        // A Settings edit can authenticate before the next client tick. Tag
        // that request immediately instead of letting the addon gate reject it.
        try { return host.equals(currentHost()); }
        catch (Exception e) { return false; }
    }

    public static HttpRequest tag(HttpRequest request) {
        if (!privateHost(request.uri().getHost())) return request;
        return HttpRequest.newBuilder(request, (name, value) -> !name.equalsIgnoreCase(Directory.HEADER))
                .header(Directory.HEADER, Directory.VERSION).build();
    }

    public static HttpRequest.Builder tag(HttpRequest.Builder builder) {
        if (privateHost(builder.build().uri().getHost())) builder.setHeader(Directory.HEADER, Directory.VERSION);
        return builder;
    }

    public static void tagSocket(Object socket) {
        if (socket == null) return;
        try {
            java.net.URI uri = (java.net.URI) socket.getClass().getMethod("getURI").invoke(socket);
            if (privateHost(uri.getHost())) socket.getClass().getMethod("addHeader", String.class, String.class)
                    .invoke(socket, Directory.HEADER, Directory.VERSION);
        } catch (Exception e) {
            LOG.log(System.Logger.Level.ERROR, "Unable to tag Figura WebSocket", e);
        }
    }
}
