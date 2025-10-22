-- Schema for Carbon Credit Marketplace
-- Uses PostgreSQL

CREATE TABLE IF NOT EXISTS company (
    company_id SERIAL PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    address VARCHAR(255),
    website VARCHAR(255),
    location VARCHAR(255),
    wallet_address VARCHAR(255) UNIQUE
);

CREATE TABLE IF NOT EXISTS company_credit (
    credit_id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES company(company_id) ON DELETE CASCADE,
    total_credit DECIMAL(10,2) NOT NULL,
    current_credit DECIMAL(10,2) NOT NULL,
    sold_credit DECIMAL(10,2) NOT NULL DEFAULT '0.00',
    offer_price DECIMAL(10,2)
);

CREATE TABLE IF NOT EXISTS credit_purchase (
    purchase_id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES company(company_id) ON DELETE CASCADE,
    user_account VARCHAR(255) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    price_per_credit DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(12,2) NOT NULL,
    payment_tx_id VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Helpful indexes
CREATE INDEX IF NOT EXISTS idx_company_wallet ON company(wallet_address);
CREATE INDEX IF NOT EXISTS idx_company_credit_company ON company_credit(company_id);
CREATE INDEX IF NOT EXISTS idx_purchase_company ON credit_purchase(company_id);


