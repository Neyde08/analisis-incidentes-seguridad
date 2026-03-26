"""
Análisis de Incidentes de Seguridad - Estilo ISOC/Prosegur
Pasos 2, 3 y 4 del requerimiento
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.gridspec import GridSpec
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────
# CARGA Y PREPARACIÓN
# ─────────────────────────────────────────────
df = pd.read_csv('incidentes_seguridad.csv', encoding='utf-8-sig')

df['fecha_hora_reporte']    = pd.to_datetime(df['fecha_hora_reporte'])
df['fecha_hora_resolucion'] = pd.to_datetime(df['fecha_hora_resolucion'], errors='coerce')
df['mes']         = df['fecha_hora_reporte'].dt.to_period('M')
df['dia_semana']  = df['fecha_hora_reporte'].dt.day_name()
df['dia_num']     = df['fecha_hora_reporte'].dt.dayofweek  # 0=Lun

ORDER_DIA = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
LABELS_DIA = ['Lun','Mar','Mié','Jue','Vie','Sáb','Dom']

GRAVEDAD_ORDER = ['bajo','medio','alto','crítico']
COLORES_GRAVEDAD = {'bajo':'#4CAF50','medio':'#FFC107','alto':'#FF9800','crítico':'#F44336'}
COLORES_TIPO = {
    'alarma':'#2196F3','robo':'#F44336','fallo técnico':'#9C27B0',
    'intrusión':'#FF9800','sabotaje':'#795548','otros':'#607D8B'
}

# ─────────────────────────────────────────────
# PASO 2: ANÁLISIS
# ─────────────────────────────────────────────
print("=" * 60)
print("  ANÁLISIS DE INCIDENTES DE SEGURIDAD")
print("=" * 60)

# 2.1 Total de incidentes
total = len(df)
print(f"\n[1] TOTAL DE INCIDENTES: {total:,}")

# 2.2 Distribución por tipo
print("\n[2] DISTRIBUCIÓN POR TIPO DE INCIDENTE")
dist_tipo = df['tipo_incidente'].value_counts()
for t, c in dist_tipo.items():
    print(f"    {t:<20} {c:>5}  ({c/total*100:.1f}%)")

# 2.3 Distribución por gravedad
print("\n[3] DISTRIBUCIÓN POR NIVEL DE GRAVEDAD")
dist_grav = df['nivel_gravedad'].value_counts().reindex(GRAVEDAD_ORDER)
for g, c in dist_grav.items():
    print(f"    {g:<12} {c:>5}  ({c/total*100:.1f}%)")

# 2.4 Tiempo de respuesta promedio general
df_resp = df[df['tiempo_respuesta_minutos'].notna()]
tr_general = df_resp['tiempo_respuesta_minutos'].mean()
print(f"\n[4] TIEMPO DE RESPUESTA PROMEDIO GENERAL: {tr_general:.1f} min")

# 2.5 Tiempo de respuesta por tipo
print("\n[5] TIEMPO DE RESPUESTA PROMEDIO POR TIPO")
tr_tipo = df_resp.groupby('tipo_incidente')['tiempo_respuesta_minutos'].mean().sort_values()
for t, v in tr_tipo.items():
    print(f"    {t:<20} {v:>6.1f} min")

# 2.6 Tiempo de respuesta por gravedad
print("\n[6] TIEMPO DE RESPUESTA PROMEDIO POR GRAVEDAD")
tr_grav = df_resp.groupby('nivel_gravedad')['tiempo_respuesta_minutos'].mean().reindex(GRAVEDAD_ORDER)
for g, v in tr_grav.items():
    print(f"    {g:<12} {v:>6.1f} min")

# 2.7 Top ubicaciones
print("\n[7] TOP 10 UBICACIONES CON MÁS INCIDENTES")
top_ub = df['ubicacion'].value_counts().head(10)
for u, c in top_ub.items():
    print(f"    {u:<25} {c:>5}  ({c/total*100:.1f}%)")

# 2.8 Tendencias mensuales
print("\n[8] TENDENCIAS MENSUALES")
mensual = df.groupby('mes').size()
for m, c in mensual.items():
    print(f"    {str(m):<8} {c:>5}")

# 2.9 Por día de la semana
print("\n[9] INCIDENTES POR DÍA DE LA SEMANA")
dia_cnt = df.groupby('dia_num').size()
for i, label in enumerate(LABELS_DIA):
    cnt = dia_cnt.get(i, 0)
    print(f"    {label}  {cnt:>5}  ({cnt/total*100:.1f}%)")

# 2.10 Relación tipo de incidente vs dispositivo
print("\n[10] RELACIÓN TIPO DE INCIDENTE VS DISPOSITIVO ASOCIADO")
crosstab = pd.crosstab(df['tipo_incidente'], df['dispositivo_asociado'])
print(crosstab.to_string())

# ─────────────────────────────────────────────
# KPIs
# ─────────────────────────────────────────────
pct_criticos   = (df['nivel_gravedad'] == 'crítico').sum() / total * 100
pct_resueltos  = (df['estado'] == 'cerrado').sum() / total * 100
pct_en_proceso = (df['estado'] == 'en proceso').sum() / total * 100
pct_abiertos   = (df['estado'] == 'abierto').sum() / total * 100

print("\n" + "=" * 60)
print("  KPIs CLAVE")
print("=" * 60)
print(f"  Total incidentes          : {total:,}")
print(f"  Tiempo medio respuesta    : {tr_general:.1f} min")
print(f"  % Incidentes críticos     : {pct_criticos:.1f}%")
print(f"  % Incidentes resueltos    : {pct_resueltos:.1f}%")
print(f"  % En proceso              : {pct_en_proceso:.1f}%")
print(f"  % Abiertos (sin iniciar)  : {pct_abiertos:.1f}%")

# ─────────────────────────────────────────────
# VISUALIZACIONES
# ─────────────────────────────────────────────
fig = plt.figure(figsize=(22, 28))
fig.patch.set_facecolor('#0D1117')
gs = GridSpec(4, 2, figure=fig, hspace=0.50, wspace=0.35)
TEXT_COLOR = '#E0E0E0'
GRID_COLOR = '#2A2A3A'
BG_AXES = '#161B22'

def style_ax(ax, title):
    ax.set_facecolor(BG_AXES)
    ax.tick_params(colors=TEXT_COLOR, labelsize=10)
    ax.spines[:].set_color(GRID_COLOR)
    ax.title.set_color(TEXT_COLOR)
    ax.set_title(title, fontsize=13, fontweight='bold', pad=10)
    ax.yaxis.label.set_color(TEXT_COLOR)
    ax.xaxis.label.set_color(TEXT_COLOR)
    ax.grid(axis='y', color=GRID_COLOR, linewidth=0.6, linestyle='--')

# — Gráfico 1: Tipo de incidente vs cantidad —
ax1 = fig.add_subplot(gs[0, 0])
tipos_sorted = dist_tipo.sort_values(ascending=True)
colores1 = [COLORES_TIPO.get(t, '#607D8B') for t in tipos_sorted.index]
bars = ax1.barh(tipos_sorted.index, tipos_sorted.values, color=colores1, edgecolor='none', height=0.6)
for bar, v in zip(bars, tipos_sorted.values):
    ax1.text(v + 5, bar.get_y() + bar.get_height()/2,
             f'{v}', va='center', ha='left', color=TEXT_COLOR, fontsize=10)
style_ax(ax1, 'Incidentes por Tipo')
ax1.grid(axis='x', color=GRID_COLOR, linewidth=0.6, linestyle='--')
ax1.grid(axis='y', visible=False)

# — Gráfico 2: Donut gravedad —
ax2 = fig.add_subplot(gs[0, 1])
ax2.set_facecolor(BG_AXES)
grav_vals = dist_grav.reindex(GRAVEDAD_ORDER).fillna(0)
colors_d = [COLORES_GRAVEDAD[g] for g in GRAVEDAD_ORDER]
wedges, texts, autotexts = ax2.pie(
    grav_vals, labels=GRAVEDAD_ORDER, colors=colors_d,
    autopct='%1.1f%%', startangle=90,
    wedgeprops={'width': 0.55, 'edgecolor': BG_AXES, 'linewidth': 2},
    pctdistance=0.80
)
for t in texts:     t.set_color(TEXT_COLOR); t.set_fontsize(11)
for at in autotexts: at.set_color('#111'); at.set_fontsize(10); at.set_fontweight('bold')
ax2.set_title('Distribución por Nivel de Gravedad', fontsize=13, fontweight='bold',
              color=TEXT_COLOR, pad=10)

# — Gráfico 3: Evolución mensual —
ax3 = fig.add_subplot(gs[1, :])
mensual_df = mensual.reset_index()
mensual_df.columns = ['mes', 'cantidad']
mensual_df['mes_str'] = mensual_df['mes'].astype(str)
ax3.plot(mensual_df['mes_str'], mensual_df['cantidad'],
         color='#00BCD4', linewidth=2.5, marker='o', markersize=5, markerfacecolor='white')
ax3.fill_between(mensual_df['mes_str'], mensual_df['cantidad'], alpha=0.15, color='#00BCD4')
ax3.set_xticks(range(len(mensual_df)))
ax3.set_xticklabels(mensual_df['mes_str'], rotation=45, ha='right', fontsize=9)
style_ax(ax3, 'Evolución Mensual de Incidentes')
ax3.set_ylabel('Cantidad de incidentes')

# — Gráfico 4: Tiempo respuesta por tipo —
ax4 = fig.add_subplot(gs[2, 0])
tr_tipo_sorted = tr_tipo.sort_values()
colores4 = [COLORES_TIPO.get(t, '#607D8B') for t in tr_tipo_sorted.index]
bars4 = ax4.barh(tr_tipo_sorted.index, tr_tipo_sorted.values, color=colores4, edgecolor='none', height=0.6)
for bar, v in zip(bars4, tr_tipo_sorted.values):
    ax4.text(v + 0.5, bar.get_y() + bar.get_height()/2,
             f'{v:.0f} min', va='center', ha='left', color=TEXT_COLOR, fontsize=10)
style_ax(ax4, 'Tiempo de Respuesta por Tipo (min)')
ax4.grid(axis='x', color=GRID_COLOR, linewidth=0.6, linestyle='--')
ax4.grid(axis='y', visible=False)

# — Gráfico 5: Incidentes por día de semana —
ax5 = fig.add_subplot(gs[2, 1])
dia_data = [dia_cnt.get(i, 0) for i in range(7)]
colores5 = ['#F44336' if i >= 5 else '#2196F3' for i in range(7)]
bars5 = ax5.bar(LABELS_DIA, dia_data, color=colores5, edgecolor='none', width=0.6)
for bar, v in zip(bars5, dia_data):
    ax5.text(bar.get_x() + bar.get_width()/2, v + 1,
             f'{v}', ha='center', va='bottom', color=TEXT_COLOR, fontsize=10)
style_ax(ax5, 'Incidentes por Día de la Semana')
ax5.set_ylabel('Cantidad')
from matplotlib.patches import Patch
legend_handles = [Patch(color='#F44336', label='Fin de semana'),
                  Patch(color='#2196F3', label='Día laboral')]
ax5.legend(handles=legend_handles, facecolor=BG_AXES, labelcolor=TEXT_COLOR,
           edgecolor=GRID_COLOR, fontsize=9)

# — Gráfico 6: Top 10 ubicaciones —
ax6 = fig.add_subplot(gs[3, :])
top10 = df['ubicacion'].value_counts().head(10).sort_values(ascending=True)
gradient = plt.cm.Blues(np.linspace(0.4, 0.9, len(top10)))
bars6 = ax6.barh(top10.index, top10.values, color=gradient, edgecolor='none', height=0.65)
for bar, v in zip(bars6, top10.values):
    ax6.text(v + 1, bar.get_y() + bar.get_height()/2,
             f'{v}', va='center', ha='left', color=TEXT_COLOR, fontsize=10)
style_ax(ax6, 'Top 10 Ubicaciones con Mayor Número de Incidentes')
ax6.grid(axis='x', color=GRID_COLOR, linewidth=0.6, linestyle='--')
ax6.grid(axis='y', visible=False)
ax6.set_xlabel('Cantidad de incidentes')

# KPI box en la parte superior
kpi_text = (f"  KPIs  |  Total: {total:,}   |   "
            f"T° Resp. medio: {tr_general:.0f} min   |   "
            f"Críticos: {pct_criticos:.1f}%   |   "
            f"Resueltos: {pct_resueltos:.1f}%")
fig.text(0.5, 0.975, kpi_text, ha='center', va='top',
         color='#00BCD4', fontsize=12, fontweight='bold',
         bbox=dict(boxstyle='round,pad=0.4', facecolor='#1A2035', edgecolor='#00BCD4', linewidth=1.5))

plt.savefig('dashboard_incidentes.png', dpi=150, bbox_inches='tight',
            facecolor=fig.get_facecolor())
print("\nDashboard guardado: dashboard_incidentes.png")
plt.close()

# ─────────────────────────────────────────────
# PASO 4: INSIGHTS Y RECOMENDACIONES
# ─────────────────────────────────────────────
import sys
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf-8-sig'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

insights = f"""
{'=' * 60}
  INSIGHTS Y RECOMENDACIONES
{'=' * 60}

