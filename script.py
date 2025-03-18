import csv
import os
import subprocess
import datetime
import re
import sys
import requests
import json

# URL del script en Vercel
VERCEL_SCRIPT_URL = "https://scriptu7dzapi.vercel.app/script.py"

# ========== SISTEMA DE ACTUALIZACIÓN ==========
def descargar_script_actualizado():
    """Descarga la última versión del script y compara con la local"""
    try:
        # Descargar script remoto
        response = requests.get(VERCEL_SCRIPT_URL, timeout=10)
        response.raise_for_status()
        contenido_remoto = response.text
        
        # Leer script local
        with open(__file__, "r", encoding="utf-8") as f:
            contenido_local = f.read()
        
        # Comparar contenidos
        if contenido_remoto.strip() == contenido_local.strip():
            print("\n[INFO] Estás usando la última versión")
            return None
            
        # Guardar actualización si hay diferencias
        with open("script_actualizado.py", "w", encoding="utf-8") as file:
            file.write(contenido_remoto)
        
        print("\n[ACTUALIZACIÓN] Nueva versión detectada!")
        return "script_actualizado.py"
        
    except Exception as e:
        print(f"\n[ERROR] Fallo al verificar actualizaciones: {str(e)}")
        return None

def actualizar_script():
    """Reemplaza el script actual si hay una nueva versión"""
    script_actualizado = descargar_script_actualizado()
    if script_actualizado:
        try:
            os.replace(script_actualizado, __file__)
            print("[ACTUALIZACIÓN] ¡Actualización aplicada con éxito!")
            print("[ACTUALIZACIÓN] Por favor vuelva a ejecutar el script para actualizar")
            sys.exit(0)
        except Exception as e:
            print(f"[ERROR] Fallo al aplicar actualización: {str(e)}")

# Verificar actualizaciones al inicio
actualizar_script()

# ========== FUNCIONES ORIGINALES DEL SCRIPT ==========
def cargar_datos_csv(archivo_csv):
    """Carga los datos del archivo CSV con los canales y claves"""
    canales = []
    links = {}
    keys = {}
    
    try:
        with open(archivo_csv, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            next(reader)  # Saltar cabecera
            for row in reader:
                if len(row) >= 3:
                    nombre = row[0]
                    link = row[1]
                    key = row[2]
                    
                    if nombre and link:  # Asegurarse de que hay datos válidos
                        canales.append(nombre)
                        links[nombre] = link
                        keys[nombre] = key
        
        return canales, links, keys
    except Exception as e:
        print(f"Error cargando el archivo CSV: {str(e)}")
        sys.exit(1)

def obtener_user_agent():
    """Devuelve un User-Agent predeterminado"""
    return "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"

def es_horario_verano(fecha):
    """Determina si una fecha está en horario de verano en España"""
    año = fecha.year
    
    # Calcular inicio del horario de verano (último domingo de marzo)
    inicio_verano = datetime.datetime(año, 3, 31)
    while inicio_verano.weekday() != 6:  # 6 es domingo
        inicio_verano -= datetime.timedelta(days=1)
    inicio_verano = inicio_verano.replace(hour=2, minute=0, second=0)
    
    # Calcular fin del horario de verano (último domingo de octubre)
    fin_verano = datetime.datetime(año, 10, 31)
    while fin_verano.weekday() != 6:
        fin_verano -= datetime.timedelta(days=1)
    fin_verano = fin_verano.replace(hour=3, minute=0, second=0)
    
    return inicio_verano <= fecha < fin_verano

def formatear_fechas(fecha_inicio, fecha_fin):
    """Formatea las fechas para usarlas en la URL, convirtiendo de hora local a UTC"""
    try:
        inicio_dt = datetime.datetime.strptime(fecha_inicio, "%Y-%m-%dT%H:%M:%S")
        fin_dt = datetime.datetime.strptime(fecha_fin, "%Y-%m-%dT%H:%M:%S")
        
        offset_inicio = 2 if es_horario_verano(inicio_dt) else 1
        offset_fin = 2 if es_horario_verano(fin_dt) else 1
        
        print(f"\n[INFO] Horario detectado:")
        print(f"- Inicio: UTC+{offset_inicio} ({'Verano' if offset_inicio == 2 else 'Invierno'})")
        print(f"- Fin: UTC+{offset_fin} ({'Verano' if offset_fin == 2 else 'Invierno'})")
        
        inicio_utc = inicio_dt - datetime.timedelta(hours=offset_inicio)
        fin_utc = fin_dt - datetime.timedelta(hours=offset_fin)
        
        inicio_utc_str = inicio_utc.strftime("%Y-%m-%dT%H:%M:%S") + "Z"
        fin_utc_str = fin_utc.strftime("%Y-%m-%dT%H:%M:%S") + "Z"
        
        return inicio_utc_str, fin_utc_str
    except Exception as e:
        print(f"Error al formatear fechas: {str(e)}")
        sys.exit(1)

def extraer_key_decryption(key_string):
    """Extrae la clave de decripción del formato key1:key2"""
    if not key_string:
        return None
    
    parts = key_string.split(':')
    return parts[1] if len(parts) == 2 else key_string

# ========== NUEVAS FUNCIONES ==========
def ejecutar_ffprobe(url, key_decryption):
    """Ejecuta ffprobe para obtener información sobre las pistas disponibles"""
    try:
        # Construir comando base
        comando_base = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_streams',
            '-headers', f'Referer: https://ver.zapitv.com',
            '-user_agent', obtener_user_agent()
        ]
        
        # Añadir clave de decriptación si existe
        if key_decryption:
            comando_base.extend(['-cenc_decryption_key', key_decryption])
        
        # Añadir URL
        comando_base.append(url)
        
        print("\n[FFPROBE] Analizando pistas disponibles...")
        result = subprocess.run(comando_base, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"\n[ERROR] FFprobe falló: {result.stderr}")
            return None
        
        return json.loads(result.stdout)
    except Exception as e:
        print(f"\n[ERROR] Error al ejecutar ffprobe: {str(e)}")
        return None

