# SQL and Nushell Database Commands

This document contains helpful SQL and Nushell commands for working with the `order_return.db` database.

## Database Location
- **Path:** `./data/order_return.db`
- **Type:** SQLite

---

## SQLite CLI Commands

### Basic SQLite CLI Usage

```bash
# Connect to database
sqlite3 ./data/order_return.db


# Connect with headers enabled
sqlite3 -header ./data/order_return.db

# Connect with headers and column mode
sqlite3 -header -column ./data/order_return.db

# Run a single query
sqlite3 -header -column ./data/order_return.db "SELECT * FROM orders LIMIT 5;"

# Pipe SQL file
sqlite3 -header ./data/order_return.db < order_returns_agent.session.sql
```

### SQLite Interactive Commands

```sql
-- Enable column headers
.headers on

-- open database within sqlite
.open ./data/order_return.db

-- Clear screen (moves cursor to top)
.shell clear
-- Or use Ctrl+L (works in most terminals)

-- Set column mode for better formatting
.mode column

-- Set column widths (adjust numbers as needed)
.width 8 10 25 20 10 15 30 20

-- Show all tables
.tables

-- Show schema for a specific table
.schema table_name

-- Exit SQLite
.quit
-- or
.exit
```

---

## SQL Queries

### 1. List All Tables

```sql
SELECT name
FROM sqlite_master
WHERE type = 'table'
ORDER BY name;
```

### 2. Get CREATE TABLE Statements (Schemas)

```sql
SELECT name, sql
FROM sqlite_master
WHERE type = 'table'
ORDER BY name;
```

### 3. Get Schema Info for a Specific Table

```sql
PRAGMA table_info(table_name);
```

**Example:**
```sql
PRAGMA table_info(customers);
```

### 4. Get Detailed Schema Info for All Tables

```sql
SELECT 
    m.name AS table_name,
    p.name AS column_name,
    p.type AS column_type,
    p."notnull" AS not_null,
    p.dflt_value AS default_value,
    p.pk AS primary_key
FROM sqlite_master m
    JOIN pragma_table_info(m.name) p
WHERE m.type = 'table'
ORDER BY m.name, p.cid;
```

### 5. Top Customers by Total Spending

```sql
SELECT 
    c.id,
    c.email,
    c.first_name,
    c.last_name,
    COUNT(o.id) AS total_orders,
    ROUND(SUM(o.total_amount), 2) AS total_spent,
    c.loyalty_tier
FROM customers c
    LEFT JOIN orders o ON c.id = o.customer_id
GROUP BY 
    c.id,
    c.email,
    c.first_name,
    c.last_name,
    c.loyalty_tier
ORDER BY total_spent DESC
LIMIT 10;
```

### 6. Get All Orders

```sql
SELECT * 
FROM orders 
ORDER BY order_date DESC 
LIMIT 100;
```

### 7. Get All Customers

```sql
SELECT * 
FROM customers 
ORDER BY id 
LIMIT 100;
```

### 8. Get Order Items for a Specific Order

```sql
SELECT * 
FROM order_items 
WHERE order_id = 1;
```

### 9. Get Customer Orders

```sql
SELECT * 
FROM orders 
WHERE customer_id = 1 
ORDER BY order_date DESC;
```

### 10. Get Active Return Policies

```sql
SELECT * 
FROM return_policies 
WHERE is_active = 1 
ORDER BY category, policy_name;
```

### 11. Get RMAs (Return Merchandise Authorizations)

```sql
SELECT * 
FROM rmas 
ORDER BY created_at DESC 
LIMIT 100;
```

---

## Nushell Commands

### Setup

First, source the nushell script to load all functions:

```nu
source order_returns_agent.session.nu
```

Or from command line:
```bash
nu -c "source order_returns_agent.session.nu; list-tables"
```

### Available Nushell Functions

#### 1. List All Tables

```nu
list-tables
```

**Output:** Table with all table names in the database.

#### 2. Get CREATE TABLE Statements

```nu
get-schemas
```

**Output:** Table with table names and their CREATE TABLE SQL statements.

#### 3. Get Schema for a Specific Table

```nu
get-table-schema <table_name>
```

**Examples:**
```nu
get-table-schema customers
get-table-schema orders
get-table-schema order_items
```

**Output:** Detailed column information for the specified table.

#### 4. Get Schema Info for All Tables

