package org.figuramc.figura.config;
public class ConfigType<T> {
 public T value; public T tempValue;
 public ConfigType(T value) { this.value=value;this.tempValue=value; }
 public static class IPConfig extends ConfigType<String> { public IPConfig(String s){super(s);} }
}