def seleccionar_mejor_pista(streams_data):
    """Selecciona la pista de video de mayor calidad"""
    if not streams_data or 'streams' not in streams_data:
        print("\n[ERROR] No se encontraron pistas de video para analizar")
        return None
    
    video_streams = [s for s in streams_data['streams'] if s.get('codec_type') == 'video']
    if not video_streams:
        print("\n[ERROR] No se encontraron pistas de video")
        return None
    
    # Ordenar por resolución (multiplicar ancho x alto)
    video_streams.sort(key=lambda x: 
        int(x.get('width', 0)) * int(x.get('height', 0)), 
        reverse=True
    )
    
    mejor_pista = video_streams[0]
    print(f"\n[INFO] Mejor pista de video encontrada:")
    print(f"- Índice: {mejor_pista.get('index')}")
    print(f"- Resolución: {mejor_pista.get('width')}x{mejor_pista.get('height')}")
    print(f"- Codec: {mejor_pista.get('codec_name')}")
    print(f"- Bitrate: {int(mejor_pista.get('bit_rate', 0))/1000:.2f} kbps")
    
    return mejor_pista

def mostrar_info_pistas(streams_data):
    """Muestra información sobre todas las pistas disponibles"""
    if not streams_data or 'streams' not in streams_data:
        return
    
    video_streams = [s for s in streams_data['streams'] if s.get('codec_type') == 'video']
    audio_streams = [s for s in streams_data['streams'] if s.get('codec_type') == 'audio']
    subtitle_streams = [s for s in streams_data['streams'] if s.get('codec_type') == 'subtitle']
    
    print("\n[INFO] Pistas disponibles:")
    print(f"- Video: {len(video_streams)} pistas")
    print(f"- Audio: {len(audio_streams)} pistas")
    print(f"- Subtítulos: {len(subtitle_streams)} pistas")
    
    if audio_streams:
        print("\n[INFO] Pistas de audio:")
        for i, audio in enumerate(audio_streams):
            lang = audio.get('tags', {}).get('language', 'desconocido')
            print(f"  {i+1}. Índice: {audio.get('index')}, Idioma: {lang}, Codec: {audio.get('codec_name')}")
    
    if subtitle_streams:
        print("\n[INFO] Pistas de subtítulos:")
        for i, sub in enumerate(subtitle_streams):
            lang = sub.get('tags', {}).get('language', 'desconocido')
            print(f"  {i+1}. Índice: {sub.get('index')}, Idioma: {lang}")

def ejecutar_ffmpeg_mejorado(url, key_decryption, nombre_archivo, streams_data):
    """Ejecuta ffmpeg para descargar y desencriptar el contenido con la mejor pista de video y todas las pistas de audio y subtítulos"""
    try:
        # Mostrar información de todas las pistas
        mostrar_info_pistas(streams_data)
        
        # Obtener la mejor pista de video
        mejor_pista = seleccionar_mejor_pista(streams_data)
        if not mejor_pista:
            return ejecutar_ffmpeg(url, key_decryption, nombre_archivo)  # Usar el método original como fallback
        
        # Construir comando base
        comando_base = [
            'ffmpeg',
            '-headers', f'Referer: https://ver.zapitv.com',
            '-user_agent', obtener_user_agent()
        ]

        # Añadir clave de decriptación si existe
        if key_decryption:
            comando_base.extend(['-cenc_decryption_key', f'"{key_decryption}"'])

        # Añadir URL de entrada
        comando_final = comando_base + ['-i', f'"{url}"', '-c', 'copy']
        
        # Mapear sólo la mejor pista de video
        comando_final.extend(['-map', f'0:{mejor_pista.get("index")}'])
        
        # Mapear TODAS las pistas de audio
        comando_final.extend(['-map', '0:a'])
        
        # Mapear TODAS las pistas de subtítulos (si existen)
        comando_final.extend(['-map', '0:s?'])
        
        # Añadir nombre del archivo
        comando_final.append(f'"{nombre_archivo}"')

        # Crear versión segura para ejecución (sin comillas internas)
        comando_ejecucion = []
        for item in comando_final:
            comando_ejecucion.append(item.replace('"', ''))

        print("\n[FFMPEG] Comando generado:")
        print(' '.join(comando_final))

        # Ejecutar con shell=False para mayor seguridad
        result = subprocess.run(comando_ejecucion, check=True)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] FFmpeg falló con código: {e.returncode}")
        return False
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        return False

