"""Build only game/loader pairs verified against published Figura binary APIs."""
from pathlib import Path
import hashlib,json,os,subprocess,zipfile,shutil,urllib.request
from generate_legacy_sources import generate
ROOT=Path(__file__).resolve().parent
VERSION='1.0.0-beta.7'
NAME='T-Zero Auto Figura IP'
AUTHOR='⋆. 𐙚˚࿔ T-Zero 𝜗𝜚˚⋆'
DESCRIPTION='จัดทำโดย\n\n'+AUTHOR
FORGE={'1.16.5':36,'1.18.2':40,'1.19.2':43,'1.19.3':44,'1.19.4':45,'1.20.1':47,'1.20.2':48,'1.20.4':49,'1.20.6':50,'1.21.1':52,'1.21.2':53,'1.21.3':53,'1.21.4':54}
entries=json.loads((ROOT/'support-matrix.json').read_text())['entries']
compiled={};outputs=[]
DEPS=ROOT/'deps';OUT=ROOT/'dist/all-versions';OUT.mkdir(parents=True,exist_ok=True)

DEPENDENCIES={
 'ecj.jar':'https://repo.maven.apache.org/maven2/org/eclipse/jdt/ecj/3.40.0/ecj-3.40.0.jar',
 'gson.jar':'https://repo.maven.apache.org/maven2/com/google/code/gson/gson/2.10.1/gson-2.10.1.jar',
 'mixin.jar':'https://maven.fabricmc.net/net/fabricmc/sponge-mixin/0.15.5+mixin.0.8.7/sponge-mixin-0.15.5+mixin.0.8.7.jar',
 'fabric-loader.jar':'https://maven.fabricmc.net/net/fabricmc/fabric-loader/0.16.14/fabric-loader-0.16.14.jar',
 'forge-47.jar':'https://maven.minecraftforge.net/net/minecraftforge/javafmllanguage/1.20.1-47.1.43/javafmllanguage-1.20.1-47.1.43.jar',
 'forge-36.jar':'https://maven.minecraftforge.net/net/minecraftforge/forge/1.16.5-36.2.42/forge-1.16.5-36.2.42-universal.jar',
 'neoforge-loader.jar':'https://maven.neoforged.net/releases/net/neoforged/fancymodloader/loader/4.0.42/loader-4.0.42.jar',
 'neoforge-loader17.jar':'https://maven.neoforged.net/releases/net/neoforged/fancymodloader/loader/2.0.17/loader-2.0.17.jar',
 'apache-httpclient.jar':'https://repo.maven.apache.org/maven2/org/apache/httpcomponents/httpclient/4.3.3/httpclient-4.3.3.jar',
 'apache-httpcore.jar':'https://repo.maven.apache.org/maven2/org/apache/httpcomponents/httpcore/4.3.2/httpcore-4.3.2.jar',
}
DEPS.mkdir(exist_ok=True)
for filename,url in DEPENDENCIES.items():
    if not (DEPS/filename).exists():
        with urllib.request.urlopen(url,timeout=90) as response:(DEPS/filename).write_bytes(response.read())

