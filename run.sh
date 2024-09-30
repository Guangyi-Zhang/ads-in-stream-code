set -e


ver=-1 # test
ver=1 # @20240929
ver=2 # @20240930
ver=-1 # test

rep=1
seed=$(date +%s)
seed=1727604251

q=0.1
p=1
typ=1

#n1=100
#for n2 in 1000 ; do
#for n2 in 1000 10000 100000; do

n1=100
for n2 in 1000 ; do

#n1=10
#for n2 in 20 ; do
    for method in "flow" "mwm" "forwardgreedy" "greedy" "onlinegreedy" "backwardgreedy" "obliviousgreedy"; do
    #for method in "greedy" ; do
        python ex.py -v $ver -r $rep -s $seed -m $method -q $q -d "randombip-$n1-$n2-$p-$typ" 
        #nohup ./build/main/Main -b $buildtype -v $ver -r $rep -s $seed -d random_graph_wTrue_nghb10_n${n}.csv -k 10 -t "note" -m $method  &
    done
done
