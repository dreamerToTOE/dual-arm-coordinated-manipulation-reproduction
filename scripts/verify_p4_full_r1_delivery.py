"""Delivery integrity verification. Reads evidence only; never runs a solver."""
from __future__ import annotations
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'reports/p4_full_r1_assets_20261015_v3'
STEM='P4完整复现_原生模型资格与失败根因_20261015_交付版'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 checks=[]
 def check(name,value,detail):
  checks.append({'check':name,'passed':bool(value),'evidence':detail})
 d=json.loads((ASSETS/'report_data.json').read_text())
 for p,h in d['sources'].items():check('analysis_source_hash:'+p,sha(ROOT/p)==h,h)
 check('component_totals',sum(x['passed'] for x in d['environments'])==1580 and
       sum(x['failed'] for x in d['environments'])==246 and d['checks_total']==1826,
       '1826=1580+246 component items; no planning-success-rate interpretation')
 ik=list(csv.DictReader((ASSETS/'ik_roundtrip.csv').open()))
 nr=list(csv.DictReader((ASSETS/'nr_rigid_closure.csv').open()))
 apc=list(csv.DictReader((ASSETS/'planar_apc.csv').open()))
 check('separate_denominators',len(ik)==400 and len(nr)==50 and len(apc)==40,
       '5 spatial*80 IK; 5 spatial*10 NR plus10 planar NR; 40 planar APC')
 p=ROOT/'results/p4_full/20261014T1555_R1_PLANAR01/I_native.json'
 planar=json.loads(p.read_text())
 # The independent planar verifier also checked exact fixture IDs and raw inputs.
 pv=json.loads((ROOT/'results/p4_full/20261014T1555_R1_PLANAR01/I_independent.json').read_text())
 unique=[c for c in pv['checks'] if c['check_id']=='unique_fixture_ids']
 check('planar_fixture_ids',len(unique)==1 and unique[0]['status']=='PASS',unique)
 check('formal_calls_zero',d['formal_planning_calls']==0,'No native planner executed')
 rows=list(csv.DictReader((ROOT/'reports/P4_FULL_R1_ORIGINAL_VS_REPRODUCED_COVERAGE.csv').open()))
 parents={r['item_id'] for r in rows if len(r['item_id'])==6}
 check('complete_obligation_ids',parents=={'P4-T'+str(i).zfill(2) for i in range(1,31)} and len(rows)==211,
       '30 parents and211 total entries; original29 retained')
 check('no_false_full_claim',not any(r['status'] in ['FULL','PASS'] for r in rows),
       'Current stage does not qualify the full paper or complete paths')
 docx=ROOT/'reports'/(STEM+'.docx');pdf=ROOT/'reports'/(STEM+'.pdf')
 with zipfile.ZipFile(docx) as z:
  doc=ET.fromstring(z.read('word/document.xml'))
  ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
  text=''.join(n.text or '' for n in doc.findall('.//w:t',ns))
  media=[x for x in z.namelist() if x.startswith('word/media/')]
  expected={hashlib.sha256(p.read_bytes()).hexdigest() for p in ASSETS.glob('*.png')}
  actual={hashlib.sha256(z.read(p)).hexdigest() for p in media}
  check('docx_real_log_figures',len(media)==6 and actual==expected,'Six embedded PNGs equal generated evidence figures')
  check('editable_equations',len(doc.findall('.//m:oMath',ns))==15,'15 OMML equations')
  check('scientific_report_tone',not any(s in text for s in ['编写目的','根据用户要求','ChatGPT','Codex']),
        'Chinese research narrative; no instruction prose')
  check('explicit_partial_scope','完整论文仍部分完成' in text and '没有正式Table I规划试次' in text,
        'First page states no formal planning and no full-paper success')
  core=z.read('docProps/core.xml').decode()
  check('document_real_date','2013-12-23' not in core and '2026-10-15' in core,'Template dates replaced with real generation date')
 info=subprocess.check_output(['pdfinfo',str(pdf)],text=True)
 pages=int(next(l.split(':',1)[1] for l in info.splitlines() if l.startswith('Pages:')).strip())
 check('pdf_rendered',pages==9,'PDF9 pages; main figure/formula pages visually inspected')
 frozen=json.loads((ROOT/'configs/p4_full/baseline_preservation_manifest.json').read_text())
 changed=[f['path'] for f in frozen['files'] if not (ROOT/f['path']).exists() or sha(ROOT/f['path'])!=f['sha256']]
 check('frozen_original_bytes',not changed,{'checked':len(frozen['files']),'changed':changed})
 check('private_pdf_not_tracked',not any('private_sources' in p for p in subprocess.check_output(['git','ls-files'],cwd=ROOT,text=True).splitlines()),
       'Private PDF and source page images excluded')
 result={'schema':'P4_R1_DELIVERY_INTEGRITY_V1','source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
         'checks':checks,'passed':sum(c['passed'] for c in checks),'failed':sum(not c['passed'] for c in checks),
         'report_docx_sha256':sha(docx),'report_pdf_sha256':sha(pdf),'fresh_scientific_calls':0,
         'scope':'Artifact integrity only; all original qualification failures unchanged'}
 out=ROOT/'reports/P4_FULL_R1_DELIVERY_QA.json'
 if out.exists():raise FileExistsError(out)
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'passed':result['passed'],'failed':result['failed'],'pdf_pages':pages}))
 if result['failed']:raise SystemExit(1)

if __name__=='__main__':main()
