import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'statewide-master.json'
D=json.load(open(P))
E=D['establishments']

def norm(s): return re.sub(r'[^a-z0-9]+','', (s or '').lower())
def h(allweek=None, **kw):
    out={}
    days=['mon','tue','wed','thu','fri','sat','sun']
    if allweek:
        for d in days: out[d]=[allweek]
    for k,v in kw.items(): out[k]=[v] if isinstance(v,str) else v
    return out
records=[
('Norridge','8321 W Lawrence','Norridge Game Cafe',h('08:00-02:00'),'norridge-game-cafe-llc'),
('Chicago Ridge','6410 W 107th','PK',h('08:00-02:00'),'pks-pantry'),
('Chicago Ridge','10602 Ridgeland','Randa',h(mon='10:00-02:00',tue='10:00-02:00',wed='10:00-02:00',thu='10:00-02:00',fri='10:00-03:00',sat='10:00-03:00',sun='10:00-02:00'),'randas-gaming-cafe-llc'),
('Worth','6606 W 111th','JD',h(mon='10:00-02:00',tue='10:00-02:00',wed='10:00-02:00',thu='10:00-02:00',fri='10:00-03:00',sat='10:00-03:00',sun='11:00-02:00'),'jds-cafe-llc'),
('North Chicago','3092 N Skokie','Shamrock Cafe',h(mon='05:00-00:00',tue='05:00-00:00',wed='05:00-00:00',thu='05:00-00:00',fri='05:00-00:00',sat='05:00-00:00',sun='06:00-00:00'),'shamrock-cafe'),
('Crystal Lake','1050 North Shore','MOE-B-DICKS',h(mon='14:00-01:00',tue='14:00-01:00',wed='14:00-01:00',thu='14:00-01:00',fri='14:00-02:00',sat='12:00-02:00',sun='12:00-01:00'),'moe-b-dicks'),
('Huntley','10520 Route 47','Bowl Hi Lanes',h(mon='16:00-01:00',tue='16:00-01:00',wed='09:00-01:00',thu='09:00-01:00',fri='12:00-02:00',sat='12:00-02:00',sun='09:00-01:00'),'bowl-hi-lanes'),
('Sullivan','13 WEST JEFFERSON','THE TOY BAR',h(mon='11:00-01:00',tue='11:00-01:00',wed='11:00-01:00',thu='11:00-01:00',fri='11:00-01:00',sat='11:00-01:00',sun='12:00-23:00'),'the-toy-bar'),
('Quincy','1801A Broadway','Tri-State Investors',h('00:00-00:00'),'tri-state-investors-group-llc-1801-broadway'),
('Decatur','918 West Eldorado','Jake',h(mon='06:30-01:00',tue='06:30-01:00',wed='06:30-01:00',thu='06:30-01:00',fri='06:30-01:00',sat='06:30-01:00',sun='10:00-01:00'),'jakes-video-gaming'),
('Carbondale','101 West Monroe','The Cellar',h(mon='15:00-02:00',tue='15:00-02:00',wed='15:00-02:00',thu='15:00-02:00',fri='13:00-02:00',sat='13:00-02:00',sun='13:00-02:00'),'the-cellar-carbondale'),
('Champaign','522 EAST GREEN','LEGENDS',h('11:00-02:00'),'legends'),
('Decatur','3611 E US Route 36','Debbie',h(mon='08:00-00:00',tue='08:00-00:00',wed='08:00-00:00',thu='08:00-00:00',fri='08:00-02:00',sat='08:00-02:00',sun='10:00-23:00'),'debbies-route-36'),
('Springfield','1919 West Iles','The Office Sports Bar',h('11:00-01:00'),'the-office-sports-bar-grill'),
('Mount Vernon','2401 Broadway','Geo',h(mon='10:00-02:00',tue='10:00-02:00',wed='10:00-02:00',thu='10:00-02:00',fri='10:00-02:00',sat='10:00-02:00',sun='10:00-00:00'),'geos-gas-station-lounge'),
('Springfield','600 Toronto','ROUTE 66 MOTORHEAD',h('08:00-00:00'),'route-66-motorhead-bar-grill-llc'),
('Springfield','3219 SOUTH 6TH','CURVE INN',h('11:00-03:00'),'curve-inn'),
('Decatur','1933 S. Taylorville','Rocco',h('12:00-02:00'),'roccos'),
('Decatur','3645 E US Route 36','Stix on 36',h(mon='11:00-01:00',tue='11:00-01:00',wed='11:00-01:00',thu='11:00-01:00',fri='11:00-02:00',sat='11:00-02:00',sun='11:00-01:00'),'stix-on-36'),
('Champaign','35 E. Green','Green Street Cafe',h('05:00-02:00'),'green-street-cafe'),
('Decatur','3745 N Woodford','Debbie',h(mon='07:00-23:00',tue='07:00-23:00',wed='07:00-23:00',thu='07:00-23:00',fri='07:00-23:00',sat='07:00-23:00',sun='10:00-23:00'),'debbies-woodford-2'),
('Rockford','4002 E State','On State',h('09:00-02:00'),'on-state'),
('Harrisburg','212 E. Sloan','JoJo',h(mon='09:00-00:00',tue='09:00-00:00',wed='09:00-00:00',thu='09:00-00:00',fri='09:00-01:00',sat='09:00-01:00',sun='12:00-19:00'),'jojos'),
('Marion','109 N Mechanic','Pookie',h(mon='11:00-00:00',tue='11:00-00:00',wed='11:00-00:00',thu='11:00-00:00',fri='11:00-01:00',sat='11:00-01:00',sun='12:00-22:00'),'pookies-inc'),
('Harrisburg','44 N Commercial','Mach 1',h('00:00-00:00'),'mach-1-harrisburg'),
('Rockford','1710 Rural','Rural on Tap',h('14:00-02:00'),'rural-on-tap'),
('Rockford','513 E State','The Office',h('12:00-02:00'),'the-office'),
('Effingham','18924 U.S. Hwy 45','The Midway',h(mon='11:00-01:00',tue='11:00-01:00',wed='11:00-01:00',thu='11:00-01:00',fri='11:00-01:00',sat='11:00-01:00',sun='11:00-22:00'),'the-midway'),
('Rockford','1428 N Main','GOAT',h('11:00-02:00'),'goat-pub-and-grill'),
('Effingham','1809 W Fayette','Chaser',h(mon='15:00-01:00',tue='15:00-01:00',wed='15:00-01:00',thu='15:00-01:00',fri='15:00-01:00',sat='12:00-01:00',sun='12:00-01:00'),'chasers-grill-and-bar'),
('Effingham','1701 W Evergreen','Pilot Travel Center #643',h('00:00-00:00'),'pilot-travel-center-643'),
('Bloomington','1607 Morrissey','Qik-N-EZ',h('00:00-00:00'),'qik-n-ez-62-morrissey-bloomington'),
('Danville','103 N Vermilion','Vermilion River Beer',h(mon='11:00-00:00',tue='11:00-00:00',wed='11:00-00:00',thu='11:00-00:00',fri='11:00-02:00',sat='11:00-02:00',sun='11:00-23:00'),'vermilion-river-beer-company'),
]
added=[]; skipped=[]
for city,addr,namefrag,hours,slug in records:
    cands=[x for x in E if norm(x.get('city'))==norm(city) and norm(addr) in norm(x.get('address'))]
    if len(cands)!=1:
        # fallback contains street number and name fragment in city
        num=re.match(r'\d+',addr.strip())
        cands=[x for x in E if norm(x.get('city'))==norm(city) and (not num or norm(x.get('address')).startswith(num.group())) and norm(namefrag)[:6] in norm(x.get('name'))]
    if len(cands)!=1:
        skipped.append((city,addr,namefrag,len(cands),[(x.get('license'),x.get('name'),x.get('address')) for x in cands[:5]])); continue
    x=cands[0]
    if x.get('hours'): skipped.append((city,addr,namefrag,'already',x.get('license'))); continue
    x['hours']=hours; x['hours_source']='official:jjgaming.com/location_page/'+slug; x['hours_verified']='2026-10-03'
    added.append((x['license'],x['name'],x['city'],x.get('county')))
meta=D.setdefault('metadata',{})
meta['verified_hours_enrichment']={
 'version':'13.5.11','verified_date':'2026-10-03',
 'policy':'Only first-party business/brand or current gaming-operator hours; ambiguous/conflicting hours excluded.',
 'sources':['jjgaming.com/location_page/*','playspinwinbrands.com/locations','suzisslots.com','playtracys.com/locations','previous verified sources'],
 'new_records_this_pass':len(added),
 'total_master_verified_hours':sum(1 for x in E if x.get('hours')),
 'counties_with_verified_hours':len({x.get('county') for x in E if x.get('hours') and x.get('county')})
}
json.dump(D,open(P,'w'),indent=2,ensure_ascii=False)
print('ADDED',len(added)); [print(a) for a in added]
print('SKIPPED',len(skipped)); [print(s) for s in skipped]
