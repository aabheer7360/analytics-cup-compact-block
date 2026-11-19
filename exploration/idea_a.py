import sys; import pathlib; sys.path.insert(0,str(pathlib.Path(__file__).parent))
from load import *
e=events(); p=phases()
pp=e[e.event_type=='player_possession'].copy()
pp['central']=pp.inside_defensive_shape_start.eq(True)&pp.channel_start.isin(['center','half_space_left','half_space_right'])&pp.third_start.isin(['attacking_third','middle_third'])
pp['lb']=pp.last_line_break.eq(True)
acc=pp.groupby(['match_id','phase_index']).agg(central=('central','any'),lbreak=('lb','any')).reset_index()
P=p.merge(acc,left_on=['match_id','index'],right_on=['match_id','phase_index'])
B=P[P.team_out_of_possession_phase_type.isin(['medium_block','low_block'])].dropna(subset=['team_out_of_possession_width_start']).copy()
B['area']=B.team_out_of_possession_width_start*B.team_out_of_possession_length_start
for blk,g in B.groupby('team_out_of_possession_phase_type'):
    g=g.assign(q=pd.qcut(g.area,4,labels=['most compact','2','3','least compact']))
    print(blk,len(g)); print(g.groupby('q',observed=True).agg(n=('area','size'),area=('area','median'),central=('central','mean'),last_line=('lbreak','mean'),shot=('team_possession_lead_to_shot','mean')).round(3).to_string())
