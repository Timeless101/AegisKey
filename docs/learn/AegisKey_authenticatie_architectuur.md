# AegisKey — authenticatie-architectuur

Ontwerpbesluit, 27 oktober 2026. Basis: commit `64759b1c5a93ebdea7ebc832b2428a40a499d7c3` van 26 oktober 2026. Dit document beschrijft voorgenomen gedrag; de integratie is niet geïmplementeerd of getest. Er zijn geen wijzigingen naar GitHub geschreven.

## 1. Wat de code nu doet

- De commit voegt `better-auth: ^1.7.13` toe aan `package.json`. In de onderzochte boom staan nog geen Better Auth-serverconfiguratie, clientconfiguratie of gemounte auth-handler.
- `src/client/authentication/auth.js` POST naar `http://127.0.0.1:8000/login`, met `username` en `pwd`, zonder expliciete JSON Content-Type. `LoginSchema` verwacht `email` en `password`. Het formulier en het model sluiten dus niet aan.
- `src/api/routers/auth/login.py` print het ontvangen model. Dat valideert geen account, maakt geen sessie en kan het wachtwoord loggen. Een geslaagde HTTP-aanroep bewijst geen authenticatie.
- `src/api/routers/credentials/credentials.py` gebruikt hardcoded `userid=1`. De opslagfunctie ondersteunt al een combinatie van credential-ID en gebruiker-ID; de vertrouwde gebruiker moet nog uit de request-authenticatie komen.
- `src/api/main.py` combineert wildcard origins met `allow_credentials=True`. Vervang dit voor browserauthenticatie door concrete toegestane origins, of gebruik één origin via een reverse proxy.

