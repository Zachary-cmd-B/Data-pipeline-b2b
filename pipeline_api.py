import httpx
from pydantic import BaseModel, Field, ValidationError

# 1. Modèle de validation pour un utilisateur / client B2B récupéré en ligne
class UtilisateurClient(BaseModel):
    id: int
    nom: str = Field(alias="name")
    email: str
    ville: str
    entreprise: str

# 2. Extraction depuis une API publique de test (Extract)
URL_API = "https://jsonplaceholder.typicode.com/users"

print("📡 Récupération des données depuis l'API...")
reponse = httpx.get(URL_API)
donnees_brutes = reponse.json()

print(f"📦 {len(donnees_brutes)} éléments bruts reçus. Validation en cours...\n")

clients_valides = []

# 3. Nettoyage et validation (Transform)
for item in donnees_brutes:
    try:
        # On extrait les champs imbriqués pour les aplatir dans notre format cible
        donnee_aplatie = {
            "id": item["id"],
            "name": item["name"],
            "email": item["email"],
            "ville": item["address"]["city"],
            "entreprise": item["company"]["name"]
        }
        client = UtilisateurClient(**donnee_aplatie)
        clients_valides.append(client)
    except ValidationError as e:
        print(f"⚠️ Donnée invalide détectée (ID {item.get('id')}) : {e}")

# 4. Résultat propre prêt pour la base de données (Load)
print(f"✅ {len(clients_valides)} profils clients parfaitement validés et typés !")
print("Premier client prêt à être inséré en base SQL :")
print(clients_valides[0])