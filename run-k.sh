set -e

ver=-4 # test
ver=4001 # @20241006: 
ver=4002 # @20241006: 
ver=4003 # @20241006: match_less

rep=3
seed=$(date +%s)
timelimit=3600 # 60 mins

p=1
q=0.1
typ=0
n1=100
n2=1000

for k in 3 10 20 50; do
    # for method in "flow" "flowgreedy" "mwm" "forwardgreedy" "greedy" "onlinegreedy" "backwardgreedy" "backwardgreedyproxy"; do
    for method in "flow" "mwm" "forwardgreedy" "greedy" "onlinegreedy" "backwardgreedy" "backwardgreedyproxy"; do
        python ex.py -v $ver -r $rep -s $seed -m $method -q $q -k $k -d "randombip-$n1-$n2-$p-$typ" 
        #nohup ./build/main/Main -b $buildtype -v $ver -r $rep -s $seed -d random_graph_wTrue_nghb10_n${n}.csv -k 10 -t "note" -m $method  &
    done
done