Broncode: [commit](https://github.com/Timeless101/AegisKey/commit/64759b1c5a93ebdea7ebc832b2428a40a499d7c3), [formulier](https://github.com/Timeless101/AegisKey/blob/64759b1c5a93ebdea7ebc832b2428a40a499d7c3/src/client/authentication/auth.js), [loginroute](https://github.com/Timeless101/AegisKey/blob/64759b1c5a93ebdea7ebc832b2428a40a499d7c3/src/api/routers/auth/login.py), [model](https://github.com/Timeless101/AegisKey/blob/64759b1c5a93ebdea7ebc832b2428a40a499d7c3/src/api/models/login_models.py), [credential-route](https://github.com/Timeless101/AegisKey/blob/64759b1c5a93ebdea7ebc832b2428a40a499d7c3/src/api/routers/credentials/credentials.py).

## 2. Gekozen taakverdeling

Gebruik Better Auth voor accountlogin en sessiebeheer. Gebruik de JWT-plugin om vanuit een geldige sessie een kortlevend toegangstoken voor FastAPI te verkrijgen. FastAPI valideert dat token en bepaalt vervolgens de lokale kluisgebruiker en diens toegang tot gegevens.

| Onderdeel | Verantwoordelijkheid |
|---|---|
| Browser | Formulier, Better Auth-client, tijdelijk JWT in geheugen, API-aanroepen |
| Better Auth-server | Registratie, wachtwoordhashing en controle, sessies, uitloggen, JWT-uitgifte en publieke verificatiesleutels |
| FastAPI | JWT-verificatie, lokale gebruikersmapping, eigendomscontrole en kluisfunctionaliteit |
| Database | Better Auth-tabellen plus eigen applicatie-/kluistabellen; afzonderlijk beheer van de schema's |

E-mailverificatie en wachtwoordherstel zijn Better Auth-functionaliteit die je apart moet configureren, inclusief mailbezorging. Installeren alleen activeert dit niet.

Better Auth heeft een JavaScript/TypeScript-serverruntime nodig. FastAPI draait Python. Ze kunnen in dezelfde repository en op dezelfde machine staan, maar vormen hier twee processen. Een aparte fysieke server is niet nodig. Een frontend-buildtool is geen vervanging voor de auth-server. Zie [installatie](https://better-auth.com/docs/installation) en [email/password](https://better-auth.com/docs/authentication/email-password).

Voorgestelde publieke indeling achter één HTTPS-origin:

| Pad | Afhandeling |
|---|---|
| `/` en statische bestanden | Frontend |
| `/api/auth/*` | Better Auth-server |
| `/api/vault/*` | FastAPI, waarbij de proxy desgewenst `/api/vault` verwijdert |

Gebruik lokaal consequent `localhost` óf `127.0.0.1`. Verschillende poorten zijn verschillende origins. Als je lokaal rechtstreeks tussen origins werkt, configureer concrete CORS-origins, credentials voor de auth-cookie en Better Auth trusted origins. Laat de origin-/CSRF-controles van Better Auth ingeschakeld.

## 3. Sessie, Bearer en JWT

- **Sessie:** Better Auth houdt de login bij; de browser stuurt de sessiecookie naar de auth-server. Kies een HttpOnly-cookie, Secure onder HTTPS, met passende SameSite-instelling.
- **Bearer:** de manier waarop de client een toegangsbewijs meestuurt: `Authorization: Bearer <waarde>`. Het woord zegt niet welk tokenformaat wordt gebruikt.
- **JWT:** een ondertekend token met claims voor FastAPI. De inhoud is leesbaar; zet er geen wachtwoord of encryptiesleutel in.

De Better Auth Bearer-plugin ondersteunt sessietokens via de Authorization-header. Dat maakt zo'n sessietoken niet automatisch een JWT dat FastAPI via JWKS kan controleren. Voor dit browserontwerp is die plugin niet nodig: de cookie onderhoudt de sessie; de JWT-plugin levert het API-token. Zie [Bearer-plugin](https://better-auth.com/docs/plugins/bearer), [JWT-plugin](https://better-auth.com/docs/plugins/jwt) en [sessiebeheer](https://better-auth.com/docs/concepts/session-management).

## 4. Requestverloop

1. Het formulier roept `authClient.signIn.email({email, password})` aan. Het accountwachtwoord gaat naar Better Auth; verwijder daarvoor de voorlopige Python-loginroute en het printen van logininformatie.
2. Better Auth controleert de login en zet de sessiecookie.
3. De client vraagt met die sessie een JWT aan via `authClient.token()` uit de JWT-clientplugin.
4. De browser bewaart het JWT alleen in geheugen en verstuurt het naar FastAPI als Bearer-token. Na een paginareload vraagt hij met de bestaande cookie een nieuw JWT aan.
5. FastAPI verifieert het JWT, zoekt de lokale gebruiker en filtert alle kluisquery's op diens interne ID.

Klein frontendvoorbeeld, na succesvolle login en met foutafhandeling rondom beide stappen:

```javascript
const { data, error } = await authClient.token();
if (error || !data?.token) return; // toon login-/sessiefout
await fetch('/api/vault/me', {
  headers: { Authorization: `Bearer ${data.token}` }
});
```

Tokens vernieuwen gebeurt via de bestaande Better Auth-sessie. Bouw voor deze opzet geen eigen FastAPI-refresh-tokenendpoint. Bij verlopen JWT: vraag één keer een nieuw token aan; mislukt dat door een verlopen sessie, laat opnieuw inloggen. Vermijd oneindige retries. Herhaal muterende verzoeken alleen wanneer zeker is dat de oorspronkelijke operatie nog niet is uitgevoerd.

Ontwerpinstellingen: JWT-levensduur **5 minuten**, vaste issuer bijvoorbeeld `https://aegiskey.example`, audience `aegiskey-api`, algoritme **EdDSA/Ed25519**. Dit zijn voorgestelde instellingen; `.example` is een placeholder. Configureer ze expliciet in Better Auth en FastAPI, en beperk de JWT-payload tot noodzakelijke gegevens. Gebruik de stabiele Better Auth user-ID als `sub`, nooit het veranderlijke e-mailadres. Controleer de daadwerkelijke lockfileversie voordat je de configuratie implementeert; `^1.7.13` is een bereik.

## 5. JWT-validatie in FastAPI

Gebruik `HTTPBearer(auto_error=False)` voor extractie en eigen consistente foutafhandeling. Dit leest de header; het bewijst nog geen identiteit. Gebruik bijvoorbeeld `PyJWT[crypto]` voor verificatie. Dat is een nieuwe, nog toe te voegen Python-dependency.

De validator moet:

1. Een ontbrekende, lege of verkeerd gevormde Bearer-header weigeren.
2. De sleutel bij `kid` ophalen uit de vaste Better Auth-JWKS-URL. Gebruik geen door het token opgegeven sleutel-URL. Cache de sleutels met begrensde geldigheid en ververs eenmaal bij onbekende `kid`.
3. Handtekening én vast toegestane algoritmen controleren; vertrouw `alg` uit de header niet als configuratie.
4. `iss`, `aud`, `exp`, `iat` en `sub` verplichten en controleren; `nbf` controleren indien aanwezig. Eis een niet-lege string als `sub`. Sta hooguit een kleine, expliciete klokmarge toe.
5. Met de geverifieerde subject-ID een bestaande, actieve applicatiegebruiker vinden. Geen terugval naar gebruiker 1.

Kleine illustratie van de cryptografische controle, binnen een aparte validator met exception handling:

```python
key = jwks_client.get_signing_key_from_jwt(token).key
claims = jwt.decode(
    token, key, algorithms=["EdDSA"],
    issuer=EXPECTED_ISSUER, audience="aegiskey-api",
    options={"require": ["iss", "aud", "exp", "iat", "sub"]},
)
```

Dit fragment vervangt de overige stappen niet. Maak één herbruikbare JWKS-client met timeout en cache. `PyJWKClient` doet blokkerende netwerk-I/O; gebruik hem in een synchrone dependency of verplaats die I/O naar een thread als de dependency async is. FastAPI heeft alleen publieke sleutels nodig, geen Better Auth-secret of private signing key. Zie [PyJWT-verificatie](https://pyjwt.readthedocs.io/en/stable/usage.html).

Ongeldig/verlopen token: **401**, met `WWW-Authenticate: Bearer`. Geldige identiteit maar geblokkeerde gebruiker: **403**. Niet-bestaande lokale mapping: **403**, geen stilzwijgende accountkoppeling. Een onbereikbare JWKS-service wanneer geen bruikbare sleutel gecachet is: gecontroleerd **503**; geef nooit toegang op basis van alleen gedecodeerde claims. Log geen tokens.

## 6. Wat Depends precies doet

De dependencyketen is: header lezen → JWT verifiëren → lokale gebruiker ophalen → route uitvoeren. `Depends` laat FastAPI die functies aanroepen en hun returnwaarde doorgeven. Het kent zelf geen gebruikers en valideert zelf geen JWT. Een exception in de keten stopt de request voordat de route de kluis benadert. Zie [current user](https://fastapi.tiangolo.com/tutorial/security/get-current-user/) en [HTTPBearer](https://fastapi.tiangolo.com/reference/security/#fastapi.security.HTTPBearer).

Pseudocode voor jouw dependency:

```python
def get_current_user(credentials=Depends(bearer_scheme)):
    token = require_bearer(credentials)       # anders 401
    claims = validate_access_token(token)     # echte verificatie
    return require_active_app_user(claims["sub"])
```

De helpers hierboven zijn te bouwen functies, geen bestaande FastAPI-functies. Voeg in de echte implementatie je types en database-dependency toe.

De route krijgt vervolgens een vertrouwd gebruikersobject:

```python
def get_item(cred_id: int, user=Depends(get_current_user)):
    return find_owned_credential(cred_id, user.id)
```

`find_owned_credential` is pseudocode voor je bestaande opslaglaag plus correcte 404- en response-afhandeling. De essentiële query is:

```sql
SELECT ... FROM vault_storage WHERE cred_id = ? AND userid = ?;
```

De eerste waarde komt uit het pad; de tweede uitsluitend uit de dependency. Geef bij een ontbrekend of andermans item dezelfde **404**, zodat de API het bestaan van andermans item niet bevestigt. Pas dit ook toe op list, search, update, delete en reveal.

Behoud voorlopig de interne integer-ID. Voeg aan de applicatiegebruiker een unieke `better_auth_user_id` toe; zo map je de externe string-ID naar de bestaande `UserID`. Maak de mapping via een gecontroleerd provisioningsproces. Koppel bestaande kluizen niet automatisch op alleen een overeenkomend e-mailadres. Een geverifieerde login bewijst niet dat de client eigenaar is van een opgegeven lokale `userid`.

## 7. Uitloggen en intrekken

Bij logout: Better Auth `signOut`, JWT uit browsergeheugen verwijderen, eventueel geopende kluis vergrendelen. Een reeds gekopieerd JWT blijft bij uitsluitend lokale verificatie geldig tot `exp`, in dit ontwerp maximaal ongeveer vijf minuten plus klokmarge. Logout is dus geen onmiddellijke JWT-intrekking. Test dit gedrag expliciet.

Dit is een bewuste beperking voor de eerste integratie met testdata. Als onmiddellijke intrekking vereist is vóór gebruik met echte kluisgegevens, voeg een servercontrole op sessie-intrekking toe: een door Better Auth ondertekende sessie-ID in het JWT en een intern endpoint dat de bijbehorende sessie actief/ongeëxpireerd verklaart en aan `sub` koppelt. FastAPI moet die controle voor toegang afdwingen; een storing geeft geen toegang. Een willekeurige `sid`-claim toevoegen trekt op zichzelf niets in. Een alternatief is sessievalidatie via een auth-bridge bij ieder verzoek, zonder zelfstandige JWT-toegang. Dit is een afzonderlijk ontwerpbesluit en extra implementatiewerk.

## 8. Authenticatie ontgrendelt de kluis niet

Het huidige [securitymodel](https://github.com/Timeless101/AegisKey/blob/64759b1c5a93ebdea7ebc832b2428a40a499d7c3/docs/SECURITY_MODEL.md) leidt de Fernet-sleutel af van het masterwachtwoord. Better Auth geeft na login geen herbruikbaar masterwachtwoord of kluissleutel terug. Een JWT mag nooit als encryptiesleutel worden gebruikt.

Voor de eerste mijlpaal: bouw login, `/me` en eigendomscontrole op testdata. Laat credentials-responses het wachtwoordveld volledig weglaten, ook de ciphertext. Bouw geen reveal-/ontsleutelingendpoint totdat sleutelbeheer is ontworpen.

Voorgestelde vervolgrichting: een afzonderlijk kluis-masterwachtwoord en expliciete unlock/lock-flow. Leg vóór implementatie vast waar de decryptie plaatsvindt, hoe sleutels tijdelijk worden bewaard, hoe bestaande kluizen migreren en wat account-password-reset betekent voor herstel. Een browserimplementatie moet compatibel zijn met de bestaande Argon2id-/Fernet-indeling of bewust migreren; gebruik niet zomaar een andere cipher. Een reset van het accountwachtwoord herstelt niet automatisch toegang tot oude versleutelde data.

## 9. Minimale endpoints

Onderstaande Better Auth-paden worden door de handler aangeboden; schrijf hun implementatie niet opnieuw in Python.

| Eigenaar | Methode en pad | Doel |
|---|---|---|
| Better Auth | `POST /api/auth/sign-up/email` | Testaccount registreren; beleid voor publieke registratie apart kiezen |
| Better Auth | `POST /api/auth/sign-in/email` | Login en sessiecookie |
| Better Auth | `GET /api/auth/get-session` | UI-sessiestatus; geen vervanging voor API-autorisatie |
| Better Auth JWT-plugin | `GET /api/auth/token` | Vanuit geldige sessie een JWT verkrijgen |
| Better Auth JWT-plugin | `GET /api/auth/jwks` | Publieke sleutels voor FastAPI |
| Better Auth | `POST /api/auth/sign-out` | Sessie beëindigen |
| FastAPI | `GET /me` | Beveiligde smoke test; alleen interne ID en noodzakelijke profieldata |
| FastAPI | `GET /credentials/{cred_id}` | Bestaande detailroute beveiligen; metadata zonder password |

Daarna: `GET /credentials`, `POST /credentials`, `PATCH /credentials/{cred_id}`, `DELETE /credentials/{cred_id}`. Voor aanmaken wordt eigenaar server-side ingevuld; schrijf-/leesroutes blijven op die eigenaar filteren. Aanmaken/wijzigen van wachtwoorddata wacht op het sleutelbeheerbesluit. Verwijder de oude `/login`-testroute na de overstap. Een extra Python `/token` of `/refresh` is voor dit ontwerp niet nodig.

## 10. Minimale acceptatietests

Gebruik alleen tijdelijke accounts en een geïsoleerde testdatabase.

| Test | Verwacht resultaat |
|---|---|
| Juiste/verkeerde login | Geldige sessie / gecontroleerde fout zonder wachtwoord in logs |
| Token ophalen zonder sessie | Geen bruikbaar JWT |
| Werkelijk Better Auth-JWT naar `/me` | 200 met de juiste gemapte applicatiegebruiker |
| Geen header, leeg token, verkeerde scheme, willekeurige tekst | 401 met Bearer-challenge |
| Payload/handtekening gewijzigd, `alg=none`, ander algoritme | 401 |
| Verlopen JWT, verkeerde issuer/audience, ontbrekende vereiste claim, lege `sub` | 401 |
| Onbekende mapping / inactieve gebruiker | 403; geen fallback |
| Gebruiker A leest eigen item | 200 zonder passwordveld |
| A vraagt item van B of niet-bestaand item | Beide 404 |
| Client levert `userid` van B mee | Geen toegang of eigendomsoverdracht |
| JWKS-keyrotatie | Nieuwe vertrouwde sleutel werkt na verversen; onbekende sleutel blijft geweigerd |
| JWKS uitgevallen zonder bruikbare cache | 503; geen onbeveiligde fallback |
| JWT verlopen, sessie geldig / verlopen | Nieuw JWT werkt / opnieuw inloggen |
| Logout met eerder gekopieerd JWT | Restgeldigheid aantonen; na `exp` 401 |
| Browserherladen, logout en CORS-preflight | Cookie-/tokenflow werkt vanaf toegestane origin; andere origin wordt niet toegestaan |

Twee kleine testideeën:

```python
assert client.get("/me").status_code == 401
assert client.get("/credentials/42", headers=as_user_a).status_code == 404
```

In het tweede geval behoort item 42 aantoonbaar aan testgebruiker B. Gebruik voor JWT-validator-tests echte ondertekende tokens met tijdelijke testsleutels; verander systematisch claims en handtekeningen. Override `get_current_user` alleen in geïsoleerde route-/ownershiptests. Zo'n override bewijst niet dat JWT-validatie werkt. Houd minstens één integratietest met een echt door Better Auth uitgegeven token en de echte dependencyketen.

## 11. Bouwvolgorde

1. Better Auth-server, database-schema, client en cookie-login opzetten; gevoelige debug-output verwijderen.
2. JWT-plugin configureren en één uitgegeven JWT controleren op issuer, audience en subject; sleutelmateriaal niet loggen.
3. Validator, mapping en `get_current_user` bouwen; `/me` groen krijgen.
4. `userid=1` vervangen door de dependency en A/B-eigendomstests uitvoeren.
5. Refresh-/logoutgedrag, JWKS-rotatie en browserinstellingen testen.
6. Kluis-unlock, sleutelbeheer, migratie en eventuele onmiddellijke intrekking afzonderlijk uitwerken voordat echte geheimen worden ontsleuteld.

Beoordelingscriterium voor de eerste mijlpaal: gebruiker A kan aantoonbaar alleen zijn eigen metadata opvragen met een geldig, door Better Auth uitgegeven en door FastAPI geverifieerd token. Er is geen Python-wachtwoordlogin meer nodig.
