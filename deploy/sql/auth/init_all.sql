/* =====================================================================
   AUTH DB one-shot init (run in SSMS with Windows Authentication).
   Creates DB + schema + capability RBAC. Idempotent — safe to re-run.
   Users are seeded separately (passwords hashed at runtime):
       uv run python scripts/seed_auth.py
   ===================================================================== */

IF DB_ID('supermarket_auth') IS NULL
    CREATE DATABASE supermarket_auth;
GO

USE supermarket_auth;
GO

/* ---- Optional: SQL login for the app/seeder (DSN uses Uid=sa) ----------
   Uncomment + set a real password if the app connects via SQL auth (sa).
   ALTER LOGIN sa ENABLE;
   ALTER LOGIN sa WITH PASSWORD = 'REPLACE_WITH_STRONG_PW';
   -- or a dedicated login:
   -- CREATE LOGIN authapp WITH PASSWORD = 'REPLACE_WITH_STRONG_PW';
   -- CREATE USER authapp FOR LOGIN authapp;
   -- ALTER ROLE db_owner ADD MEMBER authapp;
   ----------------------------------------------------------------------- */

/* ---- 001_schema (guarded) -------------------------------------------- */
IF OBJECT_ID('users', 'U') IS NULL
    CREATE TABLE users (
        user_id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        username NVARCHAR(128) NULL,
        email NVARCHAR(255) NOT NULL UNIQUE,
        display_name NVARCHAR(255) NOT NULL,
        role NVARCHAR(64) NOT NULL DEFAULT 'store_manager',
        store_ids NVARCHAR(512) NULL,
        password_hash NVARCHAR(255) NULL,
        is_active BIT NOT NULL DEFAULT 1,
        created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
    );
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'UX_users_username' AND object_id = OBJECT_ID('users'))
    CREATE UNIQUE INDEX UX_users_username ON users(username) WHERE username IS NOT NULL;
GO

IF OBJECT_ID('oauth_accounts', 'U') IS NULL
    CREATE TABLE oauth_accounts (
        oauth_id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        user_id UNIQUEIDENTIFIER NOT NULL REFERENCES users(user_id),
        provider NVARCHAR(64) NOT NULL,
        provider_user_id NVARCHAR(255) NOT NULL,
        created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
    );
GO

IF OBJECT_ID('sessions_audit', 'U') IS NULL
    CREATE TABLE sessions_audit (
        session_id NVARCHAR(64) PRIMARY KEY,
        user_id UNIQUEIDENTIFIER NOT NULL REFERENCES users(user_id),
        created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
        last_seen_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
    );
GO

/* ---- 003_password_login (guarded columns, for older DBs) ------------- */
IF COL_LENGTH('users', 'username') IS NULL
    ALTER TABLE users ADD username NVARCHAR(128) NULL;
GO
IF COL_LENGTH('users', 'password_hash') IS NULL
    ALTER TABLE users ADD password_hash NVARCHAR(255) NULL;
GO
IF COL_LENGTH('users', 'is_active') IS NULL
    ALTER TABLE users ADD is_active BIT NOT NULL CONSTRAINT DF_users_is_active DEFAULT 1;
GO

/* ---- 004_permissions (capability RBAC) ------------------------------- */
IF OBJECT_ID('permissions', 'U') IS NULL
    CREATE TABLE permissions (
        permission_key NVARCHAR(200) NOT NULL PRIMARY KEY,
        category       NVARCHAR(32)  NOT NULL,
        description    NVARCHAR(400) NULL
    );
GO
IF OBJECT_ID('roles', 'U') IS NULL
    CREATE TABLE roles (
        role_key    NVARCHAR(64)  NOT NULL PRIMARY KEY,
        description NVARCHAR(400) NULL
    );
GO
IF OBJECT_ID('role_permissions', 'U') IS NULL
    CREATE TABLE role_permissions (
        role_key       NVARCHAR(64)  NOT NULL,
        permission_key NVARCHAR(200) NOT NULL,
        CONSTRAINT PK_role_permissions PRIMARY KEY (role_key, permission_key)
    );
