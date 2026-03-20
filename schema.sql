CREATE TABLE IF NOT EXISTS Admin (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS Appliances (
    appliance_id INT AUTO_INCREMENT PRIMARY KEY,
    appliance_name VARCHAR(100) NOT NULL,
    power_rating_watts INT NOT NULL
);

CREATE TABLE IF NOT EXISTS Usage (
    usage_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    appliance_id INT NOT NULL,
    hours_per_day INT NOT NULL,
    number_of_days INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (appliance_id) REFERENCES Appliances(appliance_id)
);

CREATE TABLE IF NOT EXISTS Tariff (
    tariff_id INT AUTO_INCREMENT PRIMARY KEY,
    rate_per_kwh DECIMAL(10, 2) NOT NULL,
    effective_date DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS Bill (
    bill_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    total_units DECIMAL(10, 2) NOT NULL,
    total_cost DECIMAL(10, 2) NOT NULL,
    bill_date DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

