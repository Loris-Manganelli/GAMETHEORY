import pandas as pd
import numpy as np
import seaborn as sns
from datetime import datetime
import time
from pathlib import Path
from best_response import bestResponseDynamics
from reference_stategies import StandardStrategy, OffPeakStrategy
from C02_emissions import calculate_co2_emissions
import matplotlib.pyplot as plt
from data_extractor import data_extractor

# Assuming you have these modules in your project
# Adjust imports based on your actual project structure

# Set style for beautiful plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 10)

np.random.seed(0)
J = 10 # nombre de VE
timeSlots = 48 # nombre de créneaux temporels
initialProfile = np.random.rand(J, timeSlots) # profil initial aléatoire
idList = np.random.randint(1, 10, size=J)  # liste des identifiants des VE
date = datetime(2019, 1, 1).date() # date choisie
eta = 1e-2
K = 100

data = data_extractor(date, idList)

results = {}
computation_times = {}
co2_emissions = {}

# Run Standard Strategy
print("\nRunning Standard Strategy...")
start_time = time.time()
standard_result = StandardStrategy(data, max_power=7)
computation_times['Standard'] = time.time() - start_time
co2_emissions['Standard'] = calculate_co2_emissions(standard_result)
results['Standard'] = standard_result
print(f"  Computation time: {computation_times['Standard']:.4f}s")

# Run OffPeak Strategy
print("Running OffPeak Strategy...")
start_time = time.time()
offpeak_result = OffPeakStrategy(data, max_power=7)
computation_times['OffPeak'] = time.time() - start_time
co2_emissions['OffPeak'] = calculate_co2_emissions(offpeak_result)
results['OffPeak'] = offpeak_result
print(f"  Computation time: {computation_times['OffPeak']:.4f}s")

# Run Best Response Dynamics with three methods
print("Running Best Response Dynamics with all methods...")
methods = ['MILP', 'LP', 'WF']

for method in methods:
    print(f"  Running with {method}...")
    start_time = time.time()
    brd_result = bestResponseDynamics(initialProfile, data, eta, K, single_EV_method=method)
    computation_times[f'BRD_{method}'] = time.time() - start_time
    co2_emissions[f'BRD_{method}'] = calculate_co2_emissions(brd_result)
    results[f'BRD_{method}'] = brd_result
    print(f"    Computation time: {computation_times[f'BRD_{method}']:.4f}s")

# Create comparison visualizations
print("\nCreating visualizations...")
fig = plt.figure(figsize=(16, 12))

# Plot 1: Computation Time Comparison
ax1 = plt.subplot(2, 3, 1)
strategies = list(computation_times.keys())
times = list(computation_times.values())
colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA15E']
bars1 = ax1.bar(strategies, times, color=colors)
ax1.set_ylabel('Time (seconds)', fontsize=11, fontweight='bold')
ax1.set_title('Computation Time Comparison', fontsize=12, fontweight='bold')
ax1.tick_params(axis='x', rotation=45)

# Add value labels on bars
for bar in bars1:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.4f}s', ha='center', va='bottom', fontsize=9)

# Plot 2: CO2 Emissions Comparison
ax2 = plt.subplot(2, 3, 2)
emissions = list(co2_emissions.values())
bars2 = ax2.bar(strategies, emissions, color=colors)
ax2.set_ylabel('CO2 Emissions (kg)', fontsize=11, fontweight='bold')
ax2.set_title('CO2 Emissions Comparison', fontsize=12, fontweight='bold')
ax2.tick_params(axis='x', rotation=45)

for bar in bars2:
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.2f}', ha='center', va='bottom', fontsize=9)

# Plot 3: Time vs Emissions Scatter
ax3 = plt.subplot(2, 3, 3)
scatter = ax3.scatter(times, emissions, s=300, alpha=0.6, c=range(len(strategies)), cmap='viridis')
for i, strategy in enumerate(strategies):
    ax3.annotate(strategy, (times[i], emissions[i]), fontsize=9, ha='center')
ax3.set_xlabel('Computation Time (seconds)', fontsize=11, fontweight='bold')
ax3.set_ylabel('CO2 Emissions (kg)', fontsize=11, fontweight='bold')
ax3.set_title('Time vs Emissions Trade-off', fontsize=12, fontweight='bold')
ax3.grid(True, alpha=0.3)

# Plot 4: Normalized comparison
ax4 = plt.subplot(2, 3, 4)
norm_times = np.array(times) / max(times) * 100
norm_emissions = np.array(emissions) / max(emissions) * 100
x_pos = np.arange(len(strategies))
width = 0.35
ax4.bar(x_pos - width/2, norm_times, width, label='Time', color='#FF6B6B', alpha=0.8)
ax4.bar(x_pos + width/2, norm_emissions, width, label='Emissions', color='#4ECDC4', alpha=0.8)
ax4.set_ylabel('Normalized Score (%)', fontsize=11, fontweight='bold')
ax4.set_title('Normalized Performance (Higher is Better)', fontsize=12, fontweight='bold')
ax4.set_xticks(x_pos)
ax4.set_xticklabels(strategies, rotation=45)
ax4.legend()

# Plot 5: Summary Statistics Table
ax5 = plt.subplot(2, 3, 5)
ax5.axis('tight')
ax5.axis('off')

summary_data = []
for i, strategy in enumerate(strategies):
    summary_data.append([
        strategy,
        f'{times[i]:.4f}s',
        f'{emissions[i]:.2f}kg',
        f'{norm_times[i]:.1f}%',
        f'{norm_emissions[i]:.1f}%'
    ])

table = ax5.table(cellText=summary_data,
                    colLabels=['Strategy', 'Time', 'CO2', 'Time%', 'CO2%'],
                    cellLoc='center',
                    loc='center',
                    colWidths=[0.25, 0.15, 0.15, 0.15, 0.15])
table.auto_set_font_size(False)
table.set_fontsize(9)
table.scale(1, 2)
ax5.set_title('Summary Statistics', fontsize=12, fontweight='bold', pad=20)

# Plot 6: Efficiency Score (Lower Time + Lower Emissions)
ax6 = plt.subplot(2, 3, 6)
efficiency_scores = (norm_times + norm_emissions) / 2
bars6 = ax6.barh(strategies, efficiency_scores, color=colors)
ax6.set_xlabel('Efficiency Score (Lower is Better)', fontsize=11, fontweight='bold')
ax6.set_title('Overall Efficiency', fontsize=12, fontweight='bold')

for i, bar in enumerate(bars6):
    width = bar.get_width()
    ax6.text(width, bar.get_y() + bar.get_height()/2.,
            f'{width:.1f}', ha='left', va='center', fontsize=9, fontweight='bold')

plt.tight_layout()

# Save figure
output_path = Path(__file__).parent / 'performance_comparison_results.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Comparison plots saved to {output_path}")

# Print summary
print("\n" + "="*60)
print("PERFORMANCE COMPARISON SUMMARY (Jan 01 2019, 50 EVs)")
print("="*60)
for strategy in strategies:
    print(f"\n{strategy}:")
    print(f"  Computation Time: {computation_times[strategy]:.4f}s")
    print(f"  CO2 Emissions: {co2_emissions[strategy]:.2f}kg")

plt.show()

