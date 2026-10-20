from circular_aquaculture_berry import annual,HERE
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
S,P,M=annual('Expansion');FIG=HERE/'figures';FIG.mkdir(exist_ok=True)
labels=['Tilapia','Freshwater prawns','Atlantic salmon','Trout']
values=[40,30,20,10]
fig,axs=plt.subplots(1,2,figsize=(10.4,4.1),dpi=200,gridspec_kw={'width_ratios':[1.1,1.0]})
axs[0].barh(labels[::-1],values[::-1]);axs[0].set_xlim(0,51);axs[0].set_xlabel('Share of proposed 120,000 t/year harvest (%)');axs[0].set_title('Warm-water species are 70% of mix')
for i,v in enumerate(values[::-1]):axs[0].text(v+.7,i,f'{v}%  ({v*1.2:,.0f} kt)',va='center',fontsize=9)
axs[1].bar(['Mixed RAS','Greenhouses','Driers','Algae PBR'],[S['ras_FTE_low'],S['greenhouse_FTE_low'],S['processing_FTE_low'],S['algae_FTE_low']]);axs[1].set_ylim(0,10500);axs[1].set_title('Jobs are additional scenarios, not observed');axs[1].set_ylabel('Lower-range direct annual FTE');axs[1].tick_params(axis='x',labelrotation=20)
fig.suptitle('Alternative B.C. circular-food expansion: production and labour screening',fontsize=12);fig.tight_layout();fig.savefig(FIG/'Figure_12_Warmwater_Portfolio.png',bbox_inches='tight');plt.close(fig)
fig,ax=plt.subplots(figsize=(11.4,5.8),dpi=200);ax.set_xlim(0,11.4);ax.set_ylim(0,5.8);ax.axis('off')
items=[(0.3,3.45,2.9,1.0,'Data-centre recovered heat\n(heat-exchanger/heat pump)'),
 (4.2,4.30,2.6,.85,'Naturally lit greenhouse\nvegetables + crop residues'),
 (4.2,2.65,2.6,.85,'Warm freshwater RAS\ntilapia, prawns, trout'),
 (8.3,2.65,2.7,.85,'Hydroponic nutrient tanks\npost-treatment only'),
 (4.2,.75,2.6,.85,'Saltwater salmon RAS\nindependent saline circuit'),
 (8.3,.75,2.7,.85,'Marine microalgae PBR\nsolar light + nutrient uptake'),
 (8.3,4.30,2.7,.85,'Feed pellet mill\nvalidated residue ingredients')]
for x,y,w,h,t in items:
 ax.add_patch(patches.FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.08',fc='#e5f2f0',ec='#267569',lw=1.4));ax.text(x+w/2,y+h/2,t,ha='center',va='center',fontsize=8.8)
def arrow(a,b,text,dy=.13):
 ax.annotate('',xy=b,xytext=a,arrowprops=dict(arrowstyle='->',lw=1.8,color='#3a4f66'));ax.text((a[0]+b[0])/2,(a[1]+b[1])/2+dy,text,ha='center',va='center',fontsize=8)
arrow((3.2,3.9),(4.17,4.7),'heat');arrow((3.2,3.8),(4.17,3.05),'heat')
arrow((3.0,3.5),(4.16,1.2),'heat',-.17)
arrow((6.8,4.75),(8.25,4.75),'screened biomass')
arrow((6.84,3.05),(8.24,3.05),'treated freshwater')
arrow((6.84,1.2),(8.24,1.2),'treated saline N/P')
ax.annotate('',xy=(6.0,3.57),xytext=(8.45,4.23),arrowprops=dict(arrowstyle='->',connectionstyle='arc3,rad=.30',lw=1.35,color='#9a683f'))
ax.text(7.35,3.95,'formulated feed (partial)',ha='center',fontsize=8,color='#9a683f')
ax.annotate('',xy=(5.5,.70),xytext=(9.65,.73),arrowprops=dict(arrowstyle='->',connectionstyle='arc3,rad=-.5',lw=1.35,color='#9a683f'))
ax.text(9.0,.35,'algal oil to salmon feed',fontsize=8,ha='center',color='#9a683f')
ax.text(5.75,5.46,'No direct freshwater–saltwater mixing; biosecurity gates mandatory',ha='center',fontsize=11,weight='bold')
fig.tight_layout();fig.savefig(FIG/'Figure_13_Separated_Nutrient_Circuits.png',bbox_inches='tight');plt.close(fig)
fig,ax=plt.subplots(figsize=(9.3,4.7),dpi=200)
segments=[('Greenhouses',4000,9000),('Aquaculture RAS',1992,3468),('Drying / processing',S['processing_FTE_low'],S['processing_FTE_high']),('Algae and feed mill',35,140)]
for i,(name,low,high) in enumerate(segments):
 ax.plot([low,high],[i,i],lw=10,solid_capstyle='round');ax.plot([low,high],[i,i],'o',ms=6);ax.text(high+190,i,f'{low:,.0f}–{high:,.0f}',va='center',fontsize=9)
ax.set_yticks(range(len(segments)),[i[0] for i in segments]);ax.invert_yaxis();ax.set_xlim(0,11500);ax.grid(axis='x',alpha=.3)
ax.set_xlabel('Illustrative direct operating FTE (not verified jobs)')
ax.set_title(f'Expanded 1,000-ha / 120,000-t model: {S["annual_direct_FTE_low"]:,.0f}–{S["annual_direct_FTE_high"]:,.0f} annual FTE')
fig.tight_layout();fig.savefig(FIG/'Figure_14_Job_Staffing_Ranges.png',bbox_inches='tight');plt.close(fig)
print('figs',len(list(FIG.glob('Figure_*.png'))))