GO
IF OBJECT_ID('user_permissions', 'U') IS NULL
    CREATE TABLE user_permissions (
        user_id        UNIQUEIDENTIFIER NOT NULL,
        permission_key NVARCHAR(200)    NOT NULL,
        effect         NVARCHAR(8)      NOT NULL CONSTRAINT DF_user_permissions_effect DEFAULT 'grant',
        CONSTRAINT PK_user_permissions PRIMARY KEY (user_id, permission_key)
    );
GO

MERGE permissions AS tgt
USING (VALUES
    ('data:table:*',            'data',     'Access to all logical tables'),
    ('data:column_deny:*',      'data',     'Wildcard column denial marker'),
    ('data:store_filter:required','data',   'Force per-store filtering'),
    ('tool:*',                  'tool',     'Invoke any MCP tool'),
    ('tool:sql-gateway:validate','tool',    'sql-gateway validate_sql'),
    ('tool:sql-gateway:explain', 'tool',    'sql-gateway explain_sql / get_schema_snapshot'),
    ('tool:sql-gateway:execute', 'tool',    'sql-gateway execute_readonly'),
    ('tool:python-sandbox:run_analysis_script','tool','python-sandbox run_analysis_script'),
    ('tool:python-sandbox:preview_dataframe','tool',  'python-sandbox preview_dataframe'),
    ('tool:python-sandbox:load_dataset','tool',       'python-sandbox load_dataset'),
    ('tool:python-sandbox:merge_datasets','tool',     'python-sandbox merge_datasets'),
    ('tool:python-sandbox:plot_chart','tool',         'python-sandbox plot_chart'),
    ('tool:python-sandbox:export_excel','tool',       'python-sandbox export_excel'),
    ('tool:python-sandbox:run_recipe_tool','tool',    'python-sandbox run_recipe_tool'),
    ('function:*',              'function', 'Run any promoted sandbox recipe')
) AS src (permission_key, category, description)
ON tgt.permission_key = src.permission_key
WHEN MATCHED THEN UPDATE SET category = src.category, description = src.description
WHEN NOT MATCHED THEN INSERT (permission_key, category, description)
    VALUES (src.permission_key, src.category, src.description);
GO

MERGE roles AS tgt
USING (VALUES
    ('admin',         'Full access (all tables, tools, functions)'),
    ('hq_analyst',    'HQ analyst: broad table set, all tools/functions'),
    ('store_manager', 'Store manager: restricted tables + denied columns + store filter')
) AS src (role_key, description)
ON tgt.role_key = src.role_key
WHEN MATCHED THEN UPDATE SET description = src.description
WHEN NOT MATCHED THEN INSERT (role_key, description) VALUES (src.role_key, src.description);
GO

DELETE FROM role_permissions WHERE role_key IN ('admin', 'hq_analyst', 'store_manager');
GO

INSERT INTO role_permissions (role_key, permission_key) VALUES
    ('admin', 'data:table:*'),
    ('admin', 'tool:*'),
    ('admin', 'function:*');

INSERT INTO role_permissions (role_key, permission_key) VALUES
    ('hq_analyst', 'tool:*'),
    ('hq_analyst', 'function:*'),
    ('store_manager', 'tool:*'),
    ('store_manager', 'function:*'),
    ('store_manager', 'data:store_filter:required');

