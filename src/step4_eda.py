import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

os.makedirs('reports/figures', exist_ok=True)

# ── LOAD ─────────────────────────────────────────────────
df = pd.read_csv('data/processed/eb_consumption.csv')

# ── TASK 2: CLEAN ────────────────────────────────────────
clean = df.copy()

clean['bill_date'] = pd.to_datetime(clean['bill_date'], format='%d/%m/%Y')
clean['due_date']  = pd.to_datetime(clean['due_date'],  format='%d/%m/%Y')

clean['initial_reading_kwh'] = pd.to_numeric(clean['initial_reading_kwh'], errors='coerce')
clean['energy_charge_rs']    = pd.to_numeric(clean['energy_charge_rs'],    errors='coerce')
clean['fixed_charge_rs']     = pd.to_numeric(clean['fixed_charge_rs'],     errors='coerce')

clean = clean.sort_values('bill_date').reset_index(drop=True)

# Derive initial readings from the final reading sequence
clean['initial_reading_derived'] = [np.nan, 12985.0, 15659.0, 16570.0, 17183.0]

# Derived units = this final - previous final
clean['units_derived'] = clean['final_reading_kwh'].diff()

# Best-estimate units:
#   Feb  : 414  — OCR only (no prior reading)
#   Apr  : 774  — OCR (derived 2674 implies missing March bill)
#   Jun  : 911  — derived (Oct confirms derived method; OCR 711 likely 9->7 error)
#   Aug  : 613  — derived (Oct confirms; OCR 813 likely 6->8 error)
#   Oct  : 890  — CONFIRMED (OCR == derived)
clean['units_best_estimate'] = [414, 774, 911, 613, 890]

clean['data_quality_flag'] = [
    'OCR estimated; no prior reading in dataset',
    'OCR estimated; derived units (2674) suggest missing March 2026 bill',
    'Derived from final readings; OCR artifact (711 likely = 911)',
    'Derived from final readings; OCR artifact (813 likely = 613)',
    'CONFIRMED: OCR and derived both = 890'
]

clean_out = clean.drop(columns=['units_source'])
clean_out.to_csv('data/processed/eb_consumption_cleaned.csv', index=False)
print('Cleaned CSV saved.')

# ── TASK 3: EDA ──────────────────────────────────────────
months  = clean['billing_month'].tolist()
units   = clean['units_best_estimate'].tolist()
amounts = clean['net_payable_rs'].tolist()

print('\n=== EDA SUMMARY ===')
print(f'Records          : {len(clean)}')
print(f'Date range       : {clean["bill_date"].min().strftime("%b %Y")} to {clean["bill_date"].max().strftime("%b %Y")}')
print(f'Total units      : {sum(units)} kWh')
print(f'Average units    : {np.mean(units):.1f} kWh/cycle')
print(f'Highest cycle    : {months[units.index(max(units))]} ({max(units)} kWh)')
print(f'Lowest cycle     : {months[units.index(min(units))]} ({min(units)} kWh)')
print(f'Total amount     : Rs {sum(amounts):,.2f}')
print(f'Average amount   : Rs {np.mean(amounts):,.2f}/cycle')
print(f'Max bill         : {months[amounts.index(max(amounts))]} (Rs {max(amounts):,.2f})')
print(f'Min bill         : {months[amounts.index(min(amounts))]} (Rs {min(amounts):,.2f})')

print('\nCycle-wise breakdown:')
for i in range(len(months)):
    u_chg = '' if i == 0 else f' ({units[i]-units[i-1]:+d})'
    a_chg = '' if i == 0 else f' ({amounts[i]-amounts[i-1]:+.0f})'
    print(f'  {months[i]:<18}: {units[i]:>4} kWh{u_chg:<10}  Rs {amounts[i]:>7,.2f}{a_chg}')

# ── TASK 4: CHARTS ────────────────────────────────────────
short_months  = ['Feb 26', 'Apr 26', 'Jun 26', 'Aug 26', 'Oct 26']
colors_units  = ['#42A5F5', '#FF9800', '#EF5350', '#EF5350', '#AB47BC']
colors_amount = ['#66BB6A', '#FFA726', '#EF5350', '#EF5350', '#7B1FA2']

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10})

# Chart 1 — Units by billing cycle (bar)
fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.bar(short_months, units, color=colors_units, edgecolor='white', linewidth=0.8, width=0.55)
for bar, val in zip(bars, units):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 8,
            f'{val} kWh', ha='center', va='bottom', fontsize=9, fontweight='bold')
