"""Client-only Java 17/21 builds; no Minecraft source or mappings needed."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parent
DEPS = ROOT / 'deps'
DEPS.mkdir(exist_ok=True)
URLS = {
    'ecj.jar': 'https://repo.maven.apache.org/maven2/org/eclipse/jdt/ecj/3.40.0/ecj-3.40.0.jar',
    'gson.jar': 'https://repo.maven.apache.org/maven2/com/google/code/gson/gson/2.10.1/gson-2.10.1.jar',
    'fabric-loader.jar': 'https://maven.fabricmc.net/net/fabricmc/fabric-loader/0.16.14/fabric-loader-0.16.14.jar',
    'mixin.jar': 'https://maven.fabricmc.net/net/fabricmc/sponge-mixin/0.15.5+mixin.0.8.7/sponge-mixin-0.15.5+mixin.0.8.7.jar',
    'forge-47.jar': 'https://maven.minecraftforge.net/net/minecraftforge/javafmllanguage/1.20.1-47.1.43/javafmllanguage-1.20.1-47.1.43.jar',
    'neoforge-loader.jar': 'https://maven.neoforged.net/releases/net/neoforged/fancymodloader/loader/4.0.42/loader-4.0.42.jar',
    'neoforge-legacy-language.jar': 'https://maven.neoforged.net/releases/net/neoforged/fancymodloader/language-java/47.2.2/language-java-47.2.2.jar',
    'forge-52.jar': 'https://maven.minecraftforge.net/net/minecraftforge/javafmllanguage/1.21.1-52.0.28/javafmllanguage-1.21.1-52.0.28.jar',
}
for name, url in URLS.items():
    if not (DEPS / name).exists():
        with urllib.request.urlopen(url, timeout=90) as r:
            (DEPS / name).write_bytes(r.read())

VERSION = '1.0.0-beta.2'
DIST = ROOT / 'dist'
DIST.mkdir(exist_ok=True)
MIXINS = {
    'required': True, 'minVersion': '0.8', 'package': 'dev.t0ch1na.autocloud.mixin',
    'compatibilityLevel': 'JAVA_17',
    'client': ['NetworkMixin', 'HttpMixin', 'AuthMixin', 'SocketMixin'],
    'injectors': {'defaultRequire': 1},
}
common = list((ROOT/'src/main/java').rglob('*.java'))
for game, forge_version, java_version in [('1.20.1', '47', 17), ('1.21.1', '52', 21)]:
    for loader in ['fabric', 'forge', 'neoforge']:
        classes = ROOT / 'build' / f'{game}-{loader}'
        classes.mkdir(parents=True, exist_ok=True)
        neo_current = loader == 'neoforge' and game == '1.21.1'
        source_loader = 'forge' if loader == 'neoforge' and game == '1.20.1' else loader
        loader_dep = ('neoforge-loader.jar' if neo_current else 'neoforge-legacy-language.jar') if loader == 'neoforge' else ('fabric-loader.jar' if loader == 'fabric' else f'forge-{forge_version}.jar')
        cp = os.pathsep.join(str(DEPS/n) for n in ['gson.jar', 'mixin.jar', loader_dep])
        sources = common + list((ROOT/f'src/{source_loader}/java').rglob('*.java'))
        subprocess.run(['java', '-jar', str(DEPS/'ecj.jar'), '-21' if neo_current else '-17', '-proc:none', '-encoding', 'UTF-8',
                        '-cp', cp, '-d', str(classes)] + [str(s) for s in sources], check=True)
        name = f't0ch1na-autocloud-{VERSION}-{game}-{loader}.jar'
        with zipfile.ZipFile(DIST/name, 'w', zipfile.ZIP_DEFLATED) as z:
            for p in sorted(classes.rglob('*.class')):
                z.write(p, p.relative_to(classes).as_posix())
            mixins = dict(MIXINS)
            if neo_current: mixins['compatibilityLevel'] = 'JAVA_21'
            z.writestr('t0ch1na-autocloud.mixins.json', json.dumps(mixins))
            z.writestr('META-INF/MANIFEST.MF', 'Manifest-Version: 1.0\nMixinConfigs: t0ch1na-autocloud.mixins.json\n\n')
            z.write(ROOT/'LICENSE', 'LICENSE')
            if loader == 'fabric':
                z.writestr('fabric.mod.json', json.dumps({
                    'schemaVersion': 1, 'id': 't0ch1na_autocloud', 'version': VERSION,
                    'name': 'T0CH1NA Figura AutoCloud', 'environment': 'client',
                    'description': 'Automatic private Figura cloud discovery and official-cloud fallback.',
                    'authors': ['T0CH1NA'], 'license': 'MIT',
                    'entrypoints': {'client': ['dev.t0ch1na.autocloud.FabricEntrypoint']},
                    'mixins': ['t0ch1na-autocloud.mixins.json'],
                    'depends': {'fabricloader': '>=0.15.0', 'minecraft': game,
                                'java': f'>={java_version}', 'figura': '>=0.1.6 <0.1.7'},
                }, indent=2))
            elif neo_current:
                z.writestr('META-INF/neoforge.mods.toml', f'''modLoader="javafml"
loaderVersion="[4,)"
license="MIT"
[[mods]]
modId="t0ch1na_autocloud"
version="{VERSION}"
displayName="T0CH1NA Figura AutoCloud"
authors="T0CH1NA"
description="Automatic Figura cloud discovery and official-cloud fallback."
[[dependencies.t0ch1na_autocloud]]
modId="neoforge"
type="required"
versionRange="[21.1,)"
ordering="NONE"
side="CLIENT"
[[dependencies.t0ch1na_autocloud]]
modId="minecraft"
type="required"
versionRange="[1.21.1]"
ordering="NONE"
side="CLIENT"
[[dependencies.t0ch1na_autocloud]]
modId="figura"
type="required"
versionRange="[0.1.6,0.1.7)"
ordering="AFTER"
side="CLIENT"
[[mixins]]
config="t0ch1na-autocloud.mixins.json"
''')
            else:
                z.writestr('META-INF/mods.toml', f'''modLoader="javafml"
loaderVersion="[{forge_version},{int(forge_version)+1})"
license="MIT"
[[mods]]
modId="t0ch1na_autocloud"
version="{VERSION}"
displayName="T0CH1NA Figura AutoCloud"
authors="T0CH1NA"
displayTest="IGNORE_SERVER_VERSION"
description="Automatically discovers T0CH1NA cloud and falls back to official Figura cloud."
[[dependencies.t0ch1na_autocloud]]
modId="minecraft"
mandatory=true
versionRange="[{game}]"
ordering="NONE"
side="CLIENT"
[[dependencies.t0ch1na_autocloud]]
modId="figura"
mandatory=true
versionRange="[0.1.6,0.1.7)"
ordering="AFTER"
side="CLIENT"
''')
        print('Built:', name)
checksums = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in DIST.glob('*.jar')}
(DIST/'SHA256SUMS.txt').write_text(''.join(f'{digest}  {name}\n' for name,digest in sorted(checksums.items())))
