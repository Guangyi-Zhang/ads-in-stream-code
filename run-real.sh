set -e


ver=-5 # test
ver=5001 # @20241009: test
ver=5002 # @20241009: 
ver=5003 # @20241009: 

rep=1
seed=$(date +%s)

q=0.1

for data in criteo ; do
    #for method in "flow" "flowgreedy" "mwm" "forwardgreedy" "greedy" "onlinegreedy" "backwardgreedy" "backwardgreedyproxy"; do
    for method in "flowgreedy" "mwm" "forwardgreedy" "greedy" "onlinegreedy" "backwardgreedy" "backwardgreedyproxy"; do
        python ex.py -v $ver -r $rep -s $seed -m $method -q $q -d "realData-$data" 
        #nohup ./build/main/Main -b $buildtype -v $ver -r $rep -s $seed -d random_graph_wTrue_nghb10_n${n}.csv -k 10 -t "note" -m $method  &
    done
done


for data in yt ; do
    for method in "flow" "flowgreedy" "mwm" "forwardgreedy" "greedy" "onlinegreedy" "backwardgreedy" "backwardgreedyproxy"; do
        python ex.py -v $ver -r $rep -s $seed -m $method -q $q -d "realData-$data" 
        #nohup ./build/main/Main -b $buildtype -v $ver -r $rep -s $seed -d random_graph_wTrue_nghb10_n${n}.csv -k 10 -t "note" -m $method  &
    done
done