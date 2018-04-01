#!/usr/bin/python
# -*- coding: utf-8 -*-

# Created by David Teng on 18-3-28


"""
    计算两个字之间的关联性（基于互信息和信息熵的计算）， 以及围绕这个目的相关的一些计算
    主要是依据removetail.py文件中建立起来的词典，进行词频统计和相关互信息和信息熵的计算
"""


from removetail import *
import math

class clcaUtils():

    def __init__(self, dicpath="xinjiang_neimeng_xizang.json", toplimit=10):
        """
        :param dicpath: 加载的词典的路径（xxx_full.json是指语料库去噪程度角较轻，词典较大）
        :param toplimit: 弧边值上限（用来确定分词边界）
        """
        self.wordsdic = loadfulldict(dicpath, False)
        self.sumfreq = self.getsumfreq()
        self.keys = self.wordsdic.keys()
        self.connprob = toplimit       # 最终关联性的阈值

    def getsumfreq(self):
        """
            获取频数的总和
        :return:
        """
        sumfreq = 0
        for v in self.wordsdic.values():
            sumfreq += v
        return sumfreq


    def getsingleprob(self, a):
        """
        获取指定单字的概率
        :param a:
        :return:
        """
        if a not in self.keys:
            print "出现未登录单字"
            return False
        return float(self.wordsdic[a]) / self.sumfreq

        pass

    def getwordsprob(self, a):
        """
        获取指定词的概率
        :param a: 词语
        :return:
        """
        if a not in self.keys:      # 前面的程序保证字都是在词典中的，这里出现由字组成的词不在词典的情况，说明没有这样的搭配
            print "出现未登录词：" , a
            return False
        return float(self.wordsdic[a]) / self.sumfreq
        pass


    def calcmutualinfo(self, a, b, mode='L'):
        """
            计算两个字的互信息
        :param a: 当前中心
        :param b: a的领接字
        :param mode: L或者R， 决定b是a的左或者右领接字
        :return:
        """
        pa = self.getsingleprob(a)
        pb = self.getsingleprob(b)
        # print pa, pb
        if mode == 'L':
            tmpstr = b+a
            p_ba = self.getwordsprob(tmpstr)
            return math.log((p_ba/(pa*pb)), 2)
        else:
            tmpstr = a+b
            p_ab = self.getwordsprob(tmpstr)
            return math.log((p_ab / (pa * pb)), 2)

        pass


    def getneiborwords(self, centerwd, mode="L"):
        """
        求出中心字与其所有的左（右）领接字组成的词以及他们的频数
        :param centerwd: 中心字
        :param mode: 取值 L 或者 R， 表示neborwd是左领接还是右领接
        :return:
        """
        ansdic = {}
        if mode == 'L':
            ansdic = {key:value for key, value in self.wordsdic.items() if key.endswith(centerwd)}
        elif mode == 'R':
            ansdic = {key: value for key, value in self.wordsdic.items() if key.startswith(centerwd)}

        return ansdic
        pass


    def clcainfoEntropy(self, centwd, mode='L'):
        """
        计算指定中心字的左（右）信息熵
        :param centwd: 中心字
        :param neborwd: 领接字
        :param mode: 取值 L 或者 R， 表示求的是左信息熵还是右信息熵
        :return: 返回信息熵的值
        """

        # 求出中心字与其所有的左（右）领接字组成的词以及他们的频数
        neiborwdsdic = self.getneiborwords(centwd, mode)

        # 对每个左（右）领接字计算条件概率P(aw|w) = p(aw)/p(w) 或 P(wb|w) = p(wb)/p(w)
        sum = 0.0
        pw = self.getsingleprob(centwd)
        for k in neiborwdsdic.keys():
            P_aw = self.getwordsprob(k)
            p_cond = P_aw / pw
            sum += p_cond * math.log(p_cond, 2)

        return -sum if sum != 0 else 100    # 等于0说明只有一种搭配且在词典中只出现了一次，属于稀有搭配，给予100，表明相关性很高


    def clcaconnprob(self, centerwd, neiborwd, mode="L"):
        """
            计算中心字与领接字连接成词的可能性
        :param centerwd: 中心字
        :param neiborwd: 领接字
        :param mode: L 或者 R， 指定左邻接或者右邻接
        :return:
        """
        if not self.isindic(centerwd, neiborwd, mode):
            return -1
        MI = self.calcmutualinfo(centerwd, neiborwd, mode=mode)
        E_c = self.clcainfoEntropy(centerwd, mode=mode)
        # E_n = self.clcainfoEntropy(neiborwd, mode="L" if mode == "R" else "L")
        c_cen_nei = MI / E_c
        return c_cen_nei
        pass

    def isindic(self, centerwd, neiborword, mode):
        """
            判断需要测试的中心字，邻接字和组成的词在不在词典中
        :param centerwd:
        :param neiborword:
        :param mode:
        :return:
        """
        testlist= [centerwd, neiborword]
        if mode == "L":
            testlist.append(neiborword+centerwd)
        else:
            testlist.append(centerwd+neiborword)
        for word in testlist:
            if (word not in self.keys):
                return False
        return True

    def Ner_recognition(self, sentence):
        """ 
        少数民族地名的识别
          新疆和静县乌兰乌苏地区综合地质草图                  |
        | 乌兰乌苏地区Ⅰ号地质地球化学剖面图                   |
        | 乌兰乌苏地区Ⅳ号地质地球化学剖面图                   |
        | 地层对比图乌兰乌苏河至托斯台河                      |
        | 乌兰乌苏河至托斯台河地层对比图                      |
        | 新疆和静县乌兰乌苏地区综合地质草图                  |
        | 乌兰乌苏地区Ⅰ号地质地球化学剖面图                   |
        | 乌兰乌苏地区Ⅳ号地质地球化学剖面图 
        """
        
        tmpstr = sentence.strip()
        strlist = list(unicode(tmpstr, 'utf-8'))
        leng = len(strlist)
        taglist = [0] * (leng-1)
        for i, w in enumerate(strlist):
            if w in self.keys:
                # print i
                if i == 0:
                    # print w + strlist[i + 1], self.clcaconnprob(w, strlist[i + 1], "R")
                    # print w + strlist[i + 1], "R"
                    taglist[0] = self.clcaconnprob(w, strlist[i + 1], "R")
                elif i == len(strlist) - 1:
                    # print strlist[-2] + w, self.clcaconnprob(w, strlist[i - 1], "L")
                    taglist[i-1] = self.clcaconnprob(w, strlist[i - 1], "L")
                elif i > 0 and i < len(strlist) - 1:
                    # print strlist[i - 1] + w, self.clcaconnprob(w, strlist[i - 1], "L")
                    # print w + strlist[i + 1], self.clcaconnprob(w, strlist[i + 1], "R")
                    # print strlist[i - 1] + w, "L"
                    taglist[i-1] = self.clcaconnprob(w, strlist[i - 1], "L")
                    # print w + strlist[i + 1], "R"
                    taglist[i] = self.clcaconnprob(w, strlist[i + 1], "R")
                pass
        tmpans = " "
        print taglist
        for index, v in enumerate(taglist):
            tmpans += strlist[index]
            if v in [0, -1]: # or v > self.connprob:
                tmpans += " "
        return tmpans + strlist[-1]
        pass




