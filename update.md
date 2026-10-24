# ReMedi - Platform Update & Changelog (`update.md`)

This document tracks all architectural, performance, schema, and UI enhancements implemented across the ReMedi platform.

---

## 1. Performance & Latency Optimizations

### 1.1 Database Connection Pooling (`db.py`)
- **Previous Issue**: Every database operation called `mysql.connector.connect()`, performing a new TCP handshake and SSL negotiation per query. A typical page load triggered 4-6 queries, causing high latency (~100-300ms overhead per query).
- **Solution**: Implemented connection pooling using `mysql.connector.pooling.MySQLConnectionPool` with a pool size of 5. Pooled connections are automatically reused and returned to the pool upon closure via `conn.close()`. A standalone `connect()` function remains available for schema initialization and database migration utilities (`init_db.py`).

### 1.2 `urgent.refresh()` Throttling (`models/urgent.py`)
- **Previous Issue**: `urgent.refresh()` was executed on every visitor request to `/search`, triggering an unindexed correlated `UPDATE` subquery against the entire city inventory even when no inventory had changed.
- **Solution**: Added time-based throttling to `models/urgent.py`. Cache tracking prevents the correlated update from firing more than once every 60 seconds per city partition.

### 1.3 Unread Notification Counter Caching (`app.py`)
- **Previous Issue**: The Flask context processor called `notif.unread(user_id)` on every HTTP request for authenticated users.
- **Solution**: Added a 30-second TTL in Flask `session` (`unread_ts`) so consecutive page navigation reuses the cached count without executing additional database queries.

---

## 2. Unified User Role Architecture

### 2.1 Combining Buyer and Seller into `user`
- **Previous Issue**: Strict segregation into either `buyer` or `seller` forced users to create two accounts if they had surplus medicines to donate and also needed medicines for family members.
- **Solution**:
  - Added `'user'` to the `users.role` ENUM in `database/schema.sql` and `database/migrate.sql`.
  - Registration form now creates accounts with `role='user'` by default.
  - Route authorization across `routes/buyer.py` and `routes/seller.py` allows both `user` and legacy roles (`@needrole("buyer", "user")` and `@needrole("seller", "user")`).
  - Added a unified User Dashboard (`templates/buyer/dashboard.html`) displaying both active request metrics and donation batches side by side.

---

## 3. Role-Based Navigation & Access Control

### 3.1 Distinct Role Views in Navigation (`templates/base.html`)
- **Previous Issue**: Menu options were identical or incomplete for different roles, and NGO accounts had options to donate medicines which conflicted with quality assurance standards.
- **Solution**:
  - **Public (Unauthenticated)**: Home, Search Medicines, Notice Board, Pharmacies, Login, Register.
  - **User (Combined)**: Dashboard, Search, Donate, My Donations, My Requests, Urgent Needs, Notice Board, Pharmacies, Contacts.
  - **NGO Partner**: Dashboard, Search & Buy, Verify Donations, Manage Requests, Stock Inventory, My Procurements, Seller Contacts, Pharmacies, Notice Board.
  - **Government / Auditor (Admin)**: Governance Portal, User Registry, Audit Log, Pharmacies, Notice Board.
  - **Developer**: Dev Diagnostic Console, Governance, Users, Audit Log, Search, Notice Board.

### 3.2 Secure Pharmacy Registration (`routes/common.py`)
- **Previous Issue**: Pharmacy registration endpoint was public without authentication, allowing unverified public submissions.
- **Solution**: Added `@login_required` to `pharmadd()`.

---

## 4. Distinct Admin vs. Developer Role Split

### 4.1 Admin Governance & Audit Portal (`templates/admin/dashboard.html`, `templates/admin/audit_log.html`)
- Tailored for government health officials, auditing firms, and platform administrators.
- Added municipal compliance tracking: city-by-city breakdown of verified safe batches vs. rejected/quarantined batches.
- Added pending NGO accreditation queue with registration credentials.
- Added live regulatory audit trail viewing (`status_history`).

### 4.2 Developer Diagnostic Console (`templates/admin/dev_dashboard.html`, `routes/admin.py`)
- Distinct engineering interface with dark console styling.
- Live database diagnostics: engine details, active host/port, connection pool status, Vercel/local runtime detection.
- Live table counters showing row counts across all 11 MySQL tables.
- Live status transition event stream showing last 25 system events.
- Background dispatch actions:
  - Database ping latency test (returns query execution roundtrip in milliseconds).
  - Manual trigger for urgent needs matching.
  - Session notification cache flush.

---

## 5. Registration & City Scoping Fixes

### 5.1 Registration Friction Reduced (`templates/register.html`, `routes/auth.py`)
- Pincode, locality, and phone number are now optional in HTML and backend validation.
- City remains required to enforce safe local medicine circles.
- Fixed server-side validation consistency.

### 5.2 City Scope Synchronization (`util.py`, `routes/auth.py`)
- Logging in now synchronizes `session['city']` with the user's registered home city.
- Logging out flushes `session['city']` to prevent session leaks between users on shared browsers.
- Configurable cities: `config.py` now loads cities from `REMEDI_CITIES` or `CITIES` environment variables with fallback to default demo cities.

---

## 6. Logic Fixes & Enhancements

