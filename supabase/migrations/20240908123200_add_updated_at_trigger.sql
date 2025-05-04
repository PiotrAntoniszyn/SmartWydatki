-- Migration: Add updated_at trigger
-- Description: Creates a trigger function to automatically update the updated_at timestamp
-- when a record is updated and applies it to tables with updated_at columns

-- 1. Create trigger function
create or replace function update_updated_at_column()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

-- 2. Apply trigger to tables with updated_at
-- For categories table
drop trigger if exists trg_categories_updated_at on categories;
create trigger trg_categories_updated_at
  before update on categories
  for each row execute function update_updated_at_column();

-- For expenses table
drop trigger if exists trg_expenses_updated_at on expenses;
create trigger trg_expenses_updated_at
  before update on expenses
  for each row execute function update_updated_at_column(); 