if __name__ == '__main__':
    testlist = [
        "新疆和静县乌兰乌苏地区综合地质草图",
        "乌兰乌苏地区Ⅰ号地质地球化学剖面图",
        "乌兰乌苏地区Ⅳ号地质地球化学剖面图",
        "地层对比图乌兰乌苏河至托斯台河",
        "乌兰乌苏河至托斯台河地层对比图",
        "新疆和静县乌兰乌苏地区综合地质草图",
        "新疆阿合奇地区矿产远景调查单元素异常登记表",
        " 新疆阿合奇地区矿产远景调查数据库 ",
        " 对《新疆阿合奇地区矿产远景调查报告》初审后修改情况的说明 ",
        " 新疆维吾尔自治区阿合奇地区化探综合异常图1 / 5万 ",
        " 新疆维吾尔自治区琼库尔恰克幅K43E019022矿产远景调查说明书 ",
        " 新疆阿合奇地区矿产远景调查成果地质资料电子文件登记表 ",
        " 新疆维吾尔自治区琼库尔恰克幅区域地质矿产图 ",
        " 新疆维吾尔自治区琼库尔恰克幅矿产预测图 ",
        " 新疆维吾尔自治区琼库尔恰克幅K43E019022矿产远景调查说明书",
        "西藏自治区曲松县康金拉矿区地质草测图",
        " 西藏自治区曲松县香卡山矿区综合地质图",
        "西藏自治区乃东县鲁巴垂铬铁矿点地质草测图",
        "西藏自治区乃东县白岗铬铁矿点地质草测图",
        "西藏“一江两河”地区干旱县江孜县地质地貌图",
        "西藏“一江两河”地区干旱县江孜县综合水文地质图",
        "西藏自治区朗县秀章铬铁矿点地质草测图",
        "内蒙古1：20万达莱滨湖、兴安里、阿里河、克一河镇幅航磁△T异常等值线平面图1 / 20万",
        "内蒙古额济纳旗赛汉陶来大狐狸山石炭—二叠系干泉组实测剖面综合柱状图",
        "内蒙古乌拉特后旗赛乌素镇乌兰敖包石炭—二叠系阿木山组下段实测剖面综合柱状图",
    ]
    # c = clcaUtils("xinjiang_neimeng_xizang_full.json", 20)
    c = clcaUtils("xinjiang_neimeng_xizang.json", 10)
    # import jieba
    for item in testlist:
        # 举例 ： "托斯台"在生成词典的语料库中没有，但是能识别出来
        print c.Ner_recognition(item)

        # 结巴分词对比
        # tmpstr = ""
        # for i in jieba.cut(item.strip()):
        #     tmpstr += i + " "
        # print "jieba: ",tmpstr


    pass
