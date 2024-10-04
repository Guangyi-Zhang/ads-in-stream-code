set -e

ver=-3 # test
ver=2001 # @20241004: 

rep=1
seed=$(date +%s)
timelimit=3600 # 60 mins

p=1
typ=0
n1=100
n2=1000

for q in 0.1 0.3 0.5 0.7 0.9; do
    for method in "flow" "flowgreedy" "mwm" "forwardgreedy" "greedy" "onlinegreedy" "backwardgreedy" "backwardgreedyproxy"; do
        python ex.py -v $ver -r $rep -s $seed -m $method -q $q -d "randombip-$n1-$n2-$p-$typ" 
        #nohup ./build/main/Main -b $buildtype -v $ver -r $rep -s $seed -d random_graph_wTrue_nghb10_n${n}.csv -k 10 -t "note" -m $method  &
    done
done