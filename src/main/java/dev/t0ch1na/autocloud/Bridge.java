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
    private static volatile boolean startupWaiting = true;
    private static String statusMessage = "กำลังตรวจคลาวด์ สูงสุด 15 วินาที";
    private static String shownStatus;
    private static final long INTERVAL = 15_000_000_000L;

    private Bridge() {}

    private record ProbeResult(long revision, Directory.Result result) {}

    /** AuthHandler calls this before launching Mojang authentication. */
    public static boolean deferAuthentication() { return startupWaiting; }

    private static long millis(long nanos) { return java.util.concurrent.TimeUnit.NANOSECONDS.toMillis(nanos); }

    public static void tick() {
        if (disabled) return;
        try {
            long now = System.nanoTime();
            if (selector == null) bootstrap();
            String current = currentHost();
            if (!current.equals(applied)) {
                selector.adopt(current, millis(now));
                applied = current;
                if (Directory.allowedHost(current)) verifiedHost = current;
                lastAuth = now;
                hasProbed = false;
                setStatus("กำลังตรวจคลาวด์ที่เลือกใหม่");
            }
            boolean wasWaiting = selector.waiting();
            ProbeResult result = PENDING.getAndSet(null);
            boolean accepted = result != null && result.revision() == selector.revision();
            if (accepted) {
                selector.update(result.result(), millis(now), result.revision());
                if (result.result().state() == Directory.State.READY) {
                    verifiedHost = result.result().host();
                    setStatus("พบคลาวด์ส่วนตัว กำลังเชื่อมต่อ");
                } else setStatus(result.result().message());
            }
            String target = selector.tick(millis(now));
            startupWaiting = selector.waiting();
            if (wasWaiting && !startupWaiting && Selection.OFFICIAL.equals(target)) {
                setStatus(accepted && result.result().state() == Directory.State.OFFLINE
                        ? "คลาวด์ส่วนตัวปิด ใช้ Figura ทางการชั่วคราวและตรวจต่อ"
                        : "ตรวจไม่ทัน 15 วินาที ใช้ Figura ทางการชั่วคราวและตรวจต่อ");
            }
            if (!startupWaiting && ((!target.equals(current)) || wasWaiting)) {
                if (Selection.OFFICIAL.equals(target) && !wasWaiting)
                    setStatus("ติดต่อคลาวด์ส่วนตัวไม่ได้ ใช้ Figura ทางการชั่วคราวและตรวจต่อ");
                switchHost(target);
                lastAuth = now;
            }
            if (!startupWaiting && now - lastAuth >= 30_000_000_000L && backendStatus() == 1) {
                figura("backend2.NetworkStuff").getMethod("reAuth").invoke(null);
                lastAuth = now;
            }
            startProbe(now);
            showStatus();
        } catch (Exception e) {
            disabled = true;
            startupWaiting = false;
            LOG.log(System.Logger.Level.ERROR, "AutoCloud disabled: incompatible Figura API", e);
        }
    }

    private static void startProbe(long now) {
        if ((!hasProbed || now - lastProbe >= INTERVAL) && BUSY.compareAndSet(false, true)) {
            lastProbe = now;
            hasProbed = true;
            long revision = selector.revision();
            String configuredHost = applied;
            String cachedHost = verifiedHost;
            WORKER.execute(() -> {
                Directory.Result result;
                try { result = DIRECTORY.probe(configuredHost, cachedHost); }
                catch (Exception e) { result = new Directory.Result(null, Directory.State.UNKNOWN, "ตรวจคลาวด์ไม่สำเร็จ: " + e.getClass().getSimpleName()); }
                PENDING.set(new ProbeResult(revision, result));
                BUSY.set(false);
            });
        }
    }

    /** Prepare asynchronous discovery; never block Figura's configuration load. */
    public static void bootstrap() {
        try {
            long now = System.nanoTime();
            String current = currentHost();
            if (selector == null) selector = new Selection(current, millis(now));
            else selector.adopt(current, millis(now));
            startupWaiting = selector.waiting();
            applied = current;
            if (Directory.allowedHost(current)) verifiedHost = current;
            hasProbed = false;
            lastAuth = now;
            setStatus("กำลังตรวจลิงก์และคลาวด์ สูงสุด 15 วินาที");
            startProbe(now);
        } catch (Exception e) {
            startupWaiting = false;
            LOG.log(System.Logger.Level.ERROR, "Unable to prepare AutoCloud discovery", e);
        }
    }

    private static void setStatus(String message) {
        if (!message.equals(statusMessage)) {
            statusMessage = message;
            LOG.log(System.Logger.Level.INFO, "AutoCloud: " + message);
        }
    }
    private static void showStatus() {
        if (statusMessage.equals(shownStatus)) return;
        shownStatus = statusMessage;
        try {
            figura("gui.FiguraToast").getMethod("sendToast", Object.class, Object.class)
                    .invoke(null, "T0CH1NA AutoCloud", statusMessage);
        } catch (Exception e) {
            LOG.log(System.Logger.Level.DEBUG, "Toast unavailable: " + e.getClass().getSimpleName());
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