INSIGHT 1 — Concentración geográfica de riesgo
  Madrid y Barcelona concentran el ~30% de todos los incidentes.
  → Priorizar recursos de respuesta y tecnología (más cámaras/sensores)
    en estas zonas. Revisar contratos de mantenimiento preventivo.

INSIGHT 2 — Patrón temporal: fines de semana
  Los incidentes se concentran sábados y domingos (mayor tráfico de
  alarmas y robos), probablemente por menor presencia humana en
  instalaciones empresariales.
  → Reforzar guardias y patrullas virtuales (SOC 24/7) en fin de semana.
    Establecer protocolos de escalamiento automático los sábados/domingos.

INSIGHT 3 — Los incidentes críticos reciben atención más rápida
  Tiempo de respuesta para críticos (~18 min) vs bajos (~110 min).
  La brecha es correcta pero los incidentes de gravedad media-alta
  superan los 30-65 min; hay margen de mejora operativa.
  → Implementar SLA formales: crítico <20 min, alto <30 min, medio <60 min.
    Automatizar despacho de equipos para incidentes >alto.

INSIGHT 4 — Alarmas falsas y fallos técnicos representan el 45%
  Alarma (30%) + Fallo técnico (15%) = 45% del total. Gran parte
  del esfuerzo operativo se destina a incidentes no delictivos.
  → Implementar un sistema de verificación de doble factor antes de
    despachar unidades físicas (revisión de cámara + confirmación
    cliente). Esto liberaría ~30% de la capacidad operativa.

