# coding: utf-8
"""Regenerate charts from published observations; no causal model is fitted."""
from pathlib import Path
import json,os
os.environ.setdefault('MPLCONFIGDIR','/tmp/ira-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter
D=Path(__file__).resolve().parents[1]/'ira/impact'
rows=json.loads((D/'observations.json').read_text())
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#bbc7d1','text.color':'#17324a','axes.labelcolor':'#17324a','svg.fonttype':'none'})
fig,ax=plt.subplots(figsize=(10,4.5),layout='constrained')
v=[r['value'] for r in rows if r['series']=='IONIQ 5' and len(r['period'])==7 and r['period'].startswith('2022-')]
assert len(v)==7
ax.plot(range(6,13),v,'o-',color='#177f87',lw=3)
for x,y in zip(range(6,13),v):ax.annotate(f'{y:,}',(x,y),xytext=(0,12),textcoords='offset points',ha='center')
ax.axvline(8.5,color='#b4762c',ls='--',label='IRA enacted: Aug 16 (within August)')
# Monthly observations are positioned at month midpoints; put event at August marker.
ax.lines[-1].set_xdata([8,8])
ax.set(xticks=range(6,13),xticklabels=['Jun','Jul','Aug','Sep','Oct','Nov','Dec'],ylim=(0,3400),ylabel='US sales (units)',title='IONIQ 5 | Monthly sales, 2022')
ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'));ax.grid(axis='y',alpha=.18);ax.legend(frameon=False,loc='upper right')
fig.savefig(D/'monthly.svg');plt.close(fig)
fig,ax=plt.subplots(figsize=(10,4.5),layout='constrained')
for name,color in [('IONIQ 5','#147f88'),('IONIQ 6','#7696b1'),('EV6','#b47e2a'),('EV9','#725695')]:
 r=[r for r in rows if r['series']==name and len(r['period'])==4]
 ax.plot([int(a['period']) for a in r],[a['value'] for a in r],'o-',color=color,lw=2.5,label=name)
ax.set(xticks=[2022,2023,2024,2025],ylim=(0,55000),ylabel='US sales (units)',title='Hyundai / Kia | Annual model sales')
ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'));ax.grid(axis='y',alpha=.18);ax.legend(frameon=False,ncol=4,loc='upper left')
fig.savefig(D/'annual.svg');plt.close(fig)
print('2 SVG charts generated')
