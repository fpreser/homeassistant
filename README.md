# Home Assistant — Configuration Préser

Configuration Home Assistant d'un foyer belge (Fabien, Gillian, Louis, Emma) — installation triphasée 40 A avec PV, Tesla Model Y, chauffage Evohome, et écosystème multi-appareils.

- **HA version** : 2026.2.3
- **Localisation** : Belgique, français
- **Réseau électrique** : 3×230 V sans neutre, 40 A, ~15 930 W max théorique (limite configurée 14 000 W)
- **Run** : container Docker (`ghcr.io/home-assistant/home-assistant:stable`) + sidecar `tesla_http_proxy` (compose-file local non versionné — contient des secrets)

## Structure du repo

```
.
├── config/                 # Toute la config Home Assistant (montée dans le container)
│   ├── configuration.yaml  # Point d'entrée (helpers, sensors, includes)
│   ├── automation/         # Automations en YAML séparé (merge_list)
│   ├── script/             # Scripts en YAML séparé (merge_named)
│   ├── template_sensors/   # Template sensors modernes (HA 2025.12+)
│   ├── packages/           # Packages thématiques (Tesla, énergie, températures…)
│   ├── python_scripts/     # Scrapers Selenium (Antargaz) + helpers (poubelles)
│   ├── custom_components/  # Intégrations HACS (gitignored)
│   └── .storage/           # Lovelace versionné, reste ignoré
├── docs/                   # Documentation détaillée par thème (voir ci-dessous)
├── tests/                  # Tests pytest des automations Tesla (gitignored)
└── .gitignore              # Ignore secrets, DB, logs, custom_components, tests
```

## Documentation

La doc est segmentée par thème dans [docs/](docs/) :

| Fichier | Contenu |
|---|---|
| [01_environnement_ha.md](docs/01_environnement_ha.md) | Vue d'ensemble HA, intégrations (Evohome, Tesla, Miele, Mercedes, etc.), helpers, dashboards |
| [02_energie_et_solaire.md](docs/02_energie_et_solaire.md) | P1 meter, PV, calculs surplus solaire, Energy dashboard |
| [03_tesla_smart_charge.md](docs/03_tesla_smart_charge.md) | Recharge intelligente Tesla : 15 automations (solaire + nocturne HC + refresh sur saut/chute conso) |
| [04_presence_et_chauffage.md](docs/04_presence_et_chauffage.md) | Présence, géolocalisation, chauffage Evohome, climatisation Panasonic |
| [05_awtrix_et_audio.md](docs/05_awtrix_et_audio.md) | Afficheur LED Awtrix (MQTT) + multiroom audio (Spotcast 4 comptes Spotify) |
| [06_appareils_et_securite.md](docs/06_appareils_et_securite.md) | Électroménager, sécurité, divers |

## Conventions

- **Secrets** : tous via [config/secrets.yaml](config/secrets.yaml) (gitignored). Voir [.gitignore](.gitignore) pour la liste exhaustive.
- **YAML** : automations et scripts éclatés dans des sous-dossiers via `!include_dir_merge_*`. Les fichiers en racine (`automations.yaml`, `scripts.yaml`) sont édités par l'UI HA.
- **Template sensors** : format moderne (`template:` top-level avec `!include_dir_merge_list template_sensors`).
- **Commits** : préfixes conventionnels (`feat(scope):`, `fix(scope):`, `chore(scope):`, `refactor(scope):`, `docs(scope):`).

## Intégrations clés

Évohome (chauffage 12 zones), Tesla Fleet API (custom component), Spotcast (4 comptes Spotify), Awtrix LED matrix (MQTT), Miele, Mercedes-Benz (MBAPI2020), Home Connect, ResMed MyAir, Panasonic AC, Dreo, Synology NAS, Prometheus, HomeKit Bridge, Emulated Roku, Google Home.

Scraping Selenium (Antargaz, niveau citerne gaz) via Selenium Hub local sur `192.168.1.10:4444`.
