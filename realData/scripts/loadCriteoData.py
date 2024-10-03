import numpy as np
import sys
from sklearn.cluster import KMeans
import math
import json

fileClusters = "criteo-clust.json"

def loadClustering(filename):
    fr = open(filename, 'r')
    data = json.loads(fr.readlines()[0])
    clustering = data["clustering"]
    k = data["totAdsCategories"]
    fr.close()
    return k, clustering

def dumpJson(data, filename):
	json_object = json.dumps(data, default=str)
	with open(filename, "w") as outfile:
		outfile.write(json_object)

LENVALUES = 13 # from original data description
LENATTRS = 26 # from original data description

f = sys.argv[1]
mode = int(sys.argv[2])
if mode == 1: # clusterize ads with k-means and save file
    file = open(f, 'r')
    vectors = []
    rewards = []
    clicks = 0
    totAdsDisplayed = 0
    for i,line in enumerate(file):
        ch = line.strip().split('\t')
        currkey = ""
        if ch[0] == '1':
            clicks += 1
        #for el in ch[14:]:
        #    currkey = currkey + el + "+"
        #vectors.append(currkey)
        reward = max(sum([int(num) if num != '' else 0 for num in ch[1:LENVALUES+1]]), 0) # reward is sum over numerical counts (we do not know exact meaning)
        attributes = [int(att, 16) if att != '' else np.nan for att in ch[LENVALUES+2:]] # vector encoding attributes
        if(len(attributes) != LENATTRS):
            missing = (LENATTRS - len(attributes))
            for _ in range(missing):
                attributes.append(np.nan)
        currvec = np.array(attributes)
            #print("Len is", attributes.shape[0], len(ch[LENVALUES+2:]))
        vectors.append(currvec)
        rewards.append(reward)
        #print(len(attributes))
        #if(len(ch)< 40):
        #    print(ch[0], ch[1:14], ch[15:], line)
        #print(reward, attributes)
        #print(ch[14:])
        totAdsDisplayed += 1
        #if i > 100000:
        #    break
#print(vectors)
    print("clicks", clicks)
    print("ads displayed", totAdsDisplayed)

    X = np.array(vectors)
    print(X[0])
    print(X.shape[0], X.shape[1])
    missingVals = ~np.isfinite(X) # get nan values bool
    avgColumn = np.nanmean(X, 0) # compute mean ignoring 
    X_no_miss = np.where(missingVals, avgColumn, X)
    print(X_no_miss[0])

# There may be some columns with only nan value, remove them
    X_no_miss_no_nan = X_no_miss[:,~np.all(np.isnan(X_no_miss), axis=0)] 
    print(X_no_miss_no_nan[0])
    tot_clusters = 100
    kmeans = KMeans(n_clusters=tot_clusters, random_state=200, n_init=1).fit(X_no_miss_no_nan)
    assignment = kmeans.labels_
    assignment_list = assignment.tolist()

    clickRate = clicks/(1.*totAdsDisplayed)
    jsonfilename = fileClusters

    dict_data = {
            "dataset":"criteo-ads-clust", 
            "totAdsCategories":tot_clusters, 
            "clustering":assignment_list,
            "clickRate":clickRate 
        }
    dumpJson(dict_data, jsonfilename)
    exit(0)

elif mode == 2: # load clusters and stream of ads and generate bipartite graph
    k, clusts = loadClustering(fileClusters)
    file = open(f, 'r')
    rewards = []
    clicks = 0
    totAdsDisplayed = 0
    for i,line in enumerate(file):
        ch = line.strip().split('\t')
        currkey = ""
        if ch[0] == '1':
            clicks += 1
        reward = max(sum([int(num) if num != '' else 0 for num in ch[1:LENVALUES+1]]), 0) # reward is sum over numerical counts (we do not know exact meaning)
        rewards.append(reward)
        totAdsDisplayed += 1
    file.close()
    print("clicks", clicks)
    print("ads displayed", totAdsDisplayed)

    clickRate = clicks/(1.*totAdsDisplayed)
    time_granularity = 1440 # Display one add every 1 one minute over one day
    totAds =  time_granularity * k
    step = math.floor(totAdsDisplayed/time_granularity)
    edges = [] #(ad, slot, weight)
    current_slot = [0 for _ in range(k)]
    s_idx = 0
    ADSID = 0
    SLOTSID = totAds
    ads_current_slot = 0
    for idx, ad in enumerate(clusts):
        my_pos = min(math.floor(idx/(1.*step)), time_granularity) # keeping bucket position, not used as index!
        if my_pos > s_idx: # Changing time-slot
            curr_w = [el/ads_current_slot for el in current_slot]
            for w in curr_w:
                edges.append([ADSID, SLOTSID, w])
                ADSID += 1
            current_slot = [0 for _ in range(k)] # init empty weights
            s_idx = my_pos # update last slot position
            ads_current_slot = 0
            SLOTSID += 1
        ads_current_slot += 1
        current_slot[clusts[idx]] += rewards[idx] # update weight of current slot according to current ad

    jsonfilename = "criteo-ads-bip.json"

    dict_data = {
            "dataset":"criteo-ads", 
            "totAdsCategories":totAds, 
            "totSlots":time_granularity, 
            "totAdsOrig":totAdsDisplayed, 
            "edges":edges, 
            "clickRate":clickRate 
        }

    dumpJson(dict_data, jsonfilename)

'''
print(len(vectors))
myvect_set =  set(vectors)
print(len(myvect_set))
'''
