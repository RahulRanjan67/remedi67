# ReMedi

ReMedi is a medicine donation and access platform built around a simple idea: usable medicines should have a better path to people who need them instead of becoming unused stock.

This project connects people who can give away unused medicines with recipients, NGOs, and community pharmacies that can help those medicines reach someone who needs them safely.

---

## What ReMedi Does

A donor (user/seller) can list available medicines, an NGO verifies them against quality and expiry standards, and a recipient (user/buyer) can search verified inventory, request medicines, and track request status changes. Pharmacies provide a verified pickup/access point for secure hand-offs. The platform also supports urgent medicine shortages, NGO-recommended alternative medications, and audit logging.

### Roles & Access

- **User**: Combined role allowing members to both donate surplus medicine and request medicine when needed.
- **NGO Partner**: Verifies donor listings, manages inventory, oversees medicine requests, and suggests alternative medications.
- **Pharmacy**: Direct dispensary login role to manage pickup queues, verify patient passes, and confirm medication handovers.
- **Admin**: Municipal governance, safety compliance metrics, user directory, and NGO accreditation.
- **Developer**: System diagnostic console, latency testing, table counters, manual expiry quarantine scans, and cache inspection.

---

## Key Features & Enhancements

1. **Digital QR Code Engine**:
   - **Pickup Pass (QR)**: Printable digital pass with high-density vector QR code for patients to present at partner dispensaries or NGO centers.
   - **Package Donation Labels**: Printable QR stickers for donors to attach to medicine packages for rapid receiving scans.
   - **Dispensary GPS QR Codes**: Instant turn-by-turn navigation QR codes on all pharmacy directory cards.

2. **Urgent Needs Matching & Pre-allocation**:
   - Live shortage alerts surfaced to donors during medicine listing.
   - One-click "Fulfill Need" pre-population of medicine names and quantities.
   - Instant notification dispatch to waiting patients when a matching donation is submitted in their city.

3. **Pharmacist Dispensary Operations**:
   - Dedicated `/pharmacy/dashboard` for designated pharmacy partners.
   - Quick QR Pass Lookup (`/pharmacy/verify-pass`) to confirm patient identity and dispense medications with one click.
   - Real-time status transitions (`approved` -> `ready` -> `completed`) with buyer notification alerts.

4. **Automated Expiry Quarantining Cron**:
   - Scheduled endpoint at `/cron/quarantine` (compatible with Vercel Cron or external schedulers).
   - In-memory periodic background check on active requests.
   - Manual on-demand scan via the Developer Diagnostic Console (`/admin/developer/quarantine-expired`).
   - Automatically zeroes expired inventory, logs audit history, and safely cancels pending requests with patient notifications.

---

## Tech Stack

- **Backend**: Python 3.13, Flask 3.x, Flask-Login, Werkzeug
- **Database**: MySQL 8.0 (Aiven Cloud MySQL) via `mysql-connector-python` with connection resilience
- **QR Codes**: Native `qrcode` SVG path generation (~6KB lightweight SVGs without external image files)
- **Templating**: Jinja2 with responsive HTML5, modern CSS typography and components
- **Deployment**: Vercel Serverless Functions

---

## Database Architecture

ReMedi uses an 11-table relational schema:
- `users`: Accounts, roles (`user`, `ngo`, `pharmacy`, `admin`, `developer`), and authorization
- `ngo_profiles`: NGO accreditation details
- `pharmacies`: Registered physical exchange points and dispensary partner accounts
- `medicine_categories`: Therapeutic classifications
- `medicines`: Standard medicine catalogue
- `donations`: Medicines offered by donors
- `inventory`: Available stock managed by NGOs and direct donors
- `requests`: User requests for medicine
- `medicine_recommendations`: Alternative medicine suggestions by NGOs
- `status_history`: Complete audit trail of entity state transitions
- `notifications`: User alert notifications
- `contact_requests`: Direct donor-recipient communication requests
- `urgent_needs`: High-priority patient medicine shortages

---

## Local Setup

Keep your virtual environment outside this directory so build artifacts are isolated:

```bash
# In the parent directory
python -m venv remedi-venv
remedi-venv\Scripts\activate   # Linux/macOS: source remedi-venv/bin/activate

# In the remedi directory
cd remedi
pip install -r requirements.txt
cp .env.example .env            # Configure your MySQL credentials
python init_db.py --seed        # Initializes tables and loads demo data
python app.py                   # Starts local server at http://127.0.0.1:5000
```

---

## Demo Accounts

All demo accounts in `database/sample.sql` use synthetic demo data with password `remedi123`:

- **Developer**: `dev@example.com`
- **Administrator**: `admin@example.com`
- **Pharmacists**: `pharm1@example.com` through `pharm10@example.com` (Demo Pharmacist 1A .. 10A)
- **NGO Partners**: `ngo1@example.com` through `ngo10@example.com` (Demo NGO 1 Partner .. Demo NGO 10 Partner)
- **Pending NGO**: `ngo.pending@example.com` (for testing admin accreditation queue)
- **Citizens / Users**:
  - `user1.city1@example.com` (Demo Citizen 1A)
  - `user2.city1@example.com` (Demo Citizen 1B)
  - `user1.city2@example.com` (Demo Citizen 2A)
  - `user2.city2@example.com` (Demo Citizen 2B)
  - (through `user2.city10@example.com`)

---

## Deploying to Vercel

1. Configure environment variables in the Vercel dashboard:
   - `DB_HOST`: Hostname of your cloud MySQL instance (e.g. Aiven)
   - `DB_PORT`: 3306 (or cloud port)
   - `DB_NAME`: Database name (e.g. `remedi`)
   - `DB_USER`: Database username
   - `DB_PASSWORD`: Database password
   - `SECRET_KEY`: A strong random string
   - `DB_SSL_CA`: Relative path to CA certificate (`database/ca.pem`)
2. Deploy the project. Vercel auto-detects `app.py` via `vercel.json`.
