"""
Knowsoft Consult LTD — Corporate website
"""
import json
import os
from datetime import datetime
from functools import wraps
from flask import (
    Flask, render_template, request, flash, redirect, url_for,
    send_from_directory, session, abort
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "knowsoft-consult-change-me-in-production")
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024 * 1024
UPLOAD_DIR = os.path.join(app.root_path, "static", "uploads")
DATA_DIR = os.path.join(app.root_path, "instance")
CONTENT_FILE = os.path.join(DATA_DIR, "site_content.json")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

DEFAULT_CONTENT = {
    "youtube_id": os.environ.get("YOUTUBE_VIDEO_ID", "https://youtube.com/shorts/h_3X7vdfY5A"),
    "youtube_links": [
        "https://youtube.com/shorts/h_3X7vdfY5A",
    ],
    "youtube_interval_sec": 45,

    "hero_title": "Technology & consulting that work with ease",
    "hero_subtitle": "We design and deliver software platforms, financial workflows and advisory services for organisations that need clarity, control and results.",
    "address": "Lagos, Nigeria",
    "email": "Knowsoftconsult@gmail.com",
    "phone": "+2348081650914",
    "software": [
        {
            "id": "payme",
            "name": "Knowsoft Payme",
            "tagline": "Scan, sell and succeed for small business",
            "description": "Point-of-sale for small shops: register inventory with permanent barcodes and QR codes, scan sales with the phone camera, issue POS receipts, track cash and credit sales, purchases and expenses, share product showcase links, and view financial statements. Multi-currency, themes and offline-friendly design.",
            "version": "1.0",
            "platform": "Web · PWA · Mobile",
            "icon": "bi-phone",
            "url": "https://payme-54f8.onrender.com/",
            "download": "",
            "video_url": "https://youtube.com/shorts/h_3X7vdfY5A",
            "badge": "New",
        },
        {
            "id": "churchgate",
            "name": "Knowsoft Churchgate",
            "tagline": "Church hierarchy, membership and growth analytics",
            "description": "Manage global-to-district church structures, member registration and approvals, weekly attendance, programmes, focus groups, testimonies and admin dashboards with charts and PDF reports. Android APK available for field use.",
            "version": "1.0",
            "platform": "Web + Android",
            "icon": "bi-building",
            "url": "https://churchgate.onrender.com/",
            "download": "https://github.com/KnowsoftCloudAir/PaymeApp/raw/refs/heads/main/Churchgate.apk",
            "video_url": "https://youtube.com/shorts/h_3X7vdfY5A",
            "badge": "Enterprise",
        },
        {
            "id": "eleon",
            "name": "Knowsoft Eleon",
            "tagline": "Learning presentations and multi-user sessions",
            "description": "Eleon supports structured learning and presentation workflows for teams and training environments, with multi-user access patterns aligned to Knowsoft’s other platforms. Download the Android APK to try the mobile experience.",
            "version": "1.0",
            "platform": "Web + Android",
            "icon": "bi-easel",
            "url": "",
            "download": "https://github.com/KnowsoftCloudAir/PaymeApp/raw/refs/heads/main/Eleon.apk",
            "video_url": "https://youtube.com/shorts/h_3X7vdfY5A",
            "badge": "Training",
        },
        {
            "id": "schoolmate",
            "name": "Knowsoft SchoolMate",
            "tagline": "Connect lecturers and students with timed learning content",
            "description": "Institutions and individuals register faculties and departments; lecturers upload short video lectures and notes; students access content with codes, ask questions and build study profiles. Credits and recommendations reward knowledge sharing.",
            "version": "1.0",
            "platform": "Web",
            "icon": "bi-mortarboard",
            "url": "https://schoolmate-10.onrender.com/",
            "download": "",
            "video_url": "",
            "badge": "Education",
        },
        {
            "id": "pfm-workflow",
            "name": "FMSS / Project Financial Management",
            "tagline": "Inventory, expenses, budget variance and cost analytics",
            "description": "End-to-end project financial management: chart of accounts, payment requests, vouchers, bank reconciliation, fixed assets, procurement committee and reporting—built for organisations that need audit-ready workflows.",
            "version": "1.0",
            "platform": "Web + Windows",
            "icon": "bi-graph-up-arrow",
            "url": "https://contractconnect-inventory-mgt-5-0pv6.onrender.com/",
            "download": "",
            "video_url": "",
            "badge": "Flagship",
        },
        {
            "id": "eprocurement",
            "name": "Knowsoft eProcurement",
            "tagline": "Vendor registration, quotations and purchase workflow",
            "description": "Digital procurement: vendor onboarding, RFQs, committee evaluation, purchase orders and linkage into payment approval—so buying is controlled, traceable and faster.",
            "version": "1.0",
            "platform": "Web",
            "icon": "bi-cart-check",
            "url": "",
            "download": "",
            "video_url": "",
            "badge": "Business",
        },
    ],
    "templates": [
        {"name": "Project Budget Template", "format": "Excel", "category": "Finance", "file": "sample_budget_template.txt"},
        {"name": "Expense Claim Form", "format": "Word / PDF", "category": "Finance", "file": "sample_expense_form.txt"},
        {"name": "Variance Analysis Report", "format": "Excel", "category": "Finance", "file": "sample_variance.txt"},
        {"name": "Consulting Proposal Outline", "format": "Word", "category": "Consulting", "file": "sample_proposal.txt"},
        {"name": "Project Charter", "format": "Word", "category": "PMO", "file": "sample_charter.txt"},
        {"name": "Risk Register", "format": "Excel", "category": "PMO", "file": "sample_risk.txt"},
    ],
    "clients": [
        {"name": "Public sector partners", "sector": "Government"},
        {"name": "Development programmes", "sector": "Development"},
        {"name": "Faith & community organisations", "sector": "Non-profit"},
        {"name": "Private enterprises", "sector": "Private"},
    ],
    "gallery": [],
    "admin_password_hash": generate_password_hash(os.environ.get("ADMIN_PASSWORD", "Knowsoft@Admin2026")),
}

