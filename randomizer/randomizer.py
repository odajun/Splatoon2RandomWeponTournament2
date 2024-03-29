#!/usr/bin/python
# -*- coding: utf-8 -*-

import random
import discord
import sys
import copy
import os

from configparser import ConfigParser
from pprint import pprint

def getFilePathFromCurrenDir(file_name):
    return os.path.dirname(os.path.abspath(__file__)) + "/" + file_name

def readFileToList(path):
    full_path = getFilePathFromCurrenDir(path)
    list = []
    f = open(full_path, 'r', encoding='utf-8')
    for line in f:
        line = line.strip()
        if line.startswith('#'):
            continue
        if len(line) == 0:
            continue
        list.append(line)
    f.close()
    return list

def getWeponDict():
    weapon_dict = {}
    weapon_type_list = ["blaster", "charger", "manuver", "roller_brush", "shelter", "shooter", "shooter2", "slosher", "splatling"]
    for weapon_type in weapon_type_list :
        weapon_dict[weapon_type] = {}
        path = "weapons/" + weapon_type + "_file.txt"
        full_path = getFilePathFromCurrenDir(path)
        f = open(path, 'r', encoding='utf-8')
        for line in f:
            line = line.strip()
            if line.startswith('#'):
                continue
            if len(line) == 0:
                continue
            weapon_len = line.split(",")
            weapon_dict[weapon_type][weapon_len[0]] = weapon_len[1]
    f.close()
    return weapon_dict

def choiceUserWeapon(weapon_set, user_weapon_list, num):
    duplicated_weapon = True
    weapon = ""
    while duplicated_weapon :
        weapon = random.choice(user_weapon_list)
        duplicated_weapon = False
        for selected_weapon in weapon_set :
            if selected_weapon[num] == weapon :
                duplicated_weapon = True
                break
    return weapon

def setUsersWeapon(weapon_type_list, weapon_dict, users):
    team_weapon_dict = {}
    for i in range(len(weapon_type_list)):
        weapon_name = random.choice(list(weapon_dict[weapon_type_list[i]].keys()))
        weapon_range = weapon_dict[weapon_type_list[i]][weapon_name]
        team_weapon_dict[users[i]] = {"type": weapon_type_list[i],
                                             "name": weapon_name,
                                             "range": weapon_range}
    return team_weapon_dict

def getWeaponTotalRage(users, weapon_dict):
    total_range = 0
    for user in users:
        total_range = total_range + int(weapon_dict[user]["range"])
    return total_range

def removeWeaponFromTypeList(weapon_type_list, weapon_dict, users):
    for i in range(len(weapon_type_list)):
        weapon_type_list[i].remove(weapon_dict[users[i]]["type"])
    return weapon_type_list

def choiceTeamWeapon(user_weapon_list):
    selected_weapon = []
    for i in range(len(user_weapon_list)):
        duplicated_weapon = True
        while duplicated_weapon:
            weapon = random.choice(user_weapon_list[i])
            if weapon not in selected_weapon :
                duplicated_weapon = False
        selected_weapon.append(weapon)
    return selected_weapon

def selectSmallDiffRangeWeapons(weapon_type_list, weapon_dict, users, another_range_total):
    weapon_selecting = True
    team_weapon_dict = {}
    for i in range(int(config["setting"]["retry_max_num"])):
        selected_weapon_type = choiceTeamWeapon(weapon_type_list)
        team_weapon_dict = setUsersWeapon(selected_weapon_type, weapon_dict, users)
        weapon_range_total = getWeaponTotalRage(users, team_weapon_dict)
        diff = abs(another_range_total - weapon_range_total)
        if diff < int(config["setting"]["range_diff_cap"]):
            weapon_selecting = False
            break
    return team_weapon_dict, weapon_selecting

