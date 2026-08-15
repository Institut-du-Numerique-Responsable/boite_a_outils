import json, concurrent.futures as cf, urllib.request, urllib.error, ssl, socket, time

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

def check(url):
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, method=method, headers={"User-Agent": UA, "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
                return r.status, r.geturl()
        except urllib.error.HTTPError as e:
            if method == "HEAD" and e.code in (403, 405, 400, 501):
                continue
            return e.code, url
        except urllib.error.URLError as e:
            return f"ERR:{type(e.reason).__name__}:{e.reason}", url
        except socket.timeout:
            return "ERR:timeout", url
        except Exception as e:
            return f"ERR:{type(e).__name__}", url
    return "ERR:unknown", url

data = json.load(open("outils_raw.json"))
items = [(i, d) for i, d in enumerate(data) if d.get("Lien")]
print(f"checking {len(items)} links", flush=True)

results = []
def work(t):
    i, d = t
    url = str(d["Lien"]).strip()
    st, final = check(url)
    return {"i": i, "nom": d.get("Nom de l'outil"), "cat": d.get("Catégorie"),
            "url": url, "status": st, "final": final}

with cf.ThreadPoolExecutor(max_workers=16) as ex:
    for n, r in enumerate(ex.map(work, items), 1):
        results.append(r)
        if n % 25 == 0:
            print(f"  {n}/{len(items)}", flush=True)

json.dump(results, open("link_audit.json", "w"), ensure_ascii=False, indent=1)
bad = [r for r in results if r["status"] != 200]
print(f"\nDONE. ok={len(results)-len(bad)}  problematiques={len(bad)}")
