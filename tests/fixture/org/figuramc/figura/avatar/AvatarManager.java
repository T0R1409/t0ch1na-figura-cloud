package org.figuramc.figura.avatar;
public class AvatarManager {
 public static java.util.Map<java.util.UUID,Object> LOADED_USERS=new java.util.concurrent.ConcurrentHashMap<>();
 public static void clearAvatars(java.util.UUID id){LOADED_USERS.remove(id);}
}
