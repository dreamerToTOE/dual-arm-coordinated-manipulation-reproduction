#!/usr/bin/env python3
"""Render clearer Fig.3 labels from saved CSV only; no scientific modules."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--input', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
a=p.parse_args()
t0=time.perf_counter();c0=time.process_time()
a.output.mkdir(exist_ok=False)
rows=list(csv.DictReader((a.input/'visibility_by_distance.csv').open()))
ms=[1,2,3,7,16]
last=max(int(r['bin_id']) for r in rows if int(r['pair_count']))
fig,axes=plt.subplots(2,1,figsize=(10,8),sharex=True)
for m in ms:
 g=[r for r in rows if int(r['m'])==m and int(r['bin_id'])<=last]
 x=[(float(r['bin_left_rad'])+float(r['bin_right_rad']))/2 for r in g]
 def v(key):return [float(r[key]) if r[key] else float('nan') for r in g]
 line,=axes[0].plot(x,v('existential_rate'),marker='o',label=f'm={m}')
 if any(int(r['existential_unknown_count']) for r in g):
  axes[0].plot(x,v('existential_rate_upper'),ls=':',color=line.get_color(),label=f'm={m} upper')
 axes[1].plot(x,v('bounded_rate'),marker='o',label=f'm={m}')
for ax in axes:
 ax.set_ylim(-.03,1.04);ax.set_ylabel('Local visibility (fixed pair population)')
 ax.grid(alpha=.25);ax.legend(loc='center left',bbox_to_anchor=(.01,.5),ncol=5,fontsize=9)
axes[0].set_title('Exhaustive per-chart availability: same cached candidates')
axes[1].set_title('Actual bounded PCS: 512 midpoint projections shared across charts')
for r in rows:
 if int(r['m'])==1 and int(r['pair_count']):
  axes[1].annotate(f'n={r["pair_count"]}',((float(r['bin_left_rad'])+float(r['bin_right_rad']))/2,.015),
                   rotation=90,fontsize=8,va='bottom',ha='center')
axes[1].set_xlabel('Euclidean joint distance (rad); fixed 0.3-rad bins')
fig.text(.5,.015,'180 frozen pairs from saved trajectories; descriptive finite-population rates, no confidence claim.',ha='center',fontsize=9)
fig.tight_layout(rect=[0,.04,1,1])
fig.savefig(a.output/'fig3_controlled_visibility_by_distance.png',dpi=200)
plt.close(fig)
# Keep the already verified m/cost panel identical; this script only repairs labels.
import shutil
shutil.copyfile(a.input/'plots/fig3_controlled_visibility_and_local_cost_by_m.png',
                a.output/'fig3_controlled_visibility_and_local_cost_by_m.png')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
meta={'scope':'saved CSV plotting only; no math/model/IK/NR/RBS/collision/planner imports or calls',
 'source_csv_sha256':sha(a.input/'visibility_by_distance.csv'),'script_sha256':sha(Path(__file__)),
 'wall_sec':time.perf_counter()-t0,'cpu_sec':time.process_time()-c0,
 'images':{x.name:sha(x) for x in a.output.glob('*.png')}}
with (a.output/'render_metadata.json').open('x') as f:json.dump(meta,f,indent=2);f.write('\n')
print(json.dumps(meta))