def ejecutar_ffmpeg(url, key_decryption, nombre_archivo):
    """Función original de ffmpeg como fallback"""
    try:
        # Construir comando base
        comando_base = [
            'ffmpeg',
            '-headers', f'Referer: https://ver.zapitv.com',
            '-user_agent', obtener_user_agent()
        ]

        # Añadir clave de decriptación si existe
        if key_decryption:
            comando_base.extend(['-cenc_decryption_key', f'"{key_decryption}"'])

        # Añadir parámetros restantes entrecomillados
        comando_final = comando_base + [
            '-i', f'"{url}"',
            '-c', 'copy',
            '-map', '0:v',
            '-map', '0:a',
            '-map', '0:s?',
            f'"{nombre_archivo}"'
        ]

        # Crear versión segura para ejecución (sin comillas internas)
        comando_ejecucion = []
        for item in comando_final:
            comando_ejecucion.append(item.replace('"', ''))

        print("\n[FFMPEG] Comando generado (fallback):")
        print(' '.join(comando_final))

        # Ejecutar con shell=False para mayor seguridad
        result = subprocess.run(comando_ejecucion, check=True)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] FFmpeg falló con código: {e.returncode}")
        return False
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        return False

def verificar_url(url):
    """Verifica si una URL existe antes de intentar descargarla"""
    try:
        response = requests.head(url, headers={
            "User-Agent": obtener_user_agent(),
            "Referer": "https://ver.zapitv.com"
        }, timeout=10)
        return response.status_code < 400
    except Exception:
        return False

def ejecutar_script():
    """Función principal que ejecuta el script"""
    try:
        archivo_csv = "zapi.csv"
        canales, links, keys = cargar_datos_csv(archivo_csv)
        
        print("\n=== CANALES DISPONIBLES ===")
        for i, canal in enumerate(canales, 1):
            print(f"{i}. {canal}")
        
        try:
            seleccion = int(input("\nIngrese el número del canal: ")) - 1
            if not 0 <= seleccion < len(canales):
                print("Selección inválida")
                return
            canal_seleccionado = canales[seleccion]
        except ValueError:
            print("Ingrese un número válido")
            return
        
        enlace = links.get(canal_seleccionado)
        clave = keys.get(canal_seleccionado)
        
        if not enlace:
            print(f"No hay enlace para {canal_seleccionado}")
            return
        
        print("\n=== FECHAS (Hora Local España) ===")
        fecha_inicio = input("Fecha/hora inicio (YYYY-MM-DDTHH:MM:SS): ")
        fecha_fin = input("Fecha/hora fin (YYYY-MM-DDTHH:MM:SS): ")
        
        inicio_utc, fin_utc = formatear_fechas(fecha_inicio, fecha_fin)
        url_final = enlace.replace("{utc}", inicio_utc).replace("{utcend}", fin_utc)
        clave_decripcion = extraer_key_decryption(clave)
        
        nombre_base = f"{canal_seleccionado.replace(' ', '_')}_{datetime.datetime.strptime(fecha_inicio, '%Y-%m-%dT%H:%M:%S').strftime('%Y%m%d_%H%M')}"
        nombre_archivo = input(f"\nNombre del archivo (dejar vacío para '{nombre_base}'): ") or nombre_base
        nombre_archivo += ".ts"
        
        print(f"\n[VERIFICACIÓN] Probando URL...")
        if not verificar_url(url_final):
            print("¡URL no accesible! ¿Continuar? (s/n)")
            if input().lower() != 's':
                return
        
        print("\n=== RESUMEN ===")
        print(f"Canal: {canal_seleccionado}")
        print(f"URL: {url_final}")
        print(f"Archivo: {nombre_archivo}")
        print(f"Clave: {clave_decripcion or 'No requiere'}")
        
        if input("\n¿Iniciar descarga? (s/n): ").lower() != 's':
            print("Descarga cancelada")
            return
        
        print("\n[ANÁLISIS] Obteniendo información de las pistas...")
        streams_data = ejecutar_ffprobe(url_final, clave_decripcion)
        
        print("\n[DESCARGA] Iniciando...")
        if ejecutar_ffmpeg_mejorado(url_final, clave_decripcion, nombre_archivo, streams_data):
            print(f"\n¡Descarga completada! Guardado como: {nombre_archivo}")
        else:
            print("\nError en la descarga")
        
    except Exception as e:
        print(f"Error: {str(e)}")

def main():
    while True:
        ejecutar_script()
        if input("\n¿Descargar otro contenido? (s/n): ").lower() != 's':
            break
    print("\n¡Gracias por usar el script! - Script hecho por Archivos M08g")

if __name__ == "__main__":
    main()
