-- ReMedi migration for Aiven MySQL
-- Run this ONCE on your Aiven dashboard (Query Editor) or via any MySQL client
-- Order matters: alter tables before adding data

-- 1. Add 'user' combined role and keep legacy buyer/seller
ALTER TABLE users MODIFY COLUMN role ENUM('developer','admin','ngo','user','seller','buyer') NOT NULL;

-- 2. Add 'cancelled' and 'ready' statuses to requests
ALTER TABLE requests MODIFY COLUMN status ENUM('pending','approved','rejected','completed','cancelled','ready') DEFAULT 'pending';

-- 3. Add index on donations for faster seller queries (ignore if already exists)
ALTER TABLE donations ADD INDEX idxseller (seller_id,status);

-- 4. Add index on status_history for time-based queries (ignore if already exists)
ALTER TABLE status_history ADD INDEX idxtime (changed_at);

-- 5. Make inventory.ngo_id nullable (unverified seller medicines listed directly)
ALTER TABLE inventory MODIFY COLUMN ngo_id INT NULL;

-- 6. Sync existing pending donations into inventory if not already present
INSERT INTO inventory (donation_id,medicine_id,quantity_available,expiry_date,city,locality,condition_status,ngo_id)
SELECT donation_id,medicine_id,quantity,expiry_date,city,locality,condition_status,NULL
FROM donations
WHERE status='pending' AND donation_id NOT IN (SELECT donation_id FROM inventory);

-- 7. Convert existing buyer/seller demo accounts to 'user' role (optional but recommended)
-- UPDATE users SET role='user' WHERE role IN ('buyer','seller') AND email LIKE '%@example.com';

-- 8. Add 'pharmacy' role to users
ALTER TABLE users MODIFY COLUMN role ENUM('developer','admin','ngo','user','seller','buyer','pharmacy') NOT NULL;

-- 9. Add user_id column to pharmacies
ALTER TABLE pharmacies ADD COLUMN user_id INT NULL;
