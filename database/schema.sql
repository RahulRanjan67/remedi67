CREATE TABLE IF NOT EXISTS users (
  user_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(150) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  role ENUM('developer','admin','ngo','seller','buyer') NOT NULL,
  phone VARCHAR(20),
  city VARCHAR(100),
  pincode VARCHAR(10),
  locality VARCHAR(200),
  is_approved TINYINT(1) DEFAULT 1,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idxcity (city,role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE IF NOT EXISTS ngo_profiles (
  ngo_id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT UNIQUE NOT NULL,
  ngo_name VARCHAR(200) NOT NULL,
  registration_number VARCHAR(100),
  city VARCHAR(100),
  locality VARCHAR(200),
  FOREIGN KEY (user_id) REFERENCES users(user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE IF NOT EXISTS pharmacies (
  pharmacy_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(200) NOT NULL,
  address VARCHAR(500) NOT NULL,
  city VARCHAR(100) NOT NULL,
  pincode VARCHAR(10) NOT NULL,
  phone VARCHAR(20),
  is_active TINYINT(1) DEFAULT 1,
  INDEX idxcity (city,pincode)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE IF NOT EXISTS medicine_categories (
  category_id INT AUTO_INCREMENT PRIMARY KEY,
  category_name VARCHAR(100) UNIQUE NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE IF NOT EXISTS medicines (
  medicine_id INT AUTO_INCREMENT PRIMARY KEY,
  medicine_name VARCHAR(200) NOT NULL,
  category_id INT,
  description TEXT,
  FOREIGN KEY (category_id) REFERENCES medicine_categories(category_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE IF NOT EXISTS donations (
  donation_id INT AUTO_INCREMENT PRIMARY KEY,
  seller_id INT NOT NULL,
  medicine_id INT NOT NULL,
  quantity INT NOT NULL,
  batch_number VARCHAR(100),
  expiry_date DATE NOT NULL,
  city VARCHAR(100) NOT NULL,
  locality VARCHAR(200),
  condition_status ENUM('sealed','opened','partial') DEFAULT 'sealed',
  status ENUM('pending','verified','rejected') DEFAULT 'pending',
  rejection_reason TEXT,
  ngo_id INT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (seller_id) REFERENCES users(user_id),
  FOREIGN KEY (medicine_id) REFERENCES medicines(medicine_id),
  FOREIGN KEY (ngo_id) REFERENCES users(user_id),
  INDEX idxcity (city,status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE IF NOT EXISTS inventory (
  inventory_id INT AUTO_INCREMENT PRIMARY KEY,
  donation_id INT NOT NULL,
  medicine_id INT NOT NULL,
  quantity_available INT NOT NULL,
  expiry_date DATE NOT NULL,
  city VARCHAR(100) NOT NULL,
  locality VARCHAR(200),
  condition_status ENUM('sealed','opened','partial') DEFAULT 'sealed',
  ngo_id INT NOT NULL,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (donation_id) REFERENCES donations(donation_id),
  FOREIGN KEY (medicine_id) REFERENCES medicines(medicine_id),
  FOREIGN KEY (ngo_id) REFERENCES users(user_id),
  INDEX idxcity (city,medicine_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE IF NOT EXISTS requests (
  request_id INT AUTO_INCREMENT PRIMARY KEY,
  buyer_id INT NOT NULL,
  inventory_id INT NOT NULL,
  quantity_requested INT NOT NULL,
  fetch_method ENUM('direct','ngo','pharmacy') DEFAULT 'ngo',
  pharmacy_id INT,
  status ENUM('pending','approved','rejected','completed') DEFAULT 'pending',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (buyer_id) REFERENCES users(user_id),
  FOREIGN KEY (inventory_id) REFERENCES inventory(inventory_id),
  FOREIGN KEY (pharmacy_id) REFERENCES pharmacies(pharmacy_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE IF NOT EXISTS medicine_recommendations (
  rec_id INT AUTO_INCREMENT PRIMARY KEY,
  request_id INT NOT NULL,
  ngo_id INT NOT NULL,
  original_medicine_id INT NOT NULL,
  recommended_medicine_id INT NOT NULL,
  pharmacy_id INT NOT NULL,
  reason TEXT,
  status ENUM('pending','accepted','rejected') DEFAULT 'pending',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (request_id) REFERENCES requests(request_id),
  FOREIGN KEY (ngo_id) REFERENCES users(user_id),
  FOREIGN KEY (original_medicine_id) REFERENCES medicines(medicine_id),
  FOREIGN KEY (recommended_medicine_id) REFERENCES medicines(medicine_id),
  FOREIGN KEY (pharmacy_id) REFERENCES pharmacies(pharmacy_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE IF NOT EXISTS status_history (
  history_id INT AUTO_INCREMENT PRIMARY KEY,
  entity_type VARCHAR(50) NOT NULL,
  entity_id INT NOT NULL,
  old_status VARCHAR(50),
  new_status VARCHAR(50) NOT NULL,
  changed_by INT,
  changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idxent (entity_type,entity_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE IF NOT EXISTS notifications (
  notification_id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  message TEXT NOT NULL,
  is_read TINYINT(1) DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(user_id),
  INDEX idxuser (user_id,is_read)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE IF NOT EXISTS contact_requests (
  contact_request_id INT AUTO_INCREMENT PRIMARY KEY,
  buyer_id INT NOT NULL,
  seller_id INT NOT NULL,
  donation_id INT NOT NULL,
  status ENUM('pending','approved','rejected') DEFAULT 'pending',
  requested_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  responded_at DATETIME,
  FOREIGN KEY (buyer_id) REFERENCES users(user_id),
  FOREIGN KEY (seller_id) REFERENCES users(user_id),
  FOREIGN KEY (donation_id) REFERENCES donations(donation_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE IF NOT EXISTS urgent_needs (
  urgent_id INT AUTO_INCREMENT PRIMARY KEY,
  buyer_id INT NOT NULL,
  medicine_id INT NOT NULL,
  quantity_required INT NOT NULL,
  city VARCHAR(100) NOT NULL,
  locality VARCHAR(200),
  status ENUM('open','fulfilled') DEFAULT 'open',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (buyer_id) REFERENCES users(user_id),
  FOREIGN KEY (medicine_id) REFERENCES medicines(medicine_id),
  INDEX idxcity (city,status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
INSERT IGNORE INTO medicine_categories (category_id,category_name) VALUES
(1,'Painkiller'),(2,'Antibiotic'),(3,'Vitamin'),(4,'Diabetes'),(5,'Cardiac'),(6,'Antifungal'),(7,'Antihistamine'),(8,'Other'),(9,'Gastrointestinal'),(10,'Respiratory'),(11,'Dermatology'),(12,'Thyroid');
INSERT IGNORE INTO medicines (medicine_id,medicine_name,category_id,description) VALUES
(1,'Paracetamol 500mg',1,'Common pain and fever relief'),
(2,'Ibuprofen 400mg',1,'NSAID pain reliever'),
(3,'Amoxicillin 250mg',2,'Prescription antibiotic'),
(4,'Azithromycin 500mg',2,'Macrolide antibiotic'),
(5,'Vitamin C 500mg',3,'Vitamin C supplement'),
(6,'Vitamin D3 1000IU',3,'Vitamin D3 supplement'),
(7,'Metformin 500mg',4,'Common oral diabetes medicine'),
(8,'Insulin Glargine',4,'Long-acting insulin'),
(9,'Atorvastatin 10mg',5,'Cholesterol management medicine'),
(10,'Amlodipine 5mg',5,'Blood-pressure medicine'),
(11,'Fluconazole 150mg',6,'Antifungal medicine'),
(12,'Cetirizine 10mg',7,'Antihistamine for allergies'),
(13,'Omeprazole 20mg',9,'Acid-reducing medicine'),
(14,'Pantoprazole 40mg',9,'Acid-reducing medicine'),
(15,'ORS Lemon Sachet',8,'Oral rehydration salts'),
(16,'Salbutamol Inhaler',10,'Reliever inhaler'),
(17,'Levocetirizine 5mg',7,'Antihistamine for allergy symptoms'),
(18,'Montelukast 10mg',10,'Respiratory allergy medicine'),
(19,'Clotrimazole 1% Cream',11,'Topical antifungal cream'),
(20,'Hydrocortisone 1% Cream',11,'Topical corticosteroid cream'),
(21,'Levothyroxine 50mcg',12,'Thyroid hormone replacement'),
(22,'Levothyroxine 75mcg',12,'Thyroid hormone replacement'),
(23,'Domperidone 10mg',9,'Medicine used for nausea and motility'),
(24,'Calcium + Vitamin D3',3,'Calcium and vitamin supplement');
