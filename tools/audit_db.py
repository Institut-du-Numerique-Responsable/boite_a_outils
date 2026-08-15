import json, concurrent.futures as cf, urllib.request, urllib.error, ssl, socket

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

def check(url):
    for method in ("HEAD","GET"):
        try:
            req=urllib.request.Request(url, method=method, headers={"User-Agent":UA,"Accept":"*/*"})
            with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
                return r.status, r.geturl()
        except urllib.error.HTTPError as e:
            if method=="HEAD" and e.code in (403,405,400,501): continue
            return e.code, url
        except urllib.error.URLError as e:
            return f"ERR:{type(e.reason).__name__}", url
        except socket.timeout: return "ERR:timeout", url
        except Exception as e: return f"ERR:{type(e).__name__}", url
    return "ERR:unknown", url

# reuse previous audit as cache
cache={}
try:
    for x in json.load(open("link_audit.json")):
        cache[x["url"]]=(x["status"], x["final"])
except Exception: pass

d=json.load(open("db_dump.json"))
items=[]
for lang,tbl,cats in (("fr","tools_ifs_outils","tools_ifs_categorie"),("en","tools_ifs_en_outils","tools_ifs_en_categorie")):
    catmap={c["id"]:c["nom_cat"] for c in d[cats]}
    for o in d[tbl]:
        items.append({"lang":lang,"id":o["id"],"nom":o["nom"],"cat":catmap.get(o["id_cat"],"?"),"url":(o["lien"] or "").strip()})

todo=[it for it in items if it["url"] and it["url"] not in cache]
print(f"{len(items)} liens, {len(cache)} en cache, {len(todo)} a tester", flush=True)

def work(it):
    st,fin=check(it["url"]); it["status"]=st; it["final"]=fin; return it

with cf.ThreadPoolExecutor(max_workers=16) as ex:
    for n,_ in enumerate(ex.map(work, todo),1):
        if n%40==0: print(f"  {n}/{len(todo)}", flush=True)

for it in items:
    if "status" not in it:
        if it["url"] in cache: it["status"],it["final"]=cache[it["url"]]
        else: it["status"],it["final"]="ERR:empty",""
json.dump(items, open("db_link_audit.json","w"), ensure_ascii=False, indent=1)
bad=[i for i in items if i["status"]!=200]
print(f"DONE ok={len(items)-len(bad)} pb={len(bad)}")
