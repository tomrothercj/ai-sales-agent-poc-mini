# minimal_run.py
# No-install demo (Python 3.13 stdlib only). Produces CSVs.
import csv, random, os, sys

OUTPUT_DIR = os.path.join("data","outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

VERTICAL_SAMPLES = {
    'SaaS': ['acmeapp','cloudify','datapulse','flowhq','marketoid'],
    'Ecommerce': ['shophero','trendify','buybuddy','cartly','dealorama'],
    'Fintech': ['payflux','finastro','bankly','ledgr','coinverse']
}
COUNTRY_TLD = {'DE':'.de','AT':'.at','CH':'.ch','FR':'.fr','US':'.com'}

def ask(prompt, default=None):
    txt = input(f"{prompt} " + (f"[{default}] " if default else ""))
    if not txt and default is not None:
        return default
    return txt

def generate_companies(verticals, countries, min_visits, seed=42, cap=5):
    random.seed(seed)
    rows = []
    for v in verticals:
        names = VERTICAL_SAMPLES.get(v, VERTICAL_SAMPLES['SaaS'])
        for name in names:
            for c in countries:
                tld = COUNTRY_TLD.get(c, '.com')
                visits = random.randint(min_visits, max(min_visits+50000, min_visits*3))
                rows.append({
                    'domain': f"{name}{tld}",
                    'company_name': name.capitalize(),
                    'country': c,
                    'vertical': v,
                    'sw_visits': visits
                })
    # naive dedupe by domain
    seen = set()
    deduped = []
    for r in rows:
        if r['domain'] in seen:
            continue
        seen.add(r['domain'])
        deduped.append(r)
    # cap small
    return deduped[:cap]

def mock_salesforce_id(domain):
    random.seed(abs(hash(domain)) % 10_000)
    return f"001{random.randint(100000,999999)}" if random.random() < 0.5 else ""

def mock_zoominfo_enrich(domain):
    random.seed(abs(hash(domain)) % 10_000)
    if random.random() < 0.8:
        lid = abs(hash(domain)) % 10_000
        return {"id": f"ZC_{lid}", "linkedin_url": f"https://www.linkedin.com/company/{domain.split('.')[0]}/"}
    return None

def mock_personas(company_domain, zi_id, titles_regex):
    # produce 0..3 simple personas
    random.seed(abs(hash(company_domain)) % 10_000)
    n = random.choice([0,1,2,3])
    first = ['Jane','John','Max','Mia','Alex','Lena','Sara','Paul']
    last  = ['Muster','Doe','Klein','Weber','Fischer','Schmidt']
    titles = ['VP Marketing','Head of Marketing','Director Demand Gen','VP Sales','Head of Sales','Director Growth']
    out = []
    for _ in range(n):
        fn = random.choice(first); ln = random.choice(last); title = random.choice(titles)
        out.append({
            'company_domain': company_domain,
            'full_name': f"{fn} {ln}",
            'title': title,
            'email': "",
            'li_profile': f"https://www.linkedin.com/in/{fn.lower()}{ln.lower()}",
            'source': 'zoominfo',
            'confidence': round(random.uniform(0.6,0.95),2)
        })
    return out

def main():
    print("=== AI Sales Agent NO-INSTALL Demo ===")
    verts = ask("Verticals (Komma-separiert: SaaS,Ecommerce,Fintech)", "SaaS")
    countries = ask("Länder (Komma-separiert: DE,AT,CH,FR,US)", "DE")
    try:
        min_visits = int(ask("Mindest-Monatsvisits (Zahl)", "50000"))
    except ValueError:
        min_visits = 50000
    titles_regex = ask("Persona Regex (ignoriert im Demo)", "(Head|VP|Director) (Marketing|Sales)")
    print("\nMini-Modus aktiv: max. 5 Firmen, fixer Seed.\n")

    V = [v.strip() for v in verts.split(",") if v.strip()]
    C = [c.strip().upper() for c in countries.split(",") if c.strip()]

    # 1) Companies
    companies = generate_companies(V, C, min_visits, seed=42, cap=5)
    # 2) SF check + ZoomInfo enrich + personas
    leads = []
    for c in companies:
        c['sf_account_id'] = mock_salesforce_id(c['domain'])
        zi = mock_zoominfo_enrich(c['domain'])
        if zi:
            c['zoominfo_company_id'] = zi['id']
            c['li_company_url'] = zi['linkedin_url']
            leads += mock_personas(c['domain'], zi['id'], titles_regex)
        else:
            c['zoominfo_company_id'] = ""
            c['li_company_url'] = ""

    # 3) Needs Sales Navigator (no personas)
    domains_with_leads = {l['company_domain'] for l in leads}
    needs_sn = [c for c in companies if c['domain'] not in domains_with_leads]

    # 4) Write CSVs
    comp_cols = ['domain','company_name','country','vertical','sw_visits','sf_account_id','zoominfo_company_id','li_company_url']
    with open(os.path.join(OUTPUT_DIR, "final_companies.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=comp_cols); w.writeheader(); w.writerows(companies)

    lead_cols = ['company_domain','full_name','title','email','li_profile','source','confidence']
    with open(os.path.join(OUTPUT_DIR, "final_leads.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=lead_cols); w.writeheader(); w.writerows(leads)

    sn_cols = ['Company Name','Company Website','Company LinkedIn URL','Country']
    with open(os.path.join(OUTPUT_DIR, "sn_accounts_upload.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=sn_cols); w.writeheader()
        for c in needs_sn:
            w.writerow({
                'Company Name': c.get('company_name') or c['domain'],
                'Company Website': f"https://{c['domain']}",
                'Company LinkedIn URL': c.get('li_company_url') or "",
                'Country': c.get('country') or ""
            })

    with open(os.path.join(OUTPUT_DIR, "needs_salesnav.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=['domain','company_name','country','vertical'])
        w.writeheader()
        for c in needs_sn:
            w.writerow({k:c[k] for k in ['domain','company_name','country','vertical']})

    print("\nFertig! Dateien erstellt in:", OUTPUT_DIR)
    print(" - final_companies.csv")
    print(" - final_leads.csv")
    print(" - sn_accounts_upload.csv")
    print(" - needs_salesnav.csv")
    print("\nDiese CSVs lassen sich direkt mit Excel öffnen.")
    print("Hinweis: Für echte XLSX-Ausgabe wird später ein Zusatzpaket benötigt.")

if __name__ == "__main__":
    main()
