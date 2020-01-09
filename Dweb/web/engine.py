import pandas as pd
import numpy as np
import math
from tqdm import trange
from scipy.sparse import csc_matrix,linalg,eye

def loadData():
    fp = 'C:/Users/hasee/Desktop/tags.csv'
    data = pd.read_csv(open(fp))
    data = data.iloc[:,:-2].values
    data = data.tolist()
    #转化成字典形式
    dataset = {}
    for i in range(len(data)):
        userId = data[i][0]
        movieId = data[i][1]
        if userId not in dataset.keys():
            dataset.setdefault(userId, []).append(movieId)
        else:
            dataset[userId].append(movieId)
    return dataset

def loadMovieName():
    file = 'C:/Users/hasee/Desktop/movies.csv'
    data = pd.read_csv(open(file,'rb'))
    data = data.iloc[:,:-1].values
    data = data.tolist()
    return data

#评价指标
class Metric():

    def __init__(self, train, test, Recommend):
        '''
        :params: train, 训练数据
        :params: test, 测试数据
        :params: Recommend, 为某个用户获取推荐物品的接口函数
        '''
        self.train = train
        self.test = test
        self.Recommend = Recommend
        self.recs = self.getRec()

    # 为test中的每个用户进行推荐
    def getRec(self):
        recs = {}
        for user in self.test:
            rank = self.Recommend(user)
            recs[user] = rank
        return recs

    # 定义精确率指标计算方式
    def precision(self):
        all, hit = 0, 0
        for user in self.test:
            test_items = set(self.test[user])
            rank = self.recs[user]
            for item, score in rank:
                if item in test_items:
                    hit += 1
            all += len(rank)
        return round(hit / all * 100, 2)

    # 定义召回率指标计算方式
    def recall(self):
        all, hit = 0, 0
        for user in self.test:
            test_items = set(self.test[user])
            rank = self.recs[user]
            for item, score in rank:
                if item in test_items:
                    hit += 1
            all += len(test_items)
        return round(hit / all * 100, 2)

    # 定义覆盖率指标计算方式
    def coverage(self):
        all_item, recom_item = set(), set()
        for user in self.test:
            for item in self.train[user]:
                all_item.add(item)
            rank = self.recs[user]
            for item, score in rank:
                recom_item.add(item)
        return round(len(recom_item) / len(all_item) * 100, 2)

    # 定义新颖度指标计算方式
    def popularity(self):
        # 计算物品的流行度
        item_pop = {}
        for user in self.train:
            for item in self.train[user]:
                if item not in item_pop:
                    item_pop[item] = 0
                item_pop[item] += 1

        num, pop = 0, 0
        for user in self.test:
            rank = self.recs[user]
            for item, score in rank:
                # 取对数，防止因长尾问题带来的被流行物品所主导
                pop += math.log(1 + item_pop[item])
                num += 1
        return round(pop / num, 6)

    def eval(self):
        metric = {'Precision': self.precision(),
                  'Recall': self.recall(),
                  'Coverage': self.coverage(),
                  'Popularity': self.popularity()}
        print('Metric:', metric)
        return metric

#基于物品的协同过滤
#基于归一化的物品余弦相似度的推荐
def ItemCF_Norm(train, K, N):
    '''
        :params: train, 训练数据集
        :params: K, 超参数，设置取TopK相似物品数目
        :params: N, 超参数，设置取TopN推荐物品数目
        :return: Recommend, 推荐接口函数
        '''
    # 计算物品相似度矩阵
    sim = {}
    num = {}
    for user in train:
        items = train[user]
        for i in range(len(items)):
            u = items[i]
            if u not in num:
                num[u] = 0
            num[u] += 1
            if u not in sim:
                sim[u] = {}
            for j in range(len(items)):
                if j == i: continue
                v = items[j]
                if v not in sim[u]:
                    sim[u][v] = 0
                sim[u][v] += 1
    for u in sim:
        for v in sim[u]:
            sim[u][v] /= math.sqrt(num[u] * num[v])

    # 对相似度矩阵进行按行归一化
    for u in sim:
        s = 0
        for v in sim[u]:
            s += sim[u][v]
        if s > 0:
            for v in sim[u]:
                sim[u][v] /= s

    # 按照相似度排序
    sorted_item_sim = {k: list(sorted(v.items(), \
                                      key=lambda x: x[1], reverse=True)) \
                       for k, v in sim.items()}

    # 获取接口函数
    def Recommend(user):
        items = {}
        seen_items = set(train[user])
        for item in train[user]:
            for u, _ in sorted_item_sim[item][:K]:
                if u not in seen_items:
                    if u not in items:
                        items[u] = 0
                    items[u] += sim[item][u]
        recs = list(sorted(items.items(), key=lambda x: x[1], reverse=True))[:N]
        return recs

    return Recommend

