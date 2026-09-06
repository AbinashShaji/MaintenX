-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT CHECK(role IN ('user', 'staff', 'admin')) NOT NULL DEFAULT 'user',
    phone TEXT,
    department TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Categories Table
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Maintenance Requests Table
CREATE TABLE IF NOT EXISTS maintenance_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    assigned_to INTEGER,
    title TEXT NOT NULL,
    description TEXT,
    location TEXT,
    priority TEXT CHECK(priority IN ('low', 'medium', 'high', 'critical')) NOT NULL DEFAULT 'low',
    status TEXT CHECK(status IN ('pending', 'assigned', 'in_progress', 'resolved', 'closed')) NOT NULL DEFAULT 'pending',
    resolution_note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    closed_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
    FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL
);

-- Request Updates Table
CREATE TABLE IF NOT EXISTS request_updates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    old_status TEXT CHECK(old_status IN ('pending', 'assigned', 'in_progress', 'resolved', 'closed')),
    new_status TEXT CHECK(new_status IN ('pending', 'assigned', 'in_progress', 'resolved', 'closed')) NOT NULL,
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (request_id) REFERENCES maintenance_requests(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

CREATE INDEX IF NOT EXISTS idx_requests_user_id ON maintenance_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_requests_assigned_to ON maintenance_requests(assigned_to);
CREATE INDEX IF NOT EXISTS idx_requests_category_id ON maintenance_requests(category_id);
CREATE INDEX IF NOT EXISTS idx_requests_status ON maintenance_requests(status);
CREATE INDEX IF NOT EXISTS idx_requests_priority ON maintenance_requests(priority);
CREATE INDEX IF NOT EXISTS idx_requests_created_at ON maintenance_requests(created_at);

CREATE INDEX IF NOT EXISTS idx_updates_request_id ON request_updates(request_id);
