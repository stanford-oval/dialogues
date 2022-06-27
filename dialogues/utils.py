import os
import re
import subprocess

from word2number import w2n


def convert_to_int(val, strict=False, word2number=False):
    val = str(val)
    if val.isdigit() and not val.startswith('0'):
        return int(val)
    elif word2number and len(val.split()) == 1:
        # elif word2number:
        try:
            num = w2n.word_to_num(val)
            return num
        except:
            if strict:
                return None
            else:
                return val
    else:
        if strict:
            return None
        else:
            return val


def clean_text(text, is_formal=False):
    text = text.strip()
    text = re.sub(' +', ' ', text)
    text = re.sub('\\n|\\t', ' ', text)
    text = text.replace('，', ',')

    if not is_formal:
        text = text.replace('"', '')

    return text


def get_commit():
    directory = os.path.dirname(__file__)
    return (
        subprocess.Popen("cd {} && git log | head -n 1".format(directory), shell=True, stdout=subprocess.PIPE)
        .stdout.read()
        .split()[1]
        .decode()
    )