#基于用户的协同过滤
#基于改进的用户余弦相似度的推荐
def UserIIF(train, K, N):
    '''
    :params: train, 训练数据集
    :params: K, 超参数，设置取TopK相似用户数目
    :params: N, 超参数，设置取TopN推荐物品数目
    :return: Recommend, 推荐接口函数
    '''
    # 计算item->user的倒排索引
    item_users = {}
    for user in train:
        for item in train[user]:
            if item not in item_users:
                item_users[item] = []
            item_users[item].append(user)

    # 计算用户相似度矩阵
    sim = {}
    num = {}
    for item in item_users:
        users = item_users[item]
        for i in range(len(users)):
            u = users[i]
            if u not in num:
                num[u] = 0
            num[u] += 1
            if u not in sim:
                sim[u] = {}
            for j in range(len(users)):
                if j == i: continue
                v = users[j]
                if v not in sim[u]:
                    sim[u][v] = 0
                # 相比UserCF，主要是改进了这里
                sim[u][v] += 1 / math.log(1 + len(users))
    for u in sim:
        for v in sim[u]:
            sim[u][v] /= math.sqrt(num[u] * num[v])

    # 按照相似度排序
    sorted_user_sim = {k: list(sorted(v.items(), \
                                      key=lambda x: x[1], reverse=True)) \
                       for k, v in sim.items()}

    # 获取接口函数
    def Recommend(user):
        items = {}
        seen_items = set(train[user])
        for u, _ in sorted_user_sim[user][:K]:
            for item in train[u]:
                # 要去掉用户见过的
                if item not in seen_items:
                    if item not in items:
                        items[item] = 0
                    items[item] += sim[user][u]
        recs = list(sorted(items.items(), key=lambda x: x[1], reverse=True))[:N]
        return recs

    return Recommend

#隐语义模型
def LFM(train, ratio, K, lr, step, lmbda, N):
    '''
    :params: train, 训练数据
    :params: ratio, 负采样的正负比例
    :params: K, 隐语义个数
    :params: lr, 初始学习率
    :params: step, 迭代次数
    :params: lmbda, 正则化系数
    :params: N, 推荐TopN物品的个数
    :return: Recommend, 获取推荐结果的接口
    '''

    all_items = {}
    for user in train:
        for item in train[user]:
            if item not in all_items:
                all_items[item] = 0
            all_items[item] += 1
    all_items = list(all_items.items())
    items = [x[0] for x in all_items]
    pops = [x[1] for x in all_items]

    # 负采样函数(按照流行度进行采样)
    def nSample(data, ratio):
        new_data = {}
        # 正样本
        for user in data:
            if user not in new_data:
                new_data[user] = {}
            for item in data[user]:
                new_data[user][item] = 1
        # 负样本
        for user in new_data:
            seen = set(new_data[user])
            pos_num = len(seen)
            item = np.random.choice(items, int(pos_num * ratio * 3), pops)
            item = [x for x in item if x not in seen][:int(pos_num * ratio)]
            new_data[user].update({x: 0 for x in item})

        return new_data

    # 训练
    P, Q = {}, {}
    for user in train:
        P[user] = np.random.random(K)
    for item in items:
        Q[item] = np.random.random(K)

    for s in trange(step):
        data = nSample(train, ratio)
        for user in data:
            for item in data[user]:
                eui = data[user][item] - (P[user] * Q[item]).sum()
                P[user] += lr * (Q[item] * eui - lmbda * P[user])
                Q[item] += lr * (P[user] * eui - lmbda * Q[item])
        lr *= 0.9  # 调整学习率

    # 获取接口函数
    def Recommend(user):
        seen_items = set(train[user])
        recs = {}
        for item in items:
            if item not in seen_items:
                recs[item] = (P[user] * Q[item]).sum()
        recs = list(sorted(recs.items(), key=lambda x: x[1], reverse=True))[:N]
        return recs

    return Recommend

