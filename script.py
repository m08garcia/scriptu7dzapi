import csv
import os
import subprocess
import datetime
import re
import sys
import requests

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
    # En España, el horario de verano comienza el último domingo de marzo
    # y termina el último domingo de octubre
    año = fecha.year
    
    # Calcular inicio del horario de verano (último domingo de marzo)
    inicio_verano = datetime.datetime(año, 3, 31)
    while inicio_verano.weekday() != 6:  # 6 es domingo
        inicio_verano -= datetime.timedelta(days=1)
    inicio_verano = inicio_verano.replace(hour=2, minute=0, second=0)
    
    # Calcular fin del horario de verano (último domingo de octubre)
    fin_verano = datetime.datetime(año, 10, 31)
    while fin_verano.weekday() != 6:  # 6 es domingo
        fin_verano -= datetime.timedelta(days=1)
    fin_verano = fin_verano.replace(hour=3, minute=0, second=0)
    
    return inicio_verano <= fecha < fin_verano

def formatear_fechas(fecha_inicio, fecha_fin):
    """Formatea las fechas para usarlas en la URL, convirtiendo de hora local a UTC"""
    try:
        # Convertir strings a objetos datetime
        inicio_dt = datetime.datetime.strptime(fecha_inicio, "%Y-%m-%dT%H:%M:%S")
        fin_dt = datetime.datetime.strptime(fecha_fin, "%Y-%m-%dT%H:%M:%S")
        
        # Determinar el offset horario
        offset_inicio = 2 if es_horario_verano(inicio_dt) else 1
        offset_fin = 2 if es_horario_verano(fin_dt) else 1
        
        # Mostrar información del horario aplicado
        print(f"\nHorario detectado para fecha inicio: UTC+{offset_inicio} ({'verano' if offset_inicio == 2 else 'invierno'})")
        print(f"Horario detectado para fecha fin: UTC+{offset_fin} ({'verano' if offset_fin == 2 else 'invierno'})")
        
        # Convertir a UTC
        inicio_utc = inicio_dt - datetime.timedelta(hours=offset_inicio)
        fin_utc = fin_dt - datetime.timedelta(hours=offset_fin)
        
        # Formatear para incluir Z al final (UTC)
        inicio_utc_str = inicio_utc.strftime("%Y-%m-%dT%H:%M:%S") + "Z"
        fin_utc_str = fin_utc.strftime("%Y-%m-%dT%H:%M:%S") + "Z"
        
        return inicio_utc_str, fin_utc_str
    except Exception as e:
        print(f"Error al formatear fechas: {str(e)}")
        sys.exit(1)

def extraer_key_decryption(key_string):
    """Extrae la clave de decripción del formato key1:key2"""
    if not key_string or key_string == "":
        return None
    
    parts = key_string.split(':')
    if len(parts) == 2:
        return parts[1]  # Tomamos la segunda parte como clave de decripción
    return key_string  # Si no hay formato específico, devolvemos la clave completa

def ejecutar_ffmpeg(url, key_decryption, nombre_archivo):
    """Ejecuta ffmpeg para descargar y desencriptar el contenido"""
    try:
        comando = (
            f'ffmpeg -headers "Referer: https://ver.zapitv.com" '
            f'-user_agent "{obtener_user_agent()}" '
        )
        
        if key_decryption:
            # Usar el parámetro correcto para la desencriptación
            comando += f'-cenc_decryption_key "{key_decryption}" '
        
        comando += (
            f'-i "{url}" '
            f'-c copy -map 0:2 -map 0:a -map "0:s?" "{nombre_archivo}"'
        )
        
        print("\nComando ffmpeg generado:")
        print(comando)
        
        # Ejecutar el comando
        result = subprocess.run(comando, shell=True)
        if result.returncode != 0:
            print("Error ejecutando ffmpeg. Código de retorno:", result.returncode)
        return result.returncode == 0
    except Exception as e:
        print(f"Error ejecutando ffmpeg: {str(e)}")
        return False

def verificar_url(url):
    """Verifica si una URL existe antes de intentar descargarla"""
    try:
        cabeceras = {
            "User-Agent": obtener_user_agent(),
            "Referer": "https://ver.zapitv.com"
        }
        
        response = requests.head(url, headers=cabeceras, timeout=10)
        return response.status_code < 400
    except Exception:
        return False

