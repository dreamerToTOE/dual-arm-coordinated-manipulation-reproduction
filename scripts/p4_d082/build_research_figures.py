#!/usr/bin/env python3
"""Chinese research figures from immutable saved numerical data; no solves."""
import csv
import argparse
import gzip
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
N = ROOT / 'results/20261019_D081_numeric_pilot'
S = ROOT / 'results/20261019_D081_stability_pilot'
OUT = ROOT / 'reports/p4_d082_research_assets_20261022'

def rows(p):
    with p.open() as f:
        return list(csv.DictReader(f))

def raw(p):
    with gzip.open(p, 'rt') as f:
        return json.load(f)

def save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / name, dpi=180, facecolor='white')
    plt.close(fig)

def vertices(q):
    a = np.cumsum(q)[:19]
    return np.vstack((np.zeros(2), np.cumsum(np.sin(np.pi/38)*np.c_[np.cos(a),np.sin(a)],axis=0)))

def main():
    global OUT
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=OUT)
    OUT=parser.parse_args().output.resolve()
    OUT.mkdir(exist_ok=False)
    font = font_manager.FontProperties(fname='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
    font_manager.fontManager.addfont(font.get_file())
    plt.rcParams.update({'font.family':font.get_name(),'axes.unicode_minus':False,'font.size':10})
    payload = raw(S/'raw_planner/planner_E1_clutter_PCS_seed7.json.gz')
    path = np.array(payload['path'])
    fig, ax = plt.subplots(figsize=(7.4,5.2))
    for x,y,r in ((.45,.72,.045),(.50,.18,.065),(.72,.60,.05)):
        ax.add_patch(plt.Circle((x,y),r,color='#c95148',alpha=.4))
    for q in path:
        xy=vertices(q);ax.plot(*xy.T,color='#5284a3',alpha=.09,lw=.7)
    for i,label,c in ((0,'起点','#205e91'),(len(path)//2,'中间构型','#c38318'),(len(path)-1,'终点','#2d8264')):
        ax.plot(*vertices(path[i]).T,'o-',color=c,ms=2.7,lw=1.5,label=label)
    ax.plot([0,1],[0,0],'k--',label='固定地杆')
    ax.set(aspect='equal',xlabel='x / m',ylabel='y / m',title=f'20R 重建闭链的完整保存路径  PCS  E1  seed 7  {len(path)} 点')
    ax.legend(fontsize=9);ax.grid(alpha=.2)
    save(fig,'01_complete_trajectory.png')
    states=payload['path_metrics']['state_qualifications'];x=np.arange(len(states))
    fig,axs=plt.subplots(2,2,figsize=(9.5,6))
    for ax,key,label in zip(axs.flat,['closure_position','closure_angle','joint_margin'],['位置闭链残差 / m','角度闭链残差 / rad','最小关节余量 / rad']):
        vals=np.array([s[key] for s in states]);ax.plot(x,vals);ax.set(xlabel='路径点编号',ylabel=label);ax.grid(alpha=.2)
    axs[1,1].plot(x,[s['collision']['minimum_clearance'] for s in states],color='#2d8264')
    axs[1,1].set(xlabel='路径点编号',ylabel='最小碰撞净距 / m');axs[1,1].grid(alpha=.2)
    fig.suptitle('保存路径的原始逐点指标  离散几何轨迹  无物理时间参数')
    save(fig,'02_path_constraints.png')
    trials=rows(S/'planner_trials.csv');methods=['RSS','PCS','PCS_FIXED_0','PCS_FIXED_16','NR'];names=['RSS','PCS 全','固定 0','固定 16','NR']
    summary=json.loads((S/'planner_summary.json').read_text())['rows']
    fig,axs=plt.subplots(1,2,figsize=(10.8,4.5))
    for ax,env,title in zip(axs,['E0_sparse','E1_clutter'],['E0 稀疏障碍','E1 增加圆障碍']):
        g=[next(r for r in summary if r['environment']==env and r['method']==m) for m in methods]
        p=np.array([r['success_rate'] for r in g]);lo=np.array([r['success_rate_ci95_low'] for r in g]);hi=np.array([r['success_rate_ci95_high'] for r in g]);ix=np.arange(5)
        ax.errorbar(ix,p,yerr=[p-lo,hi-p],fmt='o',capsize=4,color='#205e91');ax.set(xticks=ix,xticklabels=names,ylim=(-.05,1.12),ylabel='成功率及 Wilson 95% 区间',title=title)
        for i,v in enumerate(p):ax.text(i,v+.045,f'{round(v*5)}/5',ha='center',fontsize=9)
        twin=ax.twinx();twin.plot(ix,[r['mean_wall_sec'] for r in g],'s--',color='#c38318');twin.set_ylabel('平均规划墙钟 / s');ax.grid(axis='y',alpha=.2)
    fig.suptitle('配对种子 7 23 41 59 73  每组 5 次  每次墙钟上限 1 s')
    save(fig,'03_paired_comparison.png')
    fig,axs=plt.subplots(1,2,figsize=(10.5,4.4))
    f3=rows(N/'fig3_pairs.csv');f4=rows(N/'fig4_visibility_pairs.csv')
    for m in (1,2,3,7,16):
        group=[r for r in f3 if int(r['m'])==m];binned(axs[0],group,f'm={m}',.3)
    for m in ('RSS','PCS','NR'):binned(axs[1],[r for r in f4 if r['method']==m],m,.3)
    axs[0].set_title('Fig 3 对应数值  各 m 的构型总体不同')
    axs[1].set_title('Fig 4 对应数值  同一组 240 点对')
    for ax in axs:ax.set(xlabel='关节空间点对距离 / rad',ylabel='局部连接成功率',ylim=(-.03,1.05));ax.legend(fontsize=8);ax.grid(alpha=.2)
    save(fig,'04_local_visibility.png')
    projection=rows(N/'projection_trials.csv');f5=rows(N/'fig5_distance_change.csv')
    fig,axs=plt.subplots(1,3,figsize=(12,3.7))
    for m,c in [('APC','#c38318'),('NR','#205e91')]:
        scales=sorted({float(r['scale_rad']) for r in projection});groups=[[r for r in projection if r['method']==m and float(r['scale_rad'])==v] for v in scales]
        axs[0].plot(scales,[sum(r['success']=='True' for r in g)/len(g) for g in groups],'o-',color=c,label=m)
        axs[1].plot(scales,[1000*np.mean([float(r['wall_sec']) for r in g]) for g in groups],'o-',color=c,label=m)
        good=[r for r in f5 if r['method']==m and r['success']=='True']; bins={}
        for r in good:bins.setdefault(int(float(r['distance_before_rad'])/.46),[]).append(float(r['absolute_distance_change_rad']))
        keys=sorted(bins);axs[2].plot([(k+.5)*.46 for k in keys],[np.mean(bins[k]) for k in keys],'o-',color=c,label=m)
    axs[0].set(ylabel='投影成功率',xlabel='初始逐关节扰动尺度 / rad');axs[1].set(ylabel='平均单次墙钟 / ms',xlabel='初始逐关节扰动尺度 / rad');axs[2].set(ylabel='平均绝对距离变化 / rad',xlabel='投影前邻点距离 / rad')
    for ax in axs:ax.grid(alpha=.2);ax.legend()
    fig.suptitle('投影每方法 768 输入  邻点距离每方法 384 输入  条件均值仅含成功投影')
    save(fig,'05_projection_and_distance.png')
    nr=raw(S/'raw_planner/planner_E0_sparse_NR_seed7.json.gz')
    event=next(e for e in nr['projection_log'] if len(e.get('trace',[]))>2)
    trace=event['trace'];fig,ax=plt.subplots(figsize=(7.2,3.9))
    ax.semilogy([t['update_index'] for t in trace],[max(t['position_m'],1e-18) for t in trace],'o-',label='位置残差 / m')
    ax.semilogy([t['update_index'] for t in trace],[max(t['rotation_rad'],1e-18) for t in trace],'s-',label='角度残差 / rad')
    ax.axhline(1e-8,ls='--',color='gray',label='各自验收阈值 1e-8');ax.set(xlabel='NR 更新编号',ylabel='各自单位下的残差',title='预定 seed 7 首个不少于三条记录的 NR 投影轨迹');ax.grid(alpha=.2);ax.legend(fontsize=9)
    save(fig,'06_nr_convergence.png')
    fig,ax=plt.subplots(figsize=(8.6,3.5));ax.axis('off')
    texts=['输入构型与约束','随机采样与树扩展','NR 或解析 IK 投影','RBS 中点递归检查','两树连接与路径回溯','独立闭链与碰撞核验']
    positions=[(.16,.73),(.49,.73),(.82,.73),(.82,.26),(.49,.26),(.16,.26)]
    for i,t in enumerate(texts):
        x,y=positions[i]
        ax.text(x,y,t,ha='center',va='center',bbox={'boxstyle':'round,pad=.5','facecolor':'#edf2f5','edgecolor':'#6c7a83'},fontsize=10)
        if i<2:ax.annotate('',xy=(x+.23,y),xytext=(x+.1,y),arrowprops={'arrowstyle':'->','color':'#6c7a83'})
        if i in (3,4):ax.annotate('',xy=(x-.23,y),xytext=(x-.1,y),arrowprops={'arrowstyle':'->','color':'#6c7a83'})
    ax.annotate('',xy=(.82,.34),xytext=(.82,.63),arrowprops={'arrowstyle':'->','color':'#6c7a83'})
    ax.set_title('复现程序的数据流示意  图中不表示实验性能')
    save(fig,'07_algorithm_flow.png')
    inputs=[N/'projection_trials.csv',N/'fig3_pairs.csv',N/'fig4_visibility_pairs.csv',N/'fig5_distance_change.csv',S/'planner_summary.json',S/'raw_planner/planner_E1_clutter_PCS_seed7.json.gz',S/'raw_planner/planner_E0_sparse_NR_seed7.json.gz']
    manifest={'classification':'PLOTS_OF_SAVED_REAL_DATA','new_planner_calls':0,'inputs':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},'figures':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.glob('*.png')}}
    (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print('figures',len(manifest['figures']))

def binned(ax,group,label,width):
    bins={}
    for r in group:bins.setdefault(int(float(r['distance_rad'])/width),[]).append(r['success']=='True')
    keys=sorted(bins);ax.plot([(k+.5)*width for k in keys],[np.mean(bins[k]) for k in keys],'o-',ms=3,label=label)

if __name__=='__main__':main()
