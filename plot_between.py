from calc_ibs_backcoal_varmu import prob_L_from_mut_precise_varmu
from parse_tract_file import get_spectrum_counts
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from math import exp
from math import log

import pylab
from matplotlib import rc

import sys
from demographic_function_builder import *

tractfile=sys.argv[1]
result_file=sys.argv[2]
output_file=sys.argv[3]


def prob_L_from_mut_precise(L,ts,N):
    return prob_L_from_mut_precise_varmu(L,ts,ts*2,1,N)

def tract_lengths(L,t_diff_vec, N_vec): # returns a history with len(t_diff_vec) population size changes
    uncoal = 1
    prob_list = [prob_L_from_mut_precise(L,t_diff_vec[0],N_vec[0])]
    time = t_diff_vec[0]
    for i in range(1,len(t_diff_vec)):
        time += t_diff_vec[i]
        uncoal = time_lapse(uncoal, N_vec[i-1], t_diff_vec[i])
        prob_list, uncoal = popsize_change(L, prob_list, uncoal, N_vec[i-1], N_vec[i],time)
    return math.fsum(prob_list)


YRI_lengths, YRI_non_cumul, YRI_cumul, YRI_total_length = get_spectrum_counts(open(tractfile))

L_series=[1]
for a in range(1,int(log(5*20**6)/log(1.25))):
    if int(1*1.25**a)>L_series[0]:
        L_series.insert(0,int(1*1.25**a))
total_length=YRI_total_length


last_prob_0, last_prob_1, last_prob_2, last_prob_3, last_prob_4, last_prob_5 = 0,0,0,0,0,0
y0, y1, y2, y3,y4,y5 = [],[],[], [],[],[]

results=open(result_file)
lines=results.readlines()
results.close()

while len(lines[-1])<2:
    lines.pop()
s1=lines[-1].lstrip('[').split(']')
s2=s1[0].split(', ')

params=[]
for entry in s2:
    if len(entry)>1:
        params.append(float(entry))

t_diffs=[]
Ns=[]
for i in range(len(params)/2):
    t_diffs.append(float(params[i]))
for i in range(len(params)/2, len(params)):
    Ns.append(float(params[i]))


for i in range(len(L_series)-1):
    L=L_series[i]
    prob5 = tract_lengths(L,t_diffs, Ns)
    print 'L, prob cumulative: ',L, prob5
    y5.append(-(prob5-last_prob_5)/(L_series[i]-L_series[i-1]))
    last_prob_5=prob5


L_series_index=0
YRI_lengths_binned=[0]
for i in range(1, len(YRI_lengths)+1):
    if YRI_lengths[-i]>=L_series[L_series_index]:
        YRI_lengths_binned[-1]+=YRI_non_cumul[-i]
    else:
        while YRI_lengths[-i]<L_series[L_series_index]:
            L_series_index+=1
            YRI_lengths_binned.append(0)
        YRI_lengths_binned[-1]+=YRI_non_cumul[-i]


def bin_dataset(data_file):
    data_lengths, data_non_cumul, data_cumul, total_length= get_spectrum_counts(data_file)
#    print data_lengths[-1]
    L_series_index=0
    data_lengths_binned=[0]
    for i in range(1, len(data_lengths)+1):
        if data_lengths[-i]>=L_series[L_series_index]:
            data_lengths_binned[-1]+=data_non_cumul[-i]
        else:
            while data_lengths[-i]<L_series[L_series_index]:
                L_series_index+=1
                data_lengths_binned.append(0)
            data_lengths_binned[-1]+=data_non_cumul[-i]
    for i in range(1,len(L_series)):
        data_lengths_binned[i]*=1.0/(total_length*(-L_series[i]+L_series[i-1]))
    data_lengths_binned[0]*=1.0/total_length
#    print 'total length:', total_length
    return data_lengths_binned, total_length

YRI_lengths_binned,total_length=bin_dataset(open(tractfile))
plt.loglog(L_series, YRI_lengths_binned, label=tractfile)
plt.loglog(L_series[:-1], y5, label='Inferred history')
plt.legend(loc='lower left')

plt.xlabel('IBS tract length (L)')

plt.ylim(ymin=10**(-16))
plt.xlim(xmin=1)
plt.xlim(xmax=10**6)
plt.xscale('log')
plt.yscale('log')

F=pylab.gcf()
F.set_size_inches(6.83,7)
rc('font',**{'family':'sans-serif','sans-serif':['Arial'],'size':5})
plt.savefig(output_file,dpi=300, format='pdf')
    
              
    
