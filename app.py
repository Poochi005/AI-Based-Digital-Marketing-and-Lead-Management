"""GreenNest Home Essentials - CRM & Marketing dashboard (student demo).
Flask + SQLite. Inspired by the Zoho marketing ecosystem; NOT connected to any Zoho product or live AI API."""
import os
import random
import sqlite3
from datetime import date, timedelta

from flask import Flask, flash, g, redirect, render_template, request, url_for

BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE, "greennest.db")

app = Flask(__name__)
app.secret_key = "greennest-student-demo"

STATUSES = ["New", "Contacted", "Qualified", "Proposal", "Converted", "Lost"]
SOURCES = ["Website", "Instagram", "Facebook", "Email Newsletter", "Referral", "Google Ads"]
PRODUCTS = ["Bamboo Kitchenware", "Organic Cotton Bedding", "Eco Cleaning Kit",
            "Indoor Plant Set", "Reusable Storage Jars", "Natural Candles"]
CHANNELS = ["Email", "Instagram", "Facebook", "WhatsApp", "Google Ads"]
CAMPAIGN_STATUSES = ["Draft", "Scheduled", "Active", "Completed"]
NAV = [("dashboard", "dashboard", "Dashboard", "🏠"), ("lead", "leads", "Leads", "🎯"),
       ("contacts", "contacts", "Contacts", "👥"), ("deals", "deals", "Deals Pipeline", "💼"),
       ("campaign", "campaigns", "Campaigns", "📣"), ("performance", "performance", "Campaign Performance", "📬"),
       ("studio", "studio", "AI Content Studio", "✨"), ("automation", "automation", "Marketing Automation", "🔁"),
       ("analytics", "analytics", "Analytics", "📊"), ("settings", "settings", "Settings", "⚙️")]


# ---------- database helpers ----------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def rows(sql, args=()):
    return get_db().execute(sql, args).fetchall()


def scalar(sql, args=()):
    return get_db().execute(sql, args).fetchone()[0]


def init_db():
    db = sqlite3.connect(DB_PATH)
    db.executescript("""
    CREATE TABLE IF NOT EXISTS leads(
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT NOT NULL, phone TEXT,
        source TEXT, status TEXT DEFAULT 'New', product_interest TEXT, created_at TEXT);
    CREATE TABLE IF NOT EXISTS campaigns(
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, channel TEXT, target_audience TEXT,
        objective TEXT, status TEXT DEFAULT 'Draft', budget REAL DEFAULT 0, created_at TEXT);""")
    if db.execute("SELECT COUNT(*) FROM leads").fetchone()[0] == 0:
        today = date.today()
        leads = [
            ("Priya Raman", "priya.raman@example.com", "98400 11201", "Website", "Converted", "Bamboo Kitchenware", 40),
            ("Arjun Mehta", "arjun.mehta@example.com", "98410 22302", "Instagram", "Qualified", "Indoor Plant Set", 34),
            ("Divya Nair", "divya.nair@example.com", "98420 33403", "Referral", "Proposal", "Organic Cotton Bedding", 31),
            ("Karthik Subramanian", "karthik.s@example.com", "98430 44504", "Google Ads", "Contacted", "Eco Cleaning Kit", 27),
            ("Sneha Iyer", "sneha.iyer@example.com", "98440 55605", "Email Newsletter", "Converted", "Natural Candles", 24),
            ("Rahul Verma", "rahul.verma@example.com", "98450 66706", "Facebook", "New", "Reusable Storage Jars", 20),
            ("Meena Lakshmi", "meena.l@example.com", "98460 77807", "Website", "Qualified", "Bamboo Kitchenware", 17),
            ("Vikram Sethu", "vikram.sethu@example.com", "98470 88908", "Instagram", "Lost", "Natural Candles", 15),
            ("Anitha George", "anitha.george@example.com", "98480 99009", "Website", "Proposal", "Indoor Plant Set", 12),
            ("Suresh Kumar", "suresh.kumar@example.com", "98490 10110", "Referral", "Contacted", "Eco Cleaning Kit", 9),
            ("Lavanya Pillai", "lavanya.p@example.com", "98500 21211", "Instagram", "New", "Organic Cotton Bedding", 6),
            ("Farhan Ali", "farhan.ali@example.com", "98510 32312", "Google Ads", "Qualified", "Reusable Storage Jars", 4),
            ("Nisha Thomas", "nisha.thomas@example.com", "98520 43413", "Email Newsletter", "New", "Natural Candles", 2),
            ("Rohit Das", "rohit.das@example.com", "98530 54514", "Website", "Converted", "Indoor Plant Set", 1)]
        db.executemany("INSERT INTO leads(name,email,phone,source,status,product_interest,created_at) VALUES(?,?,?,?,?,?,?)",
                       [(n, e, p, s, st, pr, (today - timedelta(days=d)).isoformat()) for n, e, p, s, st, pr, d in leads])
        camps = [
            ("Monsoon Home Refresh", "Email", "Existing customers", "Increase repeat orders", "Active", 15000, 30),
            ("Plant Parent Welcome Series", "Email", "New subscribers", "Nurture new leads", "Active", 8000, 22),
            ("Eco Kitchen Festival", "Instagram", "Women 25-40, urban", "Brand awareness", "Completed", 25000, 45),
            ("Festive Gifting Guide", "Facebook", "Gift buyers", "Drive festive sales", "Scheduled", 20000, 5),
            ("Switch to Reusables", "Google Ads", "Eco-conscious shoppers", "Generate leads", "Active", 30000, 18),
            ("Win-back: Quiet Customers", "Email", "Inactive 90+ days", "Re-engage customers", "Draft", 5000, 2)]
        db.executemany("INSERT INTO campaigns(name,channel,target_audience,objective,status,budget,created_at) VALUES(?,?,?,?,?,?,?)",
                       [(n, c, t, o, s, b, (today - timedelta(days=d)).isoformat()) for n, c, t, o, s, b, d in camps])
    db.commit()
    db.close()


