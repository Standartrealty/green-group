# -*- coding: utf-8 -*-
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
import json,re,hashlib,shutil
from urllib.parse import urljoin
from inspect_source import parse
R=Path(__file__).parent;S=R/'source-content';A=R/'assets';c=json.loads((S/'catalog.json').read_text());lookup={x['url']:R/x['local'] for x in c['assets'] if 'local'in x};usage=[]
def save(u,name=None,width=1600):
 if u not in lookup:return None
 name=name or hashlib.sha256(u.encode()).hexdigest()[:14];src=lookup[u]
 if src.suffix=='.svg':dest=A/(name+'.svg');shutil.copy(src,dest)
 else:
  im=Image.open(src);im.thumbnail((width,width));dest=A/(name+'.webp');im.save(dest,'WEBP',quality=85)
 usage.append({'source':u,'local':'assets/'+dest.name});return '/assets/'+dest.name
def bodytext(name):return (S/(name+'.txt')).read_text().split('\n\nОтправить\n\n',1)[-1].rsplit('\n\nАдрес\n\n',1)[0]
def sim(im):
 im=im.convert('L').resize((9,8));v=list(im.getdata());return sum((v[y*9+x]>v[y*9+x+1])<<(y*8+x) for y in range(8) for x in range(8))
spec=[(3,'green-house','Green House','Клубный дом','Центр Каспийска','42 квартиры'),(6,'arkhidom','Архидом','Сдан в 2018','Каспийск','36 квартир'),(7,'bely-dom','Белый дом','Бизнес-класс','Каспийск, пр. Насрутдинова, 221','Клубная концепция'),(1,'makhachkalinskiy','Махачкалинский','Проект компании','Агломерация Махачкала–Каспийск','2 блока · 13 этажей'),(4,'chempion','Чемпион','Сдан в 2021','Район Анжи-Арены','327 квартир'),(5,'dom-na-lenina','Дом на Ленина','Сдан в 2018','Район Анжи-Арены','11 этажей'),(8,'tsentralny','Центральный','Сдан в 2019','Каспийск, ул. Приморская','142 квартиры')]
projects=[]
for num,slug,name,status,location,fact in spec:
 file='project.php_id_'+str(num);r=parse(S/(file+'.html'));raw=(S/(file+'.html')).read_text();urls=list(dict.fromkeys(urljoin('https://green-groupp.ru/',n.a['src']) for n in r.nodes() if n.tag=='img' and n.a.get('src','').startswith('images/content/')))
 selected=[];fingerprints=[]
 for u in urls:
  if u not in lookup:continue
  im=Image.open(lookup[u]);h=sim(im)
  near=next((i for i,v in enumerate(fingerprints) if (h^v).bit_count()<=4),None)
  if near is None:selected.append(u);fingerprints.append(h)
  elif im.width>Image.open(lookup[selected[near]]).width:selected[near]=u;fingerprints[near]=h
 gallery=[save(u) for u in selected]
 cover=re.search(r'background-image:\s*url\((images/projects/[^)]+)\)',raw);coverurl=urljoin('https://green-groupp.ru/',cover.group(1)) if cover else (selected[0] if selected else None);coverimg=save(coverurl,slug) or save(selected[0],slug)
 text=bodytext(file).split('\n\nPrevious')[0];videos=[urljoin('https://green-groupp.ru/',n.a['src']) for n in r.nodes() if n.tag=='iframe' and 'youtube' in n.a.get('src','')]
 projects.append({'id':slug,'sourceId':num,'name':name,'city':'Каспийск','kind':'Клубные дома' if num in (3,6,7) else 'Жилые комплексы','status':status,'location':location,'image':coverimg,'gallery':gallery,'description':text,'facts':[fact,'Бизнес-класс' if num==7 else ('Клубный формат' if num in (3,6) else 'Кирпично-монолитные дома'),'Коммерческие помещения','Сервис управляющей компании'],'plans':[],'documents':[],'videos':videos,'source':'https://green-groupp.ru/project.php?id='+str(num)})
