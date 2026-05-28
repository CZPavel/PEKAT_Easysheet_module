# RUNBOOK

## Codex sync konflikty

1. Nejprve zopakuj doporu?en? bezpe?n? tok:
   ```powershell
   sync-codex.ps1 -Mode Down
   sync-codex.ps1 -Mode Up
   ```
2. Nema? session soubory jako prvn? krok.
3. Zachovej konfigura?n? z?lohy vytvo?en? sync skriptem.
4. Pokud commit sel?e kv?li Git identit?, nastav:
   ```powershell
   git config user.name "CZPavel"
   git config user.email "tvuj-email@example.com"
   ```

## Hard exclusions

Nikdy nesynchronizovat ani necommitovat:

- `~/.codex/auth.json`
- `~/.codex/tmp/`
- `~/.codex/models_cache.json`
- `~/.codex/skills/`
