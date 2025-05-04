-- Migration: Initial database schema setup
-- Description: Creates the initial tables, relationships, functions, and policies
-- for the expense tracking application as defined in db-plan.md

-- 1. Create custom types
create type log_level as enum ('info', 'warning', 'error');

-- 2. Create tables
-- Note: users table is managed by Supabase Auth

-- Categories table
create table categories (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  name varchar(30) not null,
  is_default boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint name_length check (char_length(name) <= 30),
  constraint unique_name_per_user unique (user_id, name)
);

-- Create a partial unique index to ensure only one default category per user
create unique index idx_single_default_per_user on categories (user_id) where is_default = true;

-- Note: Expenses and Logs tables will be created in the next migration after the get_default_category_id function

-- Create index for categories
create index idx_categories_user_default on categories (user_id, is_default);

-- Create functions and triggers for categories
-- Trigger to create "Uncategorized" category after user registration
create or replace function create_default_category_trigger() 
returns trigger language plpgsql security definer as $$
begin
  insert into categories(user_id, name, is_default)
  values (new.id, 'Uncategorized', true);
  return new;
end;
$$;

create trigger trg_create_default_category
  after insert on auth.users
  for each row execute function create_default_category_trigger();

-- Function to prevent deletion of default category
create or replace function prevent_default_category_delete() 
returns trigger language plpgsql security definer as $$
begin
  if old.is_default then
    raise exception 'Cannot delete default category';
  end if;
  return old;
end;
$$;

create trigger trg_prevent_default_category_delete
  before delete on categories
  for each row execute function prevent_default_category_delete();

-- Setup Row Level Security policies
-- Enable RLS on categories table
alter table categories enable row level security;

-- Categories RLS policies
create policy "Users can view their own categories"
  on categories for select
  using (user_id = auth.uid());

create policy "Users can insert their own categories"
  on categories for insert
  with check (user_id = auth.uid());

create policy "Users can update their own categories"
  on categories for update
  using (user_id = auth.uid())
  with check (user_id = auth.uid());

create policy "Users can delete their own non-default categories"
  on categories for delete
  using (user_id = auth.uid() and not is_default); 