ReMedi

ReMedi is a medicine donation and access platform built around a simple idea: usable medicines should have a better path to people who need them instead of becoming unused stock.

This project started as a Flask learning experiment. While learning backend development, I wanted to put the basics into something real rather than isolated practice code. I built the routes, worked through the SQL queries, connected the database, handled forms and sessions, and gradually turned the idea into a working application. Around the same period, SIH work pushed me to move early toward FastAPI, but ReMedi remained the Flask experiment I had originally imagined while learning backend fundamentals.

I used AI assistance mainly for deployment, debugging, troubleshooting and fixing some flawed parts of the code. The project was still useful to me because I had to understand the routes, SQL, database relationships and application flow well enough to keep building and correcting it.

What ReMedi does

ReMedi connects people who can give away unused medicines with people, NGOs and pharmacies that can help those medicines reach someone who needs them.

A seller can donate available medicines, an NGO can verify and manage them, and a buyer can search inventory, request medicines and follow the request through its status changes. Pharmacies provide a practical hand-off point when direct collection is not suitable. The platform also supports urgent medicine needs, recommendations, contact requests, notifications and status history.

The bigger purpose of the project is what interested me most: taking something as ordinary as an unused medicine and creating a system around it so that availability, verification, requests and delivery are not left to chance.

Roles

Buyer — searches available medicines, sends requests, raises urgent needs and manages recommendations.

Seller — lists medicines for donation and tracks submitted donations and contact requests.

NGO — verifies donations, manages inventory, handles buyer requests and can recommend alternatives.

Admin — manages users, approvals and the overall platform.

Developer — provides a separate system-level dashboard for development/administrative visibility.

Pharmacy — acts as a registered medicine pickup/access point rather than a separate login role.

Tech used

Python

Flask — application framework and routing

Flask-Login — authentication and session-based login

MySQL — relational database

mysql-connector-python — database connectivity

Jinja2 — server-side HTML templates through Flask

Werkzeug — password hashing and request/application utilities

HTML, CSS, JavaScript — frontend and interaction

Vercel — deployment

The application intentionally keeps the backend straightforward: Flask routes call small model functions, model functions run SQL through shared database helpers, and Jinja2 renders the result.

Database structure

ReMedi uses a 13-table MySQL database built around users, medicines, donations and requests:

users → accounts and roles
ngo_profiles → NGO details
pharmacies → registered pickup/access points
medicine_categories → medicine classification
medicines → medicine catalogue
donations → medicines offered by sellers
inventory → verified medicines available through NGOs
requests → buyer requests against inventory
medicine_recommendations → alternative medicine suggestions
status_history → status changes over time
notifications → user notifications
contact_requests → buyer-seller contact workflow
urgent_needs → urgent medicine requirements

The database is the core of the application rather than just a place to store login data. Most features are built around relationships between these tables, foreign keys, status fields, filtering and SQL queries.

GitHub updates after the first version

Two additional updates were made after the initial GitHub version:

Deployment + demo data: fixed environment variables not loading correctly on Vercel and replaced real-looking sample identities with safe demo data.

Cleanup: fixed broken links and routes and cleaned up the CSS and HTML pages.

What I learned

ReMedi taught me more than just Flask syntax. I learned how routes, authentication, templates, SQL and database relationships actually come together in one application. I also got practical experience debugging problems that only appeared after deployment, working with environment variables, structuring a multi-role application and thinking about a feature from both the UI and database side.

Most importantly, it changed how I look at backend development. Writing a route is easy; making many routes, roles, tables and workflows behave like one coherent system is where the real learning started.

Current status

ReMedi is a working prototype and is deployed on Vercel. One issue still remains: some pages are slower to load than I want, especially during the deployed experience. I have identified this as the next area I need to work on and improve.
