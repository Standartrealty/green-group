# -*- coding: utf-8 -*-
from pathlib import Path
from PIL import Image
from urllib.parse import urljoin
import json,re
R=Path(__file__).parent;S=R/'source-content';c=json.loads((S/'catalog.json').read_text());lookup={x['url']:R/x['local'] for x in c['assets'] if 'local'in x};usage=json.loads((S/'usage-manifest.json').read_text())
def save(u,name,w=1600):
 im=Image.open(lookup[u]);im.thumbnail((w,w));im.save(R/'assets'/(name+'.webp'),'WEBP',quality=85);usage.append({'source':u,'local':'assets/'+name+'.webp'});return '/assets/'+name+'.webp'
save('https://green-groupp.ru/images/content/1758112079757.jpg','green-house');save('https://green-groupp.ru/images/content/1758101858800.jpg','arkhidom')
p=R/'index.html';s=p.read_text().replace('Жилые проекты группы компаний «Союз»','Жилые проекты Green Group');p.write_text(s)
p=R/'news.json';news=json.loads(p.read_text());out=[]
for n in news:
 if n['title'].strip().lower()=='ww':continue
 raw=(S/('new.php_id_'+n['id']+'.html')).read_text();m=re.search(r'background-image:\s*url\((images/news/[^)]+)\)',raw)
 if m and urljoin('https://green-groupp.ru/',m.group(1)) in lookup:n['image']=save(urljoin('https://green-groupp.ru/',m.group(1)),'news-'+n['id'],1200)
 out.append(n)
p.write_text(json.dumps(out,ensure_ascii=False))
p=R/'library.json';lib=json.loads(p.read_text())
for k,v in lib.items():v['text']=re.sub(r'hello+','',v['text'],flags=re.I).strip()
lib['vacancy5']['text']='Менеджер по работе с клиентами.\n\nВакансия опубликована на сайте компании. Требования, обязанности и условия уточните в Green Group.'
p.write_text(json.dumps(lib,ensure_ascii=False));(S/'usage-manifest.json').write_text(json.dumps(usage,ensure_ascii=False,indent=2))
(S/'reviews-verified.json').write_text(json.dumps({'source':'https://yandex.ru/maps/org/grin/229847317950/reviews/','checked':'2026-10-29','rating':4.1,'ratings':105,'reviews':42,'matched':['green-groupp.ru','+7 (988) 293-10-70','Санаторий Дагестан'],'quotes':[{'name':'Марина Свистунова','date':'30 мая 2024','text':'Отличное местоположение, удачные планировки и развитая придомовая территория.'},{'name':'Алекс Иванин','date':'16 июля 2024','text':'Ответственная компания, предоставляют полную информацию по проекту, готовящейся инфрастуктуре, условиям покупки.'}],'notes':'В полной ленте есть оценки разных уровней, включая критические отзывы о сроках. Сайт показывает избранные выдержки и ссылку на всю ленту. Подтверждённая карточка 2ГИС с отзывами не найдена.'},ensure_ascii=False,indent=2))
print('NEWS',len(out),'ASSETS',len(list((R/'assets').iterdir())))
