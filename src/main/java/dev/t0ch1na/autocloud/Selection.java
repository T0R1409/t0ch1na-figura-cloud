package dev.t0ch1na.autocloud;

/** Private-cloud-only policy: outages never select Figura's official cloud. */
public final class Selection {
    private String selected;
    private long revision;

    public Selection(String initialHost) {
        selected = Directory.allowedHost(initialHost) ? initialHost : Directory.INITIAL_HOST;
    }

    public void adopt(String host) {
        if (!Directory.allowedHost(host)) throw new IllegalArgumentException("Private cloud hostname required");
        selected = host;
        revision++;
    }

    public long revision() { return revision; }
    public String selected() { return selected; }

    public String update(String reachableHost, long probeRevision) {
        if (probeRevision == revision && Directory.allowedHost(reachableHost)) selected = reachableHost;
        return selected;
    }
}
