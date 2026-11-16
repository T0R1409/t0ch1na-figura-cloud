"""Validate mixin/reflection targets against the five real released Figura JARs."""
from pathlib import Path
import struct
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def members(data):
    count=struct.unpack_from('>H',data,8)[0]; pos=10; i=1; pool={}
    while i<count:
        tag=data[pos];pos+=1
        if tag==1:
            size=struct.unpack_from('>H',data,pos)[0];pos+=2
            pool[i]=data[pos:pos+size].decode('utf-8',errors='replace');pos+=size
        elif tag in (3,4,9,10,11,12,17,18):pos+=4
        elif tag in (5,6):pos+=8;i+=1
        elif tag in (7,8,16,19,20):pos+=2
        elif tag==15:pos+=3
        else:raise ValueError(tag)
        i+=1
    pos+=6
    count=struct.unpack_from('>H',data,pos)[0];pos+=2+2*count
    result=set()
    for _ in range(2):
        count=struct.unpack_from('>H',data,pos)[0];pos+=2
        for __ in range(count):
            access,name,desc,attrs=struct.unpack_from('>HHHH',data,pos);pos+=8
            result.add((pool[name],pool[desc]))
            for ___ in range(attrs):
                size=struct.unpack_from('>I',data,pos+2)[0];pos+=6+size
    return result


TARGETS={
 'backend2/NetworkStuff': [('tick','()V'),('reAuth','()V'),('disconnect','(Ljava/lang/String;)V'),
                           ('backendStatus','I'),('API_REQUESTS','Ljava/util/concurrent/ConcurrentLinkedQueue;'),
                           ('WS_REQUESTS','Ljava/util/concurrent/ConcurrentLinkedQueue;')],
 'backend2/HttpAPI': [('header','(Ljava/lang/String;)Ljava/net/http/HttpRequest$Builder;')],
 'backend2/AuthHandler':[('request','(Ljava/net/http/HttpRequest;)Ljava/lang/String;')],
 'backend2/trust/KeyStoreHelper':[('websocketWithBackendCertificates','(Ljava/lang/String;)Lcom/neovisionaries/ws/client/WebSocket;')],
 'config/Configs':[('SERVER_IP','Lorg/figuramc/figura/config/ConfigType$IPConfig;')],
 'config/ConfigType':[('value','Ljava/lang/Object;'),('tempValue','Ljava/lang/Object;')],
 'config/ConfigManager':[('saveConfig','()V'),('loadConfig','()V')],
 'avatar/AvatarManager':[('clearAvatars','(Ljava/util/UUID;)V'),('LOADED_USERS','Ljava/util/Map;')],
 'FiguraMod':[('isLocal','(Ljava/util/UUID;)Z')],
}


def main():
    jars=list((ROOT.parent/'figura-cloud/clients').glob('*.jar'))
    assert len(jars)==5,'Download Figura for Fabric/Forge 1.20.1 and Fabric/Forge/NeoForge 1.21.1 first'
    for p in jars:
        with zipfile.ZipFile(p) as z:
            for cls, wanted in TARGETS.items():
                found=members(z.read('org/figuramc/figura/'+cls+'.class'))
                for target in wanted:
                    assert target in found,(p.name,cls,target,found)
        print('Figura contract verified:',p.name)

if __name__=='__main__':main()