```nu
get-schema-info
```

**Output:** Comprehensive schema information for all tables including column names, types, nullability, defaults, and primary keys.

#### 5. Top Customers by Total Spending

```nu
top-customers [limit]
```

**Examples:**
```nu
top-customers          # Default: top 10
top-customers 5        # Top 5 customers
top-customers 20       # Top 20 customers
```

**Output:** Table with customer information and total spending, ordered by total spent (descending).

#### 6. Get All Orders

```nu
get-orders [limit]
```

**Examples:**
```nu
get-orders            # Default: 100 orders
get-orders 50         # Get 50 orders
get-orders 1000       # Get 1000 orders
```

**Output:** Table with all orders, ordered by order_date (descending).

#### 7. Get All Customers

```nu
get-customers [limit]
```

**Examples:**
```nu
get-customers         # Default: 100 customers
get-customers 50      # Get 50 customers
```

**Output:** Table with customer information, ordered by id.

#### 8. Get Order Items for a Specific Order

```nu
get-order-items <order_id>
```

**Examples:**
```nu
get-order-items 1
get-order-items 42
```

**Output:** Table with all items for the specified order.

#### 9. Get Customer Orders

```nu
get-customer-orders <customer_id>
```

**Examples:**
```nu
get-customer-orders 1
get-customer-orders 10
```

**Output:** Table with all orders for the specified customer, ordered by order_date (descending).

#### 10. Get Return Policies

```nu
get-return-policies
```

**Output:** Table with all active return policies, ordered by category and policy name.

#### 11. Get RMAs

```nu
get-rmas [limit]
```

**Examples:**
```nu
get-rmas              # Default: 100 RMAs
get-rmas 50           # Get 50 RMAs
```

**Output:** Table with RMA information, ordered by created_at (descending).

---

## Quick Reference

### SQLite CLI Quick Commands

```bash
# Quick query with headers
sqlite3 -header -column ./data/order_return.db "SELECT * FROM orders LIMIT 5;"

# Export to CSV
sqlite3 -header -csv ./data/order_return.db "SELECT * FROM orders;" > orders.csv

# Export to JSON (requires jq)
sqlite3 -json ./data/order_return.db "SELECT * FROM orders LIMIT 5;" | jq
```

### Nushell Quick Commands

```nu
# One-liner queries
open ./data/order_return.db | query db "SELECT * FROM orders LIMIT 5;"

# Chain with other nushell commands
open ./data/order_return.db | query db "SELECT * FROM customers;" | where loyalty_tier == "Gold"

# Export to CSV
open ./data/order_return.db | query db "SELECT * FROM orders;" | to csv > orders.csv
```

---

## Database Schema

### Tables

1. **conversation_logs** - Chat conversation logs
2. **customers** - Customer information
3. **order_items** - Individual items in orders
4. **orders** - Order records
5. **return_policies** - Return policy definitions
6. **rmas** - Return Merchandise Authorizations

### Key Relationships

- `orders.customer_id` → `customers.id`
- `order_items.order_id` → `orders.id`
- `rmas.order_id` → `orders.id`
- `rmas.customer_id` → `customers.id`
- `conversation_logs.customer_id` → `customers.id`

---

## Tips and Tricks

### SQLite CLI

1. **Better Output Formatting:**
   ```sql
   .headers on
   .mode column
   .width 10 20 15 10
   ```

2. **Clear Screen:**
   - Use `.shell clear` or `Ctrl+L`

3. **History:**
   - Use arrow keys to navigate command history
   - Use `Ctrl+R` to search history

### Nushell

1. **Piping Results:**
   ```nu
   top-customers | where total_spent > 1000
   get-orders | sort-by total_amount | reverse | first 10
   ```

2. **Filtering:**
   ```nu
   get-customers | where loyalty_tier == "Gold"
   get-orders | where status == "Delivered"
   ```

3. **Exporting:**
   ```nu
   top-customers | to csv > top_customers.csv
   get-orders | to json > orders.json
   ```

---

## Files

- **SQL Queries:** `order_returns_agent.session.sql`
- **Nushell Script:** `order_returns_agent.session.nu`
- **Database:** `./data/order_return.db`

---

## Additional Resources

- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [Nushell Documentation](https://www.nushell.sh/book/)
- [SQLite Tutorial](https://www.sqlitetutorial.net/)
