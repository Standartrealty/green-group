# -*- coding: utf-8 -*-
from pathlib import Path
import json,re,html,hashlib,subprocess,concurrent.futures
from urllib.parse import urljoin,urlparse,quote,unquote,urlunparse
from html.parser import HTMLParser
from inspect_source import parse
R=Path(__file__).parent;S=R/'source-content';c=json.loads((S/'catalog.json').read_text())
def clean(u,base):
 p=urlparse(urljoin(base,html.unescape(u)));return urlunparse((p.scheme,p.netloc,quote(unquote(p.path),safe='/@:+'),p.params,p.query,''))
def fetch(u):return subprocess.check_output(['curl','-fLsS','--max-time','40',u],stderr=subprocess.DEVNULL)
raw=fetch('https://beldom.pro/');(S/'beldom.html').write_bytes(raw)
class Text(HTMLParser):
 def __init__(self):super().__init__();self.skip=0;self.out=[]
 def handle_starttag(self,t,a):
  if t in ('script','style'):self.skip+=1
 def handle_endtag(self,t):
  if t in ('script','style'):self.skip=max(0,self.skip-1)
 def handle_data(self,d):
  if not self.skip and d.strip():self.out.append(d.strip())
p=Text();p.feed(raw.decode());(S/'beldom.txt').write_text('\n\n'.join(p.out));c['pages'].append({'url':'https://beldom.pro/','local':'source-content/beldom.html','relation':'Official project website referenced by Green Group project 7'})
known={a['url'] for a in c['assets']};extra={}
for f in S.glob('*.html'):
 base='https://beldom.pro/' if f.name=='beldom.html' else 'https://green-groupp.ru/';root=parse(f);urls=[]
 for n in root.nodes():
  for key in ('src','data-original','data-src','data-lazy-src','poster','href'):
   u=n.a.get(key,'')
   if u and not u.startswith('data:') and urlparse(u).path.lower().endswith(('.jpg','.jpeg','.png','.svg','.webp','.pdf','.mp4','.webm')):urls.append(clean(u,base))
 text=f.read_text()
 for u in re.findall(r'url\([\x22\x27]?([^\x22\x27)]+)',text):
  if not u.startswith('data:'):urls.append(clean(u,base))
 for u in re.findall(r'https://[^\s\x22\x27<>\\]+\.(?:jpg|jpeg|png|svg|webp|pdf|mp4|webm)',html.unescape(text)):urls.append(clean(u,base))
 for u in urls:
  if u not in known:extra.setdefault(u,[]).append(base if f.name=='beldom.html' else f.name)
def save(item):
 u,src=item;ext=Path(urlparse(u).path).suffix.lower()
 if ext not in ('.jpg','.jpeg','.png','.svg','.webp','.pdf','.mp4','.webm'):return None
 p=S/'assets'/(hashlib.sha256(u.encode()).hexdigest()[:18]+ext)
 try:
  p.write_bytes(fetch(u));return {'url':u,'local':str(p.relative_to(R)),'sources':sorted(set(src)),'bytes':p.stat().st_size}
 except Exception as e:return {'url':u,'sources':src,'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
 out=[x for x in pool.map(save,extra.items()) if x];c['assets']+=out
(S/'catalog.json').write_text(json.dumps(c,ensure_ascii=False,indent=2));print('Added',len(out),'saved',sum('local'in x for x in out),'Total',sum('local'in x for x in c['assets']))
