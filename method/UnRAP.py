
# coding: utf-8


import pandas as pd
import numpy as np


# 测试数据。
#df1 = pd.DataFrame({'user':['u1','u2','u3','u2','u3','u4'],'item':['i1','i1','i1','i2','i3','i1'], 'rate':[1,2,3,4,5,2]}, columns=['user','item','rate'])
df = pd.read_excel('testdata.xlsx', header=None, names=['user','item','rate'])
# 取前1000行做测试，数据量太大会使计算Hv的过程耗费大量时间。
df = df.iloc[:500,:]


grouped = df['rate'].groupby(df['user'])

# rui、rUi、ruI用来计算user的Hv
rui = df.groupby(['user', 'item']).sum()
rUi = df.groupby(['item']).sum()
ruI = df.groupby(['user']).sum()


# shape[0]返回长度
user_count = ruI.shape[0]
item_count = rUi.shape[0]
rUI = rui['rate'].sum() / item_count / user_count


# 获取用户user对项目item的评分，如果不存在则返回0.
def get_rate(user, item):
    try:
        return rui.loc[user,item].rate
    except:
        return 0


# average列用于Hv(u)公式中的rUi项
rUi['average'] = rUi.apply(lambda x:x/user_count)


# average列用于Hv(u)公式中的ruI项
ruI['average'] = ruI.apply(lambda x:x/item_count)


# Hv(u)计算
def hv(user):
    # 分子
    numerator = 0
    # 分母
    denominator = 0
    for item in rUi.index:
        numerator += (get_rate(user, item) - rUi.loc[item]['average'] - ruI.loc[user]['average'] + rUI)**2
        denominator += (get_rate(user, item) - ruI.loc[user]['average'])**2
    return numerator / denominator


# 创建新的DataFrame，用户保存每个用户的Hv值
users = pd.DataFrame(ruI.index, columns=['user'])
users['hv'] = users.user.apply(lambda x:hv(x))
#print users
#print ruI.index


# 根据Hv排序，得到top10用户
top100 = users.sort_values(by='hv', ascending=False)
#print top100['user']
top10 = users.sort_values(by='hv', ascending=False)[:10]
#print top10

RUI = top100.groupby(['user']).sum()
#print RUI


#print  rUi.index
# 遍历每个item，计算top10中每个用户对该item的评分，形成一个数组，计算该数组的偏差，找到最大偏差时的item，即为目标item
target_item = None
max_deviation = -1
for item in rUi.index:
    rates = np.array([get_rate(user, item) for user in top10['user']])
    if np.std(rates) > max_deviation:
        target_item = item
        max_deviation = np.std(rates)
        
print target_item

#与top10的平均分作比较判断是PUSH或者NUKE
sumrates = 0
i = 0
for user in top10['user']:
    r = get_rate(user, target_item)
    sumrates += r;
averagerate = sumrates / 10;
flag = 'PUSH'
if(averagerate > 3):
    flag = 'PUSH'
else:
    flag = 'NUKE'
    
print flag

#寻找stoppoint
for i in range(0,16901):
	rates1 = np.array([get_rate(user, target_item) for user in top100['user'][i:i+10]])
#	print rates1
	if((np.std(rates1)>=0 and flag == 'NUKE') or (np.std(rates1)<=0 and flag == 'PUSH')):
		print top100['user'][i+10:i+11]
		stoppoint=i+10
		break

			
#对stoppoint之前的用户继续进行检测，逐步remove掉正常用户，最后得到的用户列表为虚假用户 

headlist=list(top100['user'][0:stoppoint])
for user in headlist:
	if get_rate(user, target_item)==0 or (flag == 'PUSH' and get_rate(user, target_item)<grouped.mean()[user]) or (flag == 'NUKE' and get_rate(user, target_item)>grouped.mean()[user]):
		headlist.remove(user)

print headlist


