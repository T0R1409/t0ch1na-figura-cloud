"""Lock the published Figura matrix and verify each selected binary's API."""
from pathlib import Path
import json,zipfile,hashlib,urllib.request,runpy,tomllib
ROOT=Path(__file__).resolve().parent

def main():
    with urllib.request.urlopen('https://api.modrinth.com/v2/project/figura/version') as r:versions=json.load(r)
    choices={}
    for a in versions:
        for game in a['game_versions']:
            for loader in a['loaders']:choices.setdefault((game,loader),a)
    # Current 0.1.6 listing marks 1.21.2, but Forge metadata requires 1.21.3.
    # The separately published previous build is the valid 1.21.2 choice.
    choices[('1.21.2','forge')]=next(a for a in versions if a['id']=='nwkT9d1J')
    helpers=runpy.run_path(str(ROOT/'tests/verify_figura_contract.py'))
    approved=[];blocked=[]
    for (game,loader),a in choices.items():
        f=next((f for f in a['files'] if f.get('primary')),a['files'][0]);p=ROOT/'deps/figura-all'/f['filename'];p.parent.mkdir(parents=True,exist_ok=True)
        if not p.exists():
            with urllib.request.urlopen(f['url'],timeout=90) as r:p.write_bytes(r.read())
        assert hashlib.sha512(p.read_bytes()).hexdigest()==f['hashes']['sha512']
        if (game,loader) in [('1.21','forge'),('1.21','neoforge'),('1.21.2','neoforge')]:
            blocked.append({'minecraft':game,'loader':loader,'reason':'Official Figura file metadata requires a newer Minecraft version than its Modrinth tag.'});continue
        prefix='fabric/' if loader=='quilt' else ''
        targets={k:list(v) for k,v in helpers['TARGETS'].items()}
        if game=='1.16.5':
            targets['backend2/HttpAPI']=[('header','(Ljava/lang/String;Ljava/lang/String;)Lorg/apache/http/client/methods/HttpRequestBase;')]
            targets['backend2/AuthHandler']=[('auth','(Z)V'),('request','(Lorg/apache/http/client/methods/HttpUriRequest;)Ljava/lang/String;')]
            targets['backend2/trust/KeyStoreHelper']=[('websocketWithBackendCertificates','(Ljava/lang/String;)L'+('org/figuramc/' if loader=='forge' else '')+'com/neovisionaries/ws/client/WebSocket;')]
        if loader=='quilt':
            del targets['backend2/trust/KeyStoreHelper']
            targets['backend2/websocket/WebsocketThingy']=[('<init>','(Ljava/lang/String;)V')]
        with zipfile.ZipFile(p) as z:
            for cls,wanted in targets.items():
                found=helpers['members'](z.read(prefix+'org/figuramc/figura/'+cls+'.class'))
                for name,desc in wanted:
                    if prefix:desc=desc.replace('Lorg/figuramc/figura/','Lfabric/org/figuramc/figura/')
                    assert (name,desc) in found,(game,loader,cls,name,desc)
        major=tuple(map(int,game.split('.')))
        java=8 if game=='1.16.5' else 21 if major>=(1,20,6) else 17
        approved.append({'minecraft':game,'loader':loader,'java':java,'figura':a['version_number'],'figura_id':a['id'],'figura_filename':f['filename'],'figura_url':f['url'],'figura_sha512':f['hashes']['sha512'],'namespace':'fabric.org.figuramc.figura' if prefix else 'org.figuramc.figura','profile':'legacy8' if java==8 else 'quilt' if prefix else 'modern'})
    # GitHub publishes two official 0.1.6 NeoForge builds absent from the
    # corresponding Modrinth version list. Verify those binaries as well.
    with urllib.request.urlopen('https://api.github.com/repos/FiguraMC/Figura/releases/tags/0.1.6') as response:
        release=json.load(response)
    for game in ['1.20.2','1.20.4']:
        name=f'figura-0.1.6+{game}-neoforge-mc.jar'
        asset=next(a for a in release['assets'] if a['name']==name)
        path=ROOT/'deps/figura-all'/name
        if not path.exists():
            with urllib.request.urlopen(asset['browser_download_url'],timeout=90) as response:path.write_bytes(response.read())
        if asset.get('digest'):assert 'sha256:'+hashlib.sha256(path.read_bytes()).hexdigest()==asset['digest']
        with zipfile.ZipFile(path) as archive:
            for cls,wanted in helpers['TARGETS'].items():
                found=helpers['members'](archive.read('org/figuramc/figura/'+cls+'.class'))
                assert all(t in found for t in wanted),(game,'neoforge',cls)
        row=next(r for r in approved if r['minecraft']==game and r['loader']=='neoforge')
        row.update(figura='0.1.6+'+game,figura_id='GitHub:0.1.6',figura_filename=name,
                   figura_url=asset['browser_download_url'],figura_sha512=hashlib.sha512(path.read_bytes()).hexdigest(),
                   figura_min='0.1.5',figura_upper='0.1.7')
    # Preserve the already distributed, explicitly experimental legacy port.
    original=next(x for x in approved if x['minecraft']=='1.20.1' and x['loader']=='forge')
    approved.append({**original,'loader':'neoforge','profile':'legacy-neoforge','experimental':True})
    approved.sort(key=lambda x:(tuple(map(int,x['minecraft'].split('.'))),x['loader']))
    result={'source':'https://api.modrinth.com/v2/project/figura/version','entries':approved,'blocked_pairs':blocked}
    (ROOT/'support-matrix.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print('Verified profiles:',len(approved),'Minecraft versions:',len({r['minecraft'] for r in approved}),'blocked misleading tags:',len(blocked))
if __name__=='__main__':main()
