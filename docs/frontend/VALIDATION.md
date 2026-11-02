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
