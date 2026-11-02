# AegisKey webfrontend

De nieuwe webfrontend staat in **`src/client`**. HTML, CSS en JavaScript zijn zelfstandig te hosten en hebben geen buildstap nodig.

```sh
python -m http.server 5500 --directory src/client
```

Open **http://localhost:5500** en kies **Explore the demo vault**. De demo bewaart geen vaultdata; wijzigingen verdwijnen na vernieuwen.

- [Starten, structuur, configuratie en beveiligingsgrens](docs/frontend/README.md)
- [API-contract en volgorde voor FastAPI-implementatie](docs/frontend/API_CONTRACT.md)
- [Uitgevoerde controles](docs/frontend/VALIDATION.md)

De frontend bevat de volledige interface en requests; echte authenticatie, vaultencryptie en opslag vereisen nog de Python/API-implementatie. De bestaande CLI en Python-bestanden zijn bij deze frontendoplevering niet veranderd.
