#!/usr/bin/env python3
"""Read-only recovery of saved diagnosis: never imports/evaluates field or integrates."""
import hashlib,json,subprocess
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/20261014_P2_implicit_FD_diagnosis01'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(name,data):
 p=OUT/name
 if p.exists():raise FileExistsError('Original output must be preserved: '+str(p))
 p.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
rows=[]
for epsilon in (1e-6,2e-6,5e-7):
 z=np.load(OUT/('matrices_eps_'+format(epsilon,'.1e')+'.npz'));d=z['AD']-z['FD50'];ind=np.unravel_index(np.abs(d).argmax(),d.shape)
 rows.append({'epsilon':epsilon,'max_absolute_error':float(np.abs(d).max()),'max_index':[int(i) for i in ind],'AD_row9_col27':float(z['AD'][9,27]),'FD_row9_col27':float(z['FD50'][9,27]),'error_row9_col27':float(d[9,27]),'qualifying_epsilon':epsilon==1e-6})
ratios={'double_epsilon_error_ratio':rows[1]['error_row9_col27']/rows[0]['error_row9_col27'],'half_epsilon_error_ratio':rows[2]['error_row9_col27']/rows[0]['error_row9_col27']}
write('serialization_failure.json',{'reason':'TypeError: Object of type int64 is not JSON serializable','exit_code':1,'source_commit':'c66496e','process_wall_s_from_exec_tool':0.145563236,'saved_matrix_count':3,'diagnostic_computation_complete_before_archive_failure':True,'original_summary_present':False,'source_fault':'max_index=list(numpy.unravel_index(...)) contains numpy.int64'})
write('summary.json',{'status':'DIAGNOSTIC_ONLY_ORIGINAL_FAIL_STOP_RETAINED','rows':rows,'ratios':ratios,'AD_minus_independent_Python_max':float(np.abs(z['AD']-z['Python']).max()),'wall_s':None,'wall_s_missing_due_to_original_archive_failure':True,'qualification_promoted':False,'no_state_integration':True,'no_parameter_or_threshold_change':True,'no_qualification_rerun':True,'corrections_used_after_archive_fix':2,'remaining_corrections':1})
write('archive_recovery.json',{'kind':'READ_ONLY_MATRIX_ARCHIVE_RECOVERY_NO_RECALCULATION','source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'script_sha256':sha(__file__),'before_diagnosis_script_sha256':json.loads((OUT/'metadata.json').read_text())['source_sha256']['scripts/diagnose_p2_implicit_fd.py'],'after_diagnosis_script_sha256':sha(ROOT/'scripts/diagnose_p2_implicit_fd.py'),'matrix_sha256':{p.name:sha(p) for p in sorted(OUT.glob('*.npz'))},'scientific_values_changed':False})
write('artifact_sha256.json',{p.name:sha(p) for p in sorted(OUT.iterdir()) if p.is_file()})
print(json.dumps({'rows':rows,'ratios':ratios,'corrections_used':2,'qualification_promoted':False},ensure_ascii=False))
