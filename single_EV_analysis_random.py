import numpy as np 
import scipy
import time
import matplotlib.pyplot as plt
from C02_emissions import calculate_schedule_emissions
from single_EV_problem import single_EV_water_filling, single_EV_linprogram, single_EV_MILP 
from mpl_toolkits.mplot3d import Axes3D

def get_performance(load, arrival, departure, energy_need, max_power) :
        start_time = time.time()
        water_filling_schedule = single_EV_water_filling(load, arrival, departure, energy_need, max_power, max_power/100)
        water_filling_emissions = calculate_schedule_emissions(load + water_filling_schedule)
        water_filling_time = time.time() - start_time

        start_time = time.time()
        linprog_result = single_EV_linprogram(load, arrival, departure, energy_need, max_power)
        linprog_emissions = calculate_schedule_emissions(load + linprog_result.x)
        linprog_time = time.time() - start_time

        start_time = time.time()
        MILP_result = single_EV_MILP(load, arrival, departure, energy_need, max_power)
        MILP_emissions = calculate_schedule_emissions(load + MILP_result)
        MILP_time = time.time() - start_time

        return (water_filling_emissions, water_filling_time), (linprog_emissions, linprog_time), (MILP_emissions, MILP_time)

N_points = 20
energies = np.logspace(1, 4, N_points)  # from 10 Wh to 100 kWh

multipliers = [2,4] #various power/energy ratios

emissions = np.zeros((N_points, len(multipliers), 3))  # 3 for WF, LP, MILP

average_constant = 200 #average over several random profiles for stable results
for i in range(len(energies)) :
    for m in range(len(multipliers)) :
        for a in range(average_constant) :
            power = energies[i] * multipliers[m]
            #print(f"Testing with energy need: {energies[i]} Wh and max power: {power} W")
            arrival = 36
            departure = 14
            load = np.random.rand(48)*110000 #random load profile for testing, including peak hours
            (WF_em, WF_time), (LP_em, LP_time), (MILP_em, MILP_time) = get_performance(load, arrival, departure, energies[i], power)
            emissions[i, m, 0] += WF_em
            emissions[i, m, 1] += LP_em
            emissions[i, m, 2] += MILP_em
    print(f"Completed energy level {i+1}/{N_points}")

emissions /= average_constant

fig, axes = plt.subplots(1, len(multipliers), figsize=(15, 4))

for m in range(len(multipliers)):
    ax = axes[m]
    scaler = 10000000 #for better vizualization of the difference between methods, since it's often very small compared to total emissions
    ax.plot(energies, scaler*((emissions[:, m, 0] - emissions[:,m,0])/(emissions[:,m,0] + 1e-10)), 'o-', label='Water-Filling', color='blue')
    ax.plot(energies, scaler*((emissions[:, m, 1] - emissions[:,m,0])/(emissions[:,m,0] + 1e-10)), 's-', label='Linear Programming', color='orange')
    ax.plot(energies, scaler*((emissions[:, m, 2] - emissions[:,m,0])/(emissions[:,m,0] + 1e-10)), '^-', label='MILP', color='red')
    ax.set_xscale('log')
    ax.set_yscale('asinh')
    ax.set_xlabel('Energy need [kWh]')
    ax.set_ylabel('Emissions (no unit)')
    ax.set_title(f'Minimum charging time : {multipliers[m]}h')
    ax.legend()
    ax.grid(True, alpha=0.3)
plt.suptitle('Emissions of the charge of a single vehicle for different max power/energy ratios.  \n (Water-filling baseline asinh scale, zoomed in for better visibility)')
plt.tight_layout()
plt.show()






# N_points = 15
# energies = np.logspace(1, 5, N_points)  
# powers = np.logspace(0.7, 4.7, N_points)

# print(energies)
# print(powers)

# times = np.zeros((N_points, N_points, 3))  # 3 for WF, LP, MILP


# average_constant = 50 #average over several random profiles for stable results
# for i in range(average_constant) :
#     for e in range(len(energies)) :
#         for p in range(len(powers)) :
#             if energies[e] < powers[p] * 10 :
#                 arrival = 36
#                 departure = 14
#                 load = np.random.rand(48)*110000 #random load profile for testing, including peak hours
#                 #print(f"Testing with energy need: {e} Wh and max power: {p} W")
#                 (WF_em, WF_time), (LP_em, LP_time), (MILP_em, MILP_time) = get_performance(load, arrival, departure, energies[e], powers[p])
#                 times[e, p, 0] += WF_time
#                 times[e, p, 1] += LP_time
#                 times[e, p, 2] += MILP_time
#                 emissions[e, p, 0] += WF_em
#                 emissions[e, p, 1] += LP_em
#                 emissions[e, p, 2] += MILP_em
#                 # print(f"Water-filling: Emissions = {WF_em:.4f} TCO2, Time = {WF_time:.2f} s")
#                 # print(f"Linear Programming: Emissions = {LP_em:.4f} TCO2, Time = {LP_time:.2f} s")
#                 # print(f"MILP: Emissions = {MILP_em:.4f} TCO2, Time = {MILP_time:.2f} s")
#     print(f"Completed iteration {i+1}/{average_constant}")
# times /= average_constant
# emissions /= average_constant

# #plotting results
# fig = plt.figure(figsize=(14, 5))

# # 3D plot for times
# ax1 = fig.add_subplot(121, projection='3d')
# E, P = np.meshgrid(energies, powers)
# for i, method in enumerate(['Water-Filling', 'Linear Programming', 'MILP']):
#     ax1.plot_wireframe(np.log10(E), np.log10(P), np.log10(times[:, :, i].T), label=method, color=['blue', 'orange', 'red'][i])
# ax1.set_xlabel('log10(Energy [Wh])')
# ax1.set_ylabel('log10(Power [W])')
# ax1.set_zlabel('log10(Time [s])')
# ax1.set_title('Computation Times')
# ax1.legend()

# # 3D plot for emissions
# ax2 = fig.add_subplot(122, projection='3d')
# for i, method in enumerate(['Water-Filling', 'Linear Programming', 'MILP']):
#     ax2.plot_wireframe(np.log10(E), np.log10(P), np.asinh(1000000*(emissions[:, :, i].T - emissions[:,:,0].T)/emissions[:,:,0].T), label=method, color=['blue', 'orange', 'red'][i])
# ax2.set_zscale('asinh')
# ax2.set_xlabel('log10(Energy [Wh])')
# ax2.set_ylabel('log10(Power [W])')
# ax2.set_zlabel('Emissions [TCO2] (water-filling baseline, symlog scale)')
# ax2.set_title('Emissions')
# ax2.legend()
# plt.tight_layout()
# plt.show()
    