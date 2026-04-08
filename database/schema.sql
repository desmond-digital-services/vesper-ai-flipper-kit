-- Vesper AI Flipper Kit - Order Database Schema
-- SQLite Database

-- ============================================
-- ORDERS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    customer_name TEXT NOT NULL,
    customer_email TEXT NOT NULL,
    customer_phone TEXT,
    shipping_address TEXT NOT NULL, -- JSON: {"street", "city", "state", "zip", "country"}
    order_date TEXT NOT NULL, -- ISO 8601 format
    order_total REAL NOT NULL DEFAULT 499.00,
    payment_status TEXT NOT NULL DEFAULT 'pending' CHECK (payment_status IN ('pending', 'paid', 'failed')),
    stripe_payment_intent_id TEXT,
    order_status TEXT NOT NULL DEFAULT 'pending' CHECK (order_status IN ('pending', 'building', 'testing', 'shipped', 'delivered')),
    build_start_date TEXT,
    ship_date TEXT,
    tracking_number TEXT,
    carrier TEXT DEFAULT 'USPS',
    estimated_delivery_date TEXT,
    actual_delivery_date TEXT,
    notes TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for orders
CREATE INDEX IF NOT EXISTS idx_orders_email ON orders(customer_email);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(order_status);
CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date DESC);
CREATE INDEX IF NOT EXISTS idx_orders_payment ON orders(payment_status);

-- ============================================
-- EMAIL LOG TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS email_log (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT NOT NULL,
    email_type TEXT NOT NULL CHECK (email_type IN ('confirmation', 'build', 'shipped', 'followup', 'payment_failed', 'custom')),
    subject TEXT NOT NULL,
    sent_date TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'sent' CHECK (status IN ('sent', 'failed', 'pending')),
    error_message TEXT,
    recipient_email TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
);

-- Indexes for email_log
CREATE INDEX IF NOT EXISTS idx_email_log_order ON email_log(order_id);
CREATE INDEX IF NOT EXISTS idx_email_log_date ON email_log(sent_date DESC);
CREATE INDEX IF NOT EXISTS idx_email_log_type ON email_log(email_type);

-- ============================================
-- HARDWARE PROCUREMENT TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS hardware_procurement (
    procurement_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT NOT NULL,
    supplier TEXT NOT NULL CHECK (supplier IN ('Micro Center', 'Hacker Warehouse', 'Amazon', 'Other')),
    item TEXT NOT NULL CHECK (item IN ('Flipper Zero', 'Moto G Play', 'SD Card 64GB', 'SD Card 128GB', 'USB Cable', 'Other')),
    quantity INTEGER NOT NULL DEFAULT 1,
    cost REAL NOT NULL,
    order_date TEXT NOT NULL,
    tracking_number TEXT,
    status TEXT NOT NULL DEFAULT 'ordered' CHECK (status IN ('ordered', 'shipped', 'received', 'assembled')),
    notes TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
);

-- Indexes for hardware_procurement
CREATE INDEX IF NOT EXISTS idx_procurement_order ON hardware_procurement(order_id);
CREATE INDEX IF NOT EXISTS idx_procurement_supplier ON hardware_procurement(supplier);
CREATE INDEX IF NOT EXISTS idx_procurement_status ON hardware_procurement(status);

-- ============================================
-- ORDER NOTES TABLE (for history tracking)
-- ============================================
CREATE TABLE IF NOT EXISTS order_notes (
    note_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT NOT NULL,
    note TEXT NOT NULL,
    note_type TEXT DEFAULT 'manual' CHECK (note_type IN ('manual', 'system', 'email', 'status_change')),
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
);

-- Index for order_notes
CREATE INDEX IF NOT EXISTS idx_notes_order ON order_notes(order_id);

-- ============================================
-- TRIGGER: Update updated_at timestamp
-- ============================================
CREATE TRIGGER IF NOT EXISTS update_orders_timestamp
AFTER UPDATE ON orders
BEGIN
    UPDATE orders SET updated_at = CURRENT_TIMESTAMP WHERE order_id = NEW.order_id;
END;

CREATE TRIGGER IF NOT EXISTS update_procurement_timestamp
AFTER UPDATE ON hardware_procurement
BEGIN
    UPDATE hardware_procurement SET updated_at = CURRENT_TIMESTAMP WHERE procurement_id = NEW.procurement_id;
END;

-- ============================================
-- VIEW: Order summary with procurement status
-- ============================================
CREATE VIEW IF NOT EXISTS order_summary AS
SELECT 
    o.order_id,
    o.customer_name,
    o.customer_email,
    o.order_status,
    o.payment_status,
    o.order_total,
    o.order_date,
    o.tracking_number,
    o.carrier,
    o.ship_date,
    o.actual_delivery_date,
    (SELECT COUNT(*) FROM hardware_procurement hp WHERE hp.order_id = o.order_id) as procurement_count,
    (SELECT COUNT(*) FROM hardware_procurement hp WHERE hp.order_id = o.order_id AND hp.status = 'assembled') as assembled_count,
    (SELECT COUNT(*) FROM email_log el WHERE el.order_id = o.order_id) as email_count
FROM orders o;

-- ============================================
-- SAMPLE DATA (for testing)
-- ============================================
-- Uncomment below to insert sample data for development

-- INSERT INTO orders (order_id, customer_name, customer_email, customer_phone, shipping_address, order_date, order_total, payment_status, stripe_payment_intent_id, order_status, build_start_date, ship_date, tracking_number, carrier, estimated_delivery_date) VALUES
-- ('VPR-2026-00001', 'John Smith', 'john.smith@example.com', '+1-555-123-4567', '{"street": "123 Main St", "city": "Austin", "state": "TX", "zip": "78701", "country": "US"}', '2026-04-01T10:30:00Z', 499.00, 'paid', 'pi_abc123xyz', 'building', '2026-04-03T09:00:00Z', NULL, NULL, 'USPS', '2026-04-10'),
-- ('VPR-2026-00002', 'Jane Doe', 'jane.doe@example.com', '+1-555-987-6543', '{"street": "456 Oak Ave", "city": "Dallas", "state": "TX", "zip": "75201", "country": "US"}', '2026-04-02T14:45:00Z', 499.00, 'paid', 'pi_def456uvw', 'shipped', '2026-04-04T10:00:00Z', '2026-04-07T16:30:00Z', '9400111899223334445555', 'USPS', '2026-04-09');