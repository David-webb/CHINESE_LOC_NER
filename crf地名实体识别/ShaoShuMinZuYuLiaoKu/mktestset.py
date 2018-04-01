#!/usr/bin/python
# -*- coding: utf-8 -*-

# Created by David Teng on 18-3-30

from clcaUtils import clcaUtils
import jieba
import codecs

"""
 NGAC标题数据中关于新疆、西藏、内蒙古三地的信息统计：
    新疆：   68082
    西藏：   9834
    内蒙古： 40177
"""

def gettestset(sfpath, tfpath,step=100, mode='w'):
    """
        从原始语料库ngac_title中提取一些标题
    :param sfpath: 源文件
    :param tfpath: 目标文件
    :param step: 步长（设置步长是因为源文件中，差不多每10条为一组，标题都差不多描述同一对象）
    :param mode: w: 重写， a： 追加
    :return:
    """
    with open(sfpath, 'r')as rd:
        lines = rd.readlines()
    anslines = lines[::step]
    with open(tfpath, mode)as wr:
        for line in anslines:
            wr.write(line)
    pass


def mktestset(fpath, fullmode=False):
    """
        在词典和测试文件建立好后，对测试数据进行识别， 最终的识别结果保存在"testset/goldset_1(_full).txt"
        在gettestset的基础上制作标准的测试数据集： jieba + 手工的方式
    :param fpath: 测试集原料路径
    :return:
    """
    if fullmode:
        dicpath = "xinjiang_neimeng_xizang_full.json"
    else:
        dicpath = "xinjiang_neimeng_xizang.json"
    # c = clcaUtils("xinjiang_neimeng_xizang_full.json", 16)
    c = clcaUtils(dicpath, 10)


    with open(fpath, 'r')as rd:
        testlist = rd.readlines()

    finalanslist = []
    for item in testlist:
        # 举例 ： "托斯台"在生成词典的语料库中没有，但是能识别出来
        item = item.strip()
        if item == "":
            continue
        tmpstr = c.Ner_recognition(item)
        strlist = tmpstr.split()
        anstr = ""
        for s in strlist:
            if len(s) == 1:
                anstr += s
            else:
                anstr + " "
                anstr += "[" + s + "]/ns"
                anstr += " "
        print anstr.strip()
        finalanslist.append(anstr.strip())
    # print finalanslist

    savepath = "testset/goldset_1.txt"
    if fullmode:
        savepath = "testset/goldset_1_full.txt"
    with codecs.open(savepath, "w", encoding='utf-8')as wr:
        for line in finalanslist:
            wr.write(line)
            wr.write("\n")

if __name__ == '__main__':
    # 提取用于制作测试集的原料
    # gettestset('neimenggu_testset_ngac.txt', "testset_ngac.txt")
    # gettestset("xinjiang_testset_ngac.txt", "testset_ngac.txt", mode='a')
    # gettestset("xizang_testset_ngac.txt", "testset_ngac.txt", mode='a')

    # 制作测试集
    mktestset("testset/testset_ngac.txt", False)

    # 语义
    "关于下发2007年度[自治区]/ns 两权使用费河价款出资（第三 批招标项目）[新疆]/ns [乌鲁木齐市]/ns [米东区]/ns [铁厂沟镇]/ns 等5个地质灾害专项勘查设计书评审意见的通知" # 完全识别正确
    "[新疆]/ns [和布克赛尔蒙古自治县]/ns 地质灾害防治规划图" # 完全识别
    "[内蒙古]/ns [乌拉特中]/ns 后联合旗[白音察汗]/ns 矿区 钴矿普查地质报告"  # 乌拉特中后联合旗：乌拉特中旗、乌拉特后旗
    "[内蒙古]/ns [乌兰]/ns [白旗]/ns 幅ETM-SPOT－5融合图像" # 语料中的错别字，实际应为：乌兰白其
    "[内蒙]/ns [锡盟]/ns [二连]/ns 一带超基性岩普查勘探年终报告"        # 锡盟：锡林郭勒盟的简称
    "3[内蒙]/ns [伊盟]/ns [棹子山]/ns[岗德尔]/ns铅矿地质图1/2千"               # 伊盟:伊克昭盟即鄂尔多斯市的旧称
    "24[内蒙]/ns [哲昭盟]/ns 南部[杨树沟]/ns 附近地貌图1/5万"          # 哲昭盟： 哲盟、昭盟
    "31[内蒙古自治区]/ns [四子王旗]/ns[白乃庙]/ns金矿26号脉第34勘探线剖面图1/5百" # 白乃庙: 5级以下地名,以及其他未登录词的识别不出来的情况
    "[内蒙古自治区]/ns [阿拉善左旗吉兰泰]/ns [盐湖]/ns 供水水化学图" # 阿拉善左旗吉兰泰: 阿拉善左旗，吉兰泰, 层级关系无法识别
    "[新疆]/ns [青河县]/ns [科克]/ns 玉依矿区 闪长岩饰面石材矿Ht3体解论荒料率统计水平叠合图1∶50" # 识别一半,应该是[科克玉依]/ns
    "[新疆]/ns [巴里坤县巴里坤]/ns 矿区 [别斯]/ns [库都克]/ns 露天煤矿 水文地质图" # 地名被拆分  针对这种情况，将识别出的相邻的地名连接，去地名词表中查询，因此还要保持原有的地名词表
    "[新疆]/ns [乌恰县]/ns [伊日]/ns [库勒]/ns 铜矿Ⅲ号矿体2190中段平面图" # 同上
    "[新疆]/ns [和什托洛盖]/ns 煤田[和布克赛尔蒙古自治县]/ns 布腊图勘查区详查报告2-08钻孔柱状图" # 识别度不错，除了“布腊图”

    "[新疆]/ns [乌恰县]/ns [铁克塔什]/ns 铅矿详查报告" # 铁克塔什 未登录词，但是符合用语特征
    pass
