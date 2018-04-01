#!/usr/bin/python
# -*- coding: utf-8 -*-

# Created by David Teng on 18-3-28

"""
    对语料库进行筛选并制作词典
    通过观察发现，内蒙和新疆的地名中以下面tailist中元素结尾的大都没有什么地域特色或者就是普通汉语地名，因此对于这类地名全部删除
    而西藏地名中，所有的地名基本上都属于音译地名，所以只对其删除后缀处理
    数据库导出的数据中存在"?"字符，数量不多，不影响结果，所以没有剔除...

    注意：更正一下，在代码实现中，提供了两种处理地名后缀的模式，remove和clean，clean模式不是符合后缀的单词都删掉，详情看代码备注
"""
import json

def removetail(word, mode="del"):
    """
       去除少数民族地名中的（"社区居委会"、 "社区"、"居委会"、"村委会"）等后缀
       去除方式为删除整个词，这样做样本总数会小很多，样本特征更集中
       不同于下面的cleantail函数
       :return:
       """
    word = word.strip()
    # print word
    # 需要去除的后缀
    tailist = ["社区居委会", "社区", "居委会", "村民委员会", "居民委员会", "委员会", "村委会",
               "街道办事处", "办事处", "管理区", "地区", "矿区", "试验站", "工业园区", "有限责任公司"]  # list中的元素顺序不能错
    # 需要删除整个词的后缀
    del_tailist = ["队", "连", "团", "分场", "场村", "团部", "场部", "生活区", "市辖区"]  # list中的元素顺序不能错

    noise_strlist = ["综合", "地区", "矿区", "生活区", "石灰", "工业", "建设", "技术", "石油", "实验", "生产", "有限责任公司"]
    tailist.extend(del_tailist)
    for tail in tailist:
        if word.endswith(tail):
            if mode != 'del':
                word = word.replace(tail, "")
            else:
                word = ""
    for ns in noise_strlist:
        if ns in word:
            word = ""
    return word


def cleantail(word, mode="del"):
    """
    去除少数民族地名中的（"社区居委会"、 "社区"、"居委会"、"村委会"）等后缀
    :return:
    """
    word = word.strip()
    # print word
    # 需要去除的后缀
    tailist = ["社区居委会", "社区","居委会", "村民委员会", "居民委员会", "委员会","村委会",
               "街道办事处", "办事处", "管理区","地区","矿区","试验站", "工业园区", ]  # list中的元素顺序不能错
    # 需要删除整个词的后缀
    del_tailist = ["队", "连", "团", "分场","场村", "团部", "场部","生活区", "市辖区"] # list中的元素顺序不能错
    noise_strlist = ["综合", "地区", "矿区",  "生活区", "石灰", "工业", "建设", "技术","石油", "实验", "生产", "有限责任公司"]
    for tail in tailist:
        if word.endswith(tail):
                word = word.replace(tail, "")

    if mode == 'del':
        for tail in del_tailist:
            if word.endswith(tail):
                word = ""

    for ns in noise_strlist:
        if ns in word:
            word = ""
    return word

def processYuliaoku(procmode='clean'):
    """
        从数据库(博雅)文件中导出的西藏、新疆、内蒙三地精确到乡村级的地名数据进行后缀预处理
    :param procmode:
            “clean”模式： 部分地名去后缀、部分地名（符合后缀匹配）删除
            “remove”模式： 所有符合后缀匹配的地名删除
    :return:
    """
    # tmpstr = "学而思沃土居委会"
    # print tmpstr.replace("居委会", ""), tmpstr
    filelist = ["neimenggu.txt", "xinjiang.txt", "xizang.txt"]
    mode = 'del'
    for file in filelist:
        with open(file, 'r')as rd:
            oldlines = rd.readlines()
        if file == "xizang.txt": mode = 'No_del'
        procfunc = cleantail if procmode == "clean" else removetail
        # newlines = [cleantail(line, mode) for line in oldlines]
        newlines = [procfunc(line, mode) for line in oldlines]
        newfile = file.replace(".txt", "") + "_new.txt"
        with open(newfile, "w")as wr:
            for line in newlines:
                if line:
                    wr.write(line + '\n')



def countsingleword(wdict, sentence):
    """ 统计句子中的字， 并且更新字典"""
    wdlist = list(unicode(sentence, "utf-8"))
    for i in wdlist:
        if i in wdict.keys():
            wdict[i] += 1
        else:
            wdict[i] = 1
    pass

def countwords(wdict, sentence):
    """ 将句子以相邻两个字构成词， 更新字典 """
    wdlist = list(unicode(sentence, "utf-8"))
    for i in range(len(wdlist)-1):
        tmpstr = "".join(wdlist[i:i+2])
        if tmpstr in wdict.keys():
            wdict[tmpstr] += 1
        else:
            wdict[tmpstr] = 1
    pass

def buildwirdictionary(filepath, dicpath, mode='w'):
    """

    :param filepath: 原材料文件
    :param dicpath: 统计后的字典的保存路径（json）
    :param mode: 'a'或者'w'. 'w'表示创建字典，'a'表示扩充字典， 默认'w'
    :return:
    """
    with open(filepath, 'r')as rd:
        lines = rd.readlines()
    if mode == 'a':     # 扩充字典
        wordic = loadfulldict(dicpath, sortflag=False)
    else:
        wordic = {}     # 创建字典
    for line in lines:
        line = line.strip()
        countsingleword(wordic, line)
        countwords(wordic, line)
    with open(dicpath, 'w')as wr:
        tmpjson = json.dumps(wordic)
        wr.write(tmpjson)
        pass
    pass


