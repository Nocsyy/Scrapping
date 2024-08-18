#Scrapping 

## Prérequis
Assurez-vous d'avoir installé les éléments suivants avant de commencer :

Python 3.7 ou supérieur
pip (le gestionnaire de paquets Python)
Un compte Google pour créer une clé API et un CSE ID

##Installation
Cloner le dépôt

git clone https://github.com/votre-utilisateur/votre-projet.git
cd votre-projet

##Créer un environnement virtuel

python -m venv .venv

##Activer l'environnement virtuel

Sous Windows :

.venv\Scripts\activate

Sous Linux/MacOS :

source .venv/bin/activate

Installer les dépendances:

pip install -r requirements.txt

## Configuration
Créer une clé API et un CSE ID
Pour utiliser les fonctionnalités de ce projet, vous devrez obtenir une clé API et un Custom Search Engine ID (CSE ID) de Google.

Étape 1 : Créer une clé API
Allez sur le Google Cloud Console.
Créez un nouveau projet ou sélectionnez un projet existant.
Naviguez vers API & Services > Identifiants.
Cliquez sur Créer des identifiants > Clé API.
Copiez la clé API générée.
Étape 2 : Créer un Custom Search Engine (CSE)
Allez sur le Custom Search Engine de Google.
Cliquez sur Nouveau moteur de recherche.
Sous "Sites à rechercher", entrez les domaines que vous souhaitez inclure dans les résultats de recherche.
Cliquez sur Créer.
Dans le tableau de bord CSE, cliquez sur Paramètres puis sur ID du moteur de recherche. Copiez cet ID.
Configurer les variables d'environnement
Créez un fichier .env à la racine de votre projet :

.env

Ajoutez les informations suivantes dans le fichier .env :

GOOGLE_API_KEY=votre_clé_api
GOOGLE_CSE_ID=votre_cse_id

##Utilisation

Après avoir configuré le projet, vous pouvez exécuter le script principal :

python main.py

Assurez-vous que l'environnement virtuel est activé avant d'exécuter le script.

