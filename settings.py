# -*- coding: utf-8 -*-
from util import check_conf_dir


SITE_NAME = "Анонимный Форум"
TAG_LINE = ""
FOOTER_TAG = "2017 год"
SETTINGS_FOLDER = ".small_forum"
SETTINGS_PATH = check_conf_dir(SETTINGS_FOLDER)
DB_FILENAME = "{}/{}".format(SETTINGS_PATH, "forum.db3")

RECIP = 'finalka@gmail.com'

GLOBAL_PARAMS = { 'site_name' : SITE_NAME, 'tag_line' : TAG_LINE, 'title' : SITE_NAME, 'footer_tag' : FOOTER_TAG }
