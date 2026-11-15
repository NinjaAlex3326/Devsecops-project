# 1. Start rapid

## Ce face aplicatia
Un **dashboard** care creeaza VM-uri in AWS, Azure si OCI cu un click (prin Terraform), le gestioneaza prin SSH cu comenzi presetate si iti permite sa adaugi VM-urile clientilor.

## Pasi
1. `cp .env.example .env` si completeaza valorile.
2. Genereaza o cheie SSH: `ssh-keygen -t ed25519 -f ~/.ssh/deployer`
3. `docker compose up --build`
4. Deschide `http://127.0.0.1:8000` (user: orice, parola: `ADMIN_PASSWORD`).
5. Introdu numele, providerul si **IP-ul tau public** (cauta "what is my ip"); doar acel IP va avea acces SSH.
6. Dupa 1-3 minute VM-ul apare *running*. Foloseste butoanele uptime/disk/docker etc.
7. **Distruge VM-urile pe care nu le folosesti** ca sa nu platesti degeaba.

## Depanare
Butonul **log** afiseaza outputul Terraform. Cele mai frecvente erori: credentiale lipsa, quota, regiune gresita.
