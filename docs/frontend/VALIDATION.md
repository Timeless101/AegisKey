# Frontendvalidatie — 2 november 2026

## Geautomatiseerd

`node --test src/client/tests/frontend.test.js`: **8 tests geslaagd**.

- Willekeurige generatie: lengte, iedere geselecteerde tekengroep, uitsluiting vergelijkbare tekens.
- Geen opties weigeren; numbers-only selectie.
- HTML-escaping en weigering van javascript/data/file-URLs.
- Demo-CRUD, geïsoleerde instanties, geen password in list/detailmetadata, behoud van password bij een metadata-edit.
- Cookie/CSRF-verzending, geen Authorization-header/clienttokenopslag.
- Onverwachte HTML weigeren; serverdetails niet aan gebruiker blootstellen.
- 401 alleen bij een bestaande beschermde request naar sessieverloop-handler.
- Requesttimeout.

## Browsercontroles

Uitgevoerd met echte Chromium-rendering via de lokale preview:

- Loginpagina rendert; ontbrekende backend houdt gebruiker buiten de echte vault. Demo start alleen via expliciete demokeuze/route.
- Demo-item toegevoegd met gegenereerd password; teller en paginering veranderen van 8 naar 9 items.
- Zoekterm beperkt lijst tot het juiste item.
- Detaildrawer, expliciet reveal, edit zonder bestaand password vooraf in het formulier te laden.
- Naam gewijzigd, opgeslagen en in de lijst zichtbaar.
- Verwijderbevestiging en verwijdering van een fictief demo-item; de gefilterde lijst toont daarna de no-results status.
- Handmatig lock/unlock van de demo werkt en haalt de items opnieuw op.
- Generatorpagina toont een lokaal gegenereerd wachtwoord.
- Instellingen: wisselen naar dark mode via de Appearance-select werkt.
- Responsive weergave gecontroleerd in echte iframe-viewports op 390 × 844 en 768 × 844; op mobiel is scrollWidth gelijk aan clientWidth.
- Mobiel menu opent, achtergrond wordt inert, navigatie sluit het menu. Gesloten offscreen-menu is niet tabbable.
- Mobiel secure-noteformulier gecontroleerd: velden en knoppen passen binnen het scherm.

## Grenzen

Er draait nog geen implementatie van het nieuwe API-contract. Echte accountregistratie, MFA, emailrecovery, vaultsetup, cookies, Keycloak/OIDC, encryptie, server-side sleutelbeheer en ownership moeten integraal getest worden zodra die backend er is. De frontend vervangt die onderdelen niet.

Dit is geen penetratietest of cryptografische audit. De responsive controles zijn Chromium-viewports, geen fysieke iPhone-/Android-tests. Clipboardrechten verschillen per browser/HTTPS-context; fouten worden getoond. Geautomatiseerde tests en browserchecks van de demo zijn geen bewijs van veilige serverautorisatie.


## Aanvulling — 3 november 2026: bestaande credential-API

Alle **11 Node-tests slagen** (`node --test src/client/tests/*.test.js`). De drie aanvullende tests controleren:

- Veldmapping zonder ciphertext/user-ID/extra servervelden; geen verzonnen creation timestamp; ontbrekende datums tonen Unknown.
- Een echte HTTP-testserver met dezelfde JSON-vorm als de bestaande Python-route: GET `/credentials/3`, lijst en detail, zonder auth-/cookie-/CSRF-headers. Een niet-geconfigureerd ID wordt niet opgevraagd; ontbrekend item geeft 404, geen nepdata.
- Alleen-lezen adapter: create/update/delete/reveal doen geen HTTP-mutaties. Network-, JSON- en timeoutfouten worden afgehandeld.

Browsercheck met een **fictieve HTTP-fixture**, niet met de database van de gebruiker: item 3 verschijnt in de lijst, details tonen service/username/comment en een melding dat het password versleuteld is. Er zijn geen edit/delete/favorite/reveal-knoppen. Kopieerknop heet Copy username. Leave test keert terug naar de loginpagina, waar Open local test API en Explore demo apart staan.

De persoonlijke lokaal draaiende FastAPI-server van de gebruiker is vanuit de bouwomgeving niet bereikbaar. De actuele route en het model zijn vanaf GitHub gelezen en de aansluiting is tegen die responsevorm getest. De laatste controle op de eigen database gebeurt lokaal met de gedocumenteerde startcommando's. Python en CORS-code zijn niet gewijzigd.
