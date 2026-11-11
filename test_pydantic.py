from pydantic import BaseModel, Field, ValidationError

# 1. On définit le moule strict pour un colis / chargement de fret
class Expedition(BaseModel):
    id_expedition: str
    agence_depart: str
    poids_kg: float = Field(gt=0, description="Le poids doit être strictement supérieur à 0")
    prix_ht: float = Field(ge=0, description="Le prix ne peut pas être négatif")
    est_livre: bool = False

# 2. Cas réel : une donnée "sale" reçue depuis un fichier ou une API externe
donnee_recue = {
    "id_expedition": "FR-PAR-9821",
    "agence_depart": "Agence Nord",
    "poids_kg": "45.5",   # Arrive en texte, Pydantic va le convertir en float automatiquement
    "prix_ht": 120.0,
    "est_livre": "false"  # Texte converti en booléen Python False
}

try:
    expedition_validee = Expedition(**donnee_recue)
    print("Donnée validée et propre :")
    print(expedition_validee)
    print(f"Poids typé : {type(expedition_validee.poids_kg)}")  # C'est devenu un vrai float
except ValidationError as e:
    print("Erreur de données :", e)