# AegisKey webfrontend

De responsive frontend volgt de navy/cyaan huisstijl. Hij gebruikt gewone HTML, CSS en ES-modules: geen framework, buildstap, CDN of externe afbeeldingsdienst. Je kunt de bestanden zelfstandig hosten, los van ChatGPT.

## Lokaal starten

Voer dit vanuit de repository-root uit:

```sh
python -m http.server 5500 --directory src/client
```

Open **http://localhost:5500**. Gebruik **Explore the demo vault** om zonder API te testen. Rechtstreeks naar **http://localhost:5500/#/demo** kan ook. Open `index.html` niet via `file://`, omdat browsers ES-modules daar blokkeren.

De oude URLs `authentication/index.html` en `web/vaultpage/index.html` verwijzen automatisch naar de nieuwe app.

### Wat werkt zonder backend?

- Expliciete demo met acht fictieve items, uitsluitend in het geheugen.
- Alle items, passwords, notes, identities, favorites en Personal/Work-collecties.
- Zoeken, sorteren, filters, paginering en lijst-/kaartweergave.
- Itemdetails, wachtwoord tonen/verbergen, kopiëren, toevoegen, wijzigen en definitief verwijderen met bevestiging.
- Notes en identities hebben eigen invoervelden.
- Lokale wachtwoordgenerator met Web Crypto, afwijzing van modulo-bias en gegarandeerde aanwezigheid van iedere geselecteerde tekengroep.
- Responsive sidebar en formulieren, toetsenbordbediening, focusbeheer en reduced-motion ondersteuning.
- Licht/donker thema en instelbare inactiviteitsvergrendeling.

Demo-items, gewijzigde gegevens en gegenereerde wachtwoorden worden **niet opgeslagen**. Vernieuwen wist de demo. Alleen voorkeuren en (na expliciete keuze) het e-mailadres worden lokaal bewaard. De vlag dat de view vergrendeld is staat in `sessionStorage`; geen wachtwoorden of tokens.

## Echte API aansluiten

Lees eerst [API_CONTRACT.md](API_CONTRACT.md). De huidige Python-voorbeeldroutes in deze repository implementeren dat contract nog niet. De frontend doet **geen** alsof-login wanneer die routes ontbreken. Een serverfout houdt je op de loginpagina; de demoknop is een aparte, herkenbare keuze.

Alle requests staan in `src/client/js/api.js`. De interface staat in `app.js`; voeg daar geen losse `fetch`-aanroepen toe. Stel in `src/client/config.js` de API-prefix en loginmethode in:

```js
window.AEGIS_CONFIG = Object.freeze({
  apiBaseUrl: '/api',
  loginMode: 'redirect',
  enableDemo: false,
  requestTimeoutMs: 15000,
});
```

- `password`: de eigen login-, registratie- en accountrecoveryformulieren gebruiken de gedocumenteerde JSON-endpoints. Er is ook een MFA-challengeformulier voor TOTP.
- `redirect`: de inlog-/registratieknoppen gaan naar jouw backend, die de OIDC-login afhandelt. Dit past bijvoorbeeld bij een zelfgehoste Keycloak. De backend doet code exchange, valideert OIDC en zet een sessiecookie. De frontend verwerkt geen OAuth-codes of refresh tokens.
- `enableDemo: false`: verwijdert de demoknop en blokkeert de demo-route. De backend mag nooit vertrouwen op deze clientinstelling als toegangscontrole.

**Aanbevolen hosting:** één HTTPS-origin. Reverse proxy `/api/*` naar FastAPI; statische frontend op `/`. Maak je FastAPI-routes onder `/api` beschikbaar of strip deze prefix bewust in de proxy. Voor het lokale prototype kun je `apiBaseUrl: 'http://localhost:8000'` gebruiken. Sta dan exact `http://localhost:5500` toe via CORS, met credentials; geen wildcard. Gebruik overal dezelfde hostnaam (`localhost` is niet `127.0.0.1`). Cookie- en CSRF-configuratie blijven serververantwoordelijkheden.

