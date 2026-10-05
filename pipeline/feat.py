import pandas as pd, re
ME='https://www.linkedin.com/in/YOUR-PROFILE-SLUG'  # your own LinkedIn URL
def norm(u):
    if not isinstance(u,str): return ''
    return u.strip().rstrip('/').lower().replace('http://','https://')
c=pd.read_csv('Connections.csv',skiprows=3)
c['url']=c['URL'].map(norm)
m=pd.read_csv('messages.csv')
m['date']=pd.to_datetime(m['DATE'].str.replace(' UTC',''))
m['s']=m['SENDER PROFILE URL'].map(norm)
rows=[]
for _,r in m.iterrows():
    rec=[norm(x) for x in str(r['RECIPIENT PROFILE URLS']).split(',')]
    if r['s']==norm(ME):
        for x in rec:
            if x and x!=norm(ME): rows.append((x,'out',r['date'],r['CONTENT'],r['CONVERSATION ID'],len(rec)))
    else:
        rows.append((r['s'],'in',r['date'],r['CONTENT'],r['CONVERSATION ID'],len(rec)))
e=pd.DataFrame(rows,columns=['url','dir','date','content','conv','nrec'])
e=e[e.nrec<=2]  # 1:1 only
print(len(e), e.url.nunique(), e.url.isin(c.url).mean())
g=e.groupby('url').agg(n_out=('dir',lambda s:(s=='out').sum()),n_in=('dir',lambda s:(s=='in').sum()),last=('date','max'),first=('date','min'))
print(g.describe())
print(((g.n_out>0)&(g.n_in>0)).sum(),'two-way')
e.to_pickle('edges.pkl'); g.to_pickle('g.pkl')
