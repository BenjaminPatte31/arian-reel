# Playbook — Instagram automatique @arianstudioo

Ce fichier est la mémoire de l'automatisation. Chaque passage hebdomadaire le lit en premier.

## Identité
- Arian Studio, agence web (siège à Cazères), clients partout en France : TPE, PME et artisans. Le BTP est le premier secteur, pas une spécialisation.
- Angle (refonte du site, 27/11/2026) : on ne vend pas un site, on vend des clients. Un site rapide qui fait appeler, trouvé sur Google, suivi chaque mois. **Aucun prix** dans les Reels ni les légendes ; à la place « prix fixe annoncé avant de commencer ». Offre d'entrée : **audit gratuit de votre site et de votre fiche Google, rendu sous 48 h**.
- Charte : encre #101418, crème #F2EFE8, citron #D4FF3F. Titres Bricolage Grotesque, texte Manrope, logo Montserrat (« ARIAN *STUDIO* », STUDIO en italique).
- **DA « planche » (depuis le 28/11/2026, alignée sur arianstudio.fr)** : thèmes `plan` (fond crème) et `plan-ink` (fond encre), à alterner. Grille de plan, cadre et repères de coupe, étiquette « Planche 0X · Sujet » en haut à droite (`"planche"`), cartouche en bas (`"num"` = n° du Reel), cotes sous les titres (`"cote"`: texte, ou `false`), mot clé en italique surligné citron avec `*mot*`, avant/après en croquis au trait. Les anciens thèmes `ink` / `paper` ne servent plus.
- Contact : arianstudio31@gmail.com · arianstudio.fr
- Hashtags : niveau large (#siteweb #creationsiteweb #agenceweb), cible (#tpe #pme #artisan #petiteentreprise), sujet (#referencementlocal #fichegoogle…), et 1 ou 2 locaux au plus (#hautegaronne #toulouse).
- Légendes au vouvoiement. Mot-clé d'appel à l'action : **SITE** (maquette / audit gratuit).
- Preuves réelles uniquement : Horizon Journal (site animé), PA Nuisibles (site vitrine), le site Arian Studio. Ne jamais inventer de client, de chiffre ni de témoignage. Une maquette n'est jamais présentée comme un client livré.

## Outils
- Metricool : marque `blogId 7888196` (Instagram arianstudioo), fuseau Europe/Paris. Plafond offre gratuite : **20 posts / mois**.
- Hébergement des vidéos : ce dépôt. URL publique d'une vidéo :
  `https://raw.githubusercontent.com/BenjaminPatte31/arian-reel/main/reels/<fichier>.mp4` (Metricool la récupère et la copie chez lui).
- Rendu : `cd engine && npm install` puis `python3 engine/render.py engine/specs/<id>.json` → `reels/<id>.mp4` + `reels/<id>-check.jpg`.
  Le rendu ajoute automatiquement une bande-son originale (engine/audio.py : beat 112 BPM, whoosh à chaque changement de carte, ~-14 LUFS). Libre de droits, rien à faire. Option : `"music_seed": n` dans la spec pour changer la grille d'accords.
  Types de cartes : `hook`, `lines` (liste ou `num`), `big`, `beforeafter`, `demo` (vidéo dans un faux navigateur : `video`, `url`, `start`), `cta`.

## Rythme
- 3 Reels / semaine : mardi 18 h, jeudi 18 h, samedi 10 h (pics Metricool : 10 h et 18 h).
- Mix sur le mois : 40 % démos / avant-après, 30 % conseils artisans, 20 % coulisses, 10 % offre.
- Reels de 8 à 15 s, hook dès la 1re seconde, sous-titres incrustés, une idée par Reel.

## Routine hebdomadaire (lundi)
1. Lire `plan.json` et `getScheduledPosts` : ce qui est déjà programmé, combien de posts ce mois-ci.
2. Lire les stats Metricool des Reels publiés (vues, enregistrements, partages, commentaires). Noter dans `journal.md` ce qui a marché.
3. Remplir les créneaux vides des 7 à 10 jours suivants (sans dépasser 20 posts sur le mois civil).
4. Pour chaque Reel : spec JSON dans `engine/specs/`, rendu, **contrôle visuel du `-check.jpg` et d'une image au milieu** (texte lisible, rien de coupé, aucune faute).
5. Commit + push, puis `createScheduledPost` (REEL, autoPublish true, isAiGenerated false, videoCoverMilliseconds 1200).
6. Mettre à jour `plan.json` (statut `programme` + id Metricool) et `journal.md`, commit + push.
7. Envoyer à Benjamin un récap court : les Reels de la semaine (hook + date) et le lien du planificateur Metricool, pour qu'il puisse en retirer un avant publication.

## Historique
- 28/11/2026 : nouvelle DA « planche » (thèmes plan / plan-ink) alignée sur la refonte d'arianstudio.fr ; Reels 11 et 12 refaits.
- 22/11/2026 : ajout de la bande-son automatique ; Reels 07 et 08 refaits avec son.
- 10/11/2026 : lancement. 7 Reels programmés du 10/11 au 24/11.
- 16/11/2026 : Reel 08 (fiche Google) programmé le 26/11. 8 posts en novembre.
