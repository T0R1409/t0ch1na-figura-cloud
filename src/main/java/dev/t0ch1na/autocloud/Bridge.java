package dev.t0ch1na.autocloud;

import java.lang.reflect.Field;
import java.net.http.HttpRequest;
import java.util.ArrayList;
import java.util.Map;
import java.util.Queue;
import java.util.UUID;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicBoolean;

/** All Figura mutations run inside Figura's client tick, never on the worker. */
public final class Bridge {
    private static final System.Logger LOG = System.getLogger("T0CH1NA AutoCloud");
    private static final Directory DIRECTORY = new Directory();
    private static final Selection SELECTOR = new Selection();
    private static final AtomicBoolean BUSY = new AtomicBoolean();
    private static final ExecutorService WORKER = Executors.newSingleThreadExecutor(r -> {
        Thread t = new Thread(r, "t0ch1na-cloud-discovery"); t.setDaemon(true); return t;
    });
    private static volatile String verifiedHost;
    private static volatile String desired = Selection.OFFICIAL;
    private static volatile String applied;
    private static long nextProbe;
    private static long lastAuth;
    private static boolean disabled;
    private static final long INTERVAL = 15_000_000_000L;

    private Bridge() {}

    public static void tick() {
        if (disabled) return;
        try {
            long now = System.nanoTime();
            if (!desired.equals(applied) || !desired.equals(currentHost())) {
                switchHost(desired);
                applied = desired;
                lastAuth = now;
            } else if (now - lastAuth >= 30_000_000_000L && backendStatus() == 1) {
                figura("backend2.NetworkStuff").getMethod("reAuth").invoke(null);
                lastAuth = now;
            }
            if (now >= nextProbe && BUSY.compareAndSet(false, true)) {
                nextProbe = now + INTERVAL;
                WORKER.execute(() -> {
                    try {
                        String candidate = null;
                        try { candidate = DIRECTORY.discover(); } catch (Exception ignored) {}
                        String reachable = null;
                        if (candidate != null && DIRECTORY.healthy(candidate)) reachable = candidate;
                        else if (verifiedHost != null && !verifiedHost.equals(candidate)
                                && DIRECTORY.healthy(verifiedHost)) reachable = verifiedHost;
                        if (reachable != null) verifiedHost = reachable;
                        desired = SELECTOR.update(reachable);
                    } catch (Exception e) {
                        LOG.log(System.Logger.Level.WARNING, "Cloud probe failed: " + e.getClass().getSimpleName());
                    } finally { BUSY.set(false); }
                });
            }
        } catch (Exception e) {
            disabled = true;
            LOG.log(System.Logger.Level.ERROR, "Unsupported Figura API; AutoCloud disabled", e);
        }
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
        Object setting = ipSetting();
        Class<?> type = figura("config.ConfigType");
        // Set both values explicitly; Figura's setValue only runs onChange when
        // value and tempValue already differ. Re-auth once after all changes.
        type.getField("value").set(setting, host);
        type.getField("tempValue").set(setting, host);
        figura("config.ConfigManager").getMethod("saveConfig").invoke(null);
        applied = host;
        network.getMethod("reAuth").invoke(null);
        LOG.log(System.Logger.Level.INFO, "Cloud selected: " + host);
    }

    public static boolean privateHost(String host) {
        return host != null && Directory.allowedHost(host) && host.equals(applied);
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
