# 4. Securitate

| Masura | Unde |
|---|---|
| Autentificare (parola din mediu, comparare constant-time) | `before_request` |
| Securitate cross-site: API-ul cere `Content-Type: application/json` | rutele POST |
| Fara `shell=True`, input validat cu regex/`ipaddress` | `main.py` |
| SSH doar de la IP-ul tau (security group / NSG) | `terraform/*` |
| Doar comenzi presetate pe SSH (liber doar cu `ALLOW_CUSTOM_SSH=1`) | `PRESETS` |
| Container non-root, chei montate read-only | `Dockerfile`, compose |
| Headere HTTP de securitate, fara XSS (`textContent`) | `after_request`, dashboard |
| IMDSv2, disc criptat (AWS), parola SSH dezactivata (Azure) | Terraform |

## Reguli
- Nu expune dashboardul pe internet fara VPN/reverse proxy cu HTTPS (ex. Tailscale sau Caddy).
- Nu pune niciodata `.env` sau `data/` in Git (sunt in `.gitignore`).
- Foloseste utilizatori cloud cu drepturi minime si roteste cheile.
