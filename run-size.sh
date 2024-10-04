set -e

## need `gtimeout` in OSX (brew install coreutils) or `timeout` in linux

ver=-2 # test
ver=1001 # @20241004: 
ver=1002 # @20241004: +timeout

rep=1
seed=$(date +%s)
timelimit=3600 # 60 mins

q=0.1
p=1
typ=0

#n1=100
#for n2 in 1000 ; do
#for n2 in 1000 10000 100000; do

n1=100
for n2 in 1000 10000 100000; do
    #for method in "flow" "flowgreedy" "mwm" "forwardgreedy" "greedy" "onlinegreedy" "backwardgreedy" "backwardgreedyproxy"; do
    for method in "forwardgreedy" "greedy" "onlinegreedy" "backwardgreedy" "backwardgreedyproxy"; do
    #for method in "flow" "flowgreedy" "mwm"; do
        # or `timeout` in linux
        gtimeout $timelimit python ex.py -v $ver -r $rep -s $seed -m $method -q $q -d "randombip-$n1-$n2-$p-$typ" 
        if [ $? -eq 124 ]; then
            # Timeout occurred
            echo "timeout: python ex.py -v $ver -r $rep -s $seed -m $method -q $q -d randombip-$n1-$n2-$p-$typ" 
        else
            # No hang
            echo ""
        fi
        #nohup ./build/main/Main -b $buildtype -v $ver -r $rep -s $seed -d random_graph_wTrue_nghb10_n${n}.csv -k 10 -t "note" -m $method  &
    done
done


n2=1000
for n1 in 1000 10000; do
    #for method in "flow" "flowgreedy" "mwm" "forwardgreedy" "greedy" "onlinegreedy" "backwardgreedy" "backwardgreedyproxy"; do
    for method in "forwardgreedy" "greedy" "onlinegreedy" "backwardgreedy" "backwardgreedyproxy"; do
    #for method in "flow" "flowgreedy" "mwm"; do
        gtimeout $timelimit python ex.py -v $ver -r $rep -s $seed -m $method -q $q -d "randombip-$n1-$n2-$p-$typ" 
        if [ $? -eq 124 ]; then
            # Timeout occurred
            echo "timeout: python ex.py -v $ver -r $rep -s $seed -m $method -q $q -d randombip-$n1-$n2-$p-$typ" 
        else
            # No hang
            echo ""
        fi
        #nohup ./build/main/Main -b $buildtype -v $ver -r $rep -s $seed -d random_graph_wTrue_nghb10_n${n}.csv -k 10 -t "note" -m $method  &
    done
done