De frontend is geen Keycloak-installatie. Keycloak, een database, sessies, CSRF-controle, encryptie en API-endpoints moet je nog aan de serverkant implementeren.

## Beveiligingsgrens

Deze versie sluit aan op een **server die de vault kan ontgrendelen**, vergelijkbaar met de bestaande Python/CLI-laag. Het is geen zero-knowledge/E2EE-webvault. Bij het toevoegen van een login gaat de ingevulde itempassword via HTTPS naar de server; bij expliciet reveal/copy vraagt de frontend die via HTTPS op. De frontend voegt geen eigen cryptografisch opslagformaat toe.

Wil je later client-side encryptie, dan moet het cryptografische ontwerp én dit contract eerst worden aangepast. Alleen Keycloak toevoegen maakt de vault niet end-to-end versleuteld. Accountwachtwoord en vaultwachtwoord zijn afzonderlijke concepten; OIDC levert geen decryptiesleutel. Ontwerp ook vaultsetup en herstel vóór productiegebruik.

De lokale auto-lock wist de zichtbare gegevens en vraagt de backend de vault te vergrendelen. Server-side idle/max timeouts en daadwerkelijke sleutelverwijdering zijn verplicht. Bij een netwerkfout meldt de interface dat serververgrendeling of uitloggen niet bevestigd is. Een lokale vergrendeling is geen garantie dat een server een nog geldige sessie heeft ingetrokken.

Wachtwoorden worden na 30 seconden weer gemaskeerd in details. Gegenereerde wachtwoorden verdwijnen na vijf minuten uit de generator. Dit is geen gegarandeerde geheugenoverschrijving. Kopiëren schrijft naar het systeemklembord en wist dat niet automatisch. Clipboard werkt onder HTTPS of localhost, afhankelijk van browserrechten; bij weigering volgt een melding.

Voor echte gebruikersgegevens is een onafhankelijke securityreview van de complete applicatie nodig. De bestaande CLI-securitydocumentatie blijft van toepassing op de CLI, niet als certificering van de webapp.

## Bestanden

| Bestand | Verantwoordelijkheid |
| --- | --- |
| `src/client/index.html` | Ingang van de webapp |
| `src/client/config.js` | Publieke serverconfiguratie, nooit secrets |
| `src/client/css/app.css` | Huisstijl, layout, mobile en dark mode |
| `src/client/js/app.js` | Navigatie, formulieren, UI-state en sessieflow |
| `src/client/js/api.js` | Alle HTTP-aanroepen, CSRF, timeouts en statusafhandeling |
| `src/client/js/demo.js` | Fictieve in-memory API-vervanger |
| `src/client/js/utils.js` | Escaping, veilige URLs en generator |
| `src/client/js/icons.js` | Scherpe SVG-interface-iconen |
| `src/client/assets/` | Lokale branding |

Je bestaande afbeeldingen onder `src/client/images` blijven beschikbaar. De app gebruikt een kleine consistente SVG-markering en een scherp wit/cyaan woordmerk in dezelfde huisstijl. Er worden geen sitefavicons vanaf derden opgehaald. Lettertype: lokaal geïnstalleerde Geist/Inter indien beschikbaar, anders systeemfont; geen externe fontrequests.

## Controleren

Node.js 22 of nieuwer, zonder extra packages:

```sh
node --test src/client/tests/frontend.test.js
```

De tests controleren de generator, veilige URLs/escaping, demo-CRUD, ontbreken van wachtwoorden in metadata, CSRF/cookies, sessieverloop, responsevalidatie, errorredactie en timeouts.

Browsercontrole: test demo → toevoegen → zoeken → details → wijzigen → verwijderen; notes/identities; generator; lock/unlock; settings; loginfouten. Controleer op 390px mobiel, tablet en desktop. Zie [VALIDATION.md](VALIDATION.md) voor de controles van deze oplevering.