SERVICES = [
    {"slug": "capacity-building-financial-management", "title": "Capacity building in financial management", "icon": "bi-mortarboard", "summary": "Practical training that strengthens budgeting, controls and day-to-day financial discipline.", "body": "We design and deliver capacity-building programmes for finance teams, project units and leadership. Modules cover planning, documentation, internal controls and reporting discipline tailored to your operating environment."},
    {"slug": "office-management", "title": "Office management", "icon": "bi-briefcase", "summary": "Systems and routines for efficient, accountable office operations.", "body": "From filing and workflow design to supervision tools and service standards, we help offices run with clarity, measurable performance and reduced operational friction."},
    {"slug": "spot-check", "title": "Spot check", "icon": "bi-search", "summary": "Targeted reviews to verify compliance and safeguard resources.", "body": "Our spot-check assignments test whether policies and procedures are applied in practice. Findings are documented with practical recommendations and follow-up actions."},
    {"slug": "internal-audit", "title": "Internal audit", "icon": "bi-shield-check", "summary": "Independent assurance on controls, risk and process integrity.", "body": "We support internal audit planning, fieldwork and reporting aligned with professional standards—strengthening assurance without disrupting operations."},
    {"slug": "financial-accounting", "title": "Financial accounting", "icon": "bi-journal-text", "summary": "Accurate books, clean ledgers and reliable period closes.", "body": "Advisory and hands-on support for chart of accounts design, transaction processing discipline, reconciliations and period-end quality."},
    {"slug": "reporting", "title": "Reporting", "icon": "bi-file-earmark-bar-graph", "summary": "Clear management and donor-ready reports.", "body": "We help teams produce timely, decision-useful reports—management packs, donor formats and board summaries that match your stakeholder requirements."},
    {"slug": "software-installation-training", "title": "Software installation and training", "icon": "bi-pc-display", "summary": "Deploy tools correctly and train users to adopt them.", "body": "Installation, configuration, user training and go-live support for Knowsoft products and complementary financial systems."},
    {"slug": "baseline-assessment", "title": "Baseline assessment", "icon": "bi-clipboard-data", "summary": "Evidence-based starting point for reform and investment.", "body": "Structured assessments of systems, capacity and control environment to inform project design, financing decisions and improvement roadmaps."},
    {"slug": "financial-reporting", "title": "Financial reporting", "icon": "bi-graph-up", "summary": "High-quality statutory and management financial reporting.", "body": "Support for preparation, review and improvement of financial statements and management reporting frameworks."},
    {"slug": "financial-tools-erp-hardware", "title": "Supply of financial tools, ERPs and hardware", "icon": "bi-hdd-stack", "summary": "Software, ERPs and office hardware that match your needs.", "body": "We advise on and supply appropriate financial tools including ERP options, computers, printers and office shelving—aligned to budget and operational reality."},
    {"slug": "sop-development", "title": "SoP development", "icon": "bi-list-check", "summary": "Clear standard operating procedures your teams can follow.", "body": "Co-created SOPs for finance, admin and programme operations—practical, role-based and ready for training and compliance checks."},
    {"slug": "budget-preparation-guidance", "title": "Budget preparation and guidance", "icon": "bi-calculator", "summary": "Credible budgets with assumptions you can defend.", "body": "Facilitation and technical guidance for annual and project budgets, cost structures, assumptions and variance-ready monitoring frameworks."},
    {"slug": "cost-benefit-analysis", "title": "Cost benefit analysis", "icon": "bi-balance-scale", "summary": "Structured appraisal of options and investments.", "body": "We help decision-makers compare alternatives with transparent costs, benefits, risks and sensitivity analysis."},
    {"slug": "ifrs-training", "title": "IFRS training", "icon": "bi-book", "summary": "Practical IFRS capacity for finance professionals.", "body": "Training programmes on IFRS concepts and application, tailored to your sector and the standards most relevant to your reporting."},
]