def ejecutar_script():
    """Función principal que ejecuta el script"""
    try:
        # Definir la ruta del archivo CSV
        archivo_csv = "zapi.csv"
        
        # Cargar datos del CSV
        canales, links, keys = cargar_datos_csv(archivo_csv)
        
        # Mostrar canales disponibles
        print("\nCanales disponibles:")
        for i, canal in enumerate(canales, 1):
            print(f"{i}. {canal}")
        
        # Pedir selección al usuario
        try:
            seleccion = int(input("\nIngrese el número del canal a descargar: ")) - 1
            if seleccion < 0 or seleccion >= len(canales):
                print("Selección inválida.")
                return
            
            canal_seleccionado = canales[seleccion]
        except ValueError:
            print("Por favor ingrese un número válido.")
            return
        
        # Obtener enlace y clave del canal seleccionado
        enlace = links.get(canal_seleccionado)
        clave = keys.get(canal_seleccionado)
        
        if not enlace:
            print(f"No hay enlace disponible para {canal_seleccionado}.")
            return
        
        # Pedir fechas al usuario
        print("\nFormato de fecha y hora (HORA LOCAL ESPAÑOLA): YYYY-MM-DDThh:mm:ss (ejemplo: 2025-03-16T10:30:00)")
        print("Nota: La hora se convertirá automáticamente a UTC según el horario de verano/invierno")
        fecha_inicio = input("Ingrese fecha y hora de inicio (hora local): ")
        fecha_fin = input("Ingrese fecha y hora de fin (hora local): ")
        
        # Formatear fechas para la URL, convirtiendo de hora local a UTC
        inicio_utc, fin_utc = formatear_fechas(fecha_inicio, fecha_fin)
        
        print(f"\nConversión a UTC:")
        print(f"Hora local inicial: {fecha_inicio} → UTC: {inicio_utc}")
        print(f"Hora local final: {fecha_fin} → UTC: {fin_utc}")
        
        # Reemplazar placeholders en la URL
        url_final = enlace.replace("{utc}", inicio_utc).replace("{utcend}", fin_utc)
        
        # Extraer la clave de decripción
        clave_decripcion = extraer_key_decryption(clave)
        
        # Crear nombre de archivo para guardar (usando la hora local)
        inicio_dt = datetime.datetime.strptime(fecha_inicio, "%Y-%m-%dT%H:%M:%S")
        nombre_archivo = f"{canal_seleccionado.replace(' ', '_')}_{inicio_dt.strftime('%Y-%m-%d_%H-%M')}.ts"
        
        # Verificar si el usuario quiere personalizar el nombre del archivo
        usar_nombre_personalizado = input(f"\n¿Desea usar un nombre personalizado en lugar de '{nombre_archivo}'? (s/n): ").lower()
        if usar_nombre_personalizado == 's':
            nombre_personalizado = input("Ingrese el nombre personalizado (sin extensión): ")
            if nombre_personalizado:
                nombre_archivo = f"{nombre_personalizado}.ts"
        
        # Verificar si la URL existe antes de proceder
        print(f"\nVerificando URL: {url_final}")
        if not verificar_url(url_final):
            print("¡Advertencia! La URL parece no estar accesible. ¿Desea continuar de todos modos?")
            continuar = input("Continuar (s/n): ").lower()
            if continuar != 's':
                return
        
        # Mostrar detalles antes de ejecutar
        print("\nDetalles de la descarga:")
        print(f"Canal: {canal_seleccionado}")
        print(f"Desde (hora local): {fecha_inicio}")
        print(f"Hasta (hora local): {fecha_fin}")
        print(f"URL con tiempos UTC: {url_final}")
        print(f"Archivo de salida: {nombre_archivo}")
        if clave_decripcion:
            print(f"Clave de decripción: {clave_decripcion}")
        else:
            print("No se encontró clave de decripción.")
        
        # Confirmar descarga
        confirmar = input("\n¿Proceder con la descarga? (s/n): ").lower()
        if confirmar != 's':
            print("Descarga cancelada.")
            return
        
        # Ejecutar ffmpeg
        print("\nIniciando descarga...")
        resultado = ejecutar_ffmpeg(url_final, clave_decripcion, nombre_archivo)
        
        if resultado:
            print(f"\n¡Descarga completada! Archivo guardado como: {nombre_archivo}")
        else:
            print("\nLa descarga falló o fue interrumpida.")
        
    except Exception as e:
        print(f"Error durante la ejecución: {str(e)}")

# Función para ejecutar el script en un bucle
def main():
    while True:
        ejecutar_script()
        repetir = input("\n¿Desea descargar otro contenido? (s/n): ").lower()
        if repetir != 's':
            break
    
    print("\n¡Gracias por usar el script de descarga U7D ZapiTV! - Script creado por Archivos M08g")

if __name__ == "__main__":
    main()
