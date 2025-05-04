-- Migration: Fix function ordering
-- Description: Reorders the creation of functions to ensure they exist before tables reference them
-- This is needed because the expenses table uses get_default_category_id() as a default value

-- 1. First drop the expenses table that depends on the function
drop table if exists logs;
drop table if exists expenses;

-- 2. Recreate the get_default_category_id function
drop function if exists get_default_category_id();

create or replace function get_default_category_id() 
returns uuid language plpgsql stable security definer as $$
begin
  return (
    select id from categories
    where user_id = auth.uid() and is_default = true
    limit 1
  );
end;
$$;

-- 3. Recreate the expenses table with the proper default
create table expenses (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  amount numeric(12,2) not null check (amount > 0),
  description varchar(100),
  date_of_expense timestamptz not null,
  category_id uuid not null default get_default_category_id() references categories(id) on delete set default,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint description_length check (char_length(description) <= 100)
);

-- 4. Recreate the logs table that depends on expenses
create table logs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  expense_id uuid references expenses(id) on delete cascade,
  category_id uuid references categories(id) on delete cascade,
  type log_level not null,
  error_code varchar(50),
  message text not null,
  created_at timestamptz not null default now()
);

-- 5. Recreate indexes for these tables
create index idx_expenses_user_date on expenses (user_id, date_of_expense desc);
create index idx_expenses_user_amount on expenses (user_id, amount);
create index idx_logs_user_created_at on logs (user_id, created_at desc);

-- 6. Re-enable RLS on these tables
alter table expenses enable row level security;
alter table logs enable row level security;

-- 7. Recreate RLS policies for these tables
-- Expenses RLS policies
create policy "Users can view their own expenses"
  on expenses for select
  using (user_id = auth.uid());

create policy "Users can insert their own expenses"
  on expenses for insert
  with check (user_id = auth.uid());

create policy "Users can update their own expenses"
  on expenses for update
  using (user_id = auth.uid())
  with check (user_id = auth.uid());

create policy "Users can delete their own expenses"
  on expenses for delete
  using (user_id = auth.uid());

-- Logs RLS policies
create policy "Users can view their own logs"
  on logs for select
  using (user_id = auth.uid());

create policy "Users can insert their own logs"
  on logs for insert
  with check (user_id = auth.uid()); 