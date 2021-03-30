#!/usr/bin/python3
import re
import os
import shutil
import unicodedata

def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')

if __name__ == '__main__':
    for root, dirs, files in os.walk("csv", topdown=False):
        for name in files:
            path = os.path.join(root, name)
            newpath = os.path.join(root, slugify(name[:-4])+'.csv' if name.endswith('.csv') else slugify(name))
            shutil.move(path, newpath)