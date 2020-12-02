# Projekt-AASD-DKPR
Projekt z przedmiotu AASD - Zespół DKPR

SPADE


## Instalacja
1. Zainstalować `SPADE`
```pip
pip install spade
```

2. Zainstalować `Prosody`
```pip
sudo apt-get install prosody
```

## Konfigurowanie
_LINUX/WINDOWS(WSL)_
1. do `/etc/prosody/` skopiować plik konfiguracyjny: `prosody.cfg.lua`
2. nadać uprawnienia dla folderu /etc/prosody:
   ```bash
   chown `whoami` /etc/prosody -R
   ```
3. Zrestartować prosody: systemctl restart prosody
4. Dodać agenta: np. `prosodyctl adduser {nazwa_agenta}@localhost`
5. Podać hasło