plans=[];root=parse(S/'beldom.html');mapping=[('rec532211703','21,02','studio'),('rec530870300','23,6','studio'),('rec520574396','40,6','2'),('rec520575674','43,9','2'),('rec520577311','52,3','2'),('rec530852260','68','3'),('rec520581831','75','2'),('rec532293293','101','3')]
for idx,(rid,area,kind) in enumerate(mapping):
 n=next(n for n in root.nodes() if n.a.get('id')==rid);urls=[x.a.get('data-original',x.a.get('src','')) for x in n.nodes() if x.tag=='img'];u=urls[0];img=save(u,'plan-'+str(idx+1));plans.append({'id':'bely-dom-'+str(idx+1),'projectId':'bely-dom','project':'Белый дом','type':kind,'name':'Студия' if kind=='studio' else kind+'-комнатная','area':area,'image':img,'thumb':img,'source':'https://beldom.pro/#plan','imageSource':u,'sourceRecord':rid})
next(p for p in projects if p['id']=='bely-dom')['plans']=plans
(R/'data.json').write_text(json.dumps(projects,ensure_ascii=False));(R/'home-plans.json').write_text(json.dumps(plans,ensure_ascii=False));(R/'completed.json').write_text(json.dumps([{'id':p['id'],'name':p['name'],'image':p['image'],'city':'Каспийск · '+p['status'].lower(),'source':p['source']} for p in projects if p['status'].startswith('Сдан')],ensure_ascii=False))
save('https://green-groupp.ru/assets/images/-14x-122x61.png','logo',500);save('https://green-groupp.ru/images/slides/1771166873255.jpg','hero',2000);save('https://green-groupp.ru/images/slides/1732112744236.jpg','selection',1500)
news=[]
for num in (11,9,8,7,6,5):
 f='new.php_id_'+str(num);r=parse(S/(f+'.html'));title=next((' '.join(n.text().split()) for n in r.nodes() if n.tag=='h2'),None);title=title or next((' '.join(n.text().split()) for n in r.nodes() if n.tag=='title'),'').split('|')[0].strip();imgs=[urljoin('https://green-groupp.ru/',n.a.get('src','')) for n in r.nodes() if n.tag=='img' and n.a.get('src','').startswith('images/news')];image=save(imgs[0],'news-'+str(num),1100) if imgs else None;news.append({'id':str(num),'title':title,'date':'Архив компании','image':image,'source':'https://green-groupp.ru/new.php?id='+str(num),'text':bodytext(f)})
(R/'news.json').write_text(json.dumps(news,ensure_ascii=False));(R/'documents.json').write_text(json.dumps([{'name':p['name'],'source':p['source']} for p in projects],ensure_ascii=False))
library={'about':{'title':'О Green Group','text':bodytext('company.php')}}
for i in range(1,5):library['direction'+str(i)]={'title':['Green Group','Green Недвижимость','Green Apart','Green Park'][i-1],'text':bodytext('direction.php_id_'+str(i)).replace('hellooo','')}
for i in (5,6):library['vacancy'+str(i)]={'title':'Вакансия: '+('Менеджер' if i==5 else 'Инженер ПТО'),'text':bodytext('vacancy.php_id_'+str(i))}
(R/'library.json').write_text(json.dumps(library,ensure_ascii=False));(S/'usage-manifest.json').write_text(json.dumps(usage,ensure_ascii=False,indent=2))
sheet=Image.new('RGB',(1200,580),'white');d=ImageDraw.Draw(sheet)
for i,p in enumerate(projects):
 im=ImageOps.contain(Image.open(R/p['image'].lstrip('/')).convert('RGB'),(290,250));x=(i%4)*300;y=(i//4)*290;sheet.paste(im,(x,y));d.text((x+4,y+255),p['id'],fill='black')
sheet.save(R/'covers-review.jpg');print('Projects',len(projects),'Plans',len(plans),'Assets',len(list(A.iterdir())))