def loadsinglewordic(dicpath, sortflag=True):
    """
        加载单个字的字典
    :param dicpath: 字典的json文件路径
    :param sortflag: 是否按值排序输出（逆序）,若为True，输出的是列表
    """
    with open(dicpath, "r")as rd:
        wdic = json.loads(rd.read())
    singledic = {key: value for key, value in wdic.items() if len(key) == 1}
    if not sortflag:
        return singledic
    else:
        return sorted(singledic.items(), key=lambda item: item[1], reverse=True)
    pass

def loadwordsdic(dicpath, sortflag=True):
    """
        加载词语的字典
    :param dicpath: 字典的json文件路径
    :param sortflag: 是否按值排序输出（逆序），若为True,输出的是列表
    """
    with open(dicpath, "r")as rd:
        wdic = json.loads(rd.read())
    wordsdic = {key: value for key, value in wdic.items() if len(key) > 1}
    if not sortflag:
        return wordsdic
    else:
        return sorted(wordsdic.items(), key=lambda item: item[1], reverse=True)
    pass

def loadfulldict(dicpath, sortflag=True):
    """
        加载包含字和词语统计的字典
    :param dicpath: 字典的json文件路径
    :param sortflag: 是否按值排序输出（逆序），若为True,输出的是列表
    """
    with open(dicpath, "r")as rd:
        wdic = json.loads(rd.read())
    wordsdic = wdic
    if not sortflag:
        return wordsdic
    else:
        return sorted(wordsdic.items(), key=lambda item: item[1], reverse=True)

def showdict(wdict):
    """
    显示按值排序后的字典（实际是list形式返回）
    :param wdict: 排序后的dict（实际是list形式）
    :return:
    """
    for item in wdict:
        print item[0], ": ", item[1]

def cleanUndetectdic(fpath="undetectdic.txt"):
    """
        "undetectdic.txt": 第一次用ngac_title数据测试系统时，没有识别出来的地名
    :return:
    """
    with open(fpath, 'r')as rd:
        lines = rd.readlines()
    lines = [i for i in lines if i!="\n"] # 去除空行
    ans_lines = []
    for line in lines:
        ans_lines.extend(line.strip().split(" "))

    with open("new_undetecdic.txt", "w")as wr:
        for line in ans_lines:
            wr.write(line+"\n")
    pass


if __name__ == '__main__':
    # 语料库的处理去后缀处理(注意word的处理函数，removetail和cleantail使用的区别，后者生成的更大更全，但特征也相对稀疏一些)
    # processYuliaoku("remove")
    # processYuliaoku("clean")

    # 分别制作三地的地名用字的字典和词典
    # buildwirdictionary("xizang_new.txt", "xizang_dict.json")
    # buildwirdictionary("xinjiang_new.txt", "xinjiang_dict.json")
    # buildwirdictionary("neimenggu_new.txt", "neimenggu_dict.json")

    # 分别查看三地的地名用字的字典和词典
    # showdict(loadsinglewordic("xizang_dict.json"))    # 查看西藏地名单字词典
    # showdict(loadwordsdic("xizang_dict.json"))        # 查看西藏地名词语词典
    # showdict(loadfulldict("xizang_dict.json"))          # 查看西藏地名单字和词语字典
    # showdict(loadsinglewordic("xinjiang_dict.json"))  # 查看新疆地名单字词典
    # showdict(loadwordsdic("xinjiang_dict.json"))      # 查看新疆地名词语词典
    # showdict(loadfulldict("xinjiang_dict.json"))        # 查看新疆地名单字和词语字典
    # showdict(loadsinglewordic("neimenggu_dict.json")) # 查看内蒙古地名单字词典
    # showdict(loadwordsdic("neimenggu_dict.json"))     # 查看内蒙古地名词语词典
    # showdict(loadfulldict("neimenggu_dict.json"))       # 查看内蒙古地名单字和词语字典

    # 将三地的数据放在一起统一制作地名用字的字典和词典: remove模式
    # buildwirdictionary("xizang_new.txt", "xinjiang_neimeng_xizang.json")
    # buildwirdictionary("xinjiang_new.txt", "xinjiang_neimeng_xizang.json", mode='a')
    # buildwirdictionary("neimenggu_new.txt", "xinjiang_neimeng_xizang.json", mode='a')
    # buildwirdictionary("new_undetecdic.txt", "xinjiang_neimeng_xizang.json", mode='a')

    # 将三地的数据放在一起统一制作地名用字的字典和词典: clean模式
    # buildwirdictionary("xizang_new.txt", "xinjiang_neimeng_xizang_full.json")
    # buildwirdictionary("xinjiang_new.txt", "xinjiang_neimeng_xizang_full.json", mode='a')
    # buildwirdictionary("neimenggu_new.txt", "xinjiang_neimeng_xizang_full.json", mode='a')
    # buildwirdictionary("new_undetecdic.txt", "xinjiang_neimeng_xizang_full.json", mode='a')

    # 查看三地地名用字字典的内容
    # showdict(loadsinglewordic("xinjiang_neimeng_xizang.json"))  # 显示总的单字词典
    # showdict(loadwordsdic("xinjiang_neimeng_xizang_full.json"))      # 显示总的词语字典
    showdict(loadfulldict("xinjiang_neimeng_xizang.json"))      # 显示总的字典（包含单字与词的统计）

    # 第一次测试未识别出来的地名
    # cleanUndetectdic()

    pass
