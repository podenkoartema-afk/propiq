
import streamlit as st
import csv, os, json
from datetime import datetime

st.set_page_config(page_title="PROPIQ — Login", page_icon="🔐", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #f8f6f1; }
header[data-testid="stHeader"] { display: none !important; }
#MainMenu, footer { display: none !important; }

.login-wrap {
    max-width: 440px;
    margin: 60px auto;
    background: #fff;
    border: 1px solid #ede8de;
    border-radius: 20px;
    padding: 48px 40px;
    box-shadow: 0 8px 40px rgba(0,0,0,0.07);
}
.login-logo {
    font-family: "Playfair Display", serif;
    font-size: 32px;
    font-weight: 700;
    color: #1a1a1a;
    text-align: center;
    margin-bottom: 4px;
}
.login-logo span { color: #c9a84c; }
.login-sub { font-size: 12px; color: #bbb; text-align: center; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 32px; }
.role-badge { display: inline-block; padding: 5px 14px; border-radius: 20px; font-size: 12px; font-weight: 600; }
.admin-badge { background: #1a1a1a; color: #c9a84c; }
.broker-badge { background: #e8f5ee; color: #2d7a4f; }

.stat-box { background: #fff; border: 1px solid #eee; border-radius: 12px; padding: 20px 24px; text-align: center; }
.stat-num { font-size: 36px; font-weight: 700; color: #1a1a1a; }
.stat-label { font-size: 11px; color: #999; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }
.lead-card { background: #fff; border: 1px solid #eee; border-radius: 12px; padding: 16px 20px; margin-bottom: 10px; }
.score-badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: 600; }
.section-title { font-size: 11px; font-weight: 600; color: #c9a84c; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 16px; margin-top: 8px; }
.broker-card { background: #fff; border: 1px solid #eee; border-radius: 12px; padding: 16px 20px; margin-bottom: 10px; }
.stButton > button { border-radius: 10px !important; font-weight: 600 !important; }
div[data-testid="stForm"] { border: none !important; padding: 0 !important; background: transparent !important; }
</style>
""", unsafe_allow_html=True)

ADMIN_USER = "$Admin$"
ADMIN_PASS = "PropIQ2026$"

def load_leads():
    if not os.path.exists("leads.csv"):
        return []
    with open("leads.csv", "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def save_leads(leads):
    if not leads:
        if os.path.exists("leads.csv"):
            os.remove("leads.csv")
        return
    with open("leads.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=leads[0].keys())
        writer.writeheader()
        writer.writerows(leads)

def load_brokers():
    if not os.path.exists("brokers.json"):
        return []
    with open("brokers.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_brokers(brokers):
    with open("brokers.json", "w", encoding="utf-8") as f:
        json.dump(brokers, f, ensure_ascii=False, indent=2)

if "role" not in st.session_state:
    st.session_state.role = None
if "username" not in st.session_state:
    st.session_state.username = None
if "broker_data" not in st.session_state:
    st.session_state.broker_data = {}

# ══════════════════════════════
# LOGIN PAGE
# ══════════════════════════════
if not st.session_state.role:
    _, center, _ = st.columns([1, 1.2, 1])
    with center:
        st.markdown("""
        <div class="login-wrap">
            <div class="login-logo">PROP<span>IQ</span></div>
            <div class="login-sub">Member Access</div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            login_btn = st.form_submit_button("Login →", use_container_width=True, type="primary")

        if login_btn:
            if username == ADMIN_USER and password == ADMIN_PASS:
                st.session_state.role = "admin"
                st.session_state.username = username
                st.rerun()
            else:
                brokers = load_brokers()
                broker = next((b for b in brokers if b["username"] == username and b["password"] == password), None)
                if broker:
                    st.session_state.role = "broker"
                    st.session_state.username = username
                    st.session_state.broker_data = broker
                    st.rerun()
                else:
                    st.error("Incorrect username or password")

    st.stop()

# ══════════════════════════════
# HEADER (общий)
# ══════════════════════════════
badge = f'<span class="role-badge admin-badge">Admin</span>' if st.session_state.role == "admin" else f'<span class="role-badge broker-badge">Broker</span>'
h1, h2, h3 = st.columns([3, 2, 1])
with h1:
    st.markdown(f'<div style="font-family:Playfair Display,serif;font-size:26px;font-weight:700;color:#1a1a1a;padding:8px 0">PROP<span style="color:#c9a84c">IQ</span> &nbsp; {badge}</div>', unsafe_allow_html=True)
with h2:
    st.markdown(f'<div style="font-size:13px;color:#999;padding:14px 0">Logged in as <b>{st.session_state.username}</b></div>', unsafe_allow_html=True)
with h3:
    if st.button("Logout", use_container_width=True):
        st.session_state.role = None
        st.session_state.username = None
        st.session_state.broker_data = {}
        st.rerun()

st.markdown("<hr style='border:none;border-top:1px solid #ede8de;margin:8px 0 24px'>", unsafe_allow_html=True)

# ══════════════════════════════
# ADMIN PANEL
# ══════════════════════════════
if st.session_state.role == "admin":
    tab1, tab2, tab3 = st.tabs(["Leads", "Brokers", "Add Broker"])

    with tab1:
        leads = load_leads()
        today = datetime.now().strftime("%Y-%m-%d")
        buyers = [l for l in leads if l.get("Type","Buyer") != "Broker"]
        brokers_in_leads = [l for l in leads if l.get("Type","") == "Broker"]
        scores = [int(l["Score"]) for l in leads if l.get("Score","").isdigit()]
        avg_score = round(sum(scores)/len(scores)) if scores else 0
        districts = {}
        for l in leads:
            d = l.get("District","Unknown")
            districts[d] = districts.get(d,0) + 1
        top_district = max(districts, key=districts.get) if districts else "—"

        c1,c2,c3,c4 = st.columns(4)
        c1,c2,c3,c4,c5 = st.columns(5)
        with c1: st.markdown(f'<div class="stat-box"><div class="stat-num">{len(leads)}</div><div class="stat-label">All Leads</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="stat-box"><div class="stat-num" style="color:#2d7a4f">{len(buyers)}</div><div class="stat-label">Buyers</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="stat-box"><div class="stat-num" style="color:#c9a84c">{len(brokers_in_leads)}</div><div class="stat-label">Brokers</div></div>', unsafe_allow_html=True)
        with c4: st.markdown(f'<div class="stat-box"><div class="stat-num" style="color:#1a1a1a">{sum(1 for l in leads if l.get("Date","").startswith(today))}</div><div class="stat-label">Today</div></div>', unsafe_allow_html=True)
        with c5: st.markdown(f'<div class="stat-box"><div class="stat-num" style="font-size:20px;padding-top:8px">{top_district}</div><div class="stat-label">Top District</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        sf1, sf2 = st.columns([3,1])
        with sf1: search = st.text_input("Search", placeholder="Name, WhatsApp, property...", label_visibility="collapsed")
        with sf2: filter_d = st.selectbox("District", ["All"]+list(districts.keys()), label_visibility="collapsed")

        filtered = list(reversed(leads))
        if search:
            q = search.lower()
            filtered = [l for l in filtered if q in l.get("Name","").lower() or q in l.get("WhatsApp","").lower() or q in l.get("Property","").lower()]
        if filter_d != "All":
            filtered = [l for l in filtered if l.get("District","") == filter_d]

        st.markdown(f'<div style="font-size:13px;color:#999;margin-bottom:12px">{len(filtered)} leads</div>', unsafe_allow_html=True)

        for idx, lead in enumerate(filtered):
            score = int(lead.get("Score",0)) if str(lead.get("Score","")).isdigit() else 0
            sc = "#2d7a4f" if score>=70 else "#c9a84c" if score>=50 else "#c0392b"
            sb = "#e8f5ee" if score>=70 else "#fdf6e3" if score>=50 else "#fdecea"
            wa = f"https://wa.me/{lead.get('WhatsApp','').replace('+','').replace(' ','')}"
            card_col, del_col = st.columns([11, 1])
            with card_col:
                st.markdown(f"""
                <div class="lead-card">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start">
                        <div>
                            <div style="font-size:16px;font-weight:600;color:#1a1a1a">{lead.get("Name","—")}</div>
                            <div style="font-size:13px;color:#666;margin-top:4px">📱 {lead.get("WhatsApp","—")} &nbsp;|&nbsp; ✉️ {lead.get("Email") or "—"} &nbsp;|&nbsp; 🕐 {lead.get("Date","—")} &nbsp;|&nbsp; 🌍 {lead.get("Nationality","—")}</div>
                        </div>
                        <span class="score-badge" style="color:{sc};background:{sb}">Score: {score}/100</span>
                    </div>
                    <div style="margin-top:12px;padding-top:12px;border-top:1px solid #f5f5f5;display:flex;gap:32px">
                        <div><div style="font-size:11px;color:#999;text-transform:uppercase;letter-spacing:1px">Property</div><div style="font-size:14px;font-weight:500;color:#1a1a1a;margin-top:2px">{lead.get("Property","—")}</div></div>
                        <div><div style="font-size:11px;color:#999;text-transform:uppercase;letter-spacing:1px">District</div><div style="font-size:14px;font-weight:500;color:#1a1a1a;margin-top:2px">{lead.get("District","—")}</div></div>
                        <div><div style="font-size:11px;color:#999;text-transform:uppercase;letter-spacing:1px">Timeline</div><div style="font-size:14px;font-weight:500;color:#1a1a1a;margin-top:2px">{lead.get("Timeline","—")}</div></div>
                        <div><div style="font-size:11px;color:#999;text-transform:uppercase;letter-spacing:1px">Type</div><div style="font-size:14px;font-weight:500;margin-top:2px;color:{"#c9a84c" if lead.get("Type")=="Broker" else "#2d7a4f"}">{("🏢 Broker" if lead.get("Type")=="Broker" else "👤 Buyer")}</div></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.link_button(f"Write to {lead.get('Name','').split()[0]} on WhatsApp", wa)
            with del_col:
                st.markdown("<div style='margin-top:14px'>", unsafe_allow_html=True)
                uid = f"{lead.get('Date','')}_{lead.get('WhatsApp','')}"
                if st.button("🗑", key=f"del_lead_{uid}_{idx}", help="Delete lead"):
                    all_leads = load_leads()
                    all_leads = [l for i, l in enumerate(reversed(all_leads))
                                 if i != idx]
                    all_leads = list(reversed(all_leads))
                    save_leads(all_leads)
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

        if districts:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="section-title">Leads by District</div>', unsafe_allow_html=True)
            import pandas as pd
            df = pd.DataFrame(list(districts.items()), columns=["District","Leads"]).sort_values("Leads", ascending=False)
            st.bar_chart(df.set_index("District"))

    with tab2:
        brokers = load_brokers()
        st.markdown(f'<div style="font-size:13px;color:#999;margin-bottom:16px">{len(brokers)} brokers registered</div>', unsafe_allow_html=True)
        if not brokers:
            st.info("No brokers yet. Add brokers in the next tab.")
        for b in brokers:
            wa = f"https://wa.me/{b.get('whatsapp','').replace('+','').replace(' ','')}"
            col_b, col_d = st.columns([3,1])
            with col_b:
                st.markdown(f"""
                <div class="broker-card">
                    <div style="font-size:16px;font-weight:600;color:#1a1a1a">{b.get("name","—")}</div>
                    <div style="font-size:13px;color:#666;margin-top:4px">🏢 {b.get("agency","—")} &nbsp;|&nbsp; 📱 {b.get("whatsapp","—")} &nbsp;|&nbsp; ✉️ {b.get("email","—")}</div>
                    <div style="font-size:12px;color:#bbb;margin-top:4px">Login: <b>{b.get("username","—")}</b></div>
                </div>
                """, unsafe_allow_html=True)
            with col_d:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Delete", key=f"del_{b['username']}"):
                    brokers = [x for x in brokers if x["username"] != b["username"]]
                    save_brokers(brokers)
                    st.rerun()
                st.link_button("WhatsApp", wa, use_container_width=True)

    with tab3:
        st.markdown('<div class="section-title">Add New Broker</div>', unsafe_allow_html=True)
        with st.form("add_broker"):
            nb1, nb2 = st.columns(2)
            with nb1:
                b_name = st.text_input("Full name", placeholder="John Smith")
                b_agency = st.text_input("Agency", placeholder="DAMAC Properties")
                b_username = st.text_input("Username (for login)", placeholder="john_smith")
            with nb2:
                b_wa = st.text_input("WhatsApp", placeholder="+971 50 000 0000")
                b_email = st.text_input("Email", placeholder="john@agency.com")
                b_password = st.text_input("Password", placeholder="Set password", type="password")
            add_btn = st.form_submit_button("Add Broker", use_container_width=True, type="primary")

        if add_btn:
            if b_name and b_username and b_password:
                brokers = load_brokers()
                if any(b["username"] == b_username for b in brokers):
                    st.error("Username already exists")
                else:
                    brokers.append({"name":b_name,"agency":b_agency,"username":b_username,"password":b_password,"whatsapp":b_wa,"email":b_email,"created":datetime.now().strftime("%Y-%m-%d")})
                    save_brokers(brokers)
                    st.success(f"Broker {b_name} added! Login: {b_username}")
            else:
                st.error("Fill in name, username and password")

# ══════════════════════════════
# BROKER DASHBOARD
# ══════════════════════════════
elif st.session_state.role == "broker":
    b = st.session_state.broker_data
    st.markdown(f"""
    <div style="background:#fff;border:1px solid #ede8de;border-radius:16px;padding:24px 28px;margin-bottom:24px;display:flex;gap:24px;align-items:center">
        <div style="background:#1a1a1a;color:#c9a84c;width:52px;height:52px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:22px;font-weight:700;flex-shrink:0">{b.get("name","B")[0].upper()}</div>
        <div>
            <div style="font-size:18px;font-weight:700;color:#1a1a1a">{b.get("name","—")}</div>
            <div style="font-size:13px;color:#888;margin-top:3px">🏢 {b.get("agency","—")} &nbsp;|&nbsp; 📱 {b.get("whatsapp","—")} &nbsp;|&nbsp; ✉️ {b.get("email","—")}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Quick Access</div>', unsafe_allow_html=True)
    q1, q2, q3 = st.columns(3)
    with q1:
        st.markdown('<div class="stat-box"><div style="font-size:28px">🔍</div><div style="font-size:14px;font-weight:600;color:#1a1a1a;margin-top:8px">Analyze Property</div><div style="font-size:12px;color:#999;margin-top:4px">Get Deal Score for any object</div></div>', unsafe_allow_html=True)
        st.page_link("app.py", label="Open Analyzer →", use_container_width=True)
    with q2:
        st.markdown('<div class="stat-box"><div style="font-size:28px">📊</div><div style="font-size:14px;font-weight:600;color:#1a1a1a;margin-top:8px">Dubai Market</div><div style="font-size:12px;color:#999;margin-top:4px">Live data on dubailand.gov.ae</div></div>', unsafe_allow_html=True)
        st.link_button("Open DLD →", "https://dubailand.gov.ae/en/open-data/real-estate-data/", use_container_width=True)
    with q3:
        st.markdown('<div class="stat-box"><div style="font-size:28px">🏡</div><div style="font-size:14px;font-weight:600;color:#1a1a1a;margin-top:8px">Listings</div><div style="font-size:12px;color:#999;margin-top:4px">Current listings in Dubai</div></div>', unsafe_allow_html=True)
        st.link_button("bayut.com →", "https://www.bayut.com/", use_container_width=True)
        st.link_button("propertyfinder.ae →", "https://www.propertyfinder.ae/", use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">Dubai Market Tips</div>', unsafe_allow_html=True)
    tips = [
        ("Business Bay", "High rental demand, good for investors. Avg yield 6.5-7.5%"),
        ("JVC", "Most affordable entry point. Yield up to 8%. Growing infrastructure"),
        ("Dubai Marina", "Premium segment. Strong resale market. 1200-1400 AED/sqft"),
        ("Palm Jumeirah", "Luxury tier. Limited supply keeps prices stable. 2500+ AED/sqft"),
    ]
    t1, t2 = st.columns(2)
    for i, (district, tip) in enumerate(tips):
        with (t1 if i%2==0 else t2):
            st.markdown(f'<div class="broker-card"><div style="font-size:14px;font-weight:600;color:#1a1a1a;margin-bottom:6px">📍 {district}</div><div style="font-size:13px;color:#666;line-height:1.5">{tip}</div></div>', unsafe_allow_html=True)
