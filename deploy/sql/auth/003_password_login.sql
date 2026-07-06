-- Username/password login for chat-gateway (bcrypt hash in password_hash)

IF COL_LENGTH('users', 'username') IS NULL
    ALTER TABLE users ADD username NVARCHAR(128) NULL;

IF COL_LENGTH('users', 'password_hash') IS NULL
    ALTER TABLE users ADD password_hash NVARCHAR(255) NULL;

IF COL_LENGTH('users', 'is_active') IS NULL
    ALTER TABLE users ADD is_active BIT NOT NULL CONSTRAINT DF_users_is_active DEFAULT 1;

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'UX_users_username' AND object_id = OBJECT_ID('users'))
    CREATE UNIQUE INDEX UX_users_username ON users(username) WHERE username IS NOT NULL;