#基于图的PersonalRank推荐算法
def PersonalRank(train, alpha, N):
    '''
    :params: train, 训练数据
    :params: alpha, 继续随机游走的概率
    :params: N, 推荐TopN物品的个数
    :return: Recommend, 获取推荐结果的接口
    '''

    # 构建索引
    items = []
    for user in train:
        items.extend(train[user])
    id2item = list(set(items))
    users = {u: i for i, u in enumerate(train.keys())}
    items = {u: i + len(users) for i, u in enumerate(id2item)}

    # 计算转移矩阵（按照出度进行归一化）
    item_user = {}
    for user in train:
        for item in train[user]:
            if item not in item_user:
                item_user[item] = []
            item_user[item].append(user)

    data, row, col = [], [], []
    for u in train:
        for v in train[u]:
            data.append(1 / len(train[u]))
            row.append(users[u])
            col.append(items[v])
    for u in item_user:
        for v in item_user[u]:
            data.append(1 / len(item_user[u]))
            row.append(items[u])
            col.append(users[v])

    M = csc_matrix((data, (row, col)), shape=(len(data), len(data)))

    # 获取接口函数
    def Recommend(user):
        seen_items = set(train[user])
        # 解矩阵方程 r = (1-a)r0 + a(M.T)r
        r0 = [0] * len(data)
        r0[users[user]] = 1
        r0 = csc_matrix(r0)
        r = (1 - alpha) * linalg.inv(eye(len(data)) - alpha * M.T) * r0.T
        r = r.T.toarray()[0][len(users):]
        idx = np.argsort(-r)[:N]
        recs = [(id2item[ii], r[ii]) for ii in idx]
        return recs

    return Recommend

#热门推荐
def MostPopular(train, N):
    '''
    :params: train, 训练数据集
    :params: N, 超参数，设置取TopN推荐物品数目
    :return: Recommend, 推荐接口函数
    '''
    items = {}
    for user in train:
        for item in train[user]:
            if item not in items:
                items[item] = 0
            items[item] += 1

    def Recommend(user):
        # 随机推荐N个没见过的最热门的
        user_items = set(train[user])
        rec_items = {k: items[k] for k in items if k not in user_items}
        rec_items = list(sorted(rec_items.items(), key=lambda x: x[1], reverse=True))
        return rec_items[:N]

    return Recommend

def recommendMovieName(algorithm,userId):
    dataset = loadData()
    if algorithm == 'ItemCF_Norm':
        recommend = ItemCF_Norm(dataset,5,5)
    elif algorithm == 'UserIIF':
        recommend = UserIIF(dataset, 5, 5)
    elif algorithm == 'LFM':
        recommend = LFM(dataset,ratio=1,K=100,lr=0.02,step=100,lmbda=0.01,N=5)
    elif algorithm == 'PersonalRank':
        recommend = PersonalRank(dataset,alpha=0.8,N=5)
    elif algorithm == 'MostPopular':
        recommend = MostPopular(dataset,5)
    commendId = recommend(userId)
    nameData = loadMovieName()
    finalName = []
    for i in range(len(commendId)):
        for j in range(len(nameData)):
            if commendId[i][0] == nameData[j][0]:
                finalName.append(nameData[j][1])
    return finalName

if __name__ == "__main__":
    # print('--ItemCF_Norm--')
    # recMovie = recommendMovieName('ItemCF_Norm',2)
    # print(recMovie)
    # print('--UserIIF--')
    # recMovie = recommendMovieName('UserIIF',2)
    # print(recMovie)
    # print('--LFM--')
    # recMovie = recommendMovieName('LFM',2)
    # print(recMovie)
    # print('--PersonalRank--')
    # recMovie = recommendMovieName('PersonalRank',2)
    # print(recMovie)
    # print('--MostPopular--')
    recMovie = recommendMovieName('MostPopular',2)
    print(recMovie[0][0:-7])