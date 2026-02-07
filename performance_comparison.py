import pandas as pd
import numpy as np
import seaborn as sns
from datetime import datetime
import time
from pathlib import Path
from best_response import bestResponseDynamics
from reference_stategies import standard_strategy_collective, offpeak_strategy_collective
from C02_emissions import calculate_emissions
import matplotlib.pyplot as plt
from data_extractor import data_extractor

# Assuming you have these modules in your project
# Adjust imports based on your actual project structure

# Set style for beautiful plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 10)

np.random.seed(0)

#### Parametres à choisir
J = 30 # nombre de VE
date = datetime(2019, 6, 30).date() # date choisie
powerMultiplicator = 750
###

timeSlots = 48 # nombre de créneaux temporels
initialProfile = np.random.rand(J, timeSlots) # profil initial aléatoire
idList = np.random.randint(1, 10, size=J)  # liste des identifiants des VE
eta = 1e-2
K = 100

data = data_extractor(date, idList)
data['energy_need'] = data['energy_need'] * powerMultiplicator

results = {}
computation_times = {}
co2_emissions = {}

# Run Standard Strategy
print("\nRunning Standard Strategy...")
start_time = time.time()
standard_result = standard_strategy_collective(data, max_power=7*powerMultiplicator)
computation_times['Standard'] = time.time() - start_time
co2_emissions['Standard'] = sum(calculate_emissions(data['fixedLoad'][i] + standard_result[:,i].sum()) - calculate_emissions(data['fixedLoad'][i]) for i in range(48))
results['Standard'] = standard_result
print(f"  Computation time: {computation_times['Standard']:.4f}s")

# Run OffPeak Strategy
print("Running OffPeak Strategy...")
start_time = time.time()
offpeak_result = offpeak_strategy_collective(data, max_power=7*powerMultiplicator)
computation_times['OffPeak'] = time.time() - start_time 
co2_emissions['OffPeak'] = sum(calculate_emissions(data['fixedLoad'][i] + offpeak_result[:,i].sum()) - calculate_emissions(data['fixedLoad'][i]) for i in range(48))
results['OffPeak'] = offpeak_result
print(f"  Computation time: {computation_times['OffPeak']:.4f}s")

# Run Best Response Dynamics with three methods
print("Running Best Response Dynamics with all methods...")
methods = ['WF']

for method in methods:
    print(f"  Running with {method}...")
    start_time = time.time()
    brd_result = bestResponseDynamics(initialProfile, data, eta, K, single_EV_method=method, powerMultiplicator=powerMultiplicator)
    computation_times[f'BRD_{method}'] = time.time() - start_time
    co2_emissions[f'BRD_{method}'] = sum(calculate_emissions(data['fixedLoad'][i] + brd_result[:,i].sum()) - calculate_emissions(data['fixedLoad'][i]) for i in range(48))
    results[f'BRD_{method}'] = brd_result
    print(f"    Computation time: {computation_times[f'BRD_{method}']:.4f}s")

# Create comparison visualizations
print("\nCreating visualizations...")
fig = plt.figure(figsize=(16, 12))

# Plot 1: Computation Time Comparison
ax1 = plt.subplot(1, 3, 1)
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
ax2 = plt.subplot(1, 3, 2)
emissions = list(co2_emissions.values())
bars2 = ax2.bar(strategies, emissions, color=colors)
ax2.set_ylabel('CO2 Emissions (TCO2)', fontsize=11, fontweight='bold')
ax2.set_title('CO2 Emissions Comparison', fontsize=12, fontweight='bold')
ax2.tick_params(axis='x', rotation=45)

for bar in bars2:
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.2f}', ha='center', va='bottom', fontsize=9)

# Plot 3: Time vs Emissions Scatter
ax3 = plt.subplot(1, 3, 3)
scatter = ax3.scatter(times, emissions, s=300, alpha=0.6, c=range(len(strategies)), cmap='viridis')
for i, strategy in enumerate(strategies):
    ax3.annotate(strategy, (times[i], emissions[i]), fontsize=9, ha='center')
ax3.set_xlabel('Computation Time (seconds)', fontsize=11, fontweight='bold')
ax3.set_ylabel('CO2 Emissions (TCO2)', fontsize=11, fontweight='bold')
ax3.set_title('Time vs Emissions Trade-off', fontsize=12, fontweight='bold')
ax3.grid(True, alpha=0.3)

plt.suptitle(f'Performance Comparison of EV Charging Strategies, day : {date}, number of EVs: {J}, power multiplier: {powerMultiplicator}', fontsize=14, fontweight='bold')



# Create three separate figures for load profiles
fig_standard = plt.figure(figsize=(14, 6))
ax_std = fig_standard.add_subplot(111)
fixed_load = data['fixedLoad']
ev_load_standard = results['Standard'].sum(axis=0)
ax_std.plot(fixed_load, label='Fixed Load', linewidth=2, color='#FF6B6B')
ax_std.plot(fixed_load + ev_load_standard, label='Fixed Load + EV Load (Standard)', linewidth=2, color='#4ECDC4')
ax_std.fill_between(range(timeSlots), fixed_load, fixed_load + ev_load_standard, alpha=0.2, color='#4ECDC4')
ax_std.set_xlabel('Time Slot', fontsize=11, fontweight='bold')
ax_std.set_ylabel('Load (kW)', fontsize=11, fontweight='bold')
ax_std.set_title('Load Profile - Standard Strategy', fontsize=12, fontweight='bold')
ax_std.legend(fontsize=10)
ax_std.grid(True, alpha=0.3)
fig_standard.tight_layout()


fig_offpeak = plt.figure(figsize=(14, 6))
ax_off = fig_offpeak.add_subplot(111)
ev_load_offpeak = results['OffPeak'].sum(axis=0)
ax_off.plot(fixed_load, label='Fixed Load', linewidth=2, color='#FF6B6B')
ax_off.plot(fixed_load + ev_load_offpeak, label='Fixed Load + EV Load (OffPeak)', linewidth=2, color='#45B7D1')
ax_off.fill_between(range(timeSlots), fixed_load, fixed_load + ev_load_offpeak, alpha=0.2, color='#45B7D1')
ax_off.set_xlabel('Time Slot', fontsize=11, fontweight='bold')
ax_off.set_ylabel('Load (kW)', fontsize=11, fontweight='bold')
ax_off.set_title('Load Profile - OffPeak Strategy', fontsize=12, fontweight='bold')
ax_off.legend(fontsize=10)
ax_off.grid(True, alpha=0.3)
fig_offpeak.tight_layout()


fig_brd = plt.figure(figsize=(14, 6))
ax_brd = fig_brd.add_subplot(111)
ev_load_brd = results['BRD_WF'].sum(axis=0)
ax_brd.plot(fixed_load, label='Fixed Load', linewidth=2, color='#FF6B6B')
ax_brd.plot(fixed_load + ev_load_brd, label='Fixed Load + EV Load (BRD WF)', linewidth=2, color='#96CEB4')
ax_brd.fill_between(range(timeSlots), fixed_load, fixed_load + ev_load_brd, alpha=0.2, color='#96CEB4')
ax_brd.set_xlabel('Time Slot', fontsize=11, fontweight='bold')
ax_brd.set_ylabel('Load (kW)', fontsize=11, fontweight='bold')
ax_brd.set_title('Load Profile - Best Response Dynamics (WF)', fontsize=12, fontweight='bold')
ax_brd.legend(fontsize=10)
ax_brd.grid(True, alpha=0.3)
fig_brd.tight_layout()



plt.show()