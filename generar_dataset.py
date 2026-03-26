import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

np.random.seed(42)
random.seed(42)

N = 1200

# --- Configuración de distribuciones ---
tipos_incidente = ['robo', 'alarma', 'fallo técnico', 'intrusión', 'sabotaje', 'otros']
pesos_tipo = [0.25, 0.30, 0.15, 0.15, 0.08, 0.07]

paises = ['España', 'Argentina', 'Brasil', 'México', 'Chile', 'Colombia']
pesos_pais = [0.30, 0.20, 0.20, 0.15, 0.08, 0.07]

ubicaciones_por_pais = {
    'España':    ['Madrid', 'Barcelona', 'Valencia', 'Sevilla', 'Bilbao', 'Zaragoza'],
    'Argentina': ['Buenos Aires', 'Córdoba', 'Rosario', 'Mendoza', 'Tucumán'],
    'Brasil':    ['São Paulo', 'Rio de Janeiro', 'Brasília', 'Salvador', 'Fortaleza'],
    'México':    ['Ciudad de México', 'Guadalajara', 'Monterrey', 'Tijuana', 'Puebla'],
    'Chile':     ['Santiago', 'Valparaíso', 'Concepción', 'Antofagasta'],
    'Colombia':  ['Bogotá', 'Medellín', 'Cali', 'Cartagena'],
}

# Pesos por ubicación (zonas con más carga)
pesos_ubicacion = {
    'Madrid': 0.18, 'Barcelona': 0.12, 'Valencia': 0.06, 'Sevilla': 0.05,
    'Bilbao': 0.04, 'Zaragoza': 0.03,
    'Buenos Aires': 0.12, 'Córdoba': 0.04, 'Rosario': 0.03, 'Mendoza': 0.02, 'Tucumán': 0.01,
    'São Paulo': 0.10, 'Rio de Janeiro': 0.07, 'Brasília': 0.04, 'Salvador': 0.02, 'Fortaleza': 0.02,
    'Ciudad de México': 0.09, 'Guadalajara': 0.03, 'Monterrey': 0.03, 'Tijuana': 0.02, 'Puebla': 0.01,
    'Santiago': 0.04, 'Valparaíso': 0.02, 'Concepción': 0.01, 'Antofagasta': 0.01,
    'Bogotá': 0.03, 'Medellín': 0.02, 'Cali': 0.01, 'Cartagena': 0.01,
}

niveles_gravedad = ['bajo', 'medio', 'alto', 'crítico']
pesos_gravedad = [0.30, 0.35, 0.22, 0.13]

estados = ['abierto', 'en proceso', 'cerrado']
# Los críticos tendrán más cierre; los bajos pueden quedar abiertos
pesos_estado_por_gravedad = {
    'bajo':     [0.20, 0.20, 0.60],
    'medio':    [0.10, 0.20, 0.70],
    'alto':     [0.05, 0.15, 0.80],
    'crítico':  [0.05, 0.10, 0.85],
}

dispositivos = ['sensor', 'cámara', 'alarma', 'sistema']
# Relación dispositivo-tipo
disp_por_tipo = {
    'robo':          [0.10, 0.50, 0.30, 0.10],
    'alarma':        [0.20, 0.10, 0.60, 0.10],
    'fallo técnico': [0.20, 0.10, 0.10, 0.60],
    'intrusión':     [0.15, 0.40, 0.30, 0.15],
    'sabotaje':      [0.20, 0.30, 0.20, 0.30],
    'otros':         [0.25, 0.25, 0.25, 0.25],
}

cliente_tipo = ['empresa', 'particular']
pesos_cliente = [0.65, 0.35]

# Tiempo de respuesta promedio por gravedad (minutos)
tiempo_resp_params = {
    'crítico': (18, 8),
    'alto':    (35, 12),
    'medio':   (65, 20),
    'bajo':    (110, 40),
}

# --- Generación de fechas con mayor frecuencia en fines de semana ---
fecha_inicio = datetime(2024, 1, 1)
fecha_fin = datetime(2025, 12, 31)
rango_dias = (fecha_fin - fecha_inicio).days

fechas = []
for _ in range(N):
    intentos = 0
    while True:
        dias_offset = random.randint(0, rango_dias)
        fecha_candidata = fecha_inicio + timedelta(days=dias_offset)
        dia_semana = fecha_candidata.weekday()  # 0=Lun, 6=Dom
        # Fin de semana tiene 2.5x más probabilidad
        if dia_semana >= 5:
            prob = 0.72
        else:
            prob = 0.28
        if random.random() < prob or intentos > 20:
            hora = random.randint(0, 23)
            minuto = random.randint(0, 59)
            segundo = random.randint(0, 59)
            fechas.append(fecha_candidata.replace(hour=hora, minute=minuto, second=segundo))
            break
        intentos += 1

fechas.sort()

# --- Construcción del dataset ---
data = []
for i, fecha_reporte in enumerate(fechas):
    tipo = np.random.choice(tipos_incidente, p=pesos_tipo)
    pais = np.random.choice(paises, p=pesos_pais)
    ubicaciones_pais = ubicaciones_por_pais[pais]
    pesos_ub = [pesos_ubicacion[u] for u in ubicaciones_pais]
    suma = sum(pesos_ub)
    pesos_ub = [p / suma for p in pesos_ub]
    ubicacion = np.random.choice(ubicaciones_pais, p=pesos_ub)
    gravedad = np.random.choice(niveles_gravedad, p=pesos_gravedad)
    estado = np.random.choice(estados, p=pesos_estado_por_gravedad[gravedad])
    dispositivo = np.random.choice(dispositivos, p=disp_por_tipo[tipo])
    cliente = np.random.choice(cliente_tipo, p=pesos_cliente)

    mu, sigma = tiempo_resp_params[gravedad]
    tiempo_respuesta = max(5, int(np.random.normal(mu, sigma)))

    if estado == 'cerrado':
        fecha_resolucion = fecha_reporte + timedelta(minutes=tiempo_respuesta + random.randint(0, 60))
        fecha_resolucion_str = fecha_resolucion.strftime('%Y-%m-%d %H:%M:%S')
    elif estado == 'en proceso':
        fecha_resolucion_str = ''
        # Tiempo de respuesta parcial
        tiempo_respuesta = max(5, int(tiempo_respuesta * random.uniform(0.3, 0.8)))
    else:  # abierto
        fecha_resolucion_str = ''
        tiempo_respuesta = None

    data.append({
        'id_incidente': f'INC-{str(i+1).zfill(5)}',
        'fecha_hora_reporte': fecha_reporte.strftime('%Y-%m-%d %H:%M:%S'),
        'fecha_hora_resolucion': fecha_resolucion_str,
        'tipo_incidente': tipo,
        'ubicacion': ubicacion,
        'pais': pais,
        'nivel_gravedad': gravedad,
        'tiempo_respuesta_minutos': tiempo_respuesta,
        'estado': estado,
        'dispositivo_asociado': dispositivo,
        'cliente_tipo': cliente,
    })

df = pd.DataFrame(data)
output_path = 'incidentes_seguridad.csv'
df.to_csv(output_path, index=False, encoding='utf-8-sig')
print(f"Dataset generado: {len(df)} filas -> {output_path}")
print(df.dtypes)
print(df.head(3))
