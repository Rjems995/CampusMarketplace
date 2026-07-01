-- ============================================================
-- database/seed.sql
-- Campus Marketplace — Seed Data
-- Run AFTER schema.sql
-- ============================================================

-- ── Categories ───────────────────────────────────────────────
INSERT INTO categories (name, slug, icon, description, sort_order) VALUES
('Books',                'books',               'bi-book',             'Textbooks, novels, references, and study materials.',          1),
('School Supplies',      'school-supplies',     'bi-pencil',           'Notebooks, pens, calculators, and other classroom essentials.', 2),
('Electronics',          'electronics',         'bi-laptop',           'Laptops, phones, gadgets, and accessories.',                   3),
('Clothing',             'clothing',            'bi-bag',              'Uniforms, casual wear, shoes, and fashion items.',             4),
('Furniture',            'furniture',           'bi-house',            'Chairs, desks, beds, and dorm room essentials.',               5),
('Sports',               'sports',              'bi-trophy',           'Sports gear, equipment, and activewear.',                     6),
('Musical Instruments',  'musical-instruments', 'bi-music-note-beamed','Guitars, keyboards, drums, and accessories.',                  7),
('Accessories',          'accessories',         'bi-watch',            'Bags, jewelry, watches, and personal accessories.',            8),
('Gaming',               'gaming',              'bi-controller',       'Consoles, games, and gaming peripherals.',                    9),
('Others',               'others',              'bi-three-dots',       'Miscellaneous items that do not fit other categories.',        10)
ON CONFLICT (slug) DO NOTHING;

-- ── Admin user (password: Admin@1234) ───────────────────────
-- bcrypt hash of Admin@1234
INSERT INTO users (email, password_hash, first_name, last_name, is_admin, is_verified, email_confirmed)
VALUES (
    'admin@campus.edu',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQyCgzJ6hf9e/xH1V9kCPXaWq',
    'Campus',
    'Admin',
    TRUE,
    TRUE,
    TRUE
) ON CONFLICT (email) DO NOTHING;

-- Admin profile
INSERT INTO profiles (user_id, school, bio)
SELECT id, 'Campus Marketplace HQ', 'System administrator.'
FROM users WHERE email = 'admin@campus.edu'
ON CONFLICT (user_id) DO NOTHING;
