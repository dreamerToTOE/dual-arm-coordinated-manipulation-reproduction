#!/usr/bin/env python3
"""Repair IV/V TCP observations only; compile, never execute collision queries.

The frozen v2 builder, adapter, manifest and binaries remain unchanged. The v3
manifest reuses all unaffected v2 entries and replaces only IV/V observations.
Original source collision arithmetic, models, pairs and tolerances are kept.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import resource
import shutil
import subprocess
import time

from build_p4_full_collision_adapter import ROOT, SOURCE, PQP, SPECS, PINNED, sha, replace_once

V2_BUILD = Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/collision_adapter_v2')
V3_BUILD = Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/collision_adapter_v3')


def cpu_total():
    a, b = resource.getrusage(resource.RUSAGE_SELF), resource.getrusage(resource.RUSAGE_CHILDREN)
    return a.ru_utime + a.ru_stime + b.ru_utime + b.ru_stime


def active_pairs(source, name):
    source = re.sub(r'/\*.*?\*/|//[^\n]*', '', source, flags=re.S)
    return [re.sub(r'\s+', '', x) for x in re.findall(name+r'\((.*?)\);', source, re.S)]


def without_pose_capture(source):
    return re.sub(r'^\s*p4_pose\([^\n]*\);\n', '', source, flags=re.M)


def stage(build, model, variant):
    repo, macro = SPECS[model]
    src, dest = SOURCE/repo, build/(model+'_'+variant)
    dest.mkdir(parents=True, exist_ok=False)
    for folder in ['validity_checkers', 'proj_classes', 'simulator']:
        (dest/folder).mkdir()
    originals = {}
    for rel in ['validity_checkers/collisionDetection.cpp', 'validity_checkers/collisionDetection.h',
                'validity_checkers/model.h', 'simulator/MatVec.h', 'proj_classes/def.h']:
        originals[rel] = sha(src/rel)
        shutil.copy2(src/rel, dest/rel)
    header = dest/'validity_checkers/collisionDetection.h'
    h = header.read_text().replace('#include <GL/glut.h>', '// unused rendering header omitted for standalone build')
    h = re.sub(r'#include "[^\"]*/MatVec.h"', '#include "../simulator/MatVec.h"', h)
    header.write_text(h)
    original = (src/'validity_checkers/collisionDetection.cpp').read_text()
    source = original
    alignment = []
    if variant == 'aligned':
        y = 'offsetY' if model == 'V' else '0'
        mark = '\n\tT12[0] =  0;'
        source = replace_once(source, mark,
                              f'\n\tT02[0]=offsetX/2; T02[1]={y}; T02[2]=ROBOT2_HEIGHT;'+mark)
        alignment = ['arm2 world base translation uses source APC global coordinates; no mesh local frame changed']
    source = source.replace('PQP_Tolerance(&res[', 'p4_query(&res[')
    # IV T7 is never assigned (source lines 147--152 are comments). Trod is
    # assigned at lines 154--161 with the physical 22 mm terminal offset.
    # V T7 uses a 20 mm mesh frame; physical TCP instead uses 22+400.7 mm.
    capture = ('\tp4_pose(R6,Trod); p4_pose(R62,T72);\n' if model == 'IV' else
               '\tp4_pose(R6,T6,422.7); p4_pose(R62,T72,400.7);\n')
    source = replace_once(source, '\tPQP_REAL tolerance = 8;', capture+'\tPQP_REAL tolerance = 8;')
    file = dest/'validity_checkers/collisionDetection.cpp'
    file.write_text(source)
    v2_file = V2_BUILD/(model+'_'+variant)/'validity_checkers/collisionDetection.cpp'
    pair_parity = active_pairs(original, 'PQP_Tolerance') == active_pairs(source, 'p4_query')
    observation_only = without_pose_capture(source) == without_pose_capture(v2_file.read_text())
    if not pair_parity or not observation_only:
        raise ValueError('TCP_OBSERVATION_ONLY_PARITY_FAILED')
    meshes = {}
    for p in sorted((src/'simulator').glob('*.tris')):
        (dest/'simulator'/p.name).symlink_to(p)
        meshes[p.name] = sha(p)
    exe = dest/'collision_batch'
    cmd = ['g++', '-std=c++17', '-O2', '-Wall', '-Wextra', f'-DP4_MODEL={macro}',
           '-I'+str(dest/'validity_checkers'), '-I'+str(PQP/'include'),
           str(ROOT/'baselines/p4_full/geometry_consistent/collision_batch_driver.cpp'),
           str(PQP/'lib/libPQP.a'), '-o', str(exe)]
    start, cpu_start = time.monotonic(), cpu_total()
    proc = subprocess.run(cmd, text=True, capture_output=True, timeout=120)
    (dest/'build.stdout.log').write_text(proc.stdout)
    (dest/'build.stderr.log').write_text(proc.stderr)
    return {'model': model, 'variant': variant, 'source_root': str(src), 'source_commit': PINNED[repo],
            'source_files_sha256': originals, 'mesh_sha256': meshes, 'command': cmd,
            'exit_code': proc.returncode, 'build_wall_s': time.monotonic()-start,
            'build_cpu_s': cpu_total()-cpu_start, 'binary': str(exe), 'cwd': str(dest),
            'binary_sha256': sha(exe) if exe.exists() else None,
            'physical_alignment_changes': alignment, 'instrumented_source_sha256': sha(file),
            'query_count': 0, 'tcp_observation_version': 3, 'tcp_capture_statement': capture.strip(),
            'source_observation_evidence': ({'arm1': 'collisionDetection.cpp:154-161 Trod=T6+R6*[22,0,0]; T7 assignments at 147-152 commented',
                                             'arm2': 'collisionDetection.cpp:258-263 T72=T62+R62*[22,0,0]'} if model == 'IV' else
                                            {'arm1': 'collisionDetection.cpp:140-152 T6 physical link6 frame; T7 20mm mesh frame is not physical TCP; qualified FK tool=422.7mm',
                                             'arm2': 'collisionDetection.cpp:258-263 T72 includes22mm, then qualified 400.7mm grasp offset'}),
            'v2_staged_source_sha256': sha(v2_file),
            'source_equal_to_v2_after_removing_pose_observations': observation_only,
            'all_active_source_pair_arguments_preserved': pair_parity,
            'active_call_statement_count': len(active_pairs(source, 'p4_query'))}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--build-root', type=Path, default=V3_BUILD)
    args = parser.parse_args()
    args.build_root.mkdir(parents=True, exist_ok=False)
    base_path = V2_BUILD/'manifest.json'
    base = json.loads(base_path.read_text())
    start, cpu_start = time.monotonic(), cpu_total()
    manifest = {'schema': 'P4_COLLISION_ADAPTER_ENGINEERING_BUILD_V3',
                'created_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
                'query_count': 0, 'license': base['license'],
                'pqp_library_sha256': sha(PQP/'lib/libPQP.a'),
                'base_manifest_path': str(base_path), 'base_manifest_sha256': sha(base_path),
                'builder_sha256': sha(__file__),
                'driver_sha256': sha(ROOT/'baselines/p4_full/geometry_consistent/collision_batch_driver.cpp'),
                'default_adapter_modified': False,
                'entries': [x for x in base['entries'] if x['model'] not in ('IV', 'V')]}
    try:
        for model in ('IV', 'V'):
            for variant in ('native', 'aligned'):
                row = stage(args.build_root, model, variant)
                manifest['entries'].append(row)
                print(json.dumps({k: row[k] for k in ['model', 'variant', 'exit_code', 'build_wall_s',
                                                     'source_equal_to_v2_after_removing_pose_observations',
                                                     'all_active_source_pair_arguments_preserved']}), flush=True)
                if row['exit_code']:
                    raise RuntimeError('BUILD_FAILED')
    finally:
        manifest.update(engineering_build_wall_s=time.monotonic()-start,
                        engineering_build_cpu_s=cpu_total()-cpu_start)
        (args.build_root/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')


if __name__ == '__main__':
    main()
