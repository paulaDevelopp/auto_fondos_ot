import os
import requests
import cloudinary
import cloudinary.uploader
import firebase_admin
from firebase_admin import credentials, db
import random
import time
import base64
import json

# 🚀 1. Configurar Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

# 🚀 2. Configurar Firebase
with open('firebase_credentials.json', 'r') as f:
    firebase_creds = json.load(f)

cred = credentials.Certificate(firebase_creds)
firebase_admin.initialize_app(cred, {
    'databaseURL': f"https://{firebase_creds['project_id']}-default-rtdb.firebaseio.com/"
})

# 🚀 3. Función para subir imagen a Cloudinary
def subir_a_cloudinary(path_imagen, nombre_archivo):
    print(f"🟢 Subiendo {nombre_archivo} a Cloudinary...")
    upload_result = cloudinary.uploader.upload(path_imagen, public_id=nombre_archivo, resource_type="image")
    return upload_result['secure_url']

# 🚀 4. Función para crear un nuevo item en Firebase
def crear_item_en_db(url_imagen, nombre_item, required_level):
    ref = db.reference('store_items')

    new_id = ref.push().key

    nuevo_item = {
        'id': new_id,
        'name': nombre_item,
        'price': random.randint(100, 200),
        'imageUrl': url_imagen,
        'requiredLevel': required_level,
    }

    ref.child(new_id).set(nuevo_item)
    print(f"🟣 Nuevo fondo '{nombre_item}' creado para nivel {required_level}.")

# 🚀 5. Función principal
def procesar_fondos():
    carpeta_fondos = 'fondos'
    archivo_control = 'fondos_usados.txt'
    cantidad_a_subir = 2  # 🔥 Número de fondos a subir cada vez

    # Leer imágenes ya usadas
    usados = set()
    if os.path.exists(archivo_control):
        with open(archivo_control, 'r') as f:
            usados = set(f.read().splitlines())

    # Obtener lista de fondos disponibles
    todos_fondos = [f for f in os.listdir(carpeta_fondos) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    disponibles = [f for f in todos_fondos if f not in usados]

    if not disponibles:
        print("❌ No hay más fondos disponibles para subir.")
        return

    # Ordenar para que suban de forma predecible (opcional)
    disponibles.sort()

    # Elegir hasta 'cantidad_a_subir' fondos
    seleccionados = disponibles[:cantidad_a_subir]

    # Cargar progreso de niveles
    nivel_actual = 1
    fondos_subidos_en_este_nivel = 0

    # Leer niveles ya subidos
    if os.path.exists('nivel_actual.txt'):
        with open('nivel_actual.txt', 'r') as f:
            data = f.read().strip().split(',')
            if len(data) == 2:
                nivel_actual = int(data[0])
                fondos_subidos_en_este_nivel = int(data[1])

    for fondo_elegido in seleccionados:
        path_fondo = os.path.join(carpeta_fondos, fondo_elegido)

        # Subir a Cloudinary
        nombre_archivo_cloudinary = f"background_{random.randint(1000,9999)}"
        url_imagen = subir_a_cloudinary(path_fondo, nombre_archivo_cloudinary)

        # Crear item en Firebase
        crear_item_en_db(url_imagen, nombre_item=fondo_elegido.split('.')[0], required_level=nivel_actual)

        # Actualizar usados
        with open(archivo_control, 'a') as f:
            f.write(fondo_elegido + '\n')

        fondos_subidos_en_este_nivel += 1

        # Cada 2 fondos subidos, aumenta el nivel
        if fondos_subidos_en_este_nivel >= 2:
            nivel_actual += 1
            fondos_subidos_en_este_nivel = 0

    # Guardar progreso
    with open('nivel_actual.txt', 'w') as f:
        f.write(f"{nivel_actual},{fondos_subidos_en_este_nivel}")

    print("✅ Fondos procesados correctamente.")

# 🚀 6. Ejecutar
if __name__ == "__main__":
    procesar_fondos()
