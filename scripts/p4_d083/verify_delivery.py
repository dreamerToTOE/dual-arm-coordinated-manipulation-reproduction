#!/usr/bin/env python3
"""Independent saved-evidence audit. No scientific model or solver imports.

The root reviewer uses standard-library identity, hash, topology and accounting
checks. Numerical qualifications remain those of the independent planar oracle
and the preserved spatial certificates; this is not another science batch.
"""
import argparse
import collections
import csv
import gzip
import hashlib
import json
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
B = ROOT/'results/20261022_D083_fig3_controlled02'
C = ROOT/'results/20261022_D083_difficult02'

def read(path):
    return json.loads(Path(path).read_text())

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def csvread(path):
    with Path(path).open(newline='') as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)

def verify_manifest(path, base):
    content = read(path)
    assert isinstance(content,dict)
    for key,value in content.items():
        assert sha(base/key)==value,(str(path),key)
    return len(content)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--docx',type=Path)
    args=parser.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    checks={}
    recovery=read(ROOT/'results/20261022_D083_recovery01/recovery.json')
    assert all(sha(ROOT/p)==v['sha256'] and (ROOT/p).stat().st_size==v['bytes']
               for p,v in recovery['preserved_files'].items())
    checks['predecessors']={'files_unchanged':len(recovery['preserved_files']),
                            'bytes_unchanged':sum(v['bytes'] for v in recovery['preserved_files'].values())}
    # Read raw records rather than relying on the producer's audit summary.
    _,pairs=csvread(B/'frozen_pairs.csv')
    _,candidates=csvread(B/'candidate_outcomes.csv')
    _,outcomes=csvread(B/'pair_by_m_outcomes.csv')
    assert len(pairs)==180 and len(candidates)==2880 and len(outcomes)==900
    pairmap={int(p['pair_id']):p for p in pairs}
    assert len({tuple(sorted((p['state_a'],p['state_b']))) for p in pairs})==180
    assert all(p['state_a']!=p['state_b'] for p in pairs)
    candmap={(int(p['pair_id']),int(p['partition'])):p for p in candidates}
    outmap={(int(p['pair_id']),int(p['m'])):p for p in outcomes}
    winners=collections.Counter(); qualified=points=0
    maxima={'position_m':0.,'angle_rad':0.}; minimum_clearance=float('inf')
    for pairid,pair in pairmap.items():
        with gzip.open(B/f'raw_pairs/pair_{pairid:03d}.json.gz','rt') as stream:
            raw=json.load(stream)
        assert raw['pair']['pair_id']==pairid
        for name in ('state_a','state_b','bin_id','full_unordered_pair_index'):
            assert str(raw['pair'][name])==pair[name]
        assert set(raw['candidates'])==set(map(str,range(16)))
        for partition,item in raw['candidates'].items():
            assert item['result']['success']==(candmap[pairid,int(partition)]['success']=='True')
            assert item['counters']['local_connection_calls']==1
        for m in (1,2,3,7,16):
            row=outmap[pairid,m]
            assert all(row[k]==pair[k] for k in pair)
            successful=[i for i in range(m) if raw['candidates'][str(i)]['result']['success']]
            assert int(row['existential_success'])==bool(successful)
            assert json.loads(row['successful_partitions'])==successful
            assert json.loads(row['unknown_partitions'])==[]
            bound=raw['bounded'][str(m)]
            assert bound['result']['success']==(row['bounded_success']=='True')
            assert int(row['bounded_projection_calls'])<=512
            if bound['result']['success']:
                winner=bound['result']['partition']
                assert winner==successful[0]
                assert bound['result']['path']==raw['candidates'][str(winner)]['result']['path']
                winners[winner]+=1
        for item in list(raw['candidates'].values())+list(raw['bounded'].values()):
            if item['result']['success']:
                q=item['independent_qualification']
                assert q['independently_qualified'] is True
                assert all(q[k]==0 for k in ('closure_failures','joint_limit_failures','collision_failures','branch_mismatches'))
                qualified+=1;points+=q['point_count']
                maxima['position_m']=max(maxima['position_m'],q['maximum_position_residual_m'])
                maxima['angle_rad']=max(maxima['angle_rad'],q['maximum_angle_residual_rad'])
                minimum_clearance=min(minimum_clearance,q['minimum_clearance_m'])
    bsummary=read(B/'summary.json')
    assert qualified==3254 and points==97577
    for r in bsummary['by_m']:
        assert r['existential_success_count']==sum(int(x['existential_success']) for x in outcomes if int(x['m'])==r['m'])
    checks['fig3']={'candidate_calls':len(candidates),'bounded_calls':len(outcomes),
        'exact_union_and_shared_population_checks':900,'identical_winning_paths':sum(winners.values()),
        'winners':dict(winners),'accepted_call_records_qualified':qualified,'discrete_point_references':points,
        'maximum_residuals':maxima,'minimum_clearance_m':minimum_clearance,
        'raw_manifest_files':verify_manifest(B/'artifact_sha256.json',ROOT)}
    # Spatial path traversal independently follows accepted edge node IDs.
    spatial=read(ROOT/'results/20261022_D083_spatial_visualization01/manifest.json')
    assert all(spatial[k]==0 for k in ('new_planner_calls','new_IK_calls','new_NR_or_RBS_calls','new_collision_queries'))
    spatialchecks=[]
    for item in spatial['paths']:
        protocol=read(ROOT/item['protocol'])
        assert sha(ROOT/item['protocol'])==item['protocol_sha256']
        assert sha(ROOT/item['execution'])==item['execution_sha256']
        assert sha(ROOT/item['historical_certificate'])==item['historical_certificate_sha256']
        edges=protocol['fixed_queue']['edges']
        order=[]
        for edge in edges:
            ids=edge['node_ids']
            if order:
                assert order[-1]==ids[0]
                order.extend(ids[1:])
            else:order.extend(ids)
        assert order==item['source_traversal_order_node_ids']
        roles=[edge.get('active_chain') for edge in edges]
        assert roles==item['active_roles']
        switches=[i for i in range(1,len(roles)) if roles[i]!=roles[i-1]]
        assert len(switches)==item['role_switch_count']
        assert len(order)==item['node_count']
        for i,event in zip(switches,item['role_switches']):
            node=edges[i]['node_ids'][0]
            assert event['source_node_id']==node and event['traversal_index']==order.index(node)
        if item['environment']=='III':
            assert len(switches)==4 and item['native_pose_pass_nodes']==0
            assert [e['traversal_index'] for e in item['role_switches']]==[179,248,392,492]
        spatialchecks.append({'key':item['key'],'states':len(order),'switches':len(switches)})
    checks['spatial']={'saved_paths':spatialchecks,'new_scientific_calls':0}
    # Combined actual calls include the saved-artifact failure exactly once.
    _,trials=csvread(C/'planner_trials.csv')
    assert len(trials)==36 and len({(r['condition'],r['seed'],r['registered_method']) for r in trials})==36
    unknown=[r for r in trials if r['artifact_complete']=='False']
    assert len(unknown)==1 and unknown[0]['condition']=='C1' and unknown[0]['seed']=='7' and unknown[0]['registered_method']=='PCS'
    assert unknown[0]['independently_qualified']==''
    complete=[r for r in trials if r['artifact_complete']=='True']
    assert len(complete)==35
    for row in complete:
        assert sha(ROOT/row['artifact'])==row['artifact_sha256']
        with gzip.open(ROOT/row['artifact'],'rt') as stream:raw=json.load(stream)
        assert raw['status']==row['status']
        if row['status']=='SUCCESS':assert row['independently_qualified']=='True'
    csummary=read(C/'summary.json')
    assert csummary['executed_calls']==36 and csummary['new_resume_calls']==35
    assert all(x['hard_scenario_status']=='NOT_ESTABLISHED_HARD' for x in csummary['conditions'])
    checks['difficulty']={'actual_calls':36,'complete_artifacts':35,'engineering_unknown':1,
        'independently_qualified':sum(r['independently_qualified']=='True' for r in complete),
        'hard_conditions_established':0,'raw_manifest_files':verify_manifest(C/'artifact_sha256.json',C)}
    # Historical matrix cells stay exact, even where later evidence differs.
    oldfields,oldrows=csvread(ROOT/'reports/P4_D082_ORIGINAL_VS_APPROVED_VS_ACTUAL.csv')
    fields,rows=csvread(ROOT/'reports/P4_D083_ORIGINAL_VS_APPROVED_VS_ACTUAL.csv')
    assert len(rows)==len(oldrows)==211 and len(oldfields)==257 and fields[:257]==oldfields
    assert all(all(a[k]==b[k] for k in oldfields) for a,b in zip(oldrows,rows))
    checks['coverage']={'rows':211,'historical_columns_preserved':257,'appended_columns':len(fields)-257}
    if args.docx:
        with zipfile.ZipFile(args.docx) as z:
            xml=ET.fromstring(z.read('word/document.xml'))
            ns={'m':'http://schemas.openxmlformats.org/officeDocument/2006/math','w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            equations=xml.findall('.//m:oMath',ns)
            text=''.join(x.text or '' for x in xml.findall('.//w:t',ns))
            assert len(equations)>=16 and '另1次保存失败' in text
            assert '176/180' in text and 'PARTIAL' in text
            checks['docx']={'sha256':sha(args.docx),'editable_equations':len(equations),'embedded_images':len([n for n in z.namelist() if n.startswith('word/media/')])}
    result={'schema':'P4_D083_ROOT_INDEPENDENT_SAVED_DELIVERY_AUDIT_V1','passed':True,
            'scope':'Read-only standard-library evidence identity/topology/accounting. No scientific computations or renderer claims.',
            'checks':checks,'auditor_source_sha256':sha(__file__)}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(result,ensure_ascii=False))

if __name__=='__main__':main()
