-- ============================================================================
-- DOWNGRADE: USER REGISTRATION DATABASE SCHEMA
-- ============================================================================

-- ============================================================================
-- TRIGGERS
-- ============================================================================

DROP TRIGGER IF EXISTS trigger_users_updated_at ON users;

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

DROP FUNCTION IF EXISTS update_updated_at_column();
DROP FUNCTION IF EXISTS cleanup_expired_activation_codes();

-- ============================================================================
-- INDEXES
-- ============================================================================

-- Activation codes indexes
DROP INDEX IF EXISTS idx_activation_codes_expires_at;
DROP INDEX IF EXISTS idx_activation_codes_user_code;
DROP INDEX IF EXISTS idx_activation_codes_user_id_unique;

-- Users indexes
DROP INDEX IF EXISTS idx_users_created_at;
DROP INDEX IF EXISTS idx_users_is_active;
DROP INDEX IF EXISTS idx_users_email_lower;

-- ============================================================================
-- TABLES
-- ============================================================================

DROP TABLE IF EXISTS activation_codes;
DROP TABLE IF EXISTS users;

-- ============================================================================
-- EXTENSIONS
-- ============================================================================

DROP EXTENSION IF EXISTS pg_trgm;

-- ============================================================================
-- END DOWNGRADE
-- ============================================================================