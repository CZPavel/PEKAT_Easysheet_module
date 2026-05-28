# Technical notes

- Backend je zat?m in-memory, aby bootstrap z?stal mal? a testovateln?.
- Produk?n? verze mus? doplnit SQLite/PostgreSQL persistenci a audit log.
- Formula runtime nesm? pou??vat `eval()` nad u?ivatelsk?m vstupem.
- PEKAT Code bridge mus? m?t v?dy explicitn? timeout a fallback.
