import requests
import random
import os

# Paramètres à personnaliser
NAS_URL = "https://noumaios.com"  # Votre domaine (testez si /webapi/entry.cgi est accessible ; sinon, essayez "https://noumaios.com/photo")
USERNAME = "homeassistant"  # Remplacez par votre vrai username Synology
PASSWORD = "LesPhot0sduN@S123"  # Remplacez par votre vrai password
OTP_CODE = ""  # Si 2FA activé, générez un code via votre app (ex. Google Authenticator) et mettez-le ici ; sinon laissez vide
ALBUM_ID = 123  # Remplacez par un ID test ; on le trouvera avec list_albums
SAVE_PATH = "/config/www/photo_actuelle.jpg"  # Chemin dans HA

# Session pour l'auth
session = requests.Session()
# session.verify = False  # Décommentez si erreur SSL (certificat invalide) ; mais insecure !

def login():
    params = {
        "api": "SYNO.API.Auth",
        "version": "7",  # Version 7 pour DSM 7+
        "method": "login",
        "account": USERNAME,
        "passwd": PASSWORD,
        "session": "Foto",
        "format": "sid"
    }
    if OTP_CODE:
        params["otp_code"] = OTP_CODE
    print("Tentative de login avec params :", params)  # Debug
    r = session.get(f"{NAS_URL}/webapi/entry.cgi", params=params)
    print("Status HTTP :", r.status_code)  # Debug
    print("Réponse brute :", r.text)  # Debug complet
    r.raise_for_status()  # Erreur si pas 200
    response = r.json()
    if not response.get('success', False):
        raise ValueError(f"Login échoué : {response.get('error', 'Erreur inconnue')}")
    return response["data"]["sid"]

def list_albums(sid):
    params = {
        "api": "SYNO.Foto.Browse.Album",
        "version": "1",
        "method": "list",
        "offset": 0,
        "limit": 100,
        "_sid": sid
    }
    print("Params pour list_albums :", params)  # Debug
    r = session.get(f"{NAS_URL}/webapi/entry.cgi", params=params)
    print("Status HTTP :", r.status_code)
    print("Réponse brute :", r.text)
    r.raise_for_status()
    response = r.json()
    if not response.get('success', False):
        raise ValueError(f"List albums échoué : {response.get('error', 'Erreur inconnue')}")
    albums = response["data"]["list"]
    for album in albums:
        print(f"Album: {album.get('name', 'Nom inconnu')} - ID: {album.get('id', 'ID inconnu')} - Type: {album.get('type', 'Type inconnu')}")
    return albums

def get_photos(album_id, sid):
    params = {
        "api": "SYNO.Foto.Browse.Item",
        "version": "1",
        "method": "list",
        "album_id": album_id,
        "offset": 0,
        "limit": 500,
        "_sid": sid
    }
    print("Params pour get_photos :", params)
    r = session.get(f"{NAS_URL}/webapi/entry.cgi", params=params)
    print("Status HTTP :", r.status_code)
    print("Réponse brute :", r.text)
    r.raise_for_status()
    response = r.json()
    if not response.get('success', False):
        raise ValueError(f"Get photos échoué : {response.get('error', 'Erreur inconnue')}")
    items = response["data"]["list"]
    return [item["id"] for item in items if item["type"] == "photo"]

def get_image_url(photo_id, sid):
    params = {
        "api": "SYNO.Foto.Thumbnail",
        "version": "1",
        "method": "get",
        "id": photo_id,
        "size": "xl",
        "type": "unit",
        "_sid": sid
    }
    print("Params pour get_image_url :", params)
    r = session.get(f"{NAS_URL}/webapi/entry.cgi", params=params)
    print("Status HTTP :", r.status_code)
    print("Réponse brute :", r.text)
    r.raise_for_status()
    response = r.json()
    if not response.get('success', False):
        raise ValueError(f"Get thumbnail échoué : {response.get('error', 'Erreur inconnue')}")
    cache_key = response["data"]["cache_key"]
    return f"{NAS_URL}/photo/thumbnail/{cache_key}/xl.jpg?api=SYNO.Foto.Thumbnail&method=get&version=1&_sid={sid}"

# Exécution
try:
    sid = login()
    list_albums(sid)  # Exécute ceci pour lister les albums (trouver l'ID)
    
    # Le reste est commenté pour le debug ; décommentez une fois l'ID trouvé
    # photo_ids = get_photos(ALBUM_ID, sid)
    # if not photo_ids:
    #     print("Aucune photo trouvée dans l'album")
    # else:
    #     random_id = random.choice(photo_ids)
    #     image_url = get_image_url(random_id, sid)
    #     r = session.get(image_url)
    #     print("Status HTTP image :", r.status_code)
    #     print("Téléchargement depuis :", image_url)
    #     r.raise_for_status()
    #     with open(SAVE_PATH, "wb") as f:
    #         f.write(r.content)
    #     print(f"Photo aléatoire téléchargée (ID: {random_id})")
except Exception as e:
    print(f"Erreur globale : {str(e)}")