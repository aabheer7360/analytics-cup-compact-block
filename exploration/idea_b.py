import sys; import pathlib; sys.path.insert(0,str(pathlib.Path(__file__).parent))
from load import *
e=events()
po=e[e.event_type=='passing_option'].copy()
po['d']=po.dangerous.eq(True); po['t']=po.targeted.eq(True); po['ev']=po.xpass_completion*po.xthreat
po['run']=po.associated_off_ball_run_event_id.notna()
pp=e[(e.event_type=='player_possession')&(e.end_type=='pass')][['match_id','event_id','team_shortname']]
K=['match_id','associated_player_possession_event_id']
po=po.merge(pp.rename(columns={'event_id':K[1]}),on=K,suffixes=('','_pp'))
agg=po.groupby(K).agg(avail=('d','any'),has_t=('t','any'),best_ev=('ev','max'),n_opt=('event_id','size'))
ch=po[po.t].groupby(K).agg(chosen_d=('d','any'),chosen_ev=('ev','max'))
X=agg.join(ch).reset_index()
print('passes ending possessions:',len(pp),' with options linked:',len(X),' with targeted option:',X.has_t.mean().round(3),' median options/pass:',X.n_opt.median())
X=X[X.has_t]
print('>=1 dangerous option available: %.3f'%X.avail.mean())
D=X[X.avail]; print('of those, passed to a dangerous option: %.3f (n=%d)'%(D.chosen_d.mean(),len(D)))
print('chose the best completion-x-threat option: %.3f'%(X.best_ev-X.chosen_ev<=1e-12).mean())
r=po[po.run]; thr=r.ev.quantile(.9)
print('\nrun-based options %d; top-10%% value runs (>= %.4f) targeted: %.3f; other runs %.3f; non-run options %.3f'%(len(r),thr,r[r.ev>=thr].t.mean(),r[r.ev<thr].t.mean(),po[~po.run].t.mean()))
print('dangerous run options targeted %.3f vs non-dangerous run options %.3f'%(r[r.d].t.mean(),r[~r.d].t.mean()))