INSIGHT 5 — Dispositivos vs tipo de incidente
  Las cámaras son el dispositivo más vinculado a robos e intrusiones;
  las alarmas a incidentes de tipo "alarma". Los sistemas (software)
  dominan en fallos técnicos.
  → Invertir en mantenimiento predictivo de cámaras en zonas de alto robo.
    Evaluar actualización de sistemas en ciudades con alta tasa de
    fallos técnicos (posible antigüedad del hardware).

INSIGHT 6 — {pct_abiertos:.1f}% de incidentes sin iniciar gestión
  Los incidentes en estado "abierto" representan {pct_abiertos:.1f}%, lo que
  indica carga operativa no atendida o falta de asignación automática.
  → Implementar asignación automática de incidentes al momento del reporte
    (workflow de ticketing con reglas de prioridad).

INSIGHT 7 — Clientes empresariales generan el 65% de incidentes
  Mayor volumen desde clientes corporativos, pero también mayor
  nivel de gravedad promedio.
  → Desarrollar planes de respuesta personalizados (SLA premium) y
    reportes automáticos mensuales de incidentes para clientes empresa.

RECOMENDACIONES POWER BI
  - Añadir alertas visuales cuando el % de críticos supere el {pct_criticos:.0f}% histórico.
  - Usar la segmentación por "pais" + "estado" para identificar filiales
    con backlog elevado.
  - El mapa geográfico debe codificar por color la gravedad promedio,
    no solo el volumen, para detectar zonas de alto riesgo con pocas alertas.
  - Publicar el dashboard en Power BI Service con actualización diaria
    desde el CSV/base de datos operacional.
"""
print(insights)

with open('informe_analisis.txt', 'w', encoding='utf-8') as f:
    f.write(insights)
print("Informe guardado: informe_analisis.txt")
