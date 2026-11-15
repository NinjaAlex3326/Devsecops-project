# 2. Arhitectura

```
Browser -> Flask (app/main.py) -> terraform (subprocess) -> AWS / Azure / OCI
                              -> ssh (subprocess)        -> VM-uri (ale tale / clienti)
                              -> data/deployments.json   (starea dashboardului)
```
- **Un folder Terraform separat per VM** (`data/deployments/<nume>/`) cu state propriu: distrugi un VM fara sa afectezi alte VM-uri.
- Variabilele ajung in `terraform.tfvars.json`, citit automat de Terraform.
- Terraform ruleaza in thread de fundal; dashboardul reimprospateaza statusul la 8 secunde.
- Nu se foloseste `shell=True`: argumentele sunt liste, deci inputul nu poate injecta comenzi.

## Concepte DevOps pe care le inveti aici
Infrastructure as Code, state, idempotenta, containerizare, principiul privilegiului minim.
