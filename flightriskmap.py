import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.patheffects as pe

df = pd.read_csv('zip_flight_risk_scores.csv')

def get_color(score):
    if score > 0.67:
        return '#e63946'
    elif score >= 0.33:
        return '#f4a236'
    else:
        return '#2ec47a'

df['color'] = df['flight_risk_score'].apply(get_color)

# Tier labels
def get_tier(score):
    if score > 0.67:
        return 'High'
    elif score >= 0.33:
        return 'Medium'
    else:
        return 'Low'

df['tier'] = df['flight_risk_score'].apply(get_tier)

counts = df['tier'].value_counts()

fig, ax = plt.subplots(figsize=(16, 14), facecolor='#0f1117')
ax.set_facecolor('#0f1117')

sizes = 1000

ax.scatter(
    df['ZipCode_Longitude'], df['ZipCode_Latitude'],
    c=df['color'], s=sizes, alpha=0.75,
    edgecolors='white', linewidths=0.4, zorder=3
)

for _, row in df.iterrows():
    ax.annotate(
        str(row['ZipCode']),
        (row['ZipCode_Longitude'], row['ZipCode_Latitude']),
        fontsize=5.5, fontweight='bold', color='white',
        ha='center', va='center', zorder=4,
        path_effects=[
            pe.withStroke(linewidth=2, foreground='#0f1117')
        ]
    )

# Legend
legend_elements = [
    Line2D([0], [0], marker='o', color='#0f1117', markerfacecolor='#e63946',
           markersize=14, label=f'High Risk  >67%  ({counts.get("High", 0)} ZIPs)', linewidth=0),
    Line2D([0], [0], marker='o', color='#0f1117', markerfacecolor='#f4a236',
           markersize=14, label=f'Medium Risk  33–67%  ({counts.get("Medium", 0)} ZIPs)', linewidth=0),
    Line2D([0], [0], marker='o', color='#0f1117', markerfacecolor='#2ec47a',
           markersize=14, label=f'Low Risk  <33%  ({counts.get("Low", 0)} ZIPs)', linewidth=0),
]

legend = ax.legend(
    handles=legend_elements, loc='upper left',
    fontsize=11, frameon=True, fancybox=True,
    facecolor='#1a1d27', edgecolor='#333',
    labelcolor='white', borderpad=1, handletextpad=1
)

# Title
ax.set_title(
    'ZIP Code Flight Risk Map — Orange County & Surrounding Areas',
    fontsize=18, fontweight='bold', color='white', pad=20
)

# Style axes
ax.set_xlabel('Longitude', fontsize=10, color='#8b8fa3')
ax.set_ylabel('Latitude', fontsize=10, color='#8b8fa3')
ax.tick_params(colors='#8b8fa3', labelsize=8)
for spine in ax.spines.values():
    spine.set_color('#333')

ax.set_aspect('equal')
plt.tight_layout()
plt.savefig('flight_risk_map.png', dpi=180, bbox_inches='tight', facecolor='#0f1117')
print('Map saved to flight_risk_map.png')