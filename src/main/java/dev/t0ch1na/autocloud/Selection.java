package dev.t0ch1na.autocloud;

/** Pure failover state machine. Two failed probes prevent transient flapping. */
public final class Selection {
    public static final String OFFICIAL = "figura.moonlight-devs.org";
    private String selected = OFFICIAL;
    private int failures;

    public String update(String reachableHost) {
        if (reachableHost != null) {
            failures = 0;
            selected = reachableHost;
        } else if (++failures >= 2) {
            selected = OFFICIAL;
        }
        return selected;
    }
}