@app.context_processor
def inject_globals():
    return {"NAV": NAV, "STATUSES": STATUSES, "SOURCES": SOURCES, "PRODUCTS": PRODUCTS,
            "CHANNELS": CHANNELS, "CAMPAIGN_STATUSES": CAMPAIGN_STATUSES}


def line_points(values, w=600, h=180, pad=14):
    lo, hi = min(values), max(values)
    step = (w - 2 * pad) / (len(values) - 1)
    return [(round(pad + i * step, 1), round(h - pad - (v - lo) / ((hi - lo) or 1) * (h - 2 * pad), 1))
            for i, v in enumerate(values)]


# ---------- dashboard ----------
@app.route("/")
def dashboard():
    total = scalar("SELECT COUNT(*) FROM leads")
    converted = scalar("SELECT COUNT(*) FROM leads WHERE status='Converted'")
    stats = {
        "total": total,
        "contacts": scalar("SELECT COUNT(*) FROM leads WHERE status IN ('Contacted','Qualified','Proposal','Converted')"),
        "deals": scalar("SELECT COUNT(*) FROM leads WHERE status IN ('Qualified','Proposal')"),
        "converted": converted,
        "rate": round(converted / total * 100, 1) if total else 0,
        "campaigns": scalar("SELECT COUNT(*) FROM campaigns WHERE status='Active'"),
    }
    sources = [tuple(r) for r in rows("SELECT source, COUNT(*) FROM leads GROUP BY source ORDER BY 2 DESC")]
    recent = rows("SELECT * FROM leads ORDER BY id DESC LIMIT 5")
    return render_template("dashboard.html", title="Dashboard", stats=stats, sources=sources, recent=recent)


# ---------- leads ----------
@app.route("/leads")
def leads():
    status, q = request.args.get("status", ""), request.args.get("q", "").strip()
    sql, args = "SELECT * FROM leads WHERE 1=1", []
    if status in STATUSES:
        sql += " AND status=?"
        args.append(status)
    if q:
        sql += " AND (name LIKE ? OR email LIKE ? OR product_interest LIKE ?)"
        args += [f"%{q}%"] * 3
    return render_template("leads.html", title="Leads", leads=rows(sql + " ORDER BY id DESC", args), status=status, q=q)


def read_lead_form():
    f = request.form
    return {k: f.get(k, "").strip() for k in ("name", "email", "phone", "source", "status", "product_interest")}


def validate_lead(d):
    errors = []
    if not d["name"]:
        errors.append("Name is required.")
    if "@" not in d["email"] or "." not in d["email"].split("@")[-1]:
        errors.append("Enter a valid email address.")
    if d["source"] not in SOURCES:
        errors.append("Choose a lead source.")
    if d["status"] not in STATUSES:
        errors.append("Choose a status.")
    return errors


