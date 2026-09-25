# ReMedi

Medicine donation platform connecting sellers, NGOs, buyers and pharmacies, city by city.

## Project layout

Everything in this folder is ReMedi's own code. Third-party packages are never installed
here — see "Local setup" below for keeping them in a sibling folder outside this repo.

```
remedi/
  app.py                Flask entrypoint (exposes `app`, what Vercel looks for)
  config.py              Env/config loader
  db.py                   MySQL connection + query helpers
  util.py                 Shared helpers (city matching, expiry, roles)
  models/                 One file per table/domain, plain functions
  routes/                 One blueprint per file
  templates/              Jinja2 templates
  public/                 Static assets (css/js) — served from here on Vercel too
  database/
    schema.sql            Table definitions
    sample.sql             Optional demo data (10 cities)
  init_db.py               Run once to create tables (and optionally load sample data)
  tests/test_logic.py       Pure-logic unit tests, no DB needed
  requirements.txt
  vercel.json
  .env.example
```

## Local setup

Keep your virtual environment **outside** this folder, as a sibling directory, so the
repo you push to GitHub never contains installed packages:

```bash
cd ..                              # one level above remedi/
python -m venv remedi-venv         # lives next to remedi/, not inside it
source remedi-venv/bin/activate    # Windows: remedi-venv\Scripts\activate
cd remedi
pip install -r requirements.txt
cp .env.example .env               # fill in your local MySQL credentials
python init_db.py --seed           # creates tables + loads sample data for all 10 cities
python app.py                      # http://127.0.0.1:5000
```

Sample login (any account, password `remedi123`): `dev@remedi.in` (developer),
`admin@remedi.in` (admin), `bhopal.seller1@remedi.in`, `bhopal.buyer1@remedi.in`,
`ngo.seva@remedi.in` (Bhopal NGO), etc. — see `database/sample.sql` for the full list,
one seller/buyer pair and one NGO per city.

## Deploying to GitHub + Vercel

1. Push this folder as a GitHub repo (the `.gitignore` already excludes `.env`,
   `venv/`, and anything named `*-venv/` or `*-libs/`, so nothing outside the app
   itself gets committed).
2. In Vercel, import the repo. Vercel auto-detects Flask from `app.py` — no build
   config needed (`vercel.json` here only raises the function timeout to 20s for
   slower first-time DB connections).
3. In the Vercel project's Environment Variables, set: `DB_HOST`, `DB_PORT`,
   `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `SECRET_KEY` (a long random string — the
   app refuses to boot on Vercel without one), and `DB_SSL_CA` if your MySQL
   host requires a CA file (commit the `.pem` into the repo and point to its
   relative path).
4. Point `DB_HOST` at a MySQL host reachable from the public internet — Vercel's
   functions can't reach `localhost`. Any managed MySQL works (PlanetScale,
   Railway, Aiven, AWS RDS, etc.); most require SSL, hence `DB_SSL_CA`.
5. Before or after the first deploy, run `init_db.py` against that same host from
   your machine (point `.env` at it temporarily) to create the schema, e.g.
   `python init_db.py --seed`.
6. Deploy. Static files in `public/` are served by Vercel's CDN directly at
   `/css/style.css` and `/js/script.js` — the same paths Flask serves locally,
   so nothing else changes between environments.

Note: each request opens its own short-lived MySQL connection (`db.py`), which
keeps the code simple but adds a little latency on a cold serverless function.
For a class project this is fine; if it ever needs to scale, that's the first
thing to revisit (e.g. a connection pool).

## Geofencing rules

- Buyers, sellers and admins see only the city they've selected (medicines in
  search, the notice board, and pharmacies are all filtered by that city).
- A seller's or buyer's own history (their donations, requests, contacts) is
  never filtered by city — it's their own record regardless of where they
  posted it from.
- NGO and developer accounts are not restricted by any city: their dashboards,
  search, and the NGO donation-verification queue show every city at once.

## Tests

```bash
python -m unittest tests/test_logic.py -v
```

Covers the pure-logic helpers (city matching, expiry classification, donor
tiers). It doesn't touch the database.
