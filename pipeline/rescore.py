"""v2 scoring: seniority counts on its own, India-based contacts are de-prioritised, cadence capped at 30 days."""
import pandas as pd, re, math, json
try:
    from notes import N   # optional, private: hand-written context per person (see notes.example.py)
except ImportError:
    N = {}
TODAY=pd.Timestamp.today().normalize()
d=pd.read_pickle('scored.pkl'); e=pd.read_pickle('edges.pkl')
for c in ['note','action','draft']:
    if c not in d: d[c]=''
for c in ['company','position','url','connected','last','last_dir']: d[c]=d[c].fillna('')
def has(p,s): return bool(re.search(p,s or '',re.I))
TOP=r"google|deepmind|\bmeta\b|microsoft|amazon|\baws\b|apple|nvidia|openai|anthropic|datadog|bloomberg|netflix|uber|airbnb|stripe|databricks|snowflake|salesforce|adobe|linkedin|\bramp\b|capital one|goldman|jpmorgan|j\.p\. morgan|morgan stanley|blackrock|two sigma|citadel|jane street|hudson river|d\. ?e\. ?shaw|point72|spotify|doordash|scale ai|cohere|perplexity|mistral|hugging ?face|tiktok|bytedance|intuit|palantir|mongodb|american express|bank of america|\bibm\b|servicenow|regeneron|\bamd\b|qualcomm|tesla|oracle|cisco|roblox|klaviyo|figma|notion|pinterest|snap\b|reddit|dropbox|atlassian|cloudflare|coinbase|robinhood|plaid|duolingo|xai|waymo|cruise|rivian|spacex|samsung|intel\b|broadcom|micron|visa\b|mastercard|paypal|block\b|wells fargo|\bciti\b|citigroup|barclays|\bubs\b|deutsche|fidelity|vanguard|millennium|bridgewater|jump trading|\bdrw\b|optiver|\bimc\b|susquehanna|akuna"
GOOD=r"walmart|expedia|zoom|twilio|okta|elastic|confluent|palo alto|crowdstrike|arista|seagate|pure storage|mathworks|pfizer|johnson & johnson|merck|novartis|genentech|roche|verizon|at&t|caterpillar|honeywell|ericsson|siemens|bosch|chubb|optum|unitedhealth|\bion\b|standard chartered|hsbc|nomura|state street|s&p|moody|\bey\b|\bzs\b|bain|\bbcg\b|mckinsey|deloitte|pwc|kpmg|accenture|gartner|\bsap\b|vmware|workday|autodesk|nutanix|ebay|lyft|instacart|yelp|zillow|wayfair|hubspot|shopify|square|toast|chime|sofi|affirm|brex|gusto|rippling|asana|airtable|canva|grammarly|glean|harvey|cursor|replit|vercel|supabase|pinecone|weaviate|langchain|together|fireworks|runway|character|adept|inflection|stability|midjourney|eleven ?labs|deepgram|assembly"
SVC=r"tata consultancy|\btcs\b|cognizant|wipro|infosys|capgemini|\bhcl|ltimindtree|\bltm\b|\blti\b|tech mahindra|mphasis|virtusa|hexaware|persistent|mindtree"
AGENCY=r"staffing|\bhires\b|recruitment|talent solutions|bench|recruitfox|lead generat|consultancy|it solution|hidani|rediantt|icosys|divine talent|aethrix|vision xperts|grp solutions|akhilam|3engineers|infotech|technologies inc|solutions inc|placement agency|\bh1b\b|\bopt\b|c2c|w2\b|us it recruit"
# --- India inference (the export has no location field, so this is a best guess the app lets you correct)
IN_STRONG=r"\bindia\b|bengaluru|bangalore|hyderabad|chennai|\bpune\b|mumbai|delhi|gurgaon|gurugram|noida|vellore|kolkata|\bvit\b|vellore institute|\biit\b|\bnit\b|\biiit\b|\bbits\b|\bsrm\b|manipal|amrita|anna university|"+SVC+r"|zoho|flipkart|swiggy|zomato|paytm|phonepe|razorpay|reliance|\bjio\b|\btata\b|mahindra|bajaj|hdfc|icici|kotak|axis bank|\bsbi\b|\bola\b|byju|unacademy|\bnavi\b|\bcred\b|meesho|myntra|freshworks|kpit|larsen|l&t|radico|atsuya|broadridge india|tcg digital|4i apps|suryaa|soft computing research|entrepreneurship cell|gdsc|google developer student|csi\b|ieee.*vit|drdo|isro|bharat|hindustan|adani|airtel|infoedge|naukri|makemytrip|oyo\b|dream11|sharechat|zerodha|groww|upstox|juspay|postman india|thoughtworks india|\bpvt\b|private limited|\bltd\b|limited\b"
US_EVID=r"columbia|regeneron|new york|\bnyc\b|\bnyu\b|stony brook|northeastern|carnegie|\bcmu\b|stanford|berkeley|\bmit\b|harvard|princeton|cornell|\bupenn\b|georgia tech|\busc\b|\bucla\b|\bucsd\b|purdue|\buiuc\b|arizona state|\basu\b|rutgers|\bsuny\b|\bcuny\b|university of (texas|michigan|washington|maryland|illinois|california|southern|pennsylvania|chicago|wisconsin|minnesota|florida|virginia|north carolina)|texas a&m|\bllc\b|\binc\.?\b|usa|united states|\bu\.s\.|london|toronto|canada|singapore|germany|berlin|dubai|\buk\b|europe|amsterdam|dublin|sydney|australia"
msgtext=e.groupby('url')['content'].apply(lambda s:' '.join(str(x) for x in s)).to_dict()
US_MSG=r"\bnyc\b|new york|columbia|manhattan|\bbay area\b|seattle|san francisco|\bsf\b|boston|jersey|morningside|butler|\bpdl\b|reached nyc|in the us\b"
rows=[]
for i,r in d.iterrows():
    co,pos=r.company,r.position; both=co+' '+pos
    s=0; why=[]
    tier='A' if has(TOP,co) else 'B' if has(GOOD,co) else 'C' if has(SVC,co) else 'D'
    s+= {'A':22,'B':14,'C':2,'D':7}[tier]
    if tier=='A': why.append(f'{co} is a top target employer')
    elif tier=='B': why.append(f'{co} is a relevant employer')
    agency=has(AGENCY,both)
    student=has(r'high school|honor society|student builder|\bclub\b|\bchapter\b|stuypulse|robotics team',both) or has(r'\bintern\b|internship|student|undergraduate|trainee|teaching assistant|course assistant|graduate research|research assistant|ambassador|vlogger|fellow\b|co-?op\b|apprentice|incoming|summer analyst|volunteer|\bmember\b(?! of technical)',pos)
    exec_=has(r'\b(ceo|cto|cio|coo|cpo|chief|president|svp|evp|managing director|general manager|\bgm\b|partner|head of|head,|\bhead\b|vice president|\bvp\b|avp)\b',pos)
    director=has(r'\bdirector\b|distinguished|\bfellow engineer|principal|\bstaff\b|senior staff|sr\.? staff|architect',pos)
    manager=has(r'engineering manager|manager,? (of )?(software|engineering|data|ml|ai|machine)|(software|data|ml|ai|machine learning|product|program|technical|research|science|analytics|platform|cloud) .*manager|\bmanager\b|team lead|tech lead|\blead\b|member of technical staff|\bmts\b',pos)
    senior=has(r'\bsenior\b|\bsr\.?\b|\bii\b|\biii\b|\biv\b|\b[23]\b|sde[- ]?[23]|l[5-7]\b',pos)
    recruiter=has(r'recruit|talent|university relations|campus (recruit|program)|sourcer|hiring|people partner|early career',pos)
    founder=has(r'founder|owner',pos)
    tech=has(r'engineer|scientist|developer|\bsde\b|\bswe\b|research|architect|\bml\b|\bai\b|data|software|technical|technology|product|quant|machine learning|analytics|platform|cloud|infra',pos)
    nontech=has(r'marketing|clinical|manufactur|finance business|\bsales\b|formulation|cell therapy|accounting|\bhr\b|human resources|legal|matchmaking|real estate|insurance agent|wealth|nurs|pharmac(y|ist)|supply chain|procurement|operations manager|customer (success|solution)',pos)
    cat='Peer'
    if agency: cat='Agency recruiter'; s-=18; why.append('third-party staffing')
    elif student and not (founder and not has(r'intern',pos)): cat='Student / early'; s+=3
    elif recruiter: cat='Recruiter'; s+= 30 if tier=='A' else 24 if tier=='B' else 12; why.append('in-house recruiter')
    elif has(r'career|placement|industry relations',pos) and has(r'columbia',co): cat='Career services'; s+=24; why.append('Columbia career services')
    elif exec_: cat='Senior / hiring manager'; s+= 40 if tech or tier in 'AB' else 28; why.append('executive level: can open doors or hire')
    elif director: cat='Senior / hiring manager'; s+= 36 if tech or tier in 'AB' else 24; why.append('director / principal / staff level')
    elif founder: cat='Founder'; s+=24; why.append('founder: direct hiring decision')
    elif manager: cat='Senior / hiring manager'; s+= 28 if tech else 18; why.append('manager or lead: likely interviews and refers')
    elif has(r'engineer|scientist|developer|\bsde\b|\bswe\b|researcher|analyst|quant|consultant|specialist|programmer',pos): cat='Engineer'; s+= 18 if senior else 12
    if has(r'\bai\b|\bml\b|machine learning|\bllm|genai|gen ai|generative|\bnlp\b|deep learning|applied scien|research scien|data scien|agent',pos) and cat not in('Agency recruiter',): s+=8; why.append('AI/ML role')
    if nontech and cat not in ('Recruiter','Career services') and not exec_: s-=10
    if has(r'regeneron',co): s+=3; why.append('Regeneron (your internship)')
    if has(r'columbia',co) and cat!='Student / early': s+=4
    ni,no=r.n_in,r.n_out
    if ni>0 and no>0: s+=min(18, 6+7*math.log1p(min(ni,no))); why.append(f'two-way thread ({no+ni} msgs)')
    elif ni>0: s+=4; why.append('they wrote to you')
    elif no>0: s+=1
    # India inference
    u=r.url.strip().rstrip('/').lower(); mt=msgtext.get(u,'')
    yr=int(r.connected[:4]) if r.connected else 2026
    us = has(US_EVID,both) or has(US_MSG,mt)
    india=False; inwhy=''
    if has(US_MSG,mt): pass
    elif has(IN_STRONG,both) and not has(r'columbia|regeneron',co): india=True; inwhy='employer or title points to India'
    elif yr<=2024 and not us: india=True; inwhy=f'connected in {yr}, while you were based in India, and nothing points outside India'
    rows.append((max(0,min(100,round(s))),cat,tier,why,india,inwhy))