@app.route("/leads/new", methods=["GET", "POST"])
def lead_add():
    lead = {"name": "", "email": "", "phone": "", "source": "Website", "status": "New", "product_interest": PRODUCTS[0]}
    if request.method == "POST":
        lead = read_lead_form()
        errors = validate_lead(lead)
        if not errors:
            db = get_db()
            db.execute("INSERT INTO leads(name,email,phone,source,status,product_interest,created_at) VALUES(?,?,?,?,?,?,?)",
                       (lead["name"], lead["email"], lead["phone"], lead["source"], lead["status"],
                        lead["product_interest"], date.today().isoformat()))
            db.commit()
            flash(f"Lead '{lead['name']}' added.", "ok")
            return redirect(url_for("leads"))
        for e in errors:
            flash(e, "error")
    return render_template("lead_form.html", title="Add Lead", lead=lead, editing=False)


@app.route("/leads/<int:lead_id>/edit", methods=["GET", "POST"])
def lead_edit(lead_id):
    lead = rows("SELECT * FROM leads WHERE id=?", (lead_id,))
    if not lead:
        flash("Lead not found.", "error")
        return redirect(url_for("leads"))
    lead = dict(lead[0])
    if request.method == "POST":
        lead.update(read_lead_form())
        errors = validate_lead(lead)
        if not errors:
            db = get_db()
            db.execute("UPDATE leads SET name=?,email=?,phone=?,source=?,status=?,product_interest=? WHERE id=?",
                       (lead["name"], lead["email"], lead["phone"], lead["source"], lead["status"],
                        lead["product_interest"], lead_id))
            db.commit()
            flash("Lead updated.", "ok")
            return redirect(url_for("leads"))
        for e in errors:
            flash(e, "error")
    return render_template("lead_form.html", title="Edit Lead", lead=lead, editing=True)


@app.route("/leads/<int:lead_id>/status", methods=["POST"])
def lead_status(lead_id):
    status = request.form.get("status")
    if status in STATUSES:
        db = get_db()
        db.execute("UPDATE leads SET status=? WHERE id=?", (status, lead_id))
        db.commit()
        flash(f"Status changed to {status}.", "ok")
    return redirect(request.referrer or url_for("leads"))


# ---------- contacts & deals ----------
@app.route("/contacts")
def contacts():
    data = rows("SELECT * FROM leads WHERE status IN ('Contacted','Qualified','Proposal','Converted') ORDER BY name")
    return render_template("contacts.html", title="Contacts", contacts=data)


@app.route("/deals")
def deals():
    stages = {s: rows("SELECT * FROM leads WHERE status=? ORDER BY id DESC", (s,)) for s in ("Qualified", "Proposal", "Converted")}
    return render_template("deals.html", title="Deals Pipeline", stages=stages)


# ---------- campaigns ----------
@app.route("/campaigns")
def campaigns():
    data = rows("SELECT * FROM campaigns ORDER BY id DESC")
    return render_template("campaigns.html", title="Campaigns", campaigns=data,
                           total_budget=sum(c["budget"] for c in data))


@app.route("/campaigns/new", methods=["GET", "POST"])
def campaign_add():
    c = {"name": "", "channel": "Email", "target_audience": "", "objective": "", "status": "Draft", "budget": ""}
    if request.method == "POST":
        c = {k: request.form.get(k, "").strip() for k in c}
        errors = []
        if not c["name"]:
            errors.append("Campaign name is required.")
        if c["channel"] not in CHANNELS:
            errors.append("Choose a channel.")
        try:
            budget = float(c["budget"] or 0)
            if budget < 0:
                raise ValueError
        except ValueError:
            errors.append("Budget must be a positive number.")
        if not errors:
            db = get_db()
            db.execute("INSERT INTO campaigns(name,channel,target_audience,objective,status,budget,created_at) VALUES(?,?,?,?,?,?,?)",
                       (c["name"], c["channel"], c["target_audience"], c["objective"],
                        c["status"] if c["status"] in CAMPAIGN_STATUSES else "Draft", budget, date.today().isoformat()))
            db.commit()
            flash(f"Campaign '{c['name']}' created.", "ok")
            return redirect(url_for("campaigns"))
        for e in errors:
            flash(e, "error")
    return render_template("campaign_form.html", title="New Campaign", c=c)


@app.route("/campaigns/<int:cid>/status", methods=["POST"])
def campaign_status(cid):
    status = request.form.get("status")
    if status in CAMPAIGN_STATUSES:
        db = get_db()
        db.execute("UPDATE campaigns SET status=? WHERE id=?", (status, cid))
        db.commit()
        flash("Campaign status updated.", "ok")
    return redirect(url_for("campaigns"))


