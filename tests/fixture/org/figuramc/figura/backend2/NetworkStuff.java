package org.figuramc.figura.backend2;
public class NetworkStuff {
 public static int backendStatus=2, disconnects, authentications;
 public static java.util.concurrent.ConcurrentLinkedQueue<Object> API_REQUESTS=new java.util.concurrent.ConcurrentLinkedQueue<>();
 public static java.util.concurrent.ConcurrentLinkedQueue<Object> WS_REQUESTS=new java.util.concurrent.ConcurrentLinkedQueue<>();
 public static void disconnect(String reason){disconnects++;backendStatus=1;}
 public static void reAuth(){authentications++;backendStatus=2;}
}
