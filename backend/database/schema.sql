-- ============================================================
-- database/schema.sql
-- Campus Marketplace — Full PostgreSQL Schema
-- ============================================================

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ─────────────────────────────────────────────
-- USERS
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id              SERIAL PRIMARY KEY,
    email           VARCHAR(120) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    first_name      VARCHAR(50) NOT NULL,
    last_name       VARCHAR(50) NOT NULL,
    is_admin        BOOLEAN DEFAULT FALSE,
    is_suspended    BOOLEAN DEFAULT FALSE,
    is_verified     BOOLEAN DEFAULT FALSE,   -- email verified
    email_confirmed BOOLEAN DEFAULT FALSE,
    remember_token  VARCHAR(255),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login      TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);

-- ─────────────────────────────────────────────
-- PROFILES
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS profiles (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    bio             TEXT,
    course          VARCHAR(100),
    year_level      VARCHAR(20),
    school          VARCHAR(150),
    phone           VARCHAR(20),
    location        VARCHAR(100),
    profile_picture VARCHAR(255),
    social_fb       VARCHAR(255),
    average_rating  NUMERIC(3,2) DEFAULT 0.00,
    total_reviews   INTEGER DEFAULT 0,
    total_sales     INTEGER DEFAULT 0,
    is_online       BOOLEAN DEFAULT FALSE,
    last_seen       TIMESTAMP,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_profiles_user_id ON profiles(user_id);

-- ─────────────────────────────────────────────
-- CATEGORIES
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS categories (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(80) UNIQUE NOT NULL,
    slug        VARCHAR(80) UNIQUE NOT NULL,
    icon        VARCHAR(50) DEFAULT 'bi-tag',
    description TEXT,
    sort_order  INTEGER DEFAULT 0,
    is_active   BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_categories_slug ON categories(slug);

-- ─────────────────────────────────────────────
-- PRODUCTS (Listings)
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS products (
    id              SERIAL PRIMARY KEY,
    seller_id       INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category_id     INTEGER NOT NULL REFERENCES categories(id) ON DELETE RESTRICT,
    title           VARCHAR(150) NOT NULL,
    slug            VARCHAR(200) UNIQUE NOT NULL,
    description     TEXT NOT NULL,
    price           NUMERIC(10,2) NOT NULL CHECK (price >= 0),
    condition       VARCHAR(30) NOT NULL CHECK (condition IN ('New','Like New','Good','Fair','Poor')),
    location        VARCHAR(100),
    status          VARCHAR(20) DEFAULT 'available' CHECK (status IN ('available','sold','reserved','removed')),
    views           INTEGER DEFAULT 0,
    is_featured     BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sold_at         TIMESTAMP
);

CREATE INDEX idx_products_seller_id   ON products(seller_id);
CREATE INDEX idx_products_category_id ON products(category_id);
CREATE INDEX idx_products_status      ON products(status);
CREATE INDEX idx_products_created_at  ON products(created_at DESC);
CREATE INDEX idx_products_title_trgm  ON products USING gin(title gin_trgm_ops);
CREATE INDEX idx_products_desc_trgm   ON products USING gin(description gin_trgm_ops);

-- ─────────────────────────────────────────────
-- PRODUCT IMAGES
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS product_images (
    id          SERIAL PRIMARY KEY,
    product_id  INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    filename    VARCHAR(255) NOT NULL,
    is_primary  BOOLEAN DEFAULT FALSE,
    sort_order  INTEGER DEFAULT 0,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_product_images_product_id ON product_images(product_id);

-- ─────────────────────────────────────────────
-- FAVORITES
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS favorites (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id  INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, product_id)
);

CREATE INDEX idx_favorites_user_id    ON favorites(user_id);
CREATE INDEX idx_favorites_product_id ON favorites(product_id);

-- ─────────────────────────────────────────────
-- CONVERSATIONS
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS conversations (
    id              SERIAL PRIMARY KEY,
    product_id      INTEGER REFERENCES products(id) ON DELETE SET NULL,
    buyer_id        INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    seller_id       INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    last_message_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    buyer_unread    INTEGER DEFAULT 0,
    seller_unread   INTEGER DEFAULT 0,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (product_id, buyer_id, seller_id)
);

CREATE INDEX idx_conversations_buyer_id  ON conversations(buyer_id);
CREATE INDEX idx_conversations_seller_id ON conversations(seller_id);

-- ─────────────────────────────────────────────
-- MESSAGES
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS messages (
    id              SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    sender_id       INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    body            TEXT,
    image_filename  VARCHAR(255),
    is_read         BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_sender_id       ON messages(sender_id);
CREATE INDEX idx_messages_created_at      ON messages(created_at);

-- ─────────────────────────────────────────────
-- REVIEWS
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS reviews (
    id              SERIAL PRIMARY KEY,
    reviewer_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    reviewee_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id      INTEGER REFERENCES products(id) ON DELETE SET NULL,
    rating          SMALLINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment         TEXT,
    is_approved     BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (reviewer_id, product_id)
);

CREATE INDEX idx_reviews_reviewee_id ON reviews(reviewee_id);
CREATE INDEX idx_reviews_reviewer_id ON reviews(reviewer_id);

-- ─────────────────────────────────────────────
-- NOTIFICATIONS
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS notifications (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type        VARCHAR(50) NOT NULL,
    title       VARCHAR(120) NOT NULL,
    body        TEXT,
    link        VARCHAR(255),
    is_read     BOOLEAN DEFAULT FALSE,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_notifications_user_id   ON notifications(user_id);
CREATE INDEX idx_notifications_is_read   ON notifications(is_read);

-- ─────────────────────────────────────────────
-- REPORTS
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS reports (
    id              SERIAL PRIMARY KEY,
    reporter_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id      INTEGER REFERENCES products(id) ON DELETE SET NULL,
    reason          VARCHAR(50) NOT NULL,
    description     TEXT,
    status          VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending','reviewed','dismissed','actioned')),
    admin_note      TEXT,
    reviewed_by     INTEGER REFERENCES users(id) ON DELETE SET NULL,
    reviewed_at     TIMESTAMP,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_reports_product_id  ON reports(product_id);
CREATE INDEX idx_reports_reporter_id ON reports(reporter_id);
CREATE INDEX idx_reports_status      ON reports(status);

-- ─────────────────────────────────────────────
-- ADMIN LOGS
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS admin_logs (
    id          SERIAL PRIMARY KEY,
    admin_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    action      VARCHAR(100) NOT NULL,
    target_type VARCHAR(50),
    target_id   INTEGER,
    detail      TEXT,
    ip_address  VARCHAR(45),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_admin_logs_admin_id   ON admin_logs(admin_id);
CREATE INDEX idx_admin_logs_created_at ON admin_logs(created_at DESC);

-- ─────────────────────────────────────────────
-- EMAIL VERIFICATION TOKENS
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS email_verifications (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token       VARCHAR(255) UNIQUE NOT NULL,
    expires_at  TIMESTAMP NOT NULL,
    used        BOOLEAN DEFAULT FALSE,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────────
-- PASSWORD RESETS
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS password_resets (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token       VARCHAR(255) UNIQUE NOT NULL,
    expires_at  TIMESTAMP NOT NULL,
    used        BOOLEAN DEFAULT FALSE,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────────
-- UPDATED_AT trigger function
-- ─────────────────────────────────────────────
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at    BEFORE UPDATE ON users    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
