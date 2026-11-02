# Frontend ↔ FastAPI contract

Dit is de **te implementeren** API voor de nieuwe webfrontend; de bestaande `/login/` en `/credentials/{cred_id}` voldoen hier nog niet aan. Je Python-services mogen hun huidige namen behouden. Gebruik een router/service-adapter voor de JSON-vormen hieronder.

## Basis

- Publieke prefix standaard `/api`; requests in dit document zijn relatief daaraan.
- JSON (`Content-Type: application/json`), UTF-8; timestamps ISO 8601 met timezone.
- Gebruik opaque string-IDs in responses. Numeric database-IDs mogen naar strings worden geconverteerd. Autorisatie berust nooit op onvoorspelbaarheid van een ID.
- Gebruik een server-side sessie met een `HttpOnly`, `Secure`, passende `SameSite` cookie, bij voorkeur host-only. Gebruik HTTPS, exacte Origin-validatie en CSRF-bescherming op mutaties. Geen wachtwoorden of tokens in URLs.
- `/auth/me` en succesvolle login/MFA geven een sessiegebonden `csrf_token`. Het staat uitsluitend in geheugen; mutaties sturen het in `X-CSRF-Token`. Login, registratie en recovery moeten vóór een sessie al Origin/login-CSRF bescherming en rate limits hebben.
- Sessieresponses, items, reveal en fouten: `Cache-Control: no-store`. Geen secrets in logs. Geen service-worker/offlinecache voor vaultdata.
- `401`: niet ingelogd. Frontend wist de sessieweergave. `403`: geen toegang of CSRF-fout. `423`: ingelogd maar vault vergrendeld. `429`: rate limit. Gebruik veilige foutcodes; frontend toont geen ruwe stacktrace/detailtekst.
- Optionele foutvorm: `{"error":{"code":"VAULT_LOCKED"}}`. Validation blijft ook server-side verplicht. Gebruik `400/422` voor ongeldige velden. Frontend toont daarvoor een algemene foutmelding.

## Authenticatie en ontgrendeling

| Methode | Pad | Request | Response |
| --- | --- | --- | --- |
| GET | `/auth/me` | Cookie | Sessieobject hieronder, of 401 |
| POST | `/auth/login` | `{ "email": "…", "password": "…" }` | Sessieobject, of MFA-challenge |
| POST | `/auth/mfa/verify` | `{ "challenge_id": "…", "code": "123456" }` | Sessieobject; challenge is kort geldig en eenmalig |
| POST | `/auth/register` | `{ "name": "…", "email": "…", "password": "…" }` | 202 of 204; geen automatisch veronderstelde login |
| POST | `/auth/password/reset` | `{ "email": "…", "code": "…", "password": "…" }` | 204; eenmalige code controleren, verlopen codes weigeren, sessies intrekken |
| POST | `/auth/password/reset-request` | `{ "email": "…" }` | Altijd dezelfde 202/204, ongeacht accountbestaan |
| POST | `/auth/logout` | Geen body | 204; sessie werkelijk intrekken, sleutelverwijzingen opruimen |
| POST | `/vault/setup` | `{ "password": "…" }` | `{ "vault_unlocked": true }`; alleen voor een account zonder bestaande vault |
| POST | `/vault/unlock` | `{ "password": "…" }` | `{ "vault_unlocked": true }` |
| POST | `/vault/lock` | Geen body | 204; server-side vaultsleutel opruimen en toegang blokkeren |
| GET | `/auth/account` | Cookie | Redirect naar zelfgehost accountbeheer |

Sessieobject:

```json
{
  "user": {
    "id": "user-123",
    "email": "diego@example.com",
    "name": "Diego",
    "mfa_enabled": true
  },
  "vault_initialized": true,
  "vault_unlocked": false,
  "csrf_token": "random-session-bound-csrf-value"
}
```

MFA-challenge in plaats van een volledige sessie:

```json
{ "mfa_required": true, "challenge_id": "short-lived-opaque-challenge" }
```

`vault_initialized: false` toont een afzonderlijk formulier met nieuw vaultwachtwoord en bevestiging. `/vault/setup` moet atomair controleren dat nog geen vault bestaat; nooit een bestaande vault overschrijven. Na setup gaat de frontend alleen verder bij `vault_unlocked: true`. Een nieuw account moet een bewuste recovery-/sleutelopslagstrategie krijgen.

Voor de lokale accountrecovery stuurt de server een kort geldige, willekeurige recoverycode per email. De gebruiker voert die in het resetformulier in; frontend stuurt code/email/nieuw accountwachtwoord naar `/auth/password/reset`. Codes zijn eenmalig, server-side gehasht opgeslagen en streng geratelimit. Een reset verandert nooit stilzwijgend de vaultsleutel of het vaultwachtwoord. Keycloak verzorgt dit geheel in redirect-modus.

`vault_unlocked: true` mag alleen na daadwerkelijk ontgrendelen. Een OIDC-login is op zichzelf niet voldoende om een vaultsleutel te krijgen. De frontend toont anders het afzonderlijke ontgrendelformulier.

### Keycloak / OIDC via een backend-for-frontend

Stel `loginMode: 'redirect'` in. In die modus zijn er geen lokale email/password-login- of registratie-POSTs:

1. Browser gaat naar `GET /api/auth/login?return_to=<frontend-url>` (of `/auth/register`).
2. Backend start Authorization Code + PKCE bij Keycloak, met state/nonce, strikte redirect-URIs en veilige tijdelijke loginstate.
3. Backend handelt callback en tokenvalidatie af; refresh/access tokens blijven server-side.
4. Backend maakt zijn eigen HttpOnly-sessiecookie en redirect naar de frontend.
5. Frontend vraagt `/auth/me`, ontvangt user/CSRF en toont zonodig de vault-unlockpagina.

