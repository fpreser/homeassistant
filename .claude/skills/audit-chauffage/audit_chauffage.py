#!/usr/bin/env python3
"""Audit chauffage : brûleur, circulateur, ECS et zones Evohome, à partir de Prometheus.

Usage : python -I audit_chauffage.py [jours]   (défaut 15 ; Prometheus ne garde que ~15 jours)
Lecture seule. Aucune donnée personnelle : seulement des entity_id et l'adresse locale de Prometheus.
"""
import json, sys, time, urllib.parse, urllib.request
import statistics as st
from collections import defaultdict

PROM = "http://192.168.1.10:9090/api/v1/query_range"
DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 15
STEP = 60
NOW = int(time.time())
START = NOW - DAYS * 86400
ECS_SUPPLY = 60  # brûleur avec départ >= 60 °C = charge ECS (le capteur dhw_pump_active reste à 0)

ZONES = ["salon", "cuisine", "salle_a_manger", "salle_de_bain", "hall_entree", "wc_bas",
         "hall_nuit", "polyvalent", "ch_emma", "ch_louis", "bureau_fabien", "ch_amis"]
TEMP_NAME = {"ch_emma": "chambre_emma", "ch_louis": "chambre_louis"}  # ch_amis n'a pas de sensor.temp_*


def fetch(entity):
    out, t = {}, START
    while t < NOW:
        e = min(t + 7 * 86400, NOW)
        q = '{entity="%s",__name__=~"hass_.*",__name__!~"hass_entity.*|hass_last.*|hass_state.*"}' % entity
        url = PROM + "?" + urllib.parse.urlencode({"query": q, "start": t, "end": e, "step": STEP})
        try:
            res = json.load(urllib.request.urlopen(url, timeout=120))["data"]["result"]
        except Exception as ex:
            print("ERREUR", entity, ex)
            res = []
        for r in res[:1]:
            for ts, v in r["values"]:
                try:
                    out[int(ts)] = float(v)
                except ValueError:
                    pass
        t = e
    return out


lt = time.localtime
hour = lambda ts: lt(ts).tm_hour
dkey = lambda ts: time.strftime("%Y-%m-%d", lt(ts))
dlab = lambda k: k[8:10] + "/" + k[5:7]

burner = fetch("binary_sensor.vicare_burner_active")
pump = fetch("binary_sensor.vicare_circulation_pump_active")
modu = fetch("sensor.vicare_burner_modulation")
sup = fetch("sensor.vicare_supply_temperature")
ext = fetch("sensor.vicare_outside_temperature")
temp = {z: fetch("sensor.temp_" + TEMP_NAME.get(z, z)) for z in ZONES}
defi = {z: fetch("sensor.evohome_deficit_" + z) for z in ZONES}
ts_all = sorted(burner)
if not ts_all:
    sys.exit("Aucune donnée Prometheus (service arrêté ?)")
print(f"Période : {time.strftime('%d/%m %H:%M', lt(ts_all[0]))} -> {time.strftime('%d/%m %H:%M', lt(ts_all[-1]))} ({len(ts_all)} min)")

on = lambda t: burner.get(t, 0) >= 0.5
ecs = lambda t: on(t) and sup.get(t, 0) >= ECS_SUPPLY
heat = lambda t: on(t) and sup.get(t, 0) < ECS_SUPPLY
pon = lambda t: pump.get(t, 0) >= 0.5
zdef = [z for z in ZONES if defi[z]]
unexpl = lambda t: all(defi[z].get(t, 0) < 0.1 for z in zdef)

# ---------------- Par jour ----------------
days = defaultdict(lambda: dict(n=0, h=0, e=0, c=0, cs=0, st=0, ext=[]))
runs, cur = [], None
for t in ts_all:
    r = days[dkey(t)]
    r["n"] += 1
    if t in ext:
        r["ext"].append(ext[t])
    r["h"] += heat(t)
    r["e"] += ecs(t)
    r["c"] += pon(t)
    r["cs"] += pon(t) and not on(t)
    if heat(t):
        if cur is None:
            cur = [t, 0]
            r["st"] += 1
        cur[1] += 1
    elif cur is not None:
        runs.append(cur)
        cur = None
print("\n== Par jour (minutes) ==")
print("jour  | chauffage | ECS | départs | circulateur | circ. sans brûleur | ext moy")
for k in sorted(days):
    r = days[k]
    if r["n"] < 600:
        continue
    print(f"{dlab(k)} | {r['h']:9d} | {r['e']:3d} | {r['st']:7d} | {r['c']:11d} | {r['cs']:18d} | {st.mean(r['ext']) if r['ext'] else 0:5.1f}°C")

# ---------------- Cycles ----------------
lens = [x[1] for x in runs]
gaps = [(runs[i + 1][0] - runs[i][0]) / 60 for i in range(len(runs) - 1) if runs[i + 1][0] - runs[i][0] < 7200]
print("\n== Cycles de chauffage (hors ECS) ==")
if lens:
    nd = max(1, len([k for k in days if days[k]['n'] >= 600]))
    print(f"{len(lens)} cycles ({len(lens)/nd:.0f}/jour), durée médiane {st.median(lens):.0f} min, <=2 min {sum(l<=2 for l in lens)/len(lens):.0%}, <=5 min {sum(l<=5 for l in lens)/len(lens):.0%}, >=15 min {sum(l>=15 for l in lens)/len(lens):.0%}")