def load_content():
    if not os.path.isfile(CONTENT_FILE):
        save_content(DEFAULT_CONTENT)
        return json.loads(json.dumps(DEFAULT_CONTENT))
    try:
        with open(CONTENT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # fill missing keys
        for k, v in DEFAULT_CONTENT.items():
            if k not in data:
                data[k] = v
        if not data.get("youtube_id"):
            data["youtube_id"] = DEFAULT_CONTENT.get("youtube_id", "")
        # Preserve admin-uploaded YouTube links — never replace with defaults if any exist
        existing_links = data.get("youtube_links")
        if isinstance(existing_links, str):
            existing_links = [x.strip() for x in existing_links.replace(",", "\n").splitlines() if x.strip()]
            data["youtube_links"] = existing_links
        if not data.get("youtube_links"):
            # only migrate/seed when completely empty
            links = []
            if data.get("youtube_id"):
                links.append(data["youtube_id"])
            if not links:
                links = list(DEFAULT_CONTENT.get("youtube_links") or [])
            data["youtube_links"] = links
        if not data.get("youtube_interval_sec"):
            data["youtube_interval_sec"] = DEFAULT_CONTENT.get("youtube_interval_sec", 45)
        if not data.get("software"):
            data["software"] = DEFAULT_CONTENT.get("software", [])
        return data
    except Exception:
        return json.loads(json.dumps(DEFAULT_CONTENT))


def save_content(data):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CONTENT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)



# ---------- Visitor tracking (persisted under instance/) ----------
VISITOR_LOG = os.path.join(DATA_DIR, "visitors.jsonl")
VISITOR_SKIP_PREFIXES = (
    "/static/", "/health", "/favicon", "/ks-portal",
)


def _client_ip():
    forwarded = request.headers.get("X-Forwarded-For", "") or ""
    if forwarded:
        return forwarded.split(",")[0].strip()[:80]
    return (request.remote_addr or "")[:80]


