--- 데이터베이스 생성
-- CREATE DATABASE agents_grocery;

--- agents_grocery_role 역할(Role) 생성
DROP TABLE IF EXISTS agents_grocery_config;
DROP ROLE IF EXISTS agents_grocery_role;
CREATE ROLE agents_grocery_role WITH LOGIN PASSWORD 'agents_grocery_role123!';

--- 데이터베이스 'inflo_ai'에 대한 권한 부여
GRANT CONNECT, CREATE, TEMPORARY ON DATABASE agents_grocery TO agents_grocery_role;
GRANT CONNECT, CREATE, TEMPORARY ON DATABASE inflo_ai TO agents_grocery_role;

--- 스키마 및 기존 객체에 대한 권한 부여
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO agents_grocery_role;
GRANT USAGE, CREATE ON SCHEMA public TO agents_grocery_role;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO agents_grocery_role;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO agents_grocery_role;

--- 향후 생성될 객체에 대한 기본 권한 설정 (DB 소유자로 실행)
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO agents_grocery_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON SEQUENCES TO agents_grocery_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON FUNCTIONS TO agents_grocery_role;