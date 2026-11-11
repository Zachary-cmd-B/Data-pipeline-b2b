import httpx
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

# --- 1. COUCHE BASE DE DONNÉES (SQLAlchemy) ---
# En production, on remplacerait "sqlite:///entreprises.db" par l'adresse d'un serveur PostgreSQL
engine = create_engine("sqlite:///entreprises.db", echo=False)
Base = declarative_base()

class ClientTable(Base):
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True)
    nom = Column(String, nullable=False)
    email = Column(String, nullable=False)
    ville = Column(String, nullable=False)
    entreprise = Column(String, nullable=False)

# On génère la table dans la base locale si elle n'existe pas
Base.metadata.create_all(engine)
SessionLocale = sessionmaker(bind=engine)

# --- 2. COUCHE VALIDATION (Pydantic) ---
class UtilisateurClient(BaseModel):
    id: int
    nom: str = Field(alias="name")
    email: str
    ville: str
    entreprise: str

# --- 3. PIPELINE : EXTRACT -> TRANSFORM -> LOAD ---

print("1. [EXTRACT] Appel de l'API externe...")
reponse = httpx.get("https://jsonplaceholder.typicode.com/users")
donnees_brutes = reponse.json()

print(f"2. [TRANSFORM] Validation de {len(donnees_brutes)} enregistrements...")
clients_a_sauvegarder = []

for item in donnees_brutes:
    # Validation stricte avec Pydantic
    client_valide = UtilisateurClient(
        id=item["id"],
        name=item["name"],
        email=item["email"],
        ville=item["address"]["city"],
        entreprise=item["company"]["name"]
    )
    
    # Préparation de l'objet pour la base SQL
    ligne_db = ClientTable(
        id=client_valide.id,
        nom=client_valide.nom,
        email=client_valide.email,
        ville=client_valide.ville,
        entreprise=client_valide.entreprise
    )
    clients_a_sauvegarder.append(ligne_db)

print("3. [LOAD] Insertion en base de données SQL...")
with SessionLocale() as session:
    # On vide la table pour le test puis on insère tout en un seul lot (batch)
    session.query(ClientTable).delete()
    session.add_all(clients_a_sauvegarder)
    session.commit()

print(f" Insertion de {len(clients_a_sauvegarder)} clients terminée avec succès !")

# --- 4. VÉRIFICATION IMMÉDIATE DU RÉSULTAT EN BASE ---
with SessionLocale() as session:
    premier_client = session.query(ClientTable).first()
    total = session.query(ClientTable).count()
    print(f"\n📊 Vérification en base SQL : {total} entrées trouvées.")
    print(f"Exemple en base -> ID: {premier_client.id} | Nom: {premier_client.nom} | Société: {premier_client.entreprise}")