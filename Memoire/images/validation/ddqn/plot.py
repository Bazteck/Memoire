#!/usr/bin/env python3
"""
plot_discrete_distances.py
Génère les figures avec des distances discrètes et des annotations claires
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# ===== CONFIGURATION STYLE =====
plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 11,
    'axes.titlesize': 16,
    'axes.titleweight': 'bold',
    'axes.labelsize': 14,
    'axes.labelweight': 'bold',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.linewidth': 1.2,
    'axes.grid': True,
    'grid.alpha': 0.25,
    'grid.linewidth': 0.8,
    'grid.linestyle': '--',
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'legend.fontsize': 11,
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'axes.facecolor': '#F8FAFC',
})

# Palette de couleurs
C_STD = '#2563EB'      # Bleu standard
C_DDQN = '#DC2626'     # Rouge DDQN
C_CR13 = '#4F46E5'     # Indigo pour CR 1/3
C_CR23 = '#0891B2'     # Cyan pour CR 2/3
C_GREEN = '#16A34A'    # Vert pour amélioration
C_RED = '#DC2626'      # Rouge pour dégradation

def style_ax(ax, title=None, xlabel=None, ylabel=None):
    """Style professionnel pour les axes"""
    ax.set_facecolor('#F8FAFC')
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    ax.tick_params(colors='#475569', length=5, width=1)
    if xlabel: ax.set_xlabel(xlabel, fontsize=13, fontweight='bold')
    if ylabel: ax.set_ylabel(ylabel, fontsize=13, fontweight='bold')
    if title: ax.set_title(title, fontsize=16, pad=20, fontweight='bold')
    ax.grid(True, alpha=0.25, linestyle='--', linewidth=0.8)
    ax.set_axisbelow(True)

# ===== CHARGEMENT DES DONNÉES =====
print("=" * 60)
print("CHARGEMENT DES DONNÉES")
print("=" * 60)

df = pd.read_csv('ddqn_comparison_detailed_by_distance.csv')
df = df.sort_values('distance_m')

# Sélectionner des distances discrètes pour mieux afficher
discrete_distances = [139, 331, 775, 1015, 1194, 1260, 1300, 1753, 1977, 2000, 2816, 3000, 4000]
df_discrete = df[df['distance_m'].isin(discrete_distances)].copy()
df_discrete = df_discrete.sort_values('distance_m')

print(f"Distances originales: {len(df)}")
print(f"Distances discrètes sélectionnées: {len(df_discrete)}")
print(f"Distances: {list(df_discrete['distance_m'].values)}")

# Création du dossier
os.makedirs('figures_discretes', exist_ok=True)

# ===== 1. COURBE PDR AVEC POINTS DISCRETS =====
print("\n[1/6] Courbe PDR avec points discrets...")

fig, ax = plt.subplots(figsize=(16, 8))

# Standard
ax.plot(df_discrete['distance_m'], df_discrete['std_pdr'], 
        color=C_STD, marker='s', linestyle='--', 
        linewidth=2.5, markersize=10,
        markerfacecolor=C_STD, markeredgecolor='white', markeredgewidth=2,
        label='Simulation Standard', zorder=3)

# DDQN
ax.plot(df_discrete['distance_m'], df_discrete['ddqn_pdr'],
        color=C_DDQN, marker='D', linestyle='-.',
        linewidth=2.5, markersize=10,
        markerfacecolor=C_DDQN, markeredgecolor='white', markeredgewidth=2,
        label='DDQN Adaptatif', zorder=4)

# Annotations avec fond blanc
for _, row in df_discrete.iterrows():
    # Standard
    ax.annotate(f"{row['std_pdr']:.1f}%", 
                (row['distance_m'], row['std_pdr']),
                xytext=(0, 15), textcoords='offset points',
                ha='center', fontsize=9, fontweight='bold', color=C_STD,
                bbox=dict(boxstyle='round,pad=0.3', fc='white', ec=C_STD, alpha=0.9))
    
    # DDQN
    ax.annotate(f"{row['ddqn_pdr']:.1f}%",
                (row['distance_m'], row['ddqn_pdr']),
                xytext=(0, -20), textcoords='offset points',
                ha='center', fontsize=9, fontweight='bold', color=C_DDQN,
                bbox=dict(boxstyle='round,pad=0.3', fc='white', ec=C_DDQN, alpha=0.9))

style_ax(ax, xlabel='Distance (m)', ylabel='PDR (%)')
ax.set_xlim(0, 4200)
ax.set_ylim(60, 105)
ax.set_xticks(discrete_distances)
ax.set_xticklabels([f'{d}m' for d in discrete_distances], rotation=45, ha='right')
ax.legend(loc='lower left', frameon=True, framealpha=0.95)
ax.set_title('Comparaison PDR: Standard vs DDQN\n(Points discrets)', fontsize=16, pad=30)

plt.tight_layout()
plt.savefig('figures_discretes/01_pdr_discret.png')
plt.close(fig)
print("  ✓ 01_pdr_discret.png")

# ===== 2. BARRES PDR AVEC ÉCARTS =====
print("[2/6] Barres PDR avec écarts...")

fig, ax = plt.subplots(figsize=(18, 8))

x_pos = np.arange(len(df_discrete))
bar_width = 0.35

bars1 = ax.bar(x_pos - bar_width/2, df_discrete['std_pdr'].values,
               width=bar_width, label='Standard', color=C_STD,
               alpha=0.85, edgecolor='white', linewidth=1.5)
bars2 = ax.bar(x_pos + bar_width/2, df_discrete['ddqn_pdr'].values,
               width=bar_width, label='DDQN Adaptatif', color=C_DDQN,
               alpha=0.85, edgecolor='white', linewidth=1.5)

# Valeurs dans les barres
for bars, col in [(bars1, C_STD), (bars2, C_DDQN)]:
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., h/2,
                f'{h:.1f}%', ha='center', va='center',
                fontsize=9, fontweight='bold', color='white')

# Indicateurs d'amélioration
for i, (std, ddqn) in enumerate(zip(df_discrete['std_pdr'], df_discrete['ddqn_pdr'])):
    improvement = ddqn - std
    color = C_GREEN if improvement > 0 else C_RED
    ax.text(i, max(std, ddqn) + 3, f'{improvement:+.1f}%', 
            ha='center', fontsize=10, fontweight='bold', color=color,
            bbox=dict(boxstyle='round,pad=0.2', fc='white', ec=color, alpha=0.9))

style_ax(ax, xlabel='Distance (m)', ylabel='PDR (%)')
ax.set_xticks(x_pos)
ax.set_xticklabels([f'{int(d)}m' for d in df_discrete['distance_m']], rotation=45, ha='right')
ax.set_ylim(0, 110)
ax.legend(loc='upper right', frameon=True)
ax.set_title('PDR par Distance: Standard vs DDQN', fontsize=16, pad=20)

plt.tight_layout()
plt.savefig('figures_discretes/02_pdr_bars_discret.png')
plt.close(fig)
print("  ✓ 02_pdr_bars_discret.png")

# ===== 3. TABLEAU DE VALEURS =====
print("[3/6] Tableau de valeurs...")

fig, ax = plt.subplots(figsize=(16, len(df_discrete)*0.6))
ax.axis('tight')
ax.axis('off')

# Préparer les données pour le tableau
table_data = []
headers = ['Distance (m)', 'PDR Standard (%)', 'PDR DDQN (%)', 'Écart (pts)', 'Amélioration (%)', 'Énergie Std (mJ)', 'Énergie DDQN (mJ)', 'Puissance DDQN (dBm)']

for _, row in df_discrete.iterrows():
    dist = int(row['distance_m'])
    std_pdr = row['std_pdr']
    ddqn_pdr = row['ddqn_pdr']
    ecart = ddqn_pdr - std_pdr
    amelioration = (ecart / std_pdr * 100) if std_pdr > 0 else 0
    energy_std = row['std_energy']
    energy_ddqn = row['ddqn_energy']
    power = row['ddqn_power']
    
    table_data.append([
        f"{dist}",
        f"{std_pdr:.2f}",
        f"{ddqn_pdr:.2f}",
        f"{ecart:+.2f}",
        f"{amelioration:+.1f}%",
        f"{energy_std:.3f}",
        f"{energy_ddqn:.3f}",
        f"{power:.1f}"
    ])

# Créer le tableau
table = ax.table(cellText=table_data, colLabels=headers,
                 cellLoc='center', loc='center',
                 colWidths=[0.10, 0.12, 0.12, 0.10, 0.12, 0.12, 0.12, 0.12])

# Styliser le tableau
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1.2, 1.5)

# Couleurs des en-têtes
for (i, j), cell in table.get_celld().items():
    if i == 0:
        cell.set_facecolor('#1E293B')
        cell.set_text_props(weight='bold', color='white')
    else:
        if j in [3, 4]:  # Colonnes d'écart
            val = float(table_data[i-1][j].replace('%', '').replace('+', ''))
            if val > 0:
                cell.set_facecolor('#E6F7E6')
            elif val < 0:
                cell.set_facecolor('#FFE6E6')

ax.set_title('Tableau Comparatif Détaillé', fontsize=16, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig('figures_discretes/03_tableau_valeurs.png', dpi=300, bbox_inches='tight')
plt.close(fig)
print("  ✓ 03_tableau_valeurs.png")

# ===== 4. ÉNERGIE AVEC ANNOTATIONS =====
print("[4/6] Énergie avec annotations...")

fig, ax = plt.subplots(figsize=(16, 8))

# CR 1/3
ax.plot(df_discrete['distance_m'], df_discrete['std_energy_cr13'],
        color=C_CR13, marker='^', linestyle=':', 
        linewidth=2.5, markersize=10,
        markerfacecolor=C_CR13, markeredgecolor='white', markeredgewidth=2,
        label='CR 1/3 (DR8/DR10)', zorder=2)

# CR 2/3
ax.plot(df_discrete['distance_m'], df_discrete['std_energy_cr23'],
        color=C_CR23, marker='v', linestyle=':',
        linewidth=2.5, markersize=10,
        markerfacecolor=C_CR23, markeredgecolor='white', markeredgewidth=2,
        label='CR 2/3 (DR9/DR11)', zorder=2)

# Moyenne Standard
ax.plot(df_discrete['distance_m'], df_discrete['std_energy'],
        color=C_STD, marker='s', linestyle='--',
        linewidth=2.5, markersize=10,
        markerfacecolor=C_STD, markeredgecolor='white', markeredgewidth=2,
        label='Standard (moyenne)', zorder=3)

# DDQN
ax.plot(df_discrete['distance_m'], df_discrete['ddqn_energy'],
        color=C_DDQN, marker='D', linestyle='-.',
        linewidth=2.5, markersize=10,
        markerfacecolor=C_DDQN, markeredgecolor='white', markeredgewidth=2,
        label='DDQN Adaptatif', zorder=4)

# Annotations
for _, row in df_discrete.iterrows():
    ax.annotate(f"{row['ddqn_energy']:.2f}", 
                (row['distance_m'], row['ddqn_energy']),
                xytext=(0, 10), textcoords='offset points',
                ha='center', fontsize=8, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.2', fc='white', alpha=0.9))

style_ax(ax, xlabel='Distance (m)', ylabel='Énergie par paquet (mJ)')
ax.set_xlim(0, 4200)
ax.set_ylim(20, 100)
ax.set_xticks(discrete_distances)
ax.set_xticklabels([f'{d}m' for d in discrete_distances], rotation=45, ha='right')
ax.legend(loc='lower right', frameon=True, ncol=2)
ax.set_title('Énergie par Paquet selon le Coding Rate', fontsize=16, pad=20)

plt.tight_layout()
plt.savefig('figures_discretes/04_energy_discret.png')
plt.close(fig)
print("  ✓ 04_energy_discret.png")

# ===== 5. PUISSANCE AVEC ANNOTATIONS =====
print("[5/6] Puissance avec annotations...")

fig, ax = plt.subplots(figsize=(16, 8))

# Standard (fixe)
ax.axhline(y=14, color=C_STD, linestyle='--', linewidth=2.5, 
           label='Standard (fixe 14 dBm)', zorder=2)

# DDQN
ax.plot(df_discrete['distance_m'], df_discrete['ddqn_power'],
        color=C_DDQN, marker='D', linestyle='-.',
        linewidth=2.5, markersize=12,
        markerfacecolor=C_DDQN, markeredgecolor='white', markeredgewidth=2,
        label='DDQN Adaptatif', zorder=3)

# Annotations avec valeurs
for _, row in df_discrete.iterrows():
    ax.annotate(f"{row['ddqn_power']:.1f} dBm",
                (row['distance_m'], row['ddqn_power']),
                xytext=(0, 12), textcoords='offset points',
                ha='center', fontsize=9, fontweight='bold', color=C_DDQN,
                bbox=dict(boxstyle='round,pad=0.3', fc='white', ec=C_DDQN, alpha=0.9))

style_ax(ax, xlabel='Distance (m)', ylabel='Puissance TX (dBm)')
ax.set_xlim(0, 4200)
ax.set_ylim(0, 16)
ax.set_xticks(discrete_distances)
ax.set_xticklabels([f'{d}m' for d in discrete_distances], rotation=45, ha='right')
ax.set_yticks(range(0, 17, 2))
ax.legend(loc='lower right', frameon=True)
ax.set_title('Puissance de Transmission: Standard vs DDQN', fontsize=16, pad=20)

plt.tight_layout()
plt.savefig('figures_discretes/05_power_discret.png')
plt.close(fig)
print("  ✓ 05_power_discret.png")

# ===== 6. AMÉLIORATION PDR DÉTAILLÉE =====
print("[6/6] Amélioration PDR détaillée...")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))

# Graphique 1: Amélioration en points
improvement_pts = df_discrete['ddqn_pdr'] - df_discrete['std_pdr']
colors = [C_GREEN if x > 0 else C_RED for x in improvement_pts]

bars = ax1.bar(df_discrete['distance_m'], improvement_pts, width=80, 
               color=colors, alpha=0.7, edgecolor='white', linewidth=1.5)
ax1.axhline(y=0, color='black', linewidth=1, linestyle='-', alpha=0.3)

for bar, imp in zip(bars, improvement_pts):
    height = bar.get_height()
    va = 'bottom' if height > 0 else 'top'
    offset = 0.8 if height > 0 else -0.8
    ax1.text(bar.get_x() + bar.get_width()/2., height + offset,
             f'{imp:+.1f} pts', ha='center', va=va, fontsize=9, fontweight='bold',
             bbox=dict(boxstyle='round,pad=0.2', fc='white', alpha=0.9))

style_ax(ax1, xlabel='Distance (m)', ylabel='Amélioration (points %)')
ax1.set_xticks(discrete_distances)
ax1.set_xticklabels([f'{d}m' for d in discrete_distances], rotation=45, ha='right')
ax1.set_title('Amélioration en points de pourcentage', fontsize=14, pad=15)

# Graphique 2: Amélioration en pourcentage
improvement_pct = ((df_discrete['ddqn_pdr'] - df_discrete['std_pdr']) / df_discrete['std_pdr'] * 100)
colors = [C_GREEN if x > 0 else C_RED for x in improvement_pct]

bars = ax2.bar(df_discrete['distance_m'], improvement_pct, width=80, 
               color=colors, alpha=0.7, edgecolor='white', linewidth=1.5)
ax2.axhline(y=0, color='black', linewidth=1, linestyle='-', alpha=0.3)

for bar, imp in zip(bars, improvement_pct):
    height = bar.get_height()
    va = 'bottom' if height > 0 else 'top'
    offset = 1.5 if height > 0 else -1.5
    ax2.text(bar.get_x() + bar.get_width()/2., height + offset,
             f'{imp:+.1f}%', ha='center', va=va, fontsize=9, fontweight='bold',
             bbox=dict(boxstyle='round,pad=0.2', fc='white', alpha=0.9))

style_ax(ax2, xlabel='Distance (m)', ylabel='Amélioration relative (%)')
ax2.set_xticks(discrete_distances)
ax2.set_xticklabels([f'{d}m' for d in discrete_distances], rotation=45, ha='right')
ax2.set_title('Amélioration relative en pourcentage', fontsize=14, pad=15)

plt.suptitle('Analyse de l\'Amélioration du PDR par le DDQN', fontsize=16, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('figures_discretes/06_improvement_detailed.png', dpi=300, bbox_inches='tight')
plt.close(fig)
print("  ✓ 06_improvement_detailed.png")

# ===== RÉSUMÉ =====
print("\n" + "=" * 60)
print("RÉSUMÉ DES AMÉLIORATIONS")
print("=" * 60)

print("\nAméliorations PDR par distance:")
print("-" * 80)
print(f"{'Distance':<12} {'Standard':<12} {'DDQN':<12} {'Écart (pts)':<15} {'Amélioration':<15}")
print("-" * 80)

for _, row in df_discrete.iterrows():
    dist = int(row['distance_m'])
    std = row['std_pdr']
    ddqn = row['ddqn_pdr']
    ecart = ddqn - std
    pct = (ecart / std * 100) if std > 0 else 0
    
    symbol = "✅" if ecart > 0 else "⚠️" if ecart < 0 else "➡️"
    print(f"{dist:<12} {std:<12.2f} {ddqn:<12.2f} {ecart:>+8.2f} pts   {pct:>+6.1f}%   {symbol}")

print("-" * 80)

# Statistiques globales
print(f"\nStatistiques globales:")
print(f"  • Amélioration moyenne: {improvement_pts.mean():+.2f} pts ({improvement_pct.mean():+.1f}%)")
print(f"  • Meilleure amélioration: +{improvement_pts.max():.1f} pts à {int(df_discrete.loc[improvement_pts.idxmax(), 'distance_m'])}m")
print(f"  • Pire performance: {improvement_pts.min():+.1f} pts à {int(df_discrete.loc[improvement_pts.idxmin(), 'distance_m'])}m")
print(f"  • Nombre de distances améliorées: {(improvement_pts > 0).sum()}/{len(improvement_pts)}")

print("\n" + "=" * 60)
print("GÉNÉRATION TERMINÉE!")
print("=" * 60)
print("\n6 fichiers créés dans 'figures_discretes/' :")
print("  01_pdr_discret.png           - Courbe PDR avec points discrets")
print("  02_pdr_bars_discret.png      - Barres PDR avec écarts")
print("  03_tableau_valeurs.png       - Tableau de valeurs détaillé")
print("  04_energy_discret.png        - Énergie par CR")
print("  05_power_discret.png         - Puissance TX")
print("  06_improvement_detailed.png  - Amélioration PDR détaillée")