### 6.1 Category Filtering in Search (`templates/inventory.html`, `routes/common.py`)
- Added category dropdown to the inventory search form with category options from `medicine_categories`.

### 6.2 "Also Needed" Badge on Inventory (`templates/inventory.html`, `models/inv.py`)
- `inv.needed(city)` highlights medicines currently in open urgent need, allowing buyers or NGOs to prioritize distribution.

### 6.3 Dedicated "Cancelled" and "Ready" Statuses (`models/req.py`, `routes/ngo.py`)
- Added `'cancelled'` to request status ENUM so cancellation no longer skews rejection metrics.
- Added `'ready'` status so NGOs can mark approved requests as "Ready for Pickup" prior to final completion.

### 6.4 Concurrency Fix on Status Transitions (`models/req.py`)
- Wrapped request status updates in database transactions using `SELECT ... FOR UPDATE` to prevent race conditions.

### 6.5 Notice Board Member Differentiation (`templates/notice_board.html`)
- Unauthenticated visitors see public urgent needs with sign-in prompts.
- Authenticated members see recent incoming verified donation alerts in their city with direct search links.

### 6.6 Removal of All Emojis
- Replaced all emojis across templates, CSS, and JS with clean typography, pill badges, and text indicators.

---

## 7. Open Market, NGO Procurement & Privacy Overhaul

### 7.1 Deduplication on Urgent Needs (`models/urgent.py`, `routes/buyer.py`)
- Server-side check in `urgent.create()` blocks duplicate open postings for the same buyer, medicine, and city.
- Throws clear user-facing feedback if an identical urgent need is already open.
- Validates quantity requiring `qty >= 1`.

### 7.2 Contact Request Status Visibility on Notice Board and Search (`templates/notice_board.html`, `templates/inventory.html`, `models/contact.py`, `routes/common.py`)
- **For Buyers**:
  - `inventory.html` shows real-time contact status (`Contact Pending`, `Contact Approved` with direct contact info link, `Contact Declined`) replacing the raw "Contact Donor" button when a request has already been sent.
  - `notice_board.html` features a dedicated "My Contact Requests" section showing real-time status of outreach to donors, plus inline contact status on inflow alert rows.
- **For Sellers**:
  - `notice_board.html` now includes an "Incoming Contact Requests" panel displaying active buyer/NGO requests with one-click "Approve" and "Reject" actions directly from the notice board.

### 7.3 NGO Can Buy Medicine from Sellers (`routes/buyer.py`, `templates/base.html`, `templates/inventory.html`, `templates/ngo/dashboard.html`)
- Extended procurement capabilities to the `ngo` role.
- NGOs can now search all active medicine listings, submit procurement requests, and contact donors/sellers directly via `buyer.ask`, `buyer.reach`, `buyer.reqs`, and `buyer.contacts`.
- Added "Search & Buy", "My Procurements", and "Seller Contacts" links to the NGO navigation bar and NGO dashboard.

### 7.4 NGO Privacy: Seller Location Only (`models/don.py`, `templates/ngo/verify_donations.html`)
- For donor privacy, NGOs can no longer view donor personal names or contact information during verification.
- `don.pending()` query strips seller identity joins and returns strictly locality and city.
- `verify_donations.html` displays only "Seller Location" (e.g., `Main Street, City`), preventing identity exposure before voluntary contact approval.

### 7.5 Optional NGO Verification & Recommended Batch System (`models/don.py`, `models/inv.py`, `templates/inventory.html`)
- Medicines listed by sellers are now immediately available in inventory without requiring prior NGO verification.
- `inventory.ngo_id` is now nullable (`DEFAULT NULL`) in schema and migrations.
- When an NGO verifies a medicine, it is upgraded to **Recommended** status with a **Verified Batch** endorsement badge (`Batch: <batch_number>`).
- Search results prioritize NGO-recommended batches at the top of listings, while unverified direct seller listings remain discoverable with a `Direct Listing` badge.
- Added self-request prevention guard so sellers cannot request or contact their own listings.

---

## 8. Database Migration Instructions for Live Aiven Instance

Run `database/migrate.sql` in the **Aiven MySQL Query Editor**:

```sql
-- 1. Combined 'user' role
ALTER TABLE users MODIFY COLUMN role ENUM('developer','admin','ngo','user','seller','buyer') NOT NULL;

-- 2. Added request statuses
ALTER TABLE requests MODIFY COLUMN status ENUM('pending','approved','rejected','completed','cancelled','ready') DEFAULT 'pending';

-- 3. Optimization indexes
ALTER TABLE donations ADD INDEX IF NOT EXISTS idxseller (seller_id,status);
ALTER TABLE status_history ADD INDEX IF NOT EXISTS idxtime (changed_at);

-- 4. Nullable NGO ID on inventory for instant seller listings
ALTER TABLE inventory MODIFY COLUMN ngo_id INT NULL;

-- 5. Sync existing pending donations into live inventory
INSERT INTO inventory (donation_id,medicine_id,quantity_available,expiry_date,city,locality,condition_status,ngo_id)
SELECT donation_id,medicine_id,quantity,expiry_date,city,locality,condition_status,NULL
FROM donations
WHERE status='pending' AND donation_id NOT IN (SELECT donation_id FROM inventory);
```
