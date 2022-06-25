import re
from plover.formatting import apply_case

def num_sec_to_word(num_sec, mode):
    number_words = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
    number_words_tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

    illions = ["thousand", "million", "billion", "trillion", "quadrillion", "quintillion", "sextillion", "septillion", "octillion", "nonillion", "decillion"]
    illion_prefixes = ["", "un", "duo", "tre", "quattuor", "quinqua", "se", "septe", "octo", "nove"]
    illion_prefixes_tens = ["", "deci", "viginti", "triginta", "quadraginta", "quinquaginta", "sexaginta", "septuaginta", "octoginta", "nonaginta"]
    illion_prefixes_hundreds = ["", "centi", "ducenti", "trecenti", "quadringenti", "quingenti", "sescenti", "septingenti", "octingenti", "nongenti"]

    # Mode 0: 3 digit segments
    if mode == 0:
        # add leading zeros
        if len(num_sec) == 1:
            num_sec = "00" + num_sec
        if len(num_sec) == 2:
            num_sec = "0" + num_sec
        # the hundreds
        num_sec_word = ""
        if num_sec[0] != "0":
            num_sec_word = number_words[int(num_sec[0])] + " hundred"
        # the tens
        num_tens = int(num_sec[1:3])
        if num_sec_word != "" and num_tens != "0":
            num_sec_word += " "
        if num_tens < 20:
            num_sec_word += number_words[num_tens]
        else:
            num_sec_word += number_words_tens[int(num_sec[1])]
            if num_sec[2] != "0":
                num_sec_word += "-" + number_words[int(num_sec[2])]
        return num_sec_word

    # Mode 1: -illion parts
    if mode == 1:
        if num_sec <= 10:
            return illions[num_sec]
        if num_sec >= 1000:
            return "?"
        prefix1 = illion_prefixes[num_sec%10]
        prefix2 = illion_prefixes_tens[int(num_sec/10)%10]
        if num_sec >= 100:
            prefix2 += illion_prefixes_hundreds[int(num_sec/100)]
        # tre- rule
        if num_sec%10 == 3:
            if prefix2[0] == "v" or prefix2[0] == "t" or prefix2[0] == "q" or prefix2[0] == "o" or prefix2[0] == "c":
                prefix1 += "s"
        # se- rule
        if num_sec%10 == 6:
            if prefix2[0] == "v" or prefix2[0] == "t" or prefix2[0] == "q":
                prefix1 += "s"
            if prefix2[0] == "o" or prefix2[0] == "c":
                prefix1 += "x"
        # septe- & nove- rule
        if num_sec%10 == 7 or num_sec%10 == 9:
            if prefix2[0] == "d" or prefix2[0] == "t" or prefix2[0] == "q" or prefix2[0] == "s" or prefix2[0] == "c":
                prefix1 += "n"
            if prefix2[0] == "v" or prefix2[0] == "o":
                prefix1 += "m"
        return prefix1 + prefix2[0:-1] + "illion"

    # Mode 2: single digits
    if num_sec == "0":
        return "zero"
    if num_sec == "O":
        return ""
    return number_words[int(num_sec)]


# Used for getting the correct capitalization
# This is used for converting digits to numbers
def num_to_word_get_case(ctx):
    action_gen = ctx.iter_last_actions()

    # Fails if the Plover was recently opened,
    # and there aren't any actions before the number
    try:
        # Check if there is a capitalization action after the number
        last_action = next(action_gen)
        if last_action.next_case != None:
            return last_action.next_case

        # Filter out all the actions that were part of writing the number
        while last_action.prev_attach:
            last_action = next(action_gen)

        # Use the case from action of the thing before the number
        return next(action_gen).next_case
    # Not enough actions to look at
    except StopIteration:
        return None


