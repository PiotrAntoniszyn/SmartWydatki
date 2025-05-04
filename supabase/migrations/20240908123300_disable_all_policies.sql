-- Migration: Disable all policies
-- Description: Disables all RLS policies previously defined in migrations

-- 1. Disable Categories RLS policies
drop policy if exists "Users can view their own categories" on categories;
drop policy if exists "Users can insert their own categories" on categories;
drop policy if exists "Users can update their own categories" on categories;
drop policy if exists "Users can delete their own non-default categories" on categories;

-- 2. Disable Expenses RLS policies
drop policy if exists "Users can view their own expenses" on expenses;
drop policy if exists "Users can insert their own expenses" on expenses;
drop policy if exists "Users can update their own expenses" on expenses;
drop policy if exists "Users can delete their own expenses" on expenses;

-- 3. Disable Logs RLS policies
drop policy if exists "Users can view their own logs" on logs;
drop policy if exists "Users can insert their own logs" on logs; 