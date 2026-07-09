import requests

urls = {
    "hurtos_general": "https://www.datos.gov.co/resource/9vvd-xrtg.json",
    "hurto_automotores": "https://www.datos.gov.co/resource/9vvd-xrtg.json",
    "delitos_sexuales": "https://www.datos.gov.co/resource/vuv4-n4wr.json",
    "violencia_intrafamiliar": "https://www.datos.gov.co/resource/ugsb-76vy.json",
    "homicidios": "https://www.datos.gov.co/resource/5skq-pf5n.json",
    "extorsion": "https://www.datos.gov.co/resource/5aw6-s9bn.json",
}

for name, url in urls.items():
    try:
        r = requests.get(url + "?$limit=1", timeout=5)
        print(f"{name}: {r.status_code}")
        if r.status_code == 200:
            d = r.json()
            if d:
                print("  Keys:", list(d[0].keys())[:10])
    except Exception as e:
        print(f"{name}: ERROR {e}")
