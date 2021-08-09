import re


def number_format_insert_(ctx, cmdline):
    action = ctx.copy_last_action()
    last_words = "".join(ctx.last_fragments(1))
    cmd = "".join(cmdline)
    l_cmd = len(cmd)
    l = len(last_words)
    
    key = re.compile(r"(?<!\\)N")
    cnt = len(key.findall(cmd))
    if (l < cnt):
        return action
    
    for i in range(l_cmd-1, -1, -1):
        if i > 0 and cmd[i-1] == "\\":
            continue
        if cmd[i] == 'N':
            cmd = cmd[:i] + last_words[l-1] + cmd[i+1:]
            l -= 1
            cnt -= 1
        elif (l > cnt and l > 0) and (cmd[i] == 'n' or cmd[i] == 'x' or cmd[i] == 'X' or cmd[i] == '0' or cmd[i] == '_'):
            cmd = cmd[:i] + last_words[l-1] + cmd[i+1:]
            l -= 1

    parenthesis = 0
    for i in range(l_cmd-1, -1, -1):
        if cmd[i] == '_' and cmd[i-1] != "\\":
            cmd = cmd[:i] + ' ' + cmd[i+1:]
            continue
        if (cmd[i] < 'a' or cmd[i] > 'z') and (cmd[i] < 'A' or cmd[i] > 'Z') and (cmd[i] < '0' or cmd[i] > '9'):
            if i > 0 and cmd[i-1] == 'n' and cmd[i-1] != "\\":
                cmd = cmd[:i] + "\\" + cmd[i+1:]
            if cmd[i] == ')':
                parenthesis += 1
            if cmd[i] == '(':
                if parenthesis == 0:
                    cmd = cmd[:i] + "\\" + cmd[i+1:]
                else:
                    parenthesis -= 1
        if (cmd[i] == 'n' or cmd[i] == 'x' or cmd[i] == 'X') and cmd[i-1] != "\\":
            cmd = cmd[:i] + "\\" + cmd[i+1:]
    
    action.prev_replace = last_words
    action.text = cmd.replace("\\", "").strip()
    action.word = None
    action.prev_attach = True

    return action


def number_format_roman_(ctx, cmdline):
    action = ctx.copy_last_action()
    args = cmdline.split(":")
    method = int(args[0])
    case = int(args[1])
    print("method&case", method, case)
    if method < 0 or method > 1:
        return action

    last_words = "".join(ctx.last_fragments(1))[::-1]
    num = last_words.replace(",", "").replace(".", "")
    if num.isnumeric() == False or len(num) > 4:
        return action
    print(last_words, num)

    rom = ""
    num_method = [[["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX"], ["I", "II", "III", "IIII", "V", "VI", "VII", "VIII", "VIIII"]], [["X", "XX", "XXX", "XL", "L", "LX", "LXX", "LXXX", "XC"], ["X", "XX", "XXX", "XXXX", "L", "LX", "LXX", "LXXX", "LXXXX"]], [["C", "CC", "CCC", "CD", "D", "DC", "DCC", "DCCC", "CM"], ["C", "CC", "CCC", "CCCC", "D", "DC", "DCC", "DCCC", "DCCCC"]]]

    for i in range(len(num)):
        x = int(num[i])
        if x == 0:
            continue
        if i != 3:
            rom = num_method[i][method][x-1] + rom
        else:
            for j in range(x):
                rom = "M" + rom
        print(i, rom)
    if case != 0:
        rom = rom.lower()

    action.prev_replace = last_words
    action.text = rom
    action.word = None
    action.prev_attach = True

    return action


def retro_insert_currency_(ctx, cmdline):
    action = ctx.copy_last_action()

    args = cmdline.split(":")
    word_num = int(args[0]) + 1
    symbol = args[1]

    tmp = "".join(ctx.last_fragments(count = word_num))[::-1]
    key = re.compile(r"[\d,.]+\b[,.]?")
    ans = key.search(tmp)
    if ans == None:
        return action
    last_words = "".join(reversed(tmp[:ans.end()]))
    
    action.prev_replace = last_words
    action.text = symbol + last_words
    action.word = None
    action.prev_attach = True

    return action


def number_format_insert(*args, **kwargs):
    return number_format_insert_(*args, **kwargs)


def number_format_roman(*args, **kwargs):
    return number_format_roman_(*args, **kwargs)


def retro_insert_currency(*args, **kwargs):
    return retro_insert_currency_(*args, **kwargs)