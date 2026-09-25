# ReMedi

Medicine donation platform connecting sellers, NGOs, buyers and pharmacies, city by city. Made using Flask at its core , this app seeks to solve the issue of leftover medicines going to waste while those in need stranded. This project was my experimentation using flask and many of codes have been completely manually written by me especially the routes etc.

Sample login (any account, password `remedi123`): `dev@remedi.in` (developer),
`admin@remedi.in` (admin), `bhopal.seller1@remedi.in`, `bhopal.buyer1@remedi.in`,
`ngo.seva@remedi.in` (Bhopal NGO), etc. — see `database/sample.sql` for the full list,
one seller/buyer pair and one NGO per city.


## Geofencing rules

- Buyers, sellers and admins see only the city they've selected (medicines in
  search, the notice board, and pharmacies are all filtered by that city).
- A seller's or buyer's own history (their donations, requests, contacts) is
  never filtered by city — it's their own record regardless of where they
  posted it from.
- NGO and developer accounts are not restricted by any city: their dashboards,
  search, and the NGO donation-verification queue show every city at once.