def number_format_insert_(ctx, cmdline):
    action = ctx.copy_last_action()
    last_words = "".join(ctx.last_fragments(1))
    num = last_words.replace(",", "").replace(".","")
    cmd = "".join(cmdline)
    l_cmd = len(cmd)
    l = len(num)

    # do nothing if there are not enough digits
    key = re.compile(r"(?<!\\)N")
    cnt = len(key.findall(cmd))
    if (l < cnt):
        return action

    # fill in the numbers
    for i in range(l_cmd-1, -1, -1):
        if i > 0 and cmd[i-1] == "\\":
            continue
        if cmd[i] == 'N':
            cmd = cmd[:i] + num[l-1] + cmd[i+1:]
            l -= 1
            cnt -= 1
        elif (l > cnt and l > 0) and (cmd[i] == 'n' or cmd[i] == 'x' or cmd[i] == 'X' or cmd[i] == '0' or cmd[i] == '_'):
            cmd = cmd[:i] + num[l-1] + cmd[i+1:]
            l -= 1

    # deal with the symbols
    parenthesis = 0 # no unpaired parentheses
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
    action.text = cmd.replace("\\", "").strip() # remove backslash
    action.word = None
    action.prev_attach = True
    action.next_attach = False
    action.glue = False

    return action

def number_format_roman_(ctx, cmdline):
    action = ctx.copy_last_action()
    args = cmdline.split(":")
    method = int(args[0])
    case = int(args[1])
    if method < 0 or method > 1:
        return action

    # only convert numbers less than 4 digits long
    last_words = "".join(ctx.last_fragments(1))
    num = last_words[::-1].replace(",", "").replace(".", "")
    if num.isnumeric() == False or len(num) > 4:
        return action

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
    if case != 0:
        rom = rom.lower()

    action.prev_replace = last_words
    action.text = rom
    action.word = None
    action.prev_attach = True
    action.next_attach = False
    action.glue = False

    return action