if gaps:
    print(f"Intervalle entre départs : médiane {st.median(gaps):.0f} min (10 min = cycle du relais Evohome, impulsions courtes)")
sh = [sup[t] for t in ts_all if heat(t) and t in sup]
mo = [modu[t] for t in ts_all if heat(t) and t in modu]
if sh:
    q = st.quantiles(sh, n=10)
    print(f"Départ en chauffage : médiane {st.median(sh):.0f}°C, p90 {q[8]:.0f}°C, >55°C {sum(x>55 for x in sh)/len(sh):.0%} du temps")
if mo:
    q = st.quantiles(mo, n=10)
    print(f"Modulation en chauffage : médiane {st.median(mo):.0f}% (p10 {q[0]:.0f}% - p90 {q[8]:.0f}%)")
ecs_runs, c2 = [], None
for t in ts_all:
    if ecs(t):
        if c2 is None:
            c2 = [t, 0]
        c2[1] += 1
    elif c2 is not None:
        ecs_runs.append(c2)
        c2 = None
byh = defaultdict(int)
for x in ecs_runs:
    byh[hour(x[0])] += 1
print(f"Charges ECS : {len(ecs_runs)} (durée médiane {st.median([x[1] for x in ecs_runs]) if ecs_runs else 0:.0f} min), par heure de départ : {dict(sorted(byh.items()))}")

# ---------------- Profil horaire ----------------
print("\n== Profil horaire moyen (minutes/h) ==")
hn, hb, hp, he = defaultdict(int), defaultdict(int), defaultdict(int), defaultdict(int)
for t in ts_all:
    h = hour(t)
    hn[h] += 1
    hb[h] += heat(t)
    hp[h] += pon(t)
    he[h] += ecs(t)
print("h  : " + " ".join(f"{h:02d}" for h in range(24)))
for lab, d in (("chf", hb), ("circ", hp), ("ecs", he)):
    print(f"{lab:4s}: " + " ".join(f"{d[h]/max(1,hn[h])*60:2.0f}" for h in range(24)))

# ---------------- Nuits ----------------
print("\n== Nuits (22h-05h) : minutes de brûleur chauffage, dont sans aucune zone en déficit, plus long run continu ==")
nights = {}
for t in ts_all:
    h = hour(t)
    if h >= 22 or h < 5:
        k = dkey(t - 5 * 3600)
        n = nights.setdefault(k, dict(n=0, b=0, u=0, e=[], run=0, best=0))
        n["n"] += 1
        n["e"].append(ext.get(t, 0))
        if heat(t):
            n["b"] += 1
            n["u"] += unexpl(t)
            n["run"] += 1
            n["best"] = max(n["best"], n["run"])
        else:
            n["run"] = 0
for k in sorted(nights):
    n = nights[k]
    if n["n"] >= 400:
        print(f"nuit du {dlab(k)} : {n['b']:3d} min | {n['u']:3d} sans zone en déficit | run continu max {n['best']:3d} min | ext {st.mean(n['e']):4.1f}°C")

# ---------------- Zones ----------------
print("\n== Zones ==")
hm = [t for t in ts_all if heat(t)]
print("zone            | T moy | min..max   | % temps en déficit (>=0,3°C) | déficit moy | % des minutes de brûleur où elle est en déficit")
for z in ZONES:
    T = [temp[z][t] for t in ts_all if t in temp[z]]
    D = [defi[z][t] for t in ts_all if t in defi[z]]
    if not D:
        print(f"{z:15s} | pas de données")
        continue
    ind = [d for d in D if d >= 0.3]
    sh_ = sum(1 for t in hm if defi[z].get(t, 0) >= 0.3) / max(1, len(hm))
    tt = f"{st.mean(T):5.1f} | {min(T):4.1f}..{max(T):4.1f}" if T else "  -   |   -      "
    print(f"{z:15s} | {tt} | {len(ind)/len(D):6.0%} | {st.mean(ind) if ind else 0:4.1f}°C | {sh_:5.0%}")
print(f"Minutes de brûleur chauffage sans aucune zone en déficit : {sum(1 for t in hm if unexpl(t))/max(1,len(hm)):.0%}")

# ---------------- Matins (jours de semaine) ----------------
print("\n== Matins de semaine : T à 06:30 par zone, ext, brûleur et ECS entre 05:00 et 07:30 ==")
print("jour   " + " ".join(f"{z[:6]:>6s}" for z in ZONES) + "   ext  brûleur ecs")
for k in sorted({dkey(t) for t in ts_all})[-8:]:
    wd = time.strptime(k, "%Y-%m-%d").tm_wday
    if wd >= 5:
        continue
    row = []
    for z in ZONES:
        v = next((temp[z][t] for t in ts_all if dkey(t) == k and hour(t) == 6 and lt(t).tm_min == 30 and t in temp[z]), None)
        row.append(f"{v:6.1f}" if v is not None else "     -")
    e = next((ext[t] for t in ts_all if dkey(t) == k and hour(t) == 6 and lt(t).tm_min == 30 and t in ext), 0)
    w = [t for t in ts_all if dkey(t) == k and (5 <= hour(t) < 7 or (hour(t) == 7 and lt(t).tm_min < 30))]
    print(f"{dlab(k)}  " + " ".join(row) + f" {e:5.1f}  {sum(heat(t) for t in w):4d}   {sum(ecs(t) for t in w):3d}")