d[['score','cat','tier','why','india','inwhy']]=pd.DataFrame(rows,index=d.index)
# curated overrides from reading threads
d['open_loop']=False
for i,r in d.iterrows():
    if r['name'] in N:
        p,a,dr,sc=N[r['name']]; d.at[i,'note']=p; d.at[i,'action']=a; d.at[i,'draft']=re.sub(r'\n*\s*(Best,\s*)?\n?Tanmay\s*$','',dr).strip(); d.at[i,'score']=max(sc, r.score) if sc>10 else sc; d.at[i,'india']=False
# v3 tracking rule: everyone is tracked unless there is a concrete reason not to.
#   set aside  = employer/title points to India, staffing agencies, rows LinkedIn exported with no name
#   unverified = connected in 2024 or earlier with no location evidence: tracked only from score 30 up
d['named']=~d['name'].str.contains(r'^\s*(nan)?\s*(nan)?\s*$',case=False,regex=True)
d['strong']=d.india & d.inwhy.str.startswith('employer')
d['unver']=d.india & ~d.strong
d['india']=d.strong
d['tracked']=d.named & ~d.strong & (d['cat']!='Agency recruiter') & (~d.unver | (d.score>=30))
d['cadence']=d.score.map(lambda s: 7 if s>=70 else 30)
d.loc[~d.tracked,'cadence']=0
d['band']=d.score.map(lambda s:'Inner circle' if s>=70 else 'Strategic' if s>=55 else 'Warm' if s>=40 else 'Keep alive')
d=d.sort_values('score',ascending=False)
d.to_pickle('final2.pkl')
print('tracked',int(d.tracked.sum()),'| likely India',int(d.strong.sum()),'| location unverified',int(d.unver.sum()))
