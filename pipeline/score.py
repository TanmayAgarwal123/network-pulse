import pandas as pd, numpy as np, re, json, math
TODAY=pd.Timestamp.today().normalize()
c=pd.read_csv('Connections.csv',skiprows=3)
c['url']=c['URL'].fillna('').str.strip().str.rstrip('/').str.lower()
c['connected']=pd.to_datetime(c['Connected On'],format='%d %b %Y',errors='coerce')
g=pd.read_pickle('g.pkl').reset_index()
e=pd.read_pickle('edges.pkl')
last_dir=e.sort_values('date').groupby('url').tail(1).set_index('url')['dir']
x=c.merge(g,on='url',how='left')
x[['n_out','n_in']]=x[['n_out','n_in']].fillna(0).astype(int)
x['last_dir']=x.url.map(last_dir)
T1=r"google|deepmind|meta\b|facebook|microsoft|amazon|aws|apple|nvidia|openai|anthropic|datadog|bloomberg|netflix|uber|airbnb|stripe|databricks|snowflake|salesforce|adobe|linkedin|ramp|capital one|goldman|jpmorgan|j\.p\. morgan|morgan stanley|blackrock|two sigma|citadel|jane street|hudson river|d\. ?e\. shaw|point72|spotify|doordash|scale ai|cohere|perplexity|mistral|hugging ?face|tiktok|bytedance|intuit|oracle|qualcomm|\bamd\b|intel\b|cisco|pinterest|figma|notion|palantir|mongodb|american express|bank of america|wells fargo|\bciti\b|bny|fidelity|mastercard|visa\b|paypal|block\b|square|ibm|servicenow|workday|nvidia|tesla|samsung|shopify|coinbase|robinhood|plaid|duolingo|etsy|squarespace|jump trading|millennium|bridgewater|vanguard|schwab|morningstar|walmart|expedia|dropbox|atlassian|zoom|twilio|okta|cloudflare|elastic|confluent|palo alto|crowdstrike|arista|broadcom|micron|seagate|pure storage|mathworks|bytedance|regeneron|pfizer|jnj|johnson & johnson|merck|novartis|genentech|roche|hbo|nyt|new york times|verizon|at&t|ups|caterpillar|honeywell|ericsson|siemens|bosch|chubb|optum|unitedhealth|\bion\b|standard chartered|ubs|hsbc|barclays|deutsche|nomura|state street|s&p|moody|\bey\b|zs\b|bain|bcg|mckinsey|deloitte|pwc|kpmg|accenture"
BIGAI=r"google|deepmind|meta\b|microsoft|amazon|aws|apple|nvidia|openai|anthropic|datadog|bloomberg|netflix|uber|stripe|databricks|snowflake|salesforce|adobe|linkedin|ramp|capital one|goldman|jpmorgan|morgan stanley|blackrock|two sigma|citadel|jane street|hudson river|shaw|point72|spotify|doordash|scale ai|cohere|perplexity|hugging|tiktok|bytedance|intuit|palantir|mongodb|american express|bank of america|ibm|servicenow|regeneron"
SVC=r"tata consultancy|tcs\b|cognizant|wipro|infosys|capgemini|hcl|ltm|lti|tech mahindra|mphasis|accenture in india"
AGENCY=r"staffing|bench|recruitfox|lead generat|consultancy|it solution|hidani|rediantt|icosys|divine talent|aethrix|vision xperts|grp solutions|akhilam|3engineers|infotech|technologies inc|solutions inc|placement agency|h1b|opt\b"
def has(p,s): return bool(re.search(p,s or '',re.I))
rows=[]
for _,r in x.iterrows():
    co=str(r.Company) if pd.notna(r.Company) else ''
    pos=str(r.Position) if pd.notna(r.Position) else ''
    both=co+' '+pos
    s=0; why=[]; cat='Peer'
    agency = has(AGENCY,both) or (has(r'recruit|talent|sales',pos) and not has(T1,co) and has(r'bench|staffing|c2c|w2|sales recruiter|us it',both))
    tier = 'A' if has(BIGAI,co) else ('B' if has(T1,co) else ('C' if has(SVC,co) else 'D'))
    if tier=='A': s+=22; why.append(f'works at {co}, a target employer')
    elif tier=='B': s+=12; why.append(f'{co} is a relevant employer')
    elif tier=='C': s+=2
    else: s+=7
    if agency:
        cat='Agency recruiter'; s-=15; why.append('third-party staffing — low leverage')
    elif has(r'ambassador|vlogger',pos):
        cat='Student / early'; s+=2
    elif has(r'recruit|talent|university relations|campus|sourcer|hiring',pos):
        cat='Recruiter'; s+= 22 if tier in 'AB' else 8; why.append('in-house recruiter')
    elif has(r'career|placement|industry relations',pos) and has(r'columbia',co):
        cat='Career services'; s+=14; why.append('Columbia career services')
    elif has(r'\b(vp|vice president|director|head|chief|cto|cio|principal|staff|engineering manager|manager, engineering|manager|lead|partner)\b',pos) and not has(r'product intern|student',pos):
        cat='Senior / hiring manager'; s+=20; why.append('senior — can refer or hire')
    elif has(r'founder|ceo|owner',pos):
        cat='Founder'; s+=14; why.append('founder — startup door')
    elif has(r'intern|student|undergraduate|trainee|teaching assistant|graduate research|ambassador|member\b',pos):
        cat='Student / early'; s+=3
    elif has(r'engineer|scientist|developer|sde|researcher|architect|analyst|quant',pos):
        cat='Engineer'; s+= 14 if has(r'senior|sr\.?|ii|iii|2|3',pos) else 10
    if has(r'\bai\b|ml\b|machine learning|llm|genai|generative|nlp|deep learning|applied scientist|research scientist|data scien',pos) and cat!='Agency recruiter':
        s+=8; why.append('AI/ML role — close to your target')
    if has(r'regeneron',co): s+=2; why.append('Regeneron (your internship)')
    if has(r'marketing|clinical|manufacturing|finance business|sales|formulation|cell therapy|accounting|hr\b|human resources',pos) and cat!='Recruiter':
        s-=10
    if has(r'columbia',co): s+=4; why.append('Columbia network')
    # warmth
    ni,no=r.n_in,r.n_out
    if ni>0 and no>0:
        w=min(25, 8+10*math.log1p(min(ni,no))); s+=w; why.append(f'real two-way thread ({no+ni} msgs)')
    elif no>0: s+=2; why.append('you reached out, no reply yet')
    elif ni>0: s+=3
    last=r['last'] if pd.notna(r['last']) else None
    if last is not None:
        days=(TODAY-last).days
        if days<120: s+=4
    s=max(0,min(100,round(s)))
    rows.append(dict(name=f"{r['First Name'] or ''} {r['Last Name'] or ''}".strip(),first=r['First Name'],company=co,position=pos,url=r.URL,email=r['Email Address'] if pd.notna(r['Email Address']) else '',
        connected=r.connected.strftime('%Y-%m-%d') if pd.notna(r.connected) else '',n_out=int(no),n_in=int(ni),
        last=last.strftime('%Y-%m-%d') if last is not None else '',last_dir=r.last_dir if isinstance(r.last_dir,str) else '',
        score=s,cat=cat,tier=tier,why=why))
d=pd.DataFrame(rows)
def cadence(s):
    return ('Inner circle',30) if s>=70 else ('Strategic',45) if s>=55 else ('Warm',90) if s>=40 else ('Keep alive',180) if s>=28 else ('Dormant',0)
d[['band','cadence']]=d.score.apply(lambda s: pd.Series(cadence(s)))
def due(r):
    if r.cadence==0: return ''
    base=r['last'] or None
    if not base: return TODAY.strftime('%Y-%m-%d')  # never messaged: first touch now
    dd=pd.Timestamp(base)+pd.Timedelta(days=int(r.cadence))
    return dd.strftime('%Y-%m-%d')
d['due']=d.apply(due,axis=1)
d=d.sort_values('score',ascending=False)
d.to_pickle('scored.pkl')
print(d.band.value_counts()); print(d.cat.value_counts())
pd.set_option('display.width',250);pd.set_option('display.max_colwidth',38)
print(d[['name','company','position','cat','score','n_out','n_in','last','due']].head(70).to_string())