for row in entries:
    game,loader=row['minecraft'],row['loader']
    legacy=row['profile']=='legacy8';quilt=loader=='quilt'
    entry_loader='fabric' if loader in ('fabric','quilt') else 'forge' if row['profile']=='legacy-neoforge' else loader
    level=8 if legacy else 21 if entry_loader=='neoforge' and row['java']==21 else 17
    key=(row['profile'],entry_loader,level)
    if key not in compiled:
        label='-'.join(map(str,key));generated=ROOT/'build/generated-all'/label
        generated.mkdir(parents=True,exist_ok=True)
        if legacy:
            core=generate(ROOT,generated)
            sources=list(core.rglob('*.java'))+list((generated/entry_loader).rglob('*.java'))
        elif quilt:
            core=generated/'core';core.mkdir(exist_ok=True)
            for p in (ROOT/'src/main/java').rglob('*.java'):
                target=core/p.relative_to(ROOT/'src/main/java');target.parent.mkdir(parents=True,exist_ok=True)
                target.write_text(p.read_text().replace('org.figuramc.figura.','fabric.org.figuramc.figura.'))
            (core/'dev/t0ch1na/autocloud/mixin/SocketMixin.java').write_text('''package dev.t0ch1na.autocloud.mixin;
import dev.t0ch1na.autocloud.Bridge;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
@Mixin(targets="fabric.org.figuramc.figura.backend2.websocket.WebsocketThingy",remap=false)
public abstract class SocketMixin {
 @Inject(method="<init>",at=@At("RETURN"),remap=false)
 private void tag(String token,CallbackInfo ci){Bridge.tagSocket(this);}
}
''')
            sources=list(core.rglob('*.java'))+list((ROOT/'src/fabric/java').rglob('*.java'))
        else:sources=list((ROOT/'src/main/java').rglob('*.java'))+list((ROOT/f'src/{entry_loader}/java').rglob('*.java'))
        dependency='fabric-loader.jar' if entry_loader=='fabric' else 'forge-36.jar' if legacy else ('neoforge-loader.jar' if level==21 else 'neoforge-loader17.jar') if entry_loader=='neoforge' else 'forge-47.jar'
        deps=['mixin.jar','gson.jar',dependency]+(['apache-httpclient.jar','apache-httpcore.jar'] if legacy else [])
        for dep in deps:assert (DEPS/dep).is_file(),dep
        classes=ROOT/'build/all-classes'/label
        if classes.exists():shutil.rmtree(classes)
        classes.mkdir(parents=True)
        subprocess.run(['java','-jar',str(DEPS/'ecj.jar'),f'-{level}','-warn:-deprecation','-proc:none','-encoding','UTF-8','-cp',os.pathsep.join(str(DEPS/d) for d in deps),'-d',str(classes)]+[str(p) for p in sources],check=True)
        compiled[key]=classes
    classes=compiled[key]
    path=OUT/f'T-Zero-{game}-{loader}-beta7.jar'
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(classes.rglob('*.class')):z.write(p,p.relative_to(classes).as_posix())
        for name in ['LICENSE','ARTWORK.md']:z.write(ROOT/name,name)
        z.write(ROOT/'src/main/resources/icon.png','icon.png')
        z.writestr('META-INF/MANIFEST.MF','Manifest-Version: 1.0\nMixinConfigs: t0ch1na-autocloud.mixins.json\n\n')
        z.writestr('t0ch1na-autocloud.mixins.json',json.dumps({'required':True,'minVersion':'0.8','package':'dev.t0ch1na.autocloud.mixin','compatibilityLevel':f'JAVA_{level}','client':['BootstrapMixin','NetworkMixin','HttpMixin','AuthMixin','SocketMixin'],'injectors':{'defaultRequire':1}}))
        base=row.get('figura_min',row['figura'].split('+')[0]);upper='.'.join([*base.split('.')[:2],str(int(base.split('.')[2])+1)])
        upper=row.get('figura_upper',upper)
        if entry_loader=='fabric':
            depends={'fabricloader':'>=0.14.25','minecraft':game,'java':f'>={row["java"]}','figura':f'>={base} <{upper}'}
            if quilt:depends['quilt_loader']='>=0.20.0'
            z.writestr('fabric.mod.json',json.dumps({'schemaVersion':1,'id':'t0ch1na_autocloud','version':VERSION,'name':NAME,'description':DESCRIPTION,'authors':[AUTHOR],'license':'MIT','icon':'icon.png','environment':'client','entrypoints':{'client':['dev.t0ch1na.autocloud.FabricEntrypoint']},'mixins':['t0ch1na-autocloud.mixins.json'],'depends':depends},ensure_ascii=False,indent=2))
        else:
            neo=entry_loader=='neoforge';modern_neo=neo and row['java']==21
            meta='META-INF/neoforge.mods.toml' if modern_neo else 'META-INF/mods.toml'
            fml='[1,)' if neo else f'[{FORGE[game]},{FORGE[game]+1})'
            data=f'''modLoader="javafml"
loaderVersion="{fml}"
license="MIT"
[[mods]]
modId="t0ch1na_autocloud"
version="{VERSION}"
displayName="{NAME}"
logoFile="icon.png"
authors={json.dumps(AUTHOR,ensure_ascii=False)}
description={json.dumps(DESCRIPTION,ensure_ascii=False)}
'''
            platform = ('neoforge', '[' + '.'.join(game.split('.')[1:]) + ',)') if neo else ('forge', f'[{FORGE[game]},{FORGE[game]+1})')
            if not neo:data+='displayTest="IGNORE_SERVER_VERSION"\n'
            for mod,version in [platform,('minecraft',f'[{game}]'),('figura',f'[{base},{upper})')]:
                data+=f'''[[dependencies.t0ch1na_autocloud]]
modId="{mod}"
'''+('type="required"\n' if modern_neo else 'mandatory=true\n')+f'versionRange="{version}"\nordering="'+('AFTER' if mod=='figura' else 'NONE')+'"\nside="CLIENT"\n'
            if neo:data+='[[mixins]]\nconfig="t0ch1na-autocloud.mixins.json"\n'
            z.writestr(meta,data)
    outputs.append({**row,'addon_filename':path.name,'addon_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytecode':level})
    print('Built',game,loader,'Figura',base,'Java',level)
(ROOT/'build/all-build-manifest.json').write_text(json.dumps(outputs,indent=2,ensure_ascii=False)+'\n')
print('Total',len(outputs),'artifacts;',len(compiled),'compiled code profiles')
