-- Ekvira Transport Dashboard Database Schema (MySQL Compatible)

CREATE DATABASE IF NOT EXISTS smart_transport;
USE smart_transport;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'Manager', -- 'Admin' or 'Manager'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 2. Drivers Table
CREATE TABLE IF NOT EXISTS drivers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    mobile VARCHAR(15) NOT NULL,
    license_number VARCHAR(50) NOT NULL UNIQUE,
    license_expiry DATE NOT NULL,
    address TEXT,
    aadhaar_number VARCHAR(12) NOT NULL UNIQUE,
    joining_date DATE NOT NULL,
    salary DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Active', -- 'Active', 'Inactive', 'On Trip'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 3. Vehicles Table
CREATE TABLE IF NOT EXISTS vehicles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_number VARCHAR(20) NOT NULL UNIQUE,
    vehicle_name VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    registration_number VARCHAR(50) NOT NULL UNIQUE,
    capacity DECIMAL(5, 2) NOT NULL, -- in tons
    driver_id INT UNIQUE,
    insurance_date DATE NOT NULL,
    fitness_date DATE NOT NULL,
    puc_date DATE NOT NULL,
    status VARCHAR(25) NOT NULL DEFAULT 'Idle', -- 'Active', 'Idle', 'Maintenance'
    current_latitude DECIMAL(10, 8) DEFAULT 22.9734, -- Default regional location
    current_longitude DECIMAL(11, 8) DEFAULT 78.6569,
    odometer DECIMAL(10, 2) NOT NULL DEFAULT 0.0,
    fuel_type VARCHAR(20) NOT NULL DEFAULT 'Diesel',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (driver_id) REFERENCES drivers(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- Update drivers to assign vehicle_id
ALTER TABLE drivers ADD COLUMN vehicle_id INT UNIQUE;
ALTER TABLE drivers ADD CONSTRAINT fk_driver_vehicle FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE SET NULL;

-- 4. Destinations Table
CREATE TABLE IF NOT EXISTS destinations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    distance DECIMAL(10, 2) NOT NULL, -- in km
    rate_per_ton DECIMAL(10, 2) NOT NULL,
    estimated_time DECIMAL(5, 2) NOT NULL, -- in hours
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 5. Trips Table
CREATE TABLE IF NOT EXISTS trips (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_id INT NOT NULL,
    driver_id INT NOT NULL,
    destination_id INT NOT NULL,
    source VARCHAR(100) NOT NULL DEFAULT 'Mine Loading Point',
    coal_weight DECIMAL(10, 2) NOT NULL, -- in tons
    start_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_date DATE,
    end_time TIME,
    status VARCHAR(20) NOT NULL DEFAULT 'Loading', -- 'Loading', 'Running', 'Delivered', 'Cancelled'
    freight_amount DECIMAL(12, 2) NOT NULL DEFAULT 0.0,
    diesel_used DECIMAL(10, 2) DEFAULT 0.0,
    toll_cost DECIMAL(10, 2) DEFAULT 0.0,
    misc_expense DECIMAL(10, 2) DEFAULT 0.0,
    profit DECIMAL(12, 2) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id),
    FOREIGN KEY (driver_id) REFERENCES drivers(id),
    FOREIGN KEY (destination_id) REFERENCES destinations(id)
) ENGINE=InnoDB;

-- 6. Fuel Table
CREATE TABLE IF NOT EXISTS fuel (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_id INT NOT NULL,
    date DATE NOT NULL,
    fuel_filled DECIMAL(10, 2) NOT NULL, -- in liters
    price DECIMAL(10, 2) NOT NULL, -- price per liter
    mileage DECIMAL(5, 2), -- computed fuel mileage (km/l)
    fuel_station VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 7. Maintenance Table
CREATE TABLE IF NOT EXISTS maintenance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_id INT NOT NULL,
    service_date DATE NOT NULL,
    next_service_date DATE NOT NULL,
    tyre_change BOOLEAN DEFAULT FALSE,
    oil_change BOOLEAN DEFAULT FALSE,
    battery_change BOOLEAN DEFAULT FALSE,
    service_cost DECIMAL(10, 2) NOT NULL,
    workshop_name VARCHAR(150),
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 8. Expenses Table
CREATE TABLE IF NOT EXISTS expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(50) NOT NULL, -- 'Diesel', 'Driver Salary', 'Toll', 'Repair', 'Maintenance', 'Miscellaneous'
    amount DECIMAL(12, 2) NOT NULL,
    date DATE NOT NULL,
    description TEXT,
    vehicle_id INT,
    trip_id INT,
    maintenance_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE SET NULL,
    FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE SET NULL,
    FOREIGN KEY (maintenance_id) REFERENCES maintenance(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- 9. Income Table
CREATE TABLE IF NOT EXISTS income (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(50) NOT NULL, -- 'Freight Charges', 'Trip Income', 'Total Revenue'
    amount DECIMAL(12, 2) NOT NULL,
    date DATE NOT NULL,
    description TEXT,
    trip_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- 10. Notifications Table
CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_id INT,
    driver_id INT,
    type VARCHAR(50) NOT NULL, -- 'Service Due', 'Insurance Expiry', 'Fitness Expiry', 'PUC Expiry', 'License Expiry', 'Low Fuel', 'Breakdown', 'Trip Delay'
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE SET NULL,
    FOREIGN KEY (driver_id) REFERENCES drivers(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- Add indexes for optimization
CREATE INDEX idx_trips_status ON trips(status);
CREATE INDEX idx_vehicles_status ON vehicles(status);
CREATE INDEX idx_expenses_date ON expenses(date);
CREATE INDEX idx_income_date ON income(date);