INSERT INTO role_permissions (role_key, permission_key) VALUES
    ('hq_analyst', 'data:table:STRANS'),
    ('hq_analyst', 'data:table:PMTRANS'),
    ('hq_analyst', 'data:table:TRANSHDR'),
    ('hq_analyst', 'data:table:TRANSHDR_ARC'),
    ('hq_analyst', 'data:table:CRDTRANS'),
    ('hq_analyst', 'data:table:CRDTRANS_ARC'),
    ('hq_analyst', 'data:table:CRDTRANS_TMP'),
    ('hq_analyst', 'data:table:STRANS_TMP'),
    ('hq_analyst', 'data:table:SUSPEND'),
    ('hq_analyst', 'data:table:CASH_ST'),
    ('hq_analyst', 'data:table:CTRANS'),
    ('hq_analyst', 'data:table:CUSTOMER'),
    ('hq_analyst', 'data:table:CSCARD'),
    ('hq_analyst', 'data:table:CRD_INFO'),
    ('hq_analyst', 'data:table:CUSTHIST'),
    ('hq_analyst', 'data:table:CustSumm'),
    ('hq_analyst', 'data:table:SKU_DEF'),
    ('hq_analyst', 'data:table:PLU'),
    ('hq_analyst', 'data:table:BARCODE'),
    ('hq_analyst', 'data:table:ASSOLST'),
    ('hq_analyst', 'data:table:ASSO_INF'),
    ('hq_analyst', 'data:table:SUPPLIER'),
    ('hq_analyst', 'data:table:PARTNER'),
    ('hq_analyst', 'data:table:HISRTPR'),
    ('hq_analyst', 'data:table:HISSPPR'),
    ('hq_analyst', 'data:table:RDISCINF'),
    ('hq_analyst', 'data:table:STK_DTL'),
    ('hq_analyst', 'data:table:ST_ORDER'),
    ('hq_analyst', 'data:table:INV_HDR'),
    ('hq_analyst', 'data:table:INV_ISS'),
    ('hq_analyst', 'data:table:PMCRDINF'),
    ('hq_analyst', 'data:table:PMCRDSTK'),
    ('hq_analyst', 'data:table:PMCRDISS'),
    ('hq_analyst', 'data:table:PMCRDRCV'),
    ('hq_analyst', 'data:table:ACCOUNT'),
    ('hq_analyst', 'data:table:DEBT'),
    ('hq_analyst', 'data:table:sku_activity'),
    ('hq_analyst', 'data:table:WebRpt_sales_sku_daily'),
    ('hq_analyst', 'data:table:WebRpt_inventory_daily'),
    ('hq_analyst', 'data:table:WebRpt_rfm_snapshot');

INSERT INTO role_permissions (role_key, permission_key) VALUES
    ('store_manager', 'data:table:STRANS'),
    ('store_manager', 'data:table:PMTRANS'),
    ('store_manager', 'data:table:TRANSHDR'),
    ('store_manager', 'data:table:CRDTRANS'),
    ('store_manager', 'data:table:CUSTOMER'),
    ('store_manager', 'data:table:CSCARD'),
    ('store_manager', 'data:table:CustSumm'),
    ('store_manager', 'data:table:CUSTHIST'),
    ('store_manager', 'data:table:SKU_DEF'),
    ('store_manager', 'data:table:BARCODE'),
    ('store_manager', 'data:table:PLU'),
    ('store_manager', 'data:table:SUPPLIER'),
    ('store_manager', 'data:table:WebRpt_sales_sku_daily'),
    ('store_manager', 'data:table:WebRpt_inventory_daily'),
    ('store_manager', 'data:table:WebRpt_rfm_snapshot');

INSERT INTO role_permissions (role_key, permission_key) VALUES
    ('store_manager', 'data:column_deny:SPPRICE'),
    ('store_manager', 'data:column_deny:LASTSPPR'),
    ('store_manager', 'data:column_deny:cogs'),
    ('store_manager', 'data:column_deny:gross_profit'),
    ('store_manager', 'data:column_deny:free_cogs'),
    ('store_manager', 'data:column_deny:value_onhand'),
    ('store_manager', 'data:column_deny:PASSCODE'),
    ('store_manager', 'data:column_deny:PERSON_ID');
GO

PRINT 'AUTH DB schema + RBAC ready. Now seed users: uv run python scripts/seed_auth.py';
GO
