"""Append one settled own-cost execution and preserve every previous coverage cell."""
from pathlib import Path
import argparse,csv,hashlib,json,math
R=Path(__file__).resolve().parents[3]
O=Path('/home/ubuntu2004/Documents/Codex/2026-10-15/codex-p4-https-github-com-dreamertotoe/outputs')
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def new(p,v):
 with p.open('x')as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
a=argparse.ArgumentParser();a.add_argument('--version',type=int,required=True);a.add_argument('--execution',required=True);a.add_argument('--old-csv',required=True);a.add_argument('--stem',required=True);a.add_argument('--scope',required=True);a.add_argument('--status',required=True);a.add_argument('--engineering',action='store_true');x=a.parse_args()
op=R/f'results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V{x.version-1}.json';old=load(op);ep=R/x.execution;e=load(ep)
assert x.execution not in {v['execution']for v in old['executions']}
for v in old['executions']:assert sha(R/v['execution'])==v['execution_sha256']
entry=dict(run_id=e['run_id'],execution=x.execution,execution_sha256=sha(ep),source_commit=e['source_commit'],status=e['status'],classification=e['classification'],engineering_only=x.engineering,wall_s=e['wall_s'],cpu_s=e['cpu_s'],counts=e.get('counts',{}),authorization_budget_id=None,formal_planning_calls=0)
rows=sorted(old['executions']+[entry],key=lambda v:v['execution']);wall=math.fsum(v['wall_s']for v in rows);cpu=math.fsum(v['cpu_s']for v in rows)
actual={str(p.relative_to(R))for p in(R/'results/p4_full').glob('20261015_R2_*/execution.json')};assert actual=={v['execution']for v in rows}
sci=[v for v in rows if not v['engineering_only']];eng=[v for v in rows if v['engineering_only']]
lp=R/f'results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V{x.version}.json'
l={**old,'schema':f'P4_R2_RECOVERY_ACTUAL_LEDGER_V{x.version}','previous_snapshot':str(op.relative_to(R)),'previous_snapshot_sha256':sha(op),'executions':rows,'count':len(rows),'science_count':len(sci),'engineering_count':len(eng),'science_wall_s':math.fsum(v['wall_s']for v in sci),'science_cpu_s':math.fsum(v['cpu_s']for v in sci),'engineering_wall_s':math.fsum(v['wall_s']for v in eng),'engineering_cpu_s':math.fsum(v['cpu_s']for v in eng),'conservative_r2_sum_wall_s':wall,'conservative_r2_sum_cpu_s':cpu,'r2_remaining':{'wall_s':3600-wall,'cpu_s':7200-cpu},'scope':x.scope,'new_scientific_calls':0,'saved_only_analysis':True,'last_actual_execution':entry}
assert l['vi_B_remaining']['candidate_constructions']==0 and l['formal_table_I_calls']==0 and min(l['r2_remaining'].values())>0
with(R/x.old_csv).open(newline='')as f:rd=csv.DictReader(f);fields=rd.fieldnames;before=list(rd)
assert len(before)==211 and len({v['item_id']for v in before})==211
extra=[f'v{x.version}_status',f'v{x.version}_scope',f'v{x.version}_execution',f'v{x.version}_ledger'];assert not set(extra)&set(fields)
updated=[]
for row in before:
 v=dict(row);related=v['item_id']in {'P4-T05','P4-T08','P4-T09','P4-T11','P4-T12','P4-T17','P4-T25'}
 v.update(zip(extra,[x.status if related else'NO_NEW_EVIDENCE_FOR_THIS_OBLIGATION',x.scope if related else'本阶段本义务无新科学结论，原完整义务保持。',x.execution if related else'NOT_APPLICABLE',str(lp.relative_to(R))]));updated.append(v)
cp=R/f'reports/{x.stem}.csv';mp=cp.with_suffix('.md');new(lp,l)
with cp.open('x',newline='')as f:w=csv.DictWriter(f,fieldnames=fields+extra);w.writeheader();w.writerows(updated)
with cp.open(newline='')as f:assert [{k:v[k]for k in fields}for v in csv.DictReader(f)]==before
with mp.open('x')as f:
 f.write(f'# P4全文范围：{x.stem}\n\n211行前{len(fields)}列逐值保留，新增4列。{x.scope}\n\n{len(rows)}execution={len(sci)}科学账+{len(eng)}工程，自身成本各一次，wall{wall:.17g}/CPU{cpu:.17g}。VI974余0、正式0/22500。原500000投影/约50000点对、三方法三搜索器六环境、全部Fig3–5/TableI–II及消融不缩。不P2/Isaac。\n\n|ID|原完整义务|原规模|本次范围|\n|---|---|---|---|\n')
 for row in updated:f.write('|'+ '|'.join(str(row[k]).replace('|','\\|').replace('\n','<br>')for k in['item_id','original_requirement','original_repeats',extra[1]])+'|\n')
for p in[lp,cp,mp]:
 with(O/p.name).open('xb')as f:f.write(p.read_bytes())
print(json.dumps({'ledger':str(lp.relative_to(R)),'executions':len(rows),'science':len(sci),'engineering':len(eng),'wall_s':wall,'cpu_s':cpu,'columns':len(fields)+4}))
