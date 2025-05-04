# Database Schema

## 1. Tables



### users

This table is managed by Supabase Auth.


Columns:
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid()
- `email` VARCHAR(255) NOT NULL
- `encrypted_password` VARCHAR(255) NOT NULL
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()
- `confirmed_at` TIMESTAMPTZ

Constraints:
- `UNIQUE (email)`

### categories
Columns:
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid()
- `user_id` UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE
- `name` VARCHAR(30) NOT NULL
- `is_default` BOOLEAN NOT NULL DEFAULT FALSE
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()
- `updated_at` TIMESTAMPTZ NOT NULL DEFAULT now()

Constraints:
- `CHECK (char_length(name) <= 30)`
- `UNIQUE (user_id, name)`
- `UNIQUE (user_id) WHERE is_default = TRUE`

### expenses
Columns:
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid()
- `user_id` UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE
- `amount` NUMERIC(12,2) NOT NULL CHECK (amount > 0)
- `description` VARCHAR(100)
- `date_of_expense` TIMESTAMPTZ NOT NULL
- `category_id` UUID NOT NULL DEFAULT get_default_category_id() REFERENCES categories(id) ON DELETE SET DEFAULT
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()
- `updated_at` TIMESTAMPTZ NOT NULL DEFAULT now()

Constraints:
- `CHECK (char_length(description) <= 100)`

### logs
Columns:
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid()
- `user_id` UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE
- `expense_id` UUID REFERENCES expenses(id) ON DELETE CASCADE
- `category_id` UUID REFERENCES categories(id) ON DELETE CASCADE
- `type` log_level NOT NULL
- `error_code` VARCHAR(50)
- `message` TEXT NOT NULL
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()

## 2. Relationships
- `users` (1) → (many) `categories`
- `users` (1) → (many) `expenses`
- `users` (1) → (many) `logs`
- `categories` (1) → (many) `expenses`
- `categories` (1) → (many) `logs`
- `expenses` (1) → (many) `logs`

## 3. Indexes
```sql
CREATE INDEX idx_categories_user_default ON categories (user_id, is_default);
CREATE INDEX idx_expenses_user_date ON expenses (user_id, date_of_expense DESC);
CREATE INDEX idx_expenses_user_amount ON expenses (user_id, amount);
CREATE INDEX idx_logs_user_created_at ON logs (user_id, created_at DESC);
```

## 4. PostgreSQL Policies & Triggers

### 4.1 Custom Types
```sql
CREATE TYPE log_level AS ENUM ('info','warning','error');
```

### 4.2 Row Level Security (RLS)
```sql
ALTER TABLE categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE expenses ENABLE ROW LEVEL SECURITY;
ALTER TABLE logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY user_access_categories ON categories
  USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());

CREATE POLICY user_access_expenses ON expenses
  USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());

CREATE POLICY user_access_logs ON logs
  USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());

-- RLS policies for users
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
CREATE POLICY user_self_select ON users
  FOR SELECT USING (id = auth.uid());
CREATE POLICY user_self_insert ON users
  FOR INSERT WITH CHECK (id = auth.uid());
CREATE POLICY user_self_update ON users
  FOR UPDATE USING (id = auth.uid()) WITH CHECK (id = auth.uid());
CREATE POLICY user_self_delete ON users
  FOR DELETE USING (id = auth.uid());
```

### 4.3 Default Category Logic
```sql
-- Function to get default category for current user
CREATE FUNCTION get_default_category_id() RETURNS UUID
  LANGUAGE plpgsql STABLE SECURITY DEFINER AS $$
BEGIN
  RETURN (
    SELECT id FROM categories
    WHERE user_id = auth.uid() AND is_default = TRUE
    LIMIT 1
  );
END;
$$;

-- Trigger to create "Uncategorized" category after user registration
CREATE FUNCTION create_default_category_trigger() RETURNS trigger AS $$
BEGIN
  INSERT INTO categories(user_id, name, is_default)
  VALUES (NEW.id, 'Uncategorized', TRUE);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_create_default_category
  AFTER INSERT ON users
  FOR EACH ROW EXECUTE FUNCTION create_default_category_trigger();
```

### 4.4 Prevent Deletion of Default Category
```sql
CREATE FUNCTION prevent_default_category_delete() RETURNS trigger AS $$
BEGIN
  IF OLD.is_default THEN
    RAISE EXCEPTION 'Cannot delete default category';
  END IF;
  RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_prevent_default_category_delete
  BEFORE DELETE ON categories
  FOR EACH ROW EXECUTE FUNCTION prevent_default_category_delete();
```

## 5. Additional Notes
- All timestamps are stored in UTC via `TIMESTAMPTZ`.
- Offset-limit pagination for expenses: `ORDER BY date_of_expense DESC LIMIT 20 OFFSET x`.
- Nightly snapshots and simple snake_case migrations. 