def getWeaponSet(weapon_dict, alpha_users, bravo_users):
    weapon_set = {}
    all_weapon_selecting = True
    while all_weapon_selecting :
        weapon_type_list = ["blaster", "charger", "manuver", "roller_brush",
                            "shelter", "shooter", "shooter2", "slosher", "splatling"]
        alpha_weapon_type_list = []
        bravo_weapon_type_list = []
        for alpha_user in alpha_users:
            alpha_weapon_type_list.append(copy.deepcopy(weapon_type_list))
        for bravo_user in bravo_users:
            bravo_weapon_type_list.append(copy.deepcopy(weapon_type_list))

        selected_weapon_type_list = random.sample(weapon_type_list, 4)
        alpha_weapon_dict = setUsersWeapon(selected_weapon_type_list, weapon_dict, alpha_users)
        alpha_weapon_range_total = getWeaponTotalRage(alpha_users, alpha_weapon_dict)

        bravo_weapon_dict, weapon_selecting = \
            selectSmallDiffRangeWeapons(bravo_weapon_type_list,weapon_dict,bravo_users,alpha_weapon_range_total)
        if weapon_selecting:
            continue
        alpha_weapon_type_list = \
            removeWeaponFromTypeList(alpha_weapon_type_list,alpha_weapon_dict,alpha_users)
        bravo_weapon_type_list = \
            removeWeaponFromTypeList(bravo_weapon_type_list,bravo_weapon_dict,bravo_users)
        weapon_set["1st"] = {}
        weapon_set["1st"] = {}
        weapon_set["1st"]["alpha"] = alpha_weapon_dict
        weapon_set["1st"]["bravo"] = bravo_weapon_dict

        #### 以下同じコードが続くのでできれば綺麗にまとめたいけど一旦動くものを作成
        ### 2戦目の武器決定
        alpha_weapon_type_selected = choiceTeamWeapon(alpha_weapon_type_list)
        alpha_weapon_dict = setUsersWeapon(alpha_weapon_type_selected, weapon_dict, alpha_users)
        alpha_weapon_range_total = getWeaponTotalRage(alpha_users, alpha_weapon_dict)

        bravo_weapon_dict, weapon_selecting = \
            selectSmallDiffRangeWeapons(bravo_weapon_type_list,weapon_dict,bravo_users,alpha_weapon_range_total)
        if weapon_selecting:
            continue
        alpha_weapon_type_list = \
            removeWeaponFromTypeList(alpha_weapon_type_list,alpha_weapon_dict,alpha_users)
        bravo_weapon_type_list = \
            removeWeaponFromTypeList(bravo_weapon_type_list,bravo_weapon_dict,bravo_users)
        weapon_set["2nd"] = {}
        weapon_set["2nd"] = {}
        weapon_set["2nd"]["alpha"] = alpha_weapon_dict
        weapon_set["2nd"]["bravo"] = bravo_weapon_dict

        ### 3番目の武器決定
        alpha_weapon_type_selected = choiceTeamWeapon(alpha_weapon_type_list)
        alpha_weapon_dict = setUsersWeapon(alpha_weapon_type_selected, weapon_dict, alpha_users)
        alpha_weapon_range_total = getWeaponTotalRage(alpha_users, alpha_weapon_dict)

        bravo_weapon_dict, weapon_selecting = \
            selectSmallDiffRangeWeapons(bravo_weapon_type_list,weapon_dict,bravo_users,alpha_weapon_range_total)
        if weapon_selecting:
            continue
        alpha_weapon_type_list = \
            removeWeaponFromTypeList(alpha_weapon_type_list,alpha_weapon_dict,alpha_users)
        bravo_weapon_type_list = \
            removeWeaponFromTypeList(bravo_weapon_type_list,bravo_weapon_dict,bravo_users)
        weapon_set["3rd"] = {}
        weapon_set["3rd"] = {}
        weapon_set["3rd"]["alpha"] = alpha_weapon_dict
        weapon_set["3rd"]["bravo"] = bravo_weapon_dict

        ### 4番目の武器決定
        alpha_weapon_type_selected = choiceTeamWeapon(alpha_weapon_type_list)
        alpha_weapon_dict = setUsersWeapon(alpha_weapon_type_selected, weapon_dict, alpha_users)
        alpha_weapon_range_total = getWeaponTotalRage(alpha_users, alpha_weapon_dict)

        bravo_weapon_dict, weapon_selecting = \
            selectSmallDiffRangeWeapons(bravo_weapon_type_list,weapon_dict,bravo_users,alpha_weapon_range_total)
        if weapon_selecting:
            continue
        alpha_weapon_type_list = \
            removeWeaponFromTypeList(alpha_weapon_type_list,alpha_weapon_dict,alpha_users)
        bravo_weapon_type_list = \
            removeWeaponFromTypeList(bravo_weapon_type_list,bravo_weapon_dict,bravo_users)
        weapon_set["4th"] = {}
        weapon_set["4th"] = {}
        weapon_set["4th"]["alpha"] = alpha_weapon_dict
        weapon_set["4th"]["bravo"] = bravo_weapon_dict

        ### 5番目の武器決定
        alpha_weapon_type_selected = choiceTeamWeapon(alpha_weapon_type_list)
        alpha_weapon_dict = setUsersWeapon(alpha_weapon_type_selected, weapon_dict, alpha_users)
        alpha_weapon_range_total = getWeaponTotalRage(alpha_users, alpha_weapon_dict)

        bravo_weapon_dict, weapon_selecting = \
            selectSmallDiffRangeWeapons(bravo_weapon_type_list,weapon_dict,bravo_users,alpha_weapon_range_total)
        if weapon_selecting:
            continue
        weapon_set["5th"] = {}
        weapon_set["5th"] = {}
        weapon_set["5th"]["alpha"] = alpha_weapon_dict
        weapon_set["5th"]["bravo"] = bravo_weapon_dict

        all_weapon_selecting = False
    return weapon_set