@app.route("/performance")
def performance():
    email_campaigns = rows("SELECT * FROM campaigns WHERE channel='Email' ORDER BY id")
    selected = None
    if email_campaigns:
        selected = next((c for c in email_campaigns if str(c["id"]) == request.args.get("id")), email_campaigns[0])

    def sample(cid):  # illustrative numbers only, seeded by campaign id
        r = random.Random(cid)
        sent = r.randint(1200, 4200)
        return {"sent": sent, "opens": round(sent * r.uniform(.28, .46)),
                "clicks": round(sent * r.uniform(.04, .11)), "conv": round(sent * r.uniform(.01, .035))}

    table = [(c, sample(c["id"])) for c in email_campaigns]
    return render_template("performance.html", title="Campaign Performance", selected=selected,
                           campaigns=email_campaigns, metrics=sample(selected["id"]) if selected else None, table=table)


# ---------- AI content studio (local templates only) ----------
TONES = {
    "Friendly": {
        "subjects": ["{p}: a little upgrade your home will love", "Hi {a}! Meet your new favourite {p}",
                     "Small swap, big difference: {p}", "{o} — made for {a}", "Your home called. It wants {p}."],
        "headlines": ["Make home feel greener with {p}", "{p} for people who love a calmer home",
                      "Better for you, kinder to the planet"],
        "body": "Hello {a},\n\nAt GreenNest we believe small changes at home add up. Our {p} range is made with "
                "sustainable materials and designed to make everyday life simpler.\n\n{o}\n\nTake a look and find "
                "something that fits your space.\n\nWarmly,\nTeam GreenNest"},
    "Professional": {
        "subjects": ["Introducing GreenNest {p}", "{p}: sustainable quality for {a}", "{o} on {p}",
                     "A responsible choice for your home: {p}", "GreenNest update: {p} now available"],
        "headlines": ["Sustainably made {p}", "Quality you can trust, materials you can feel good about",
                      "{p} from GreenNest Home Essentials"],
        "body": "Dear {a},\n\nGreenNest Home Essentials is pleased to present our {p} collection, produced with "
                "responsibly sourced materials and built to last.\n\n{o}\n\nVisit our store to view the full range.\n\n"
                "Regards,\nGreenNest Home Essentials"},
    "Urgent": {
        "subjects": ["Last chance: {o}", "{p} — only a few days left", "Don't miss out, {a}: {p}",
                     "Ends soon: {o}", "Stock is running low on {p}"],
        "headlines": ["Offer ends soon: {p}", "Grab {p} before it's gone", "{o} — this week only"],
        "body": "Hi {a},\n\nTime is running out! Our {p} are going fast and this offer won't last.\n\n{o}\n\n"
                "Order today so you don't miss out.\n\nTeam GreenNest"}}


@app.route("/studio", methods=["GET", "POST"])
def studio():
    form = {"product": PRODUCTS[0], "audience": "eco-conscious families", "tone": "Friendly", "offer": "Get 15% off your first order."}
    result = None
    if request.method == "POST":
        form = {k: request.form.get(k, "").strip() or form[k] for k in form}
        t = TONES.get(form["tone"], TONES["Friendly"])
        fill = lambda s: s.format(p=form["product"], a=form["audience"], o=form["offer"])
        result = {"subjects": [fill(s) for s in t["subjects"]], "headlines": [fill(h) for h in t["headlines"]],
                  "body": fill(t["body"])}
    return render_template("studio.html", title="AI Content Studio", form=form, result=result, tones=list(TONES))


# ---------- automation, analytics, settings ----------
@app.route("/automation")
def automation():
    return render_template("automation.html", title="Marketing Automation")


@app.route("/analytics")
def analytics():
    visitors = [820, 940, 880, 1100, 1250, 1180, 1420]
    orders = [("Mon", 34), ("Tue", 41), ("Wed", 38), ("Thu", 52), ("Fri", 63), ("Sat", 71), ("Sun", 58)]
    pipeline = [(s, scalar("SELECT COUNT(*) FROM leads WHERE status=?", (s,))) for s in STATUSES]
    budget = [(r["name"], int(r["budget"])) for r in rows("SELECT name, budget FROM campaigns ORDER BY budget DESC")]
    return render_template("analytics.html", title="Analytics", visitors=visitors, points=line_points(visitors),
                           days=[d for d, _ in orders], orders=orders, pipeline=pipeline, budget=budget,
                           total_budget=sum(b for _, b in budget))


@app.route("/settings")
def settings():
    counts = {"leads": scalar("SELECT COUNT(*) FROM leads"), "campaigns": scalar("SELECT COUNT(*) FROM campaigns")}
    return render_template("settings.html", title="Settings", counts=counts)


init_db()

if __name__ == "__main__":
    app.run(debug=True)
