--- Revoke all privileges from agents_grocery_role
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public REVOKE ALL PRIVILEGES ON TABLES FROM agents_grocery_role;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public REVOKE ALL PRIVILEGES ON SEQUENCES FROM agents_grocery_role;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public REVOKE ALL PRIVILEGES ON FUNCTIONS FROM agents_grocery_role;

-- Revoke all direct privileges from agents_grocery_role first
REVOKE ALL PRIVILEGES ON DATABASE agents_grocery FROM agents_grocery_role;
REVOKE ALL PRIVILEGES ON DATABASE inflo_ai FROM agents_grocery_role;
REVOKE ALL PRIVILEGES ON SCHEMA public FROM agents_grocery_role;

-- Drop config table
DROP TABLE IF EXISTS agents_grocery_config;

-- Drop agents_grocery_role
DROP ROLE IF EXISTS agents_grocery_role;