def number_word_conversion_(ctx, cmdline):
    action = ctx.copy_last_action()
    args = cmdline.split(":")
    card_ord = int(args[0]) # maintain/cardinal/ordinal
    num_word = int(args[1]) # maintain(TODO)/number/word
    separator = 0 # maintain/+/-
    sig_dec = 0 # NA/significant figures/decimal places
    figures = -1 # number of sig_dec
    hyphen_minus = 0 # maintain/hyphen/minus

    if len(args) > 2:
        for i in range(2, len(args)):
            # c for comma separators
            if args[i][0] == "c":
                separator = int(args[i][1:])
            # s for significant figures
            if args[i][0] == "s":
                sig_dec = 1
                figures = int(args[i][1:])
            # d for decimal places
            if args[i][0] == "d":
                sig_dec = 2
                figures = int(args[i][1:])
            # m for minus
            if args[i][0] == "m":
                hyphen_minus = int(args[i][1:])
            # z for leading zero
            # A for and
            # N for negative
            # P for decimal point
            # D for decimal part

    num = ""
    num_to_word = ""
    num_dec = ""
    is_negative = False

    fragment = "".join(ctx.last_fragments(1)) # TODO: READ WORDS PROPERLY
    # check cardinal/ordinal
    tmp = fragment[-2:]
    if tmp == "st" or tmp == "nd" or tmp == "rd" or tmp == "th":
        tmp = fragment[:-2]
        if card_ord == 0:
            card_ord = 2
    else:
        tmp = fragment
        if card_ord == 0:
            card_ord = 1
    # check number/word
    if tmp.replace(",", "").replace(".", "").replace("-", "").replace("−", "").isdecimal() == False:
        return action
    # check separator
    if separator == 0:
        if re.search(",", tmp) == None:
            separator = 2
        else:
            separator = 1
    # check positive/negative
    if re.search(r"-|−", tmp) != None:
        is_negative = True
        if hyphen_minus == 0:
            if tmp[0] == "-":
                hyphen_minus = 1
            else:
                hyphen_minus = 2
    num = tmp.replace(",", "").replace("-", "").replace("−", "")
    # split decimal
    if re.search(r"\.", tmp) != None:
        tmp = num.split(".", 1)
        num = tmp[0]
        num_dec = tmp[1].replace(".", "")
        if (num_dec == ""):
            num_dec = "O"
    # sig fig
    if sig_dec == 1 and figures > 0:
        l = len(num)
        cut = l - figures;
        if cut > 0:
            for i in range(0, cut):
                num = num[:l-i-1] + "0" + num[l-i+1:]
            num_dec = ""
        else:
            sig_dec = 2
            figures = -cut
    # decimal places
    if sig_dec == 2 and figures >= 0:
        if num_dec == "O":
            num_dec = ""
        if figures <= len(num_dec):
            num_dec = num_dec[:figures]
        else:
            append = figures - len(num_dec)
            for i in range(append):
                num_dec += "0"
        if num_dec == "" and num[-1] == "0":
            num_dec = "O"

    # number to word conversion TODO: customization options for words
    if num_word == 2:
        for i in range(len(num)-1, -1, -3):
            num_sec = num_sec_to_word(num[max(0, i-2):i+1], 0)
            if num_sec != "":
                if i != len(num)-1:
                    num_sec += " " + num_sec_to_word(int((len(num)-i-1)/3)-1, 1)
                if num_to_word != "":
                    num_sec += " "
                num_to_word = num_sec + num_to_word
        if num == "0" and num_to_word == "":
            num_to_word = "zero"
        # negative numbers
        if is_negative:
            num_to_word = "negative " + num_to_word
        # decimal numbers
        if num_dec != "":
            if num_to_word != "":
                num_to_word += " "
            num_to_word += "point"
        for i in num_dec:
            num_to_word += " " + num_sec_to_word(i, 2)
        # ordinal numbers
        if card_ord == 2 and num_dec == "":
            tmp = num_to_word[-3:]
            if tmp == "one":
                num_to_word = num_to_word[:-3] + "first"
            elif tmp == "two":
                num_to_word = num_to_word[:-3] + "second"
            elif tmp == "ree":
                num_to_word = num_to_word[:-3] + "ird"
            elif tmp == "ive":
                num_to_word = num_to_word[:-3] + "ifth"
            elif tmp == "ght":
                num_to_word = num_to_word[:-3] + "ghth"
            elif tmp == "ine":
                num_to_word = num_to_word[:-3] + "inth"
            elif tmp == "lve":
                num_to_word = num_to_word[:-3] + "lfth"
            elif num_to_word[-2:] == "ty":
                num_to_word = num_to_word[:-2] + "tieth"
            else:
                num_to_word += "th"
    # no number to word conversion
    else:
        # add comma
        if separator == 1:
            for i in range(len(num)-3, 0, -3):
                num = num[:i] + "," + num[i:]
        # ordinal
        if card_ord == 2 and num_dec == "":
            tmp = num[-1]
            if tmp == "1" and num[-2:] != "11":
                num += "st"
            elif tmp == "2" and num[-2:] != "12":
                num += "nd"
            elif tmp == "3" and num[-2:] != "13":
                num += "rd"
            else:
                num += "th"
        # decimal part
        if num_dec != "":
            if num_dec == "O":
                num_dec = ""
            num += "." + num_dec
        # negative
        if is_negative == True:
            if hyphen_minus == 1:
                num = "-" + num
            else:
                num = "−" + num

    last_words = fragment
    action.prev_replace = last_words
    if num_word == 2:
        # get the case to use
        case = num_to_word_get_case(ctx)
        action.text = apply_case(num_to_word, case)

    else:
        action.text = num
    action.word = None
    action.prev_attach = True
    action.next_attach = False
    action.glue = False

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
    action.next_attach = False
    action.glue = False

    return action


def number_format_insert(*args, **kwargs):
    return number_format_insert_(*args, **kwargs)

def number_format_roman(*args, **kwargs):
    return number_format_roman_(*args, **kwargs)

def number_word_conversion(*args, **kwargs):
    return number_word_conversion_(*args, **kwargs)

def retro_insert_currency(*args, **kwargs):
    return retro_insert_currency_(*args, **kwargs)
