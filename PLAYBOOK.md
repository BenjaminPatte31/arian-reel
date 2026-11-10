# Playbook — Instagram automatique @arianstudioo

Ce fichier est la mémoire de l'automatisation. Chaque passage hebdomadaire le lit en premier.

## Identité
- Arian Studio, agence web à Cazères (Haute-Garonne) : sites, sécurité, automatisation pour artisans, commerçants, TPE du Comminges et du sud toulousain.
- Angle à marteler : moins cher que les agences à 2 000 € · un site pensé pour faire contacter · visible sur Google (SEO). Site dès 400 €, prix fixe.
- Charte : encre #101418, crème #F2EFE8, citron #D4FF3F. Titres Bricolage Grotesque, texte Manrope, logo Montserrat.
- Contact : arianstudio31@gmail.com · arianstudio.netlify.app
- Légendes au vouvoiement. Mot-clé d'appel à l'action : **SITE** (maquette / audit gratuit).
- Preuves réelles uniquement : Horizon Journal (site animé), PA Nuisibles (site vitrine), le site Arian Studio. Ne jamais inventer de client, de chiffre ni de témoignage. Une maquette n'est jamais présentée comme un client livré.

## Outils
- Metricool : marque `blogId 7888196` (Instagram arianstudioo), fuseau Europe/Paris. Plafond offre gratuite : **20 posts / mois**.
- Hébergement des vidéos : ce dépôt. URL publique d'une vidéo :
  `https://raw.githubusercontent.com/BenjaminPatte31/arian-reel/main/reels/<fichier>.mp4` (Metricool la récupère et la copie chez lui).
- Rendu : `cd engine && npm install` puis `python3 engine/render.py engine/specs/<id>.json` → `reels/<id>.mp4` + `reels/<id>-check.jpg`.
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
- 10/11/2026 : lancement. 7 Reels programmés du 10/11 au 24/11.
