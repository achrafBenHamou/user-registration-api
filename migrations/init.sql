-- ============================================================================
-- USER REGISTRATION DATABASE SCHEMA
-- ============================================================================
-- Optimized for high-volume CRUD operations
-- ============================================================================

-- ============================================================================
-- EXTENSIONS
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For future full-text search on emails

-- ============================================================================
-- TABLES
-- ============================================================================

-- Users table: Stores user account information
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),  -- Native PG function (15-20% faster than uuid-ossp)
    email VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Activation codes table: Temporary 4-digit codes with 1-minute TTL
CREATE TABLE IF NOT EXISTS activation_codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    code VARCHAR(4) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    CONSTRAINT chk_expires_after_created CHECK (expires_at > created_at)
);

-- ============================================================================
-- INDEXES (HIGH-PERFORMANCE OPTIMIZATIONS)
-- ============================================================================

-- ----------------------------------------
-- Users Table Indexes
-- ----------------------------------------

-- Email lookup: Case-insensitive unique index (used for login)
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email_lower
    ON users(LOWER(email));

-- Only indexes users waiting for activation
CREATE INDEX IF NOT EXISTS idx_users_is_active
    ON users(is_active)
    WHERE is_active = FALSE;

-- Index for sorting by creation date
CREATE INDEX IF NOT EXISTS idx_users_created_at
    ON users(created_at DESC);

-- ----------------------------------------
-- Activation Codes Table Indexes
-- ----------------------------------------

-- Unique constraint: One active code per user (prevents duplicate codes)
CREATE UNIQUE INDEX IF NOT EXISTS idx_activation_codes_user_id_unique
    ON activation_codes(user_id);

-- Composite index for activation validation (most common query)
CREATE INDEX IF NOT EXISTS idx_activation_codes_user_code
    ON activation_codes(user_id, code);

-- Index for cleanup queries (sorting by expiration)
CREATE INDEX IF NOT EXISTS idx_activation_codes_expires_at
    ON activation_codes(expires_at);

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Cleanup expired activation codes
-- Usage: SELECT cleanup_expired_activation_codes();
-- Schedule with pg_cron: */1 * * * * (every minute)
CREATE OR REPLACE FUNCTION cleanup_expired_activation_codes()
RETURNS TABLE(deleted_count BIGINT) AS $$
DECLARE
    rows_deleted BIGINT;
BEGIN
    DELETE FROM activation_codes WHERE expires_at < NOW();
    GET DIAGNOSTICS rows_deleted = ROW_COUNT;
    RETURN QUERY SELECT rows_deleted;
END;
$$ LANGUAGE plpgsql;

-- Auto-update updated_at column on users table
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Automatically update updated_at when user record is modified
CREATE TRIGGER trigger_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
-- ============================================================================