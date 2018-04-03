#!/usr/bin/python
# -*- coding: utf-8 -*-



"""
    测试复杂地名（少数民族地名）识别系统精度的模块
    包括：
        1. 准确率、召回率和F值的计算
        2. 对正确识别(trueans.txt)、错误识别(wrongdetec.txt)和未识别出(undetecpath.txt)的地名的统计
"""

import re
import sys
import json
sys.path.append("..")
from removetail import *
import os
# Created by David Teng on 18-4-1


def extractloc(fpath, tpath):
    """
        提取文件中 [xxx]/ns 对象
    :param fpath: 用于提取的源文件
    :param tpath: 用于保存提取结果的文件（与fpath文件按行对应）
    :return: 返回loc的总数
    """
    # pat = re.compile("\[.+?\]/ns")
    with open(fpath, 'r')as rd:
        lines = rd.readlines()

    finalans = []
    sumloc = 0
    pat = re.compile(r"\[.+?\]/ns")
    for line in lines:
        ansline = pat.findall(line)
        ansline = [i.replace("[", "").replace("]/ns", "") for i in ansline]
        sumloc += len(ansline)
        finalans.append(ansline)

    with open(tpath, "w")as wr:
        for linelist in finalans:
            wr.write(" ".join(linelist) + "\n")

    return sumloc
    pass

def cmpline(dline, gline, truepath="trueans.txt", wrongdetecpath="wrongdetec.txt", undetecpath="undetectpath.txt"):
    """
        计算dline中的地名命中gline中的地名个数
    :param dline: 识别结果字符串
    :param gline: 标准切分字符串
    :param truepath: 保存命中的地名
    :param wrongdetecpath: 保存错误识别的地名
    :param undetecpath: 保存没有识别到的地名
    :return: 返回正确识别的个数
    """
    dline = dline.strip().split(" ")
    gline = gline.strip().split(" ")
    truecount = 0
    truelist = []
    wronglist = []
    undeteclist = []
    for g in gline:
        if dline and g in dline:
            truelist.append(g)
            dline.remove(g)  # 删除第一个匹配项
            truecount += 1
        else:
            undeteclist.append(g)
    if dline:
        wronglist.extend(dline)

    with open(truepath, "aw")as wr:
        tmpstr = " ".join(truelist)+"\n" if truelist else "\n"
        wr.write(tmpstr)

    with open(wrongdetecpath, "aw")as wr:
        tmpstr = " ".join(wronglist)+"\n" if wronglist else "\n"
        wr.write(tmpstr)

    with open(undetecpath, "aw")as wr:
        tmpstr = " ".join(undeteclist)+"\n" if undeteclist else "\n"
        wr.write(tmpstr)

    return truecount
    pass

def deletmpfile():
    """
        计算精度前，前删除“trueans\undetectpath\wrongdetec三个文件”
    :return:
    """
    filelist = ["trueans.txt", "undetectpath.txt", "wrongdetec.txt"]
    for f in filelist:
        if os.path.exists(f):
            os.remove(f)
    pass

def clcaprecision(fpath, goldpath, fsum, goldsum):
    """
        计算识别结果的精度
    :param fpath: 保存识别结果的文件路径
    :param goldpath: 标准切分路径
    :param fsum: 识别出的地名总数
    :param goldsum: 标准切分包含的地名数
    :return: 准确率、召回率和F值
    """

    deletmpfile()

    with open(fpath, "r")as rd:
        detectlines = rd.readlines()

    with open(goldpath, "r")as rd:
        goldlines = rd.readlines()

    csum = 0
    for (dl, gl) in zip(detectlines, goldlines):
        csum += cmpline(dl, gl)

    P = float(csum) / fsum
    R = float(csum) / goldsum
    print "精确率：", P
    print "召回率：", R
    print "F值:", 2 * P * R / (P + R)

    pass

def detecount(fpath):
    """
        对测试后生成的wrongdetec.txt、undetectpath.txt等文件做词频统计
    :param fpath: 文件路径
    :return:
    """
    wordDic = {}
    with open(fpath, "r")as rd:
        lines = rd.readlines()
    lines = [line for line in lines if line != "\n"]

    for line in lines:
        tmpline = line.strip().split()
        for l in tmpline:
            if l not in wordDic.keys():
                wordDic[l] = 1
            else:
                wordDic[l] += 1
    anslist = sorted(wordDic.items(), key=lambda item: item[1], reverse=True)
    for item in anslist:
        print item[0], ":", item[1]
        pass
    pass

if __name__ == '__main__':
    # dsum = extractloc("goldset_1.txt", "tmp.txt")
    # gsum = extractloc("goldset_282行.txt", "tmpgold.txt")
    # clcaprecision("tmp.txt", "tmpgold.txt", dsum, gsum)
    #
    detecount("wrongdetec.txt")
    pass
