# -*- coding: utf-8 -*-
import web


def post_add_form(page_id=''):
    return web.form.Form(
        web.form.Textbox("username", web.form.notnull, value='Аноним', size=20, description="Имя"),
        web.form.Password("password", description="Пароль"),
        web.form.Textbox("title", web.form.notnull, size=50, description="Заголовок"),
        web.form.Textarea("content", web.form.notnull, rows=10, cols=70, description="Контент"),
        web.form.Hidden('id', value=page_id),
        web.form.Button(u"Опубликовать"),
    )
