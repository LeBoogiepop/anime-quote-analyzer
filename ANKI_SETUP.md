# Guide d'installation AnkiConnect

Pour utiliser la fonctionnalité d'export vers Anki, vous devez installer l'addon AnkiConnect dans Anki.

## Étapes d'installation

### 1. Installer AnkiConnect

1. Ouvrez Anki
2. Allez dans **Outils** → **Modules complémentaires** (Tools → Add-ons)
3. Cliquez sur **Obtenir des modules complémentaires...** (Get Add-ons...)
4. Entrez le code : **2055492159**
5. Cliquez sur **OK** et attendez l'installation
6. Redémarrez Anki

### 2. Vérifier l'installation

AnkiConnect démarre automatiquement quand Anki est ouvert. Il écoute sur `http://localhost:8765`.

Pour vérifier que tout fonctionne :
- Ouvrez Anki
- L'addon devrait être actif automatiquement (pas besoin de configuration supplémentaire)

### 3. Utiliser l'export

1. Assurez-vous qu'Anki est **ouvert** avant d'exporter
2. Cliquez sur le bouton **"Exporter vers Anki"** sur une carte de phrase
3. La carte sera automatiquement ajoutée au deck **"Japanese::Anime Quotes"**
4. Si le deck n'existe pas, il sera créé automatiquement

## Format des cartes

Les cartes créées utilisent le modèle **"Japanese Sentence"** avec les champs suivants :

- **Japanese** : La phrase japonaise originale
- **Reading** : Lecture avec furigana (ex: 私[わたし])
- **Translation** : Traduction (vide par défaut, à remplir manuellement)
- **Grammar** : Structures grammaticales détectées
- **Vocabulary** : Vocabulaire extrait avec traductions
- **JLPT** : Niveau JLPT (N5-N1)
- **Tags** : Tags automatiques (JLPT level, patterns, "anime", "sentence")

## Dépannage

### Erreur : "AnkiConnect is not available"

**Solutions :**
1. Vérifiez qu'Anki est **ouvert** (AnkiConnect ne fonctionne que si Anki est lancé)
2. Vérifiez que l'addon AnkiConnect est installé (Outils → Modules complémentaires)
3. Redémarrez Anki
4. Vérifiez qu'aucun firewall ne bloque `localhost:8765`

### Erreur : "Failed to add note to Anki"

**Solutions :**
1. Vérifiez que le deck "Japanese::Anime Quotes" existe ou peut être créé
2. Vérifiez les permissions d'Anki
3. Redémarrez Anki

### Le modèle de carte n'est pas créé automatiquement

Si le modèle "Japanese Sentence" n'est pas créé automatiquement, vous pouvez le créer manuellement :

1. Dans Anki : **Outils** → **Gérer les types de notes** (Tools → Manage Note Types)
2. Cliquez sur **Ajouter** (Add)
3. Nommez-le "Japanese Sentence"
4. Ajoutez les champs : Japanese, Reading, Translation, Grammar, Vocabulary, JLPT, Tags
5. Configurez le modèle de carte selon vos préférences

## Ressources

- [AnkiConnect GitHub](https://github.com/FooSoft/anki-connect)
- [Documentation AnkiConnect](https://foosoft.net/projects/anki-connect/)

