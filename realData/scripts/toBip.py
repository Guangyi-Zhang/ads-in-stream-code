import sys
import pandas as pd
import random
import json

def dumpJson(data, filename):
	json_object = json.dumps(data, default=str)
	with open(filename, "w") as outfile:
		outfile.write(json_object)

def getMeanAndStd(values):
    mean = sum(values)/(1.*len(values))
    var = sum([(v-mean)**2 for v in values])/(1.*len(values))
    std = var**0.5
    return mean, std

fname = sys.argv[1]


#if(fname == "dow_jones_index.data"):
df = pd.read_csv(fname, sep=",", header=0)
print(df)
print(df.category.unique())
print(df['category'].value_counts())
videos = []
rewards = [[] for _ in range(len(df.category.unique()))] # keep all values for mean and variance, as we will draw weights as normally distributed
totCats = [0 for _ in range(len(df.category.unique()))]
categories = [[] for _ in range(len(df.category.unique()))] # i-th position list [video_1,,..., video_k]
X = df.to_numpy()
remapCat = {}
IDC = 0
for idx,video in enumerate(X):
    videoCat = video[-1]
    if videoCat not in remapCat.keys():
        remapCat[videoCat] = IDC
        IDC += 1
    myCatID = remapCat[videoCat]
    rewards[myCatID].append(video[1]) # adview 
    categories[myCatID].append(idx) # save video id to category 
    videos.append(myCatID)

# Find random order
random.seed(100)
for i in range(len(categories)):
    random.shuffle(categories[i])

#start from the first category
curr_cat = 0
video_id = categories[curr_cat][0]
positions = [0 for _ in range(len(categories))]
positions[curr_cat] += 1
catAlive = [True for _ in range(len(categories))]
#taken = [False for _ in range(len(videos))]
#taken[video_id] = True
order = [video_id]
for i in range(len(videos)-1):
    rtoss = (random.random() < 0.5)
    cat_exp = -1
    if rtoss and (catAlive[curr_cat]):
        cat_exp = curr_cat
    else:
        cv = []
        for cat in range(len(categories)):
            if catAlive[cat]:
                cv.append(cat)
        cat_exp = random.choice(cv)

    index = positions[cat_exp]
    order.append(categories[cat_exp][index])
    positions[cat_exp] += 1
    if positions[cat_exp] == len(categories[cat_exp]):
        catAlive[cat_exp] = False
    curr_cat = cat_exp

means = []
stds = []
for rewC in rewards:
    me, std = getMeanAndStd(rewC)
    means.append(me)
    stds.append(std)
    #print(rewC)
items = []
shrink = 0.01
myshrink = 0.8
totN1 = len(categories) * len(order) # ads
totN2 = len(order) # weight
edges = [] # (ad, video, weight)
IDL1 = 0
IDL2 = totN1
for video in order:
    videoc = videos[video]
    rewardWeights = []
    for index, vals in enumerate(zip(means,stds)):
        rew = abs(random.gauss(mu=vals[0], sigma=vals[1]))
        weight = myshrink if index == videoc else shrink
        rewardWeights.append(weight*rew)
    for re in rewardWeights:
        edges.append([IDL1, IDL2, re])
        IDL1 += 1
    IDL2 += 1

jsonfilename = "youtube-ads.json"
dict_data = {
		"dataset":"youtube-adv", 
		"totAdsCategories":totN1, 
		"totSlots":totN2, 
		"edges":edges, 
    }

dumpJson(dict_data, jsonfilename)



#print(order)
    


# Draw random rewards for edges


#df1 = df.drop(['date','percent_change_volume_over_last_wk','previous_weeks_volume'], axis=1)
#mapStocks = {}
#counter = count(0)
#df1['stock'] = df1['stock'].apply(lambda x: remapStocks(x, mapStocks, counter))
#df1['open'] = df1['open'].str.replace('$', '')
#df1['high'] = df1['high'].str.replace('$', '')
#df1['low'] = df1['low'].str.replace('$', '')
#df1['close'] = df1['close'].str.replace('$', '')
#df1['next_weeks_open'] = df1['next_weeks_open'].str.replace('$', '')
#df1['next_weeks_close'] = df1['next_weeks_close'].str.replace('$', '')
