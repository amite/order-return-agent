# Order Returns Agent - Database Queries
# Database: ./data/order_return.db
# 
# Usage:
#   source order_returns_agent.session.nu
#   list-tables
#   get-schemas
#   get-schema-info
#   top-customers
#   get-conversation-logs
#   get-session-logs <session-id>
#   get-sessions
#   get-session-summary <session-id>

# Database path constant
const DB_PATH = "./data/order_return.db"

# List all tables in the database
def list-tables [] {
    open $DB_PATH | query db "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name;"
}

# Get CREATE TABLE statements (schemas) for all tables
def get-schemas [] {
    open $DB_PATH | query db "SELECT name, sql FROM sqlite_master WHERE type = 'table' ORDER BY name;"
}

# Get detailed schema info for a specific table
# Usage: get-table-schema <table_name>
def get-table-schema [table_name: string] {
    let sql = ('PRAGMA table_info(' + $table_name + ');')
    open $DB_PATH | query db $sql
}

# Get schema info for all tables (using a query)
def get-schema-info [] {
    open $DB_PATH | query db 'SELECT m.name AS table_name, p.name AS column_name, p.type AS column_type, p."notnull" AS not_null, p.dflt_value AS default_value, p.pk AS primary_key FROM sqlite_master m JOIN pragma_table_info(m.name) p WHERE m.type = "table" ORDER BY m.name, p.cid;'
}

# Top customers by total spending
# Usage: top-customers [limit: int]
def top-customers [
    limit: int = 10  # Number of top customers to return
] {
    let sql = ('SELECT c.id, c.email, c.first_name, c.last_name, COUNT(o.id) AS total_orders, ROUND(SUM(o.total_amount), 2) AS total_spent, c.loyalty_tier FROM customers c LEFT JOIN orders o ON c.id = o.customer_id GROUP BY c.id, c.email, c.first_name, c.last_name, c.loyalty_tier ORDER BY total_spent DESC LIMIT ' + ($limit | into string) + ';')
    open $DB_PATH | query db $sql
}

# Get all orders
# Usage: get-orders [limit: int]
def get-orders [
    limit: int = 100
] {
    let sql = ('SELECT * FROM orders ORDER BY order_date DESC LIMIT ' + ($limit | into string) + ';')
    open $DB_PATH | query db $sql
}

# Get all customers
# Usage: get-customers [limit: int]
def get-customers [
    limit: int = 100
] {
    let sql = ('SELECT * FROM customers ORDER BY id LIMIT ' + ($limit | into string) + ';')
    open $DB_PATH | query db $sql
}

# Get order items for a specific order
# Usage: get-order-items <order_id>
def get-order-items [order_id: int] {
    let sql = ('SELECT * FROM order_items WHERE order_id = ' + ($order_id | into string) + ';')
    open $DB_PATH | query db $sql
}

# Get customer orders
# Usage: get-customer-orders <customer_id>
def get-customer-orders [customer_id: int] {
    let sql = ('SELECT * FROM orders WHERE customer_id = ' + ($customer_id | into string) + ' ORDER BY order_date DESC;')
    open $DB_PATH | query db $sql
}

# Get return policies
def get-return-policies [] {
    open $DB_PATH | query db "SELECT * FROM return_policies WHERE is_active = 1 ORDER BY category, policy_name;"
}

# Get RMAs (Return Merchandise Authorizations)
# Usage: get-rmas [limit: int]
def get-rmas [
    limit: int = 100
] {
    let sql = ('SELECT * FROM rmas ORDER BY created_at DESC LIMIT ' + ($limit | into string) + ';')
    open $DB_PATH | query db $sql
}

# Get conversation logs from all sessions (most recent first)
# Usage: get-conversation-logs [limit: int]
def get-conversation-logs [
    limit: int = 50
] {
    let sql = ('SELECT id, substr(session_id, 1, 8) as session_id, message_type, substr(content, 1, 80) as content_preview, created_at FROM conversation_logs ORDER BY created_at DESC LIMIT ' + ($limit | into string) + ';')
    open $DB_PATH | query db $sql
}

# Get conversation logs for a specific session (chronological order)
# Usage: get-session-logs <session-id> [limit: int]
def get-session-logs [
    session_id: string,
    limit: int = 100
] {
    let sql = ('SELECT id, substr(session_id, 1, 8) as session_id, message_type, substr(content, 1, 80) as content_preview, created_at FROM conversation_logs WHERE session_id LIKE "' + $session_id + '%" ORDER BY created_at ASC LIMIT ' + ($limit | into string) + ';')
    open $DB_PATH | query db $sql
}

# Get all unique conversation sessions
# Usage: get-sessions [limit: int]
def get-sessions [
    limit: int = 20
] {
    let sql = ('SELECT substr(session_id, 1, 8) as session_id, COUNT(*) as message_count, MIN(created_at) as started_at, MAX(created_at) as ended_at FROM conversation_logs GROUP BY session_id ORDER BY MAX(created_at) DESC LIMIT ' + ($limit | into string) + ';')
    open $DB_PATH | query db $sql
}

# Get summary statistics for a specific session
# Usage: get-session-summary <session-id>
def get-session-summary [
    session_id: string
] {
    let sql = ('SELECT substr(session_id, 1, 8) as session_id, SUM(CASE WHEN message_type = "user" THEN 1 ELSE 0 END) as user_messages, SUM(CASE WHEN message_type = "assistant" THEN 1 ELSE 0 END) as assistant_messages, COUNT(*) as total_messages, MIN(created_at) as started_at, MAX(created_at) as ended_at FROM conversation_logs WHERE session_id LIKE "' + $session_id + '%" GROUP BY session_id;')
    open $DB_PATH | query db $sql
}
