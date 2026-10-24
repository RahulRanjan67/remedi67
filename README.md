# ReMedi

ReMedi is a medicine donation and access platform built around a simple idea: usable medicines should have a better path to people who need them instead of becoming unused stock.

This project connects people who can give away unused medicines with recipients, NGOs, and community pharmacies that can help those medicines reach someone who needs them safely.

---

## What ReMedi Does

A donor (user/seller) can list available medicines, an NGO verifies them against quality and expiry standards, and a recipient (user/buyer) can search verified inventory, request medicines, and track request status changes. Pharmacies provide a verified pickup/access point for secure hand-offs. The platform also supports urgent medicine shortages, NGO-recommended alternative medications, and audit logging.

### Roles & Access

- **User**: Combined role allowing members to both donate surplus medicine and request medicine when needed.
- **NGO Partner**: Verifies donor listings, manages inventory, oversees medicine requests, and suggests alternative medications.
- **Admin**: Municipal governance, safety compliance metrics, user directory, and NGO accreditation.
- **Developer**: System diagnostic console, latency testing, table counters, and cache inspection.
- **Pharmacy**: Registered physical pickup/exchange locations mapped across cities.

---

## Tech Stack

- **Backend**: Python 3.13, Flask 3.x, Flask-Login, Werkzeug
- **Database**: MySQL 8.0 (Aiven Cloud MySQL) via `mysql-connector-python` with connection resilience
- **Templating**: Jinja2 with responsive HTML5, modern CSS typography and components
- **Deployment**: Vercel Serverless Functions

---

## Database Architecture

ReMedi uses an 11-table relational schema:
- `users`: Accounts, roles, and authorization
- `ngo_profiles`: NGO accreditation details
- `pharmacies`: Registered physical exchange points
- `medicine_categories`: Therapeutic classifications
- `medicines`: Standard medicine catalogue
- `donations`: Medicines offered by donors
- `inventory`: Available stock managed by NGOs
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
- **NGO Partners**: `ngo1@example.com` through `ngo10@example.com` (Demo NGO 1 Partner .. Demo NGO 10 Partner)
- **Pending NGO**: `ngo.pending@example.com` (for testing admin accreditation queue)
- **Citizens / Users**:
  - `user1.city1@example.com` (Demo Citizen 1A)
  - `user2.city1@example.com` (Demo Citizen 1B)
  - `user1.city2@example.com` (Demo Citizen 2A)
  - `user2.city2@example.com` (Demo Citizen 2B)

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
