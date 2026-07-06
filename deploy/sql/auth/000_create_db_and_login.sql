/* =====================================================================
   Run in SSMS with Windows Authentication (sysadmin).
   Creates the AUTH database + one SQL login with just-enough rights so the
   app / init / seed scripts can connect via SQL auth.
   After this: uv run python scripts/init_auth_db.py
   ===================================================================== */

IF DB_ID('supermarket_auth') IS NULL
    CREATE DATABASE supermarket_auth;
GO

-- Server-level SQL login used by AUTH_DB_DSN (Uid=auth_analysis_agent).
-- Change the password if you like, then update Pwd in .env to match.
IF NOT EXISTS (SELECT 1 FROM sys.server_principals WHERE name = 'auth_analysis_agent')
    CREATE LOGIN auth_analysis_agent WITH PASSWORD = 'Auth_Db!Str0ng#2026', CHECK_POLICY = ON;
GO

USE supermarket_auth;
GO

IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'auth_analysis_agent')
    CREATE USER auth_analysis_agent FOR LOGIN auth_analysis_agent;
GO

-- Just-enough: create/alter tables + read + write (no server/db admin).
ALTER ROLE db_ddladmin   ADD MEMBER auth_analysis_agent;
ALTER ROLE db_datawriter ADD MEMBER auth_analysis_agent;
ALTER ROLE db_datareader ADD MEMBER auth_analysis_agent;
GO

PRINT 'DB supermarket_auth + login auth_analysis_agent ready. Next: uv run python scripts/init_auth_db.py';
GO
