package dev.t0ch1na.autocloud;

/** Main-thread policy with a bounded first decision and conservative later failover. */
public final class Selection {
    public static final String OFFICIAL = "figura.moonlight-devs.org";
    public static final long STARTUP_WAIT_MS = 15_000;
    private String selected;
    private boolean waiting = true;
    private long started;
    private long revision;
    private int failures;
    private long failureSince;

    public Selection(String initialHost, long now) {
        selected = Directory.allowedHost(initialHost) ? initialHost : OFFICIAL;
        started = now;
    }
    public boolean waiting() { return waiting; }
    public String selected() { return selected; }
    public long revision() { return revision; }

    public void adopt(String host, long now) {
        selected = Directory.allowedHost(host) ? host : OFFICIAL;
        failures = 0;
        revision++;
        if (waiting) started = now;
    }
    public String tick(long now) {
        if (waiting && now - started >= STARTUP_WAIT_MS) {
            selected = OFFICIAL;
            waiting = false;
        }
        return selected;
    }
    public String update(Directory.Result result, long now, long probeRevision) {
        if (probeRevision != revision) return tick(now);
        if (result.state() == Directory.State.READY && Directory.allowedHost(result.host())) {
            selected = result.host();
            waiting = false;
            failures = 0;
        } else if (waiting) {
            // GitHub/network failure is not proof that the cloud is closed.
            if (result.state() == Directory.State.OFFLINE) {
                selected = OFFICIAL;
                waiting = false;
            }
        } else if (Directory.allowedHost(selected)) {
            if (failures++ == 0) failureSince = now;
            if (failures >= 3 && now - failureSince >= 60_000) {
                selected = OFFICIAL;
                failures = 0;
            }
        }
        return tick(now);
    }
}