def log_visit(path=None):
    """Append one visit record. Safe no-op on errors."""
    try:
        path = path or request.path or "/"
        if any(path.startswith(p) for p in VISITOR_SKIP_PREFIXES):
            return
        if request.method not in ("GET", "HEAD"):
            return
        # skip obvious bots lightly
        ua = (request.headers.get("User-Agent") or "")[:300]
        rec = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "path": path[:200],
            "ip": _client_ip(),
            "ua": ua,
            "ref": (request.headers.get("Referer") or "")[:300],
            "lang": (request.headers.get("Accept-Language") or "")[:80],
        }
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(VISITOR_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception as e:
        print("visit log error:", e)


def read_visits(limit=500):
    rows = []
    if not os.path.isfile(VISITOR_LOG):
        return rows
    try:
        with open(VISITOR_LOG, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for line in lines[-limit:]:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                pass
        rows.reverse()  # newest first
    except Exception:
        pass
    return rows


def visit_stats(rows):
    total = len(rows)
    paths = {}
    ips = set()
    today = datetime.utcnow().strftime("%Y-%m-%d")
    today_count = 0
    for r in rows:
        p = r.get("path") or "/"
        paths[p] = paths.get(p, 0) + 1
        if r.get("ip"):
            ips.add(r["ip"])
        if (r.get("ts") or "").startswith(today):
            today_count += 1
    top_paths = sorted(paths.items(), key=lambda x: -x[1])[:12]
    return {
        "total_in_log": total,
        "unique_ips": len(ips),
        "today": today_count,
        "top_paths": top_paths,
    }


@app.before_request
def _track_visitor():
    try:
        log_visit()
    except Exception:
        pass


def admin_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not session.get("ks_admin"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return wrapped


def youtube_embed_id(url_or_id):
    """Extract YouTube video id from watch, shorts, youtu.be, embed, or raw id."""
    if not url_or_id:
        return ""
    s = (url_or_id or "").strip()
    # already a bare id
    if s and "://" not in s and "/" not in s and " " not in s and len(s) <= 20:
        return s.split("?")[0]
    if "youtube.com" in s or "youtu.be" in s or "youtube-nocookie.com" in s:
        if "shorts/" in s:
            return s.split("shorts/")[-1].split("?")[0].split("/")[0]
        if "v=" in s:
            return s.split("v=")[-1].split("&")[0].split("#")[0]
        if "youtu.be/" in s:
            return s.split("youtu.be/")[-1].split("?")[0].split("/")[0]
        if "embed/" in s:
            return s.split("embed/")[-1].split("?")[0].split("/")[0]
        if "live/" in s:
            return s.split("live/")[-1].split("?")[0].split("/")[0]
    return s.split("?")[0].split("/")[-1] if s else ""


def youtube_id_list(c):
    """Build ordered list of embed IDs from youtube_links and legacy youtube_id."""
    raw = c.get("youtube_links") or []
    if isinstance(raw, str):
        raw = [x.strip() for x in raw.replace(",", "\n").splitlines() if x.strip()]
    ids = []
    seen = set()
    for item in raw:
        yid = youtube_embed_id(item)
        if yid and yid not in seen:
            seen.add(yid)
            ids.append(yid)
    if not ids:
        yid = youtube_embed_id(c.get("youtube_id", ""))
        if yid:
            ids.append(yid)
    return ids


@app.context_processor
def inject_globals():
    c = load_content()
    yids = youtube_id_list(c)
    return {
        "year": datetime.utcnow().year,
        "company": "Knowsoft Consult LTD",
        "content": c,
        "services": SERVICES,
        "youtube_id": yids[0] if yids else "",
        "youtube_ids": yids,
        "youtube_interval_sec": int(c.get("youtube_interval_sec") or 45),
    }


@app.route("/")
def home():
    c = load_content()
    return render_template("index.html", software=c.get("software", [])[:3])


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/software")
def software():
    c = load_content()
    return render_template("software.html", items=c.get("software", []))


@app.route("/templates")
def templates_page():
    c = load_content()
    return render_template("templates_page.html", items=c.get("templates", []))


@app.route("/services")
def services_index():
    return render_template("services.html")


@app.route("/services/<slug>")
def service_detail(slug):
    svc = next((s for s in SERVICES if s["slug"] == slug), None)
    if not svc:
        abort(404)
    return render_template("service_detail.html", svc=svc)


@app.route("/gallery")
def gallery():
    c = load_content()
    return render_template("gallery.html", images=c.get("gallery", []))


@app.route("/clients")
def clients():
    c = load_content()
    return render_template("clients.html", clients=c.get("clients", []))


@app.route("/request-consulting", methods=["GET", "POST"])
def request_consulting():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        org = request.form.get("organization", "").strip()
        service = request.form.get("service", "").strip()
        message = request.form.get("message", "").strip()
        if not name or not email or not message:
            flash("Please complete the required fields.", "warning")
            return redirect(url_for("request_consulting"))
        with open(os.path.join(DATA_DIR, "consulting_requests.txt"), "a", encoding="utf-8") as f:
            f.write(f"\n--- {datetime.utcnow().isoformat()}Z ---\n")
            f.write(f"Name: {name}\nEmail: {email}\nPhone: {phone}\nOrg: {org}\nService: {service}\n{message}\n")
        flash("Thank you. Knowsoft Consult LTD has received your request.", "success")
        return redirect(url_for("request_consulting"))
    return render_template("request_consulting.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()
        if not name or not email or not message:
            flash("Please complete name, email and message.", "warning")
            return redirect(url_for("contact"))
        with open(os.path.join(DATA_DIR, "contact_leads.txt"), "a", encoding="utf-8") as f:
            f.write(f"\n--- {datetime.utcnow().isoformat()}Z ---\n")
            f.write(f"Name: {name}\nEmail: {email}\n{message}\n")
        flash("Thank you. We will respond shortly.", "success")
        return redirect(url_for("contact"))
    return render_template("contact.html")


@app.route("/downloads/<path:filename>")
def download_file(filename):
    folder = os.path.join(app.root_path, "static", "downloads")
    return send_from_directory(folder, filename, as_attachment=True)


# Hidden admin entry — linked only from footer "…with ease"
@app.route("/ks-portal/sign-in", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        password = request.form.get("password", "")
        c = load_content()
        if check_password_hash(c.get("admin_password_hash", ""), password):
            session["ks_admin"] = True
            flash("Welcome back.", "success")
            return redirect(url_for("admin_dashboard"))
        flash("Invalid credentials.", "danger")
    return render_template("admin_login.html")


@app.route("/ks-portal/sign-out")
def admin_logout():
    session.pop("ks_admin", None)
    return redirect(url_for("home"))


@app.route("/ks-portal")
@admin_required
def admin_dashboard():
    c = load_content()
    rows = read_visits(500)
    stats = visit_stats(rows)
    return render_template("admin_dashboard.html", c=c, visit_stats=stats)


@app.route("/ks-portal/save", methods=["POST"])
@admin_required
def admin_save():
    c = load_content()
    raw_links = request.form.get("youtube_links", "").strip()
    links = [ln.strip() for ln in raw_links.replace(",", "\n").splitlines() if ln.strip()]
    if links:
        c["youtube_links"] = links
        c["youtube_id"] = links[0]
    else:
        # Do not wipe existing links if admin left the field empty by mistake
        c["youtube_links"] = c.get("youtube_links") or []
        if c["youtube_links"]:
            c["youtube_id"] = c["youtube_links"][0] if isinstance(c["youtube_links"][0], str) else c.get("youtube_id", "")
    try:
        interval = int(request.form.get("youtube_interval_sec") or 45)
        c["youtube_interval_sec"] = max(15, min(120, interval))  # 15s–2min
    except Exception:
        c["youtube_interval_sec"] = 45
    c["hero_title"] = request.form.get("hero_title", c.get("hero_title", "")).strip()
    c["hero_subtitle"] = request.form.get("hero_subtitle", c.get("hero_subtitle", "")).strip()
    c["address"] = request.form.get("address", "Lagos, Nigeria").strip()
    c["email"] = request.form.get("email", "Knowsoftconsult@gmail.com").strip()
    c["phone"] = request.form.get("phone", "+2348081650914").strip()

    # Software rows
    names = request.form.getlist("sw_name")
    software = []
    for i, name in enumerate(names):
        if not name.strip():
            continue
        software.append({
            "id": request.form.getlist("sw_id")[i] if i < len(request.form.getlist("sw_id")) else f"item-{i}",
            "name": name.strip(),
            "tagline": request.form.getlist("sw_tagline")[i] if i < len(request.form.getlist("sw_tagline")) else "",
            "version": request.form.getlist("sw_version")[i] if i < len(request.form.getlist("sw_version")) else "1.0",
            "platform": request.form.getlist("sw_platform")[i] if i < len(request.form.getlist("sw_platform")) else "Web",
            "icon": request.form.getlist("sw_icon")[i] if i < len(request.form.getlist("sw_icon")) else "bi-app",
            "url": request.form.getlist("sw_url")[i] if i < len(request.form.getlist("sw_url")) else "",
            "download": request.form.getlist("sw_download")[i] if i < len(request.form.getlist("sw_download")) else "",
            "video_url": request.form.getlist("sw_video")[i] if i < len(request.form.getlist("sw_video")) else "",
            "badge": request.form.getlist("sw_badge")[i] if i < len(request.form.getlist("sw_badge")) else "",
        })
    if software:
        c["software"] = software

    # Clients
    client_names = request.form.getlist("client_name")
    clients = []
    for i, n in enumerate(client_names):
        if n.strip():
            sector = request.form.getlist("client_sector")[i] if i < len(request.form.getlist("client_sector")) else ""
            clients.append({"name": n.strip(), "sector": sector.strip()})
    if clients:
        c["clients"] = clients

    new_pw = request.form.get("new_password", "").strip()
    if new_pw and len(new_pw) >= 8:
        c["admin_password_hash"] = generate_password_hash(new_pw)

    save_content(c)
    flash("Site content saved.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/ks-portal/gallery", methods=["POST"])
@admin_required
def admin_gallery_upload():
    c = load_content()
    f = request.files.get("image")
    caption = request.form.get("caption", "").strip()
    if f and f.filename:
        name = secure_filename(f.filename)
        stamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        fname = f"{stamp}_{name}"
        f.save(os.path.join(UPLOAD_DIR, fname))
        gallery = c.get("gallery", [])
        gallery.insert(0, {"file": fname, "caption": caption})
        c["gallery"] = gallery[:48]
        save_content(c)
        flash("Image added to gallery.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/ks-portal/visitors")
@admin_required
def admin_visitors():
    rows = read_visits(800)
    stats = visit_stats(rows)
    return render_template(
        "admin_visitors.html",
        visits=rows[:200],
        stats=stats,
    )


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
