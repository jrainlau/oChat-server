from random import choice

adjWord = [
    '优雅', '神奇', '变态', '疯狂', '无解', '淫荡', '无敌', '高尚', '无私', '流利', '神秘', '痴线', '搞笑', '可爱', '可怕', '风流', '倜傥'
]

preWord = [
    '的', '地', '得', '之', 'の', '乃', '\'s'
]

nonWord = [
    '组织', '社团', '群聊', '天团', '小分队', '游击队', '先锋队', '敢死队', '集体', '班级', '小窝', '论坛', '步行街'
]

def generateRoomName():
    return choice(adjWord) + choice(preWord) + choice(nonWord)
