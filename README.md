# Visualitzacio-de-dades-PAC4

**PAC4 - Visualització de Dades**  

*Universitat Oberta de Catalunya (UOC)*  

**Títol del projecte:** *Music Genres: How Music Genres Move Us*

**Autor:** Albert Vila Vidal

## Objectiu

Aquest projecte explora la relació entre els gèneres musicals i les emocions que transmeten les cançons a partir de dues variables principals: **valence** i **energy**. A partir d’un conjunt de dades de Spotify, es visualitza com ha evolucionat l'estil emocional de la música popular al llarg de les últimes dècades.

## Visualització
La visualització creada està disponible en el següent enllaç:
[Music Genres: How Music Genres Move Us](https://avilavida.github.io/Visualitzacio-de-dades-PAC4/)

## Dataset

El dataset s’ha obtingut de [Spotify Tracks Dataset (Kaggle)](https://www.kaggle.com/datasets/maharshipandya/-spotify-tracks-dataset/data) i ha estat processat per:

- Eliminar valors nuls, duplicats i outliers
- Completar l’any de publicació utilitzant les APIs [WebA API(Spotify)](https://developer.spotify.com/documentation/web-api), [Discogs API](https://www.discogs.com/developers?srsltid=AfmBOoodJFeuHn21VEnMab1vmAzmuW9gzq9WHCKjVo3EXz0nsisQ9Fz-) i [MusicBrainz API](https://musicbrainz.org/doc/MusicBrainz_API)
- Seleccionar una mostra representativa de 10.000 cançons per limitar la càrrega de dades
- Assignar cada cançó a un gènere musical principal

## Metodologia

- Aplicació de **K-Means** per identificar agrupacions de cançons segons els valors de `valence` i `energy` en clusters de gèneres
- Agrupació de gèneres musicals similars per facilitar la representació visual
- Divisió del pla valence-energy en quatre quadrants emocionals
- Interpolació de dades entre dècades per una animació fluida

## Visualització

La visualització ha estat creada amb **HTML**, **CSS** i **JavaScript** i inclou:

- Un **mapa KDE** amb totes les cançons, on cada punt té el color del gènere amb més densitat en aquell espai
- **Capes individuals per gènere**, amb opció de superposar-les mitjançant controls d’opacitat
- **Línies de referència** en valors de 0.5 (valence i energy) per dividir el gràfic en zones emocionals
- **Animació per dècades**, amb interpolació entre períodes (1980, 1990, 2000, 2010, 2020)
- **Controls d’interacció**: play/pause, pas següent/precedent, selecció de gènere i control d’opacitat
- **Caixa d'informació**: al fer click en una zona del gràfic per obtenir informació d'aquell gènere.
- **Informació contextual** en fer clic a una zona concreta: número de cançons, valors mitjans, etc.

## Com interpretar els eixos

- **Valence**: indica el grau de felicitat o tristor d’una cançó. Valors alts corresponen a cançons alegres i optimistes; valors baixos, a cançons tristes o melancòliques.
- **Energy**: mesura la intensitat i activitat de la cançó. Valors alts indiquen cançons ràpides, fortes i dinàmiques; valors baixos, cançons lentes i calmades.
