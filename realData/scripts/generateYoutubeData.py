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
K = int(sys.argv[2])


#load raw youtube data
df = pd.read_csv(fname, sep=",", header=0)
print(df)
print(df.category.unique())
print(df['category'].value_counts())
videos = []
rewards = [[] for _ in range(len(df.category.unique()))] # keep all values for mean and variance for each category, as we will draw weights as normally distributed
totCats = [0 for _ in range(len(df.category.unique()))] # number of videos for each category
categories = [[] for _ in range(len(df.category.unique()))] # i-th position list [video_1,,..., video_|category_i|]
X = df.to_numpy()
remapCat = {}
IDC = 0
# iterate videos and store sum of rewards, as well as split categories
for idx,video in enumerate(X):
    videoCat = video[-1]
    if videoCat not in remapCat.keys():
        remapCat[videoCat] = IDC
        IDC += 1
    myCatID = remapCat[videoCat]
    rewards[myCatID].append(video[1]) # adview 
    categories[myCatID].append(idx) # save video id to category 
    videos.append(myCatID)

# Find random order of all videos, we will use a random-walk like model
random.seed(100)
for i in range(len(categories)):
    random.shuffle(categories[i])

#start from a first random category and pick a random video
curr_cat = 0
video_id = categories[curr_cat][0]
positions = [0 for _ in range(len(categories))]
positions[curr_cat] += 1
catAlive = [True for _ in range(len(categories))]
order = [video_id]
# to find the ordering over the remaining videos
for i in range(len(videos)-1):
    # with probability 0.5 pick another random video in the same category
    rtoss = (random.random() < 0.5)
    cat_exp = -1
    if rtoss and (catAlive[curr_cat]):
        cat_exp = curr_cat
    # otherwise draw a video from a diffrent category u.a.r
    else:
        cv = []
        for cat in range(len(categories)):
            if catAlive[cat]:
                cv.append(cat)
        cat_exp = random.choice(cv)

    # append the video in the list
    index = positions[cat_exp]
    order.append(categories[cat_exp][index])
    positions[cat_exp] += 1
    if positions[cat_exp] == len(categories[cat_exp]):
        catAlive[cat_exp] = False
    curr_cat = cat_exp

# we now need the average and std over video categories (this is from original data)
means = []
stds = []
for rewC in rewards:
    me, std = getMeanAndStd(rewC)
    means.append(me)
    stds.append(std)

# create an empty slot S_i after each video i
# and a total of K advertisers offering |categories| ads (K*len(categories)), i.e., adv_1^{c_1},... ,adv_1^{|cat|},adv_K^{c_1},... ,adv_K^{|cat|}
# each ad can be assigned to each slot S_i, the reward is normally distributed and shrinked by 0.8 if the video matches the ad category, otherwise shrinked by 0.01
items = []
shrink = 0.01
myshrink = 0.8
totN1 = len(categories) * K # ads
totN2 = len(order) # weight
edges = [] # (ad, video, weight)
IDL1 = 0
IDL2 = totN1
for video in order:
    videoc = videos[video]
    IDL1 = 0
    for j in range(K):
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
