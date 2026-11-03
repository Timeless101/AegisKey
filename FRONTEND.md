# AegisKey webfrontend

De nieuwe webfrontend staat in **`src/client`**. HTML, CSS en JavaScript zijn zelfstandig te hosten en hebben geen buildstap nodig.

```sh
python -m http.server 5500 --directory src/client
```

Open **http://localhost:5500** en kies **Explore the demo vault**. De demo bewaart geen vaultdata; wijzigingen verdwijnen na vernieuwen.

Je nieuwe loginformulier gebruikt nu `POST /auth/login`. Start FastAPI en vul op **http://localhost:5500** een bestaand testaccount in bij **Test sign in**. Na succes verschijnt de gecontroleerde gebruiker; de route maakt nog geen sessie/token. Encryptiesleutels gaan niet naar de browser.

Je bestaande `/credentials/3` is aangesloten: start ook `fastapi dev src/api/main.py` en kies **Open local test API**, of open **http://localhost:5500/#/test-api**. Dit toont de echte response alleen-lezen, zonder login. Wachtwoorddecryptie en schrijfendpoints zijn nog niet aangesloten.

- [Starten, structuur, configuratie en beveiligingsgrens](docs/frontend/README.md)
- [API-contract en volgorde voor FastAPI-implementatie](docs/frontend/API_CONTRACT.md)
- [Uitgevoerde controles](docs/frontend/VALIDATION.md)

De frontend bevat de volledige interface en requests; echte authenticatie, vaultencryptie en opslag vereisen nog de Python/API-implementatie. De CLI-verificatielogica blijft behouden. Alleen de API-loginroute is aangepast voor een veilige response zonder encryptiesleutel en correcte foutstatussen.