def getMemberList(name):
    # 1行目にチーム名
    # 2行目以降にメンバー名画列挙されている想定
    path = "teams/" + name + ".txt"
    team_name_members = readFileToList(path)
    team_name = team_name_members[0]
    members = team_name_members[1:]
    return team_name, members

def getUserWeaponText(team_name, game_result_set):
    total_range = 0
    text = ""
    for user in game_result_set[team_name] :
        weapon_range = int(game_result_set[team_name][user]['range'])
        total_range = total_range + weapon_range
        text = text + user + " : " + game_result_set[team_name][user]['name'] + ":" + str(weapon_range) + "\n"
    text = text + "合計射程：" + str(total_range) + "\n"
    return text

def getOutMessage(result_set):
    alpha_text = ""
    bravo_text = ""
    rule_text = {"fess":"フェス(ナワバリ)", "area":"ガチエリア",
                 "clam":"ガチアサリ","rainmaker":"ガチホコ","tower":"ガチヤグラ"}
    for game in result_set :
        header = "\n" + game + " game : " + rule_text[result_set[game]['rule']] \
               + " : " + result_set[game]['stage'] + "\n"
        alpha_text = alpha_text + header + getUserWeaponText('alpha', result_set[game])
        bravo_text = bravo_text + header + getUserWeaponText('bravo', result_set[game])
    return alpha_text, bravo_text

def run_randomizer(alpha_name, bravo_name):
    result_set = {}
    rule_list = ["fess","area","clam", "rainmaker", "tower"]
    random.shuffle(rule_list)
    stage_all_list = readFileToList("stage.txt")
    stage_list = random.sample(stage_all_list, 5)
    fess_stage_list = readFileToList("fess_stage.txt")
    fess_stage = random.choice(fess_stage_list)
    alpha_name, alpha_users = getMemberList(alpha_name)
    bravo_name, bravo_users = getMemberList(bravo_name)

    # 武器の決定
    weapon_dict = getWeponDict()
    weapon_set = getWeaponSet(weapon_dict, alpha_users, bravo_users)

    num_list = ["1st","2nd","3rd","4th","5th"]
    for i in range(len(num_list)):
        result_set[num_list[i]] = {}
        result_set[num_list[i]]["rule"] = rule_list[i]
        if rule_list[i] == "fess" :
            result_set[num_list[i]]["stage"] = fess_stage
        else :
            result_set[num_list[i]]["stage"] = stage_list[i]
        result_set[num_list[i]]["alpha"] = weapon_set[num_list[i]]["alpha"]
        result_set[num_list[i]]["bravo"] = weapon_set[num_list[i]]["bravo"]

    if config["setting"]["debug_mode"] == "on":
        pprint(result_set)

    alpha_text, bravo_text = getOutMessage(result_set)
    return alpha_text, bravo_text

def getTeamTextChannelIdFromName(team_name):
    # チームとチャネルの対応表を列挙
    team_channel = {"teamA":"team1", "teamB":"team2"}
    return config['text_id'][team_channel[team_name]]

ini_file = getFilePathFromCurrenDir("randomizer.ini")
if not os.path.exists(ini_file) :
    print("Can't find randoizer.ini file : " + ini_file)
    sys.exit(1)

config = ConfigParser()
config.read(ini_file)
client = discord.Client()

if config["setting"]["debug_mode"] == "on":
    run_randomizer("teamA", "teamB")
    sys.exit(0)

@client.event
async def on_ready():
    print('Lgged in as')
    print(client.user.name)
    print(client.user.id)
    print('--------')
    msg = "ランダマイザー起動中"
    bot_channel = client.get_channel(int(config['text_id']['bot_channel']))
    await bot_channel.send(msg)

@client.event
async def on_message(message):
    # 入力されたメッセージに従って制御
    if message.content.startswith('reset,'):
        if message.channel.id == int(config['text_id']['bot_channel']):
            contents = message.content.split(",")
            alpha_msg, bravo_msg = run_randomizer(contents[1],contents[2])
            alpha_id = int(getTeamTextChannelIdFromName(contents[1]))
            bravo_id = int(getTeamTextChannelIdFromName(contents[2]))
            alpha_channel = client.get_channel(alpha_id)
            bravo_channel = client.get_channel(bravo_id)
            await alpha_channel.send(alpha_msg)
            await bravo_channel.send(bravo_msg)

client.run(config['access_token']['token'])