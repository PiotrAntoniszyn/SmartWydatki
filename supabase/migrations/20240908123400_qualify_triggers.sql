-- Migration: Qualify triggers and functions to see public.categories
-- Description: Removes old trigger and functions, recreates them with explicit schema qualification and search_path

-- 1. Drop existing trigger and function
DROP TRIGGER IF EXISTS trg_create_default_category ON auth.users;
DROP FUNCTION IF EXISTS create_default_category_trigger();

-- 2. Recreate create_default_category_trigger with schema qualification and search_path
CREATE OR REPLACE FUNCTION create_default_category_trigger()
  RETURNS trigger
  LANGUAGE plpgsql
  SECURITY DEFINER
  SET search_path = public, auth, pg_catalog AS $$
BEGIN
  INSERT INTO public.categories(user_id, name, is_default)
    VALUES (NEW.id, 'Uncategorized', TRUE);
  RETURN NEW;
END;
$$;

CREATE TRIGGER trg_create_default_category
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION create_default_category_trigger();

-- 3. Drop and recreate get_default_category_id function with schema qualification and search_path

-- Remove default on expenses.category_id to allow dropping the function
ALTER TABLE IF EXISTS expenses ALTER COLUMN category_id DROP DEFAULT;

DROP FUNCTION IF EXISTS get_default_category_id();

CREATE OR REPLACE FUNCTION get_default_category_id()
  RETURNS uuid
  LANGUAGE plpgsql
  SECURITY DEFINER
  SET search_path = public, auth, pg_catalog AS $$
BEGIN
  RETURN (
    SELECT id FROM public.categories
    WHERE user_id = auth.uid() AND is_default = TRUE
    LIMIT 1
  );
END;
$$;

-- Restore default on expenses.category_id
ALTER TABLE IF EXISTS expenses ALTER COLUMN category_id SET DEFAULT get_default_category_id();