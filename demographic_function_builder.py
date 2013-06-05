import math
from math import exp
from calc_ibs_backcoal_varmu import prob_L_from_mut_precise_varmu

#### Hardcoded mutation rate and recombination rate parameters. May be modified as desired. Should ALWAYS be modified for use with non-human data
var_mutrate_param=0.039
theta=0.001
rho=0.0004
N_0=10000
####

def prob_L_from_mut_precise(L,ts,N):
    return prob_L_from_mut_precise_varmu(L,ts,2*ts,1,N,var_mutrate_param)


#### Callable demographic functions

def initialize_pop(L,prob_list, uncoalesced, size):
    prob_list.append(uncoalesced*prob_L_from_mut_precise(L,0,size))
    return prob_list

### Changes the size of a single population
### MS command: -en t 1 oldsize newsize
def popsize_change(L, prob_list,uncoalesced, oldsize, newsize, t):
    prob_list.append(-uncoalesced*prob_L_from_mut_precise(L,t,oldsize))
    prob_list.append(uncoalesced*prob_L_from_mut_precise(L,t,newsize))
    return prob_list, uncoalesced

### An instantaneous (possibly asymmetric) exchange of genetic material between two populations
### MS command: -es t 1 1-f1 -es 2 1 1-f2 -ej t 3 2 -ej t 4 1  
def two_way_admixture(L, prob_list, uncoal1, uncoal2, uncoal_between,size1,size2,t,f1, f2):
    new_uncoal1=(1-f1)**2*uncoal1+f2**2*uncoal2+(1-f1)*f2*uncoal_between
    new_uncoal2=(1-f2)**2*uncoal2+f1**2*uncoal1+(1-f2)*f1*uncoal_between
    new_between=2*f1*(1-f1)*uncoal1+2*f2*(1-f2)*uncoal2+((1-f1)*(1-f2)+f1*f2)*uncoal_between
    prob_list.append((new_uncoal1-uncoal1)*prob_L_from_mut_precise(L,t,size1))
    prob_list.append((new_uncoal2-uncoal2)*prob_L_from_mut_precise(L,t,size2))
    return prob_list, new_uncoal1, new_uncoal2, new_between

### An instantaneous (possibly asymmetric) exchange of genetic material between two populations. Simultaneous with a size change in one population
### MS command: -es t 1 1-f1 -es 2 1 1-f2 -ej t 3 2 -ej t 4 1 -en t 1 oldsize1 newsize1  
def two_way_admixture_change_one_size(L, prob_list, uncoal1, uncoal2, uncoal_between,oldsize1,size1,size2,t,f1, f2):
    new_uncoal1=(1-f1)**2*uncoal1+f2**2*uncoal2+(1-f1)*f2*uncoal_between
    new_uncoal2=(1-f2)**2*uncoal2+f1**2*uncoal1+(1-f2)*f1*uncoal_between
    new_between=2*f1*(1-f1)*uncoal1+2*f2*(1-f2)*uncoal2+((1-f1)*(1-f2)+f1*f2)*uncoal_between
    prob_list.append(-uncoal1*prob_L_from_mut_precise(L,t,oldsize1))
    prob_list.append((new_uncoal2-uncoal2)*prob_L_from_mut_precise(L,t,size2))
    prob_list.append(new_uncoal1*prob_L_from_mut_precise(L,t,size1))
    return prob_list, new_uncoal1, new_uncoal2, new_between

### An instantaneous (possibly asymmetric) exchange of genetic material between two populations. Simultaneous with size changes in both populations
### MS command: -es t 1 1-f1 -es 2 1 1-f2 -ej t 3 2 -ej t 4 1 -en t 1 oldsize1 newsize1   -en t 2 oldsize2 newsize2
def two_way_admixture_change_both_sizes(L, prob_list, uncoal1, uncoal2, uncoal_between,oldsize1,oldsize2,size1,size2,t,f1, f2):
    new_uncoal1=(1-f1)**2*uncoal1+f2**2*uncoal2+(1-f1)*f2*uncoal_between
    new_uncoal2=(1-f2)**2*uncoal2+f1**2*uncoal1+(1-f2)*f1*uncoal_between
    new_between=2*f1*(1-f1)*uncoal1+2*f2*(1-f2)*uncoal2+((1-f1)*(1-f2)+f1*f2)*uncoal_between
    prob_list.append(-uncoal1*prob_L_from_mut_precise(L,t,oldsize1))
    prob_list.append(-uncoal2*prob_L_from_mut_precise(L,t,oldsize2))
    prob_list.append(new_uncoal1*prob_L_from_mut_precise(L,t,size1))
    prob_list.append(new_uncoal2*prob_L_from_mut_precise(L,t,size2))
    return prob_list, new_uncoal1, new_uncoal2, new_between

### Moves time pointer back in time. Must be called separately for each population in between events that are separated in time.
### No corresponding MS command
def time_lapse(uncoalesced,size, elapsed_time):
    uncoalesced*=exp(-elapsed_time/size)
    return uncoalesced

### Corresponds to population splitting forward in time    
### MS command: -ej t 2 1 -en t 1 newsize
def pop_merge(L, prob_list, uncoal1, uncoal2, uncoal_between, oldsize1, oldsize2, newsize, t):
    prob_list.append(-uncoal1*prob_L_from_mut_precise(L,t,oldsize1))
    prob_list.append(-uncoal2*prob_L_from_mut_precise(L,t,oldsize2))
    uncoal_merged=uncoal1+uncoal2+uncoal_between
    prob_list.append(uncoal_merged*prob_L_from_mut_precise(L,t,newsize))
    return prob_list, uncoal_merged

### Corresponds to ghost admixture forward in time
### MS command: -es t 1 f
def ghost_pop_split(L,prob_list,uncoal, oldsize, newsize_main, newsize_ghost, t, f):
    prob_list.append(-uncoal*prob_L_from_mut_precise(L,t,oldsize))
    ghost_uncoal=f**2*uncoal
    main_uncoal=(1-f)**2*uncoal
    between_uncoal=2*f*(1-f)*uncoal
    prob_list.append(ghost_uncoal*prob_L_from_mut_precise(L,t,newsize_ghost))
    prob_list.append(main_uncoal*prob_L_from_mut_precise(L,t,newsize_main))
    return prob_list, main_uncoal, ghost_uncoal, between_uncoal


