"""Turn the scored table into the compact contacts.json the app embeds."""
import pandas as pd, json, re
try:
    from notes import N   # optional, private: hand-written context per person (see notes.example.py)
except ImportError:
    N = {}
d=pd.read_pickle('final2.pkl'); e=pd.read_pickle('edges.pkl')
junk={k for k,v in N.items() if v[3]<=10}
out=[]; ids=set()
def autonote(r):
    mo=lambda s: pd.Timestamp(s).strftime('%b %Y')
    if r['name'] in N: return r.note
    if r.n_in and r.n_out: return f"Two-way thread ({r.n_in+r.n_out} msgs), last {mo(r['last'])}" + (" (you spoke last)" if r.last_dir=='out' else " (they spoke last)")
    if r.n_out: return f"You messaged {mo(r['last'])}; no reply yet"
    if r.n_in: return f"They messaged you {mo(r['last'])}"
    return f"Connected {mo(r.connected)}; never messaged" if r.connected else "Never messaged"
for _,r in d.iterrows():
    if r['name'] in junk or not r.named: continue
    u=r.url.strip().rstrip('/'); slug=re.sub(r'[^A-Za-z0-9_\-.~:@+]','_',u.split('/in/')[-1])[:150] or 'x'
    while slug in ids: slug+='_'
    ids.add(slug); h=[]
    if u and (r.n_out+r.n_in)>0:
        ms=e[e.url==u.lower()].sort_values('date').tail(3)
        h=[[m.date.strftime('%Y-%m-%d'),m.dir,str(m.content).replace('\n',' ')[:220]] for _,m in ms.iterrows() if str(m.content)!='nan']
    o=dict(id=slug,n=r['name'],c=r.company,p=r.position,t=r['cat'],s=int(r.score),cd=int(r.cadence),l=r['last'],cn=r.connected,
        no=int(r.n_out),ni=int(r.n_in),note=autonote(r),act=r.action if r['name'] in N else '',dr=r.draft if r['name'] in N else '',u=r.url,h=h,tr=bool(r.tracked),why='; '.join(r.why[:3]))
    if r.india: o['ind']=1; o['iw']=r.inwhy
    elif r.unver: o['unv']=1
    out.append(o)
open('../data/contacts.json','w').write(json.dumps(out,ensure_ascii=False,separators=(',',':')))
print(len(out),'contacts;',sum(o['tr'] for o in out),'tracked;',sum('ind' in o for o in out),'likely India;',sum('unv' in o for o in out),'location unverified')
