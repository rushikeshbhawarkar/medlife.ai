# Database design

PostgreSQL is the only supported database. Configure it with `POSTGRES_*` variables or a PostgreSQL `DATABASE_URL`.

## ER diagram

```text
Account (1) ───────< FamilyMember (1) ───────< ChatMessage
   email unique       slot 1..4                  position unique per member
                      tokens_used 0..100          role, text, ts (bigint)
```

- **Account** stores a normalized, unique email, a creation timestamp, and `password` (a Django PBKDF2 hash, never plain text; empty for older email-only accounts until they sign up). The admin page hides this column.
- **FamilyMember** stores the camelCase frontend profile using conventional snake_case database columns. `(account, slot)` is unique; slot is constrained to 1–4. `tokens_used` is constrained to 0–100.
- **ChatMessage** belongs to one member with cascade deletion. `(member, position)` is unique and indexed. `ts` is a `BigIntegerField` so JavaScript millisecond timestamps round-trip without conversion.

## Integrity and concurrency

The member-add service locks the parent `Account` row inside a transaction before counting members and choosing the lowest unused slot. Requests adding members to the same account therefore serialize, preventing two simultaneous requests from both observing only three members and creating a fifth. Unique constraints provide a second layer of protection.

Token consumption locks the parent account row inside a transaction, checks the current count, and increments it before committing. This serializes competing requests and the database check constraint rejects values outside 0–100. A per-member row lock could be used instead; locking the account is simple and consistent with member-add locking.

Chat saving deletes and bulk-creates the supplied list in one transaction. The position field preserves array order and the timestamp is stored as sent. Deleting a family member cascades to its chat messages.

## Privacy

These tables contain sensitive profile and conversation data. Admin access must be restricted. Use encrypted database storage, TLS connections where supported, backups with restricted access, and a documented retention policy before production.