ax.set_title('Electricity Consumption by Billing Cycle (2026)', fontsize=13, fontweight='bold', pad=12)
ax.set_xlabel('Billing Cycle', labelpad=8)
ax.set_ylabel('Units Consumed (kWh)', labelpad=8)
ax.set_ylim(0, max(units) * 1.18)
ax.yaxis.set_major_locator(mticker.MultipleLocator(100))
ax.grid(axis='y', linestyle='--', alpha=0.4)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
fig.tight_layout()
fig.savefig('reports/figures/chart1_units_by_cycle.png', dpi=150, bbox_inches='tight')
plt.close()
print('\nChart 1 saved: reports/figures/chart1_units_by_cycle.png')

# Chart 2 — Bill amount by billing cycle (bar)
fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.bar(short_months, amounts, color=colors_amount, edgecolor='white', linewidth=0.8, width=0.55)
for bar, val in zip(bars, amounts):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 30,
            f'Rs {val:,.0f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
ax.set_title('Bill Amount by Billing Cycle (2026)', fontsize=13, fontweight='bold', pad=12)
ax.set_xlabel('Billing Cycle', labelpad=8)
ax.set_ylabel('Net Payable (Rs)', labelpad=8)
ax.set_ylim(0, max(amounts) * 1.18)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'Rs {x:,.0f}'))
ax.grid(axis='y', linestyle='--', alpha=0.4)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
fig.tight_layout()
fig.savefig('reports/figures/chart2_amount_by_cycle.png', dpi=150, bbox_inches='tight')
plt.close()
print('Chart 2 saved: reports/figures/chart2_amount_by_cycle.png')

# Chart 3 — Consumption trend (line)
fig, ax = plt.subplots(figsize=(9, 5))
x = range(len(short_months))
ax.plot(list(x), units, color='#1565C0', linewidth=2.5,
        marker='o', markersize=9, markerfacecolor='white', markeredgewidth=2.2)
for i, (m, u) in enumerate(zip(short_months, units)):
    ax.annotate(f'{u} kWh', (i, u), textcoords='offset points',
                xytext=(0, 11), ha='center', fontsize=9, color='#1565C0', fontweight='bold')
ax.fill_between(list(x), units, alpha=0.08, color='#1565C0')
ax.set_xticks(list(x))
ax.set_xticklabels(short_months)
ax.set_title('Electricity Consumption Trend (Feb - Oct 2026)', fontsize=13, fontweight='bold', pad=12)
ax.set_xlabel('Billing Cycle', labelpad=8)
ax.set_ylabel('Units Consumed (kWh)', labelpad=8)
ax.set_ylim(0, max(units) * 1.22)
ax.grid(axis='y', linestyle='--', alpha=0.4)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
fig.tight_layout()
fig.savefig('reports/figures/chart3_consumption_trend.png', dpi=150, bbox_inches='tight')
plt.close()
print('Chart 3 saved: reports/figures/chart3_consumption_trend.png')

# Chart 4 — Units vs Amount dual-axis comparison (grouped bar)
fig, ax1 = plt.subplots(figsize=(10, 5))
xpos = list(range(len(short_months)))
w = 0.38
bars1 = ax1.bar([i - w/2 for i in xpos], units, width=w,
                color='#1E88E5', label='Units (kWh)', alpha=0.85)
ax2 = ax1.twinx()
bars2 = ax2.bar([i + w/2 for i in xpos], amounts, width=w,
                color='#E53935', label='Bill Amount (Rs)', alpha=0.85)
ax1.set_xticks(xpos)
ax1.set_xticklabels(short_months)
ax1.set_xlabel('Billing Cycle', labelpad=8)
ax1.set_ylabel('Units Consumed (kWh)', color='#1E88E5', labelpad=8)
ax2.set_ylabel('Net Payable (Rs)', color='#E53935', labelpad=8)
ax1.tick_params(axis='y', labelcolor='#1E88E5')
ax2.tick_params(axis='y', labelcolor='#E53935')
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'Rs {x:,.0f}'))
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', framealpha=0.9)
ax1.set_title('Consumption vs Bill Amount — Side-by-Side Comparison (2026)',
              fontsize=12, fontweight='bold', pad=12)
ax1.spines['top'].set_visible(False)
ax2.spines['top'].set_visible(False)
fig.tight_layout()
fig.savefig('reports/figures/chart4_units_vs_amount.png', dpi=150, bbox_inches='tight')
plt.close()
print('Chart 4 saved: reports/figures/chart4_units_vs_amount.png')

# Print cleaned CSV preview
print('\n=== CLEANED CSV PREVIEW ===')
preview_cols = ['billing_month','bill_date','final_reading_kwh',
                'units_best_estimate','units_derived','net_payable_rs','data_quality_flag']
print(clean_out[preview_cols].to_string())

print('\nAll Step 4 tasks complete.')