Valideer `return_to` tegen een vaste allowlist; nooit een open redirect. Gebruik een bestaande OIDC-clientlibrary voor de serverintegratie. MFA, registratie, emailverificatie en recovery worden in deze modus door Keycloak afgehandeld. Dit contract levert de frontendhelft, geen complete OIDC-serverimplementatie.

De bestaande Python-loginroute die inloggegevens print is geen veilige implementatie van dit contract. Sluit hem niet rechtstreeks als productie-authenticatie aan.

## Items

Alle onderstaande routes vereisen zowel een geldige sessie als een ontgrendelde vault. Haal `userid` uit de geverifieerde serversessie. **Vertrouw nooit op een user-ID uit de browser.** Filter iedere read/update/delete/reveal op eigenaar.

### GET `/items`

```json
{
  "items": [
    {
      "id": "cred-42",
      "type": "login",
      "name": "GitHub",
      "username": "diego@example.com",
      "url": "https://github.com",
      "collection": "Personal",
      "favorite": true,
      "created_at": "2026-11-02T10:00:00Z",
      "updated_at": "2026-11-02T10:00:00Z"
    }
  ]
}
```

Geen `password`, encryptiesleutels of ciphertext. Deze frontend zoekt/filtert/pagineert de teruggegeven metadata client-side. Lever dus de volledige metadata-lijst van de ingelogde gebruiker, niet alleen een eerste serverpagina. Voor zeer grote vaults kun je later serverpaginering in de adapter toevoegen.

`type`: `login`, `note` of `identity`. `collection`: `Personal` of `Work`. `brand` is optioneel, alleen een lokale presentatiehint; bekende waarden zijn `github`, `google`, `notion`, `figma`, `stripe`, `aws`, `note`, `identity`. Zonder hint gebruikt de frontend initialen/type-iconen. Geen verzoek naar een externe faviconservice.

### GET `/items/{id}`

Dezelfde metadata plus de toepasselijke detailvelden, zonder `password`:

- Alle types: `notes` (string).
- Identity: `full_name`, `phone`, `address`; `username` is het emailadres.

Notities en identiteitsgegevens zijn ook gevoelige data: passende server-side encryptie en autorisatie zijn nodig. Of en hoe je deze velden opslaat is onderdeel van je backend-securitymodel.

### POST `/items`

Login-request:

```json
{
  "type": "login",
  "name": "GitHub",
  "username": "diego@example.com",
  "password": "example-only-password",
  "url": "https://github.com",
  "notes": "Personal account",
  "collection": "Personal",
  "favorite": false
}
```

Note: `type`, `name`, `notes`, `collection`, `favorite`.

Identity: `type`, `name`, `username`, `full_name`, `phone`, `address`, `notes`, `collection`, `favorite`.

Response 201: het opgeslagen detailobject, met server-ID/timestamps, **zonder password**. Encryptie en sleutels blijven de verantwoordelijkheid van de server voor deze contractversie.

### PATCH `/items/{id}`

Alleen meegegeven velden wijzigen. Bij een lege wachtwoordinvoer laat de frontend het `password`-veld weg: bestaand wachtwoord behouden. Een expliciete favorite-toggle verstuurt alleen `{ "favorite": true }` of `false`.

Response 200: bijgewerkt detailobject, zonder password. Een eigenaar/type mag niet willekeurig gewijzigd worden; whitelist en valideer toegestane velden server-side.

### DELETE `/items/{id}`

Response 204 na definitieve verwijdering. De frontend vraagt eerst om bevestiging. Geen success-response als de delete niet opgeslagen is.

### POST `/items/{id}/reveal`

Geen body. Response:

```json
{ "password": "decrypted-example-only-password" }
```

Alleen voor een loginitem van de actieve eigenaar, na vault-unlock. Vereist CSRF-controle; rate limiting en audit van de actie zonder de inhoud zijn aanbevolen. De frontend roept dit alleen aan bij expliciet tonen/kopiëren. Een ciphertext/bytesveld van de huidige credentialroute is **geen** vervanging voor deze response.

## Mapping op de huidige code

| Bestaand veld | Nieuw frontendveld |
| --- | --- |
| `cred_id` | `id` als string |
| `service` | `name` |
| `username` | `username` |
| `comment` | `notes` bij detail |
| `editeddate` | `updated_at` als ISO timestamp |
| `userid` | Alleen intern; uit de serversessie |
| `password` (Fernet bytes) | Niet in metadata; pas na expliciete decryptie via reveal |

Aanvullende velden/type/collecties/favorites vereisen uitbreiding of een bewuste backendmapping. Verzin geen `created_at` als je die nog niet opslaat; maak het veld aan of stuur `null` tot de migratie klaar is. De UI toont dan Unknown.

## Volgorde om de Python-API aan te sluiten

1. `/auth/me`, login/redirect, logout en CSRF; met fake vaultdata testen.
2. Vault-unlock/lock, server-side sleutelbeheer en idle/max timeouts.
3. `/items` en details; ownershiptests met twee verschillende accounts.
4. Aanmaken/wijzigen/verwijderen; invoervalidatie en database-transacties.
5. Reveal met decryptiefouten, CSRF- en ownershiptests.
6. Registratie, emailverificatie, MFA en recovery/vaultsetup volgens het gekozen securitymodel.

Test 401, 403, 423, 429, onverwachte HTML-responses, netwerkverlies en dat een andere gebruiker nooit een item kan lezen/wijzigen/verwijderen/revealen door een ID te veranderen.
