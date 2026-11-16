package dev.t0ch1na.autocloud;

/** Client-thread policy: preserve the current cloud until failures are confirmed. */
public final class Selection {
    public static final String OFFICIAL = "figura.moonlight-devs.org";
    public static final long FAILURE_GRACE_MS = 60_000;
    public static final int MIN_FAILURES = 3;
    private String selected;
    private int failures;
    private long failureSince;
    private long revision;

    public Selection(String initialHost) {
        selected = Directory.allowedHost(initialHost) ? initialHost : OFFICIAL;
    }

    /** A manual configuration change invalidates probes started for the old host. */
    public void adopt(String host) {
        selected = Directory.allowedHost(host) ? host : OFFICIAL;
        failures = 0;
        revision++;
    }

    public long revision() { return revision; }
    public String selected() { return selected; }

    public String update(String reachableHost, long nowMillis, long probeRevision) {
        if (probeRevision != revision) return selected;
        if (Directory.allowedHost(reachableHost)) {
            failures = 0;
            selected = reachableHost;
        } else if (Directory.allowedHost(selected)) {
            if (failures++ == 0) failureSince = nowMillis;
            if (failures >= MIN_FAILURES && nowMillis - failureSince >= FAILURE_GRACE_MS) {
                selected = OFFICIAL;
                failures = 0;
            }
        }
        return selected;
    }
}
