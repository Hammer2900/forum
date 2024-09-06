import os
import random

from fastapi import FastAPI, Form, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import hashlib
from typing import Optional
import markdown
from faker import Faker
from domonic.html import *

DOMConfig.HTMX_ENABLED = True

# Database setup
SQLALCHEMY_DATABASE_URL = 'sqlite:///./forum.db'
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Models
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    created = Column(DateTime, default=datetime.utcnow)
    username = Column(String, unique=True, index=True)
    password = Column(String)


class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True, index=True)
    created = Column(DateTime, default=datetime.utcnow)
    title = Column(String, index=True)
    content = Column(String)
    parent = Column(Integer, default=0)

    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)


class File(Base):
    __tablename__ = 'files'
    id = Column(Integer, primary_key=True, index=True)
    created = Column(DateTime, default=datetime.utcnow)
    filename = Column(String, index=True)
    file_type = Column(String)
    content = Column(LargeBinary)

    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)


class ActivityLog(Base):
    __tablename__ = 'activity_logs'
    id = Column(Integer, primary_key=True, index=True)
    created = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String)
    user_agent = Column(String)
    action = Column(String)

    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)


Base.metadata.create_all(bind=engine)

app = FastAPI()
# /home/izot/Downloads/___/forum/templates
templates = Jinja2Templates(directory='templates')


def generate_test_data():
    fake = Faker()
    DB_TEST_USERS = [
        {'id': '1', 'username': 'user1', 'password': 'password123', 'created': datetime.utcnow()},
        {
            'id': '2',
            'username': 'user2',
            'password': 'another_password',
            'created': datetime.utcnow() - timedelta(days=7),
        },
        {'id': '3', 'username': 'admin', 'password': 'admin123', 'created': datetime.utcnow()},
    ]

    DB_TEST_POSTS = []
    for i in range(12):
        user_id = random.choice([user['id'] for user in DB_TEST_USERS])
        DB_TEST_POSTS.append(
            {
                'title': fake.text(max_nb_chars=50),
                'content': fake.text(max_nb_chars=500) + '\n',
                'user_id': user_id,
                'created': (datetime.utcnow() - timedelta(days=i)).strftime('%d %B %Y, %A'),
            }
        )

    return DB_TEST_USERS, DB_TEST_POSTS


DB_TEST_USERS, DB_TEST_POSTS = generate_test_data()
# print('[✖]', DB_TEST_POSTS)
# print('[✖]', DB_TEST_USERS)


class ForumSmallExperemental:
    def __init__(self):
        pass

    def __action_post_panel(self):
        return html(
            div(
                button(
                    'ответить ',
                    i(_class='bi bi-arrow-right-square'),
                    _type='button',
                    _class='btn btn-outline-secondary',
                ),
                button('экспорт ', i(_class='bi bi-book'), _type='button', _class='btn btn-outline-secondary'),
                button('удалить ', i(_class='bi bi-bucket'), _type='button', _class='btn btn-outline-secondary'),
                _class='btn-group btn-group-sm',
                role='group',
            ),
            hr(),
        )

    def __base(self, content):
        return str(
            html(
                head(
                    meta(charset='UTF-8'),
                    meta(name='viewport', content='width=device-width, initial-scale=1.0'),
                    title('Анонимный Форум'),
                    link(
                        _href='https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css',
                        _rel='stylesheet',
                    ),
                    link(
                        _href='https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css',
                        _rel='stylesheet',
                    ),
                    link(
                        _href='https://unpkg.com/pattern.css',
                        _rel='stylesheet',
                    ),
                    style("""
            body { font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; max-width: 800px; margin: 0 auto; }
            header { background: #f4f4f4; padding: 1rem; }
            nav a { margin-right: 10px; }
            .content { background: #fff; padding: 1rem; flex: 1 0 auto; }
            footer { text-align: center; margin-top: 1rem; font-size: 0.9rem; flex-shrink: 0;}
        """),
                ),
                body(
                    header(
                        h1('Анонимный Форум 🐍'),
                        nav(
                            a('Стена постов', _href='/'),
                            a('Популярные', _href='/tagged'),
                            a('Новый пост', _href='/add_index_form'),
                            a('Регистрация', _href='/register'),
                            a('Логин', _href='/login'),
                            a('Файлы', _href='/files'),
                            a('Статистика', _href='/statistic'),
                            a('О форуме', _href='/about_form'),
                            a('Выход', _href='/exit'),
                        ),
                    ),
                    div(content, _class='content'),
                    footer('&copy; 2023 Анонимный Форум'),
                    script(src='https://unpkg.com/htmx.org@2.0.2'),
                    script(defer=1, src='https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js'),
                    _class='container d-flex flex-column h-100',
                    # _class='d-flex flex-column',
                ),
                # _class='h-100 pattern-dots-sm bg-primary text-white',
                # _class='pattern-triangles-sm',
            )
        )

    def register(self):
        content = div(
            h1('Регистрация', class_='mb-4'),
            # h1('', **{'x-data':"{ message: 'I ❤️ Alpine' }", 'x-text':"message"}),
            form(
                div(
                    label('Имя пользователя', for_='username', _class='form-label'),
                    input(type='text', id='username', name='username', _class='form-control', required=True),
                    _class='mb-3',
                ),
                div(
                    label('Пароль', for_='password', _class='form-label'),
                    input(type='password', id='password', name='password', _class='form-control', required=True),
                    _class='mb-3',
                ),
                div(
                    label('Повторите пароль', for_='confirm_password', _class='form-label'),
                    input(
                        type='password',
                        id='confirm_password',
                        name='confirm_password',
                        _class='form-control',
                        required=True,
                    ),
                    _class='mb-3',
                ),
                button('Зарегистрироваться', type='submit', _class='btn btn-primary'),
                _class='needs-validation',
                action='/register_new_user',
                method='POST',
                novalidate=True,
            ),
            # class_='container mt-5',
        )
        return self.__base(content)

    def login(self):
        content = html(
            h1('Логин', class_='mb-4'),
            form(
                div(
                    label('Имя пользователя', for_='username', _class='form-label'),
                    input(type='text', id='username', name='username', _class='form-control', required=True),
                    _class='mb-3',
                ),
                div(
                    label('Пароль', for_='password', _class='form-label'),
                    input(type='password', id='password', name='password', _class='form-control', required=True),
                    _class='mb-3',
                ),
                button('Войти', type='submit', _class='btn btn-primary'),
                _class='needs-validation',
            ),
        )
        return self.__base(content)

    def list(self):
        con2 = html(
            div(
                span('Search: ', _class='input-group-text'),
                input(value='', _type='text', _class='form-control'),
                hr(),
                _class='input-group input-group-sm mb-4',
            ),
            div(
                ul(
                    *[
                        li(
                            h4(lines.get('title')),
                            p(lines.get('content')),
                            p(lines.get('created')),
                            self.__action_post_panel(),
                            _class='mb-3',
                        )
                        for lines in DB_TEST_POSTS
                    ]
                )
            ),
            div(
                nav(
                    ul(
                        li(a('Предыдущий', _class='page-link', href='#'), _class='page-item'),
                        li(a('1', _class='page-link', href='#'), _class='page-item'),
                        li(a('...', _class='page-link', href='#'), _class='page-item'),
                        li(a('100', _class='page-link', href='#'), _class='page-item'),
                        li(a('Следующий', _class='page-link', href='#'), _class='page-item'),
                        _class='pagination mt-5 d-flex justify-content-center',
                    )
                )
            ),
        )
        return self.__base(con2)

    def tagged(self):
        content = html()
        return self.__base(content)

    def add_form(self):
        content = html(
            h2('Создать новый пост'),
            form(
                div(
                    label('Имя:', _for='username', _class='form-label'),
                    input(
                        type='text',
                        _class='form-control',
                        _id='username',
                        name='username',
                        value='Аноним',
                        required=True,
                    ),
                    _class='mb-3',
                ),
                div(
                    label('Пароль:', _for='password', _class='form-label'),
                    input(type='password', _class='form-control', _id='password', name='password', value='empty'),
                    _class='mb-3',
                ),
                div(
                    label('Заголовок:', _for='title', _class='form-label'),
                    input(type='text', _class='form-control', _id='title', required=True),
                    _class='mb-3',
                ),
                div(
                    label('Содержание:', _for='content', _class='form-label'),
                    textarea(
                        type='text', _class='form-control', _id='content', name='content', rows='15', required=True
                    ),
                    _class='mb-3',
                ),
                button('Опубликовать', type='submit', _class='btn btn-primary'),
                method='post',
                action='/add',
            ),
        )
        return self.__base(content)

    def about(self):
        content = html(
            h2('О нашем анонимном форуме'),
            p(
                'Добро пожаловать на наш анонимный форум! Здесь вы можете свободно обсуждать различные темы, не раскрывая свою; личность.'
            ),
            p('Правила форума:'),
            ul(
                li('Уважайте других участников'),
                li('Не публикуйте личную информацию'),
                li('Избегайте оскорблений и угроз'),
                li('Не нарушайте законодательство'),
            ),
            p('Доступ на форум:'),
            ul(
                li('Форум доступен по адресу https://127.0.0.1:8080'),
                li('---'),
                li('---'),
                li('---'),
            ),
            p('Приятного общения!'),
        )
        return self.__base(content)

    def files(self):
        content = html(ul(li('-'), li('-'), li('-'), li('-')))
        return self.__base(content)

    def statistic(self):
        content = html(
            div(
                # h1('Статистика', _class='mb-4'),
                div(
                    div(
                        h2('Пользователи', _class='card-title'),
                        ul(
                            li(p('Количество пользователей: 5000', _class='')),
                            li(p('Количество зарегистрированных пользователей за сегодня: 20', _class='')),
                            li(p('Количество зарегистрированных пользователей за месяц: 150', _class='')),
                            li(p('Количество зарегистрированных пользователей за год: 1200', _class='')),
                            _class='list-unstyled',
                        ),
                        _class='card-body',
                    ),
                    _class='card mb-4',
                ),
                div(
                    div(
                        h2('Посты', _class='card-title'),
                        ul(
                            li(p('Общее количество постов: 500', _class='')),
                            li(p('Общее количество тегированных постов: 700', _class='')),
                            _class='list-unstyled',
                        ),
                        _class='card-body',
                    ),
                    _class='card mb-4',
                ),
                div(
                    div(
                        h2('Файлы', _class='card-title'),
                        ul(
                            li(p('Количество всех файлов: 120', _class='')),
                            _class='list-unstyled',
                        ),
                        _class='card-body',
                    ),
                    _class='card mb-4',
                ),
                div(
                    div(
                        h2('Веб сервер', _class='card-title'),
                        ul(
                            li(p('Сколько раз заходили на сервер: 560', _class='')),
                            li(p('Занимаемое место статикой: 50 MB', _class='')),
                            _class='list-unstyled',
                        ),
                        _class='card-body',
                    ),
                    _class='card mb-4',
                ),
                # _class='container mt-5',
            ),
        )
        return self.__base(content)

    def view(self):
        pass


html_doc = html(
    head(
        meta(charset='UTF-8'),
        meta(name='viewport', content='width=device-width, initial-scale=1.0'),
        title('Анонимный Форум'),
        style("""
            body { font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; max-width: 800px; margin: 0 auto; }
            header { background: #f4f4f4; padding: 1rem; margin-bottom: 1rem; }
            nav a { margin-right: 10px; }
            .content { background: #fff; padding: 1rem; }
            footer { text-align: center; margin-top: 1rem; font-size: 0.8rem; }
        """),
    ),
    body(
        header(
            h1('Анонимный Форум'),
            nav(a('Главная', _href='/'), a('Новая тема', _href='/add_index_form'), a('О форуме', _href='/about_form')),
        ),
        div(p('Главная'), _class='content'),
        footer('&copy; 2023 Анонимный Форум'),
    ),
)

html_about = html(
    h2('О нашем анонимном форуме'),
    p(
        'Добро пожаловать на наш анонимный форум! Здесь вы можете свободно обсуждать различные темы, не раскрывая свою; личность.'
    ),
    p('Правила форума:'),
    ul(
        li('Уважайте других участников'),
        li('Не публикуйте личную информацию'),
        li('Избегайте оскорблений и угроз'),
        li('Не нарушайте законодательство'),
    ),
    p('Приятного общения!'),
)

html_list = html(div(_id='content'))
html_add_form = html(
    h2('Создать новый пост'),
    form(
        div(
            label('Имя:', _for='username'),
            input(type='text', _id='username', name='username', value='Аноним', required=True),
        ),
        div(label(_for=''), input(type='text', _id='1', value='=', required=True)),
        div(label(_for=''), input(type='text', _id='1', value='=', required=True)),
        div(label(_for=''), input(type='text', _id='1', value='=', required=True)),
        button('Опубликовать', type='submit'),
        method='post',
        action='/add',
    ),
)
html_view = html()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Helper functions
def register_or_login(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        pwdhash = hashlib.md5(password.encode()).hexdigest()
        new_user = User(username=username, password=pwdhash)
        db.add(new_user)
        db.commit()
        return new_user.id
    else:
        if login(db, username, password):
            return user.id
    return None


def login(db: Session, username: str, password: str):
    pwdhash = hashlib.md5(password.encode()).hexdigest()
    user = db.query(User).filter(User.username == username, User.password == pwdhash).first()
    return user is not None


def count_comments(db: Session, parent_id: int):
    comments = db.query(Post).filter(Post.parent == parent_id).all()
    count = len(comments)
    for comment in comments:
        count += count_comments(db, comment.id)
    return count


# Routes
@app.get('/', response_class=HTMLResponse)
async def index(request: Request, db: Session = Depends(get_db)):
    posts = db.query(Post).filter(Post.parent == 0).order_by(Post.id.desc()).limit(10).all()
    # return templates.TemplateResponse('index.html', {'request': request, 'posts': posts})
    # return HTMLResponse(content=page.to_html())
    # return HTMLResponse(content=base_page.render())
    # return HTMLResponse(content=str(html_doc))
    return HTMLResponse(content=str(ForumSmallExperemental().list()))


@app.get('/add_index_form', response_class=HTMLResponse)
async def index(request: Request, db: Session = Depends(get_db)):
    return HTMLResponse(content=str(ForumSmallExperemental().add_form()))


@app.get('/about_form', response_class=HTMLResponse)
async def index(request: Request, db: Session = Depends(get_db)):
    # return templates.TemplateResponse('about.html', {'request': request})
    return HTMLResponse(content=str(ForumSmallExperemental().about()))


@app.get('/register', response_class=HTMLResponse)
async def index(request: Request, db: Session = Depends(get_db)):
    return HTMLResponse(content=str(ForumSmallExperemental().register()))


@app.get('/login', response_class=HTMLResponse)
async def index(request: Request, db: Session = Depends(get_db)):
    return HTMLResponse(content=str(ForumSmallExperemental().login()))


@app.get('/tagged', response_class=HTMLResponse)
async def index(request: Request, db: Session = Depends(get_db)):
    return HTMLResponse(content=str(ForumSmallExperemental().tagged()))


@app.get('/files', response_class=HTMLResponse)
async def index(request: Request, db: Session = Depends(get_db)):
    return HTMLResponse(content=str(ForumSmallExperemental().files()))


@app.get('/statistic', response_class=HTMLResponse)
async def index(request: Request, db: Session = Depends(get_db)):
    return HTMLResponse(content=str(ForumSmallExperemental().statistic()))


@app.get('/view/{post_id}', response_class=HTMLResponse)
async def view_post(request: Request, post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail='Post not found')
    user = db.query(User).filter(User.id == post.user_id).first()
    comments = db.query(Post).filter(Post.parent == post_id).all()
    return templates.TemplateResponse(
        'view.html', {'request': request, 'post': post, 'user': user, 'comments': comments}
    )


@app.post('/register_new_user')
async def add_post(
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db),
):
    print('[✖]', db, username, password)
    # user_id = register_or_login(db, username, password)
    user = db.query(User).filter(User.username == username).first()
    if not user:
        # pwdhash = hashlib.md5(password.encode()).hexdigest()
        # new_user = User(username=username, password=pwdhash)
        # db.add(new_user)
        # db.commit()
        return 1
    # else:
    #     if login(db, username, password):
    #         return user.id
    return 2


@app.post('/add')
async def add_post(
    username: str = Form(...),
    password: str = Form(...),
    title: str = Form(...),
    content: str = Form(...),
    db: Session = Depends(get_db),
):
    user_id = register_or_login(db, username, password)
    if user_id:
        new_post = Post(title=title, content=content, user_id=user_id)
        db.add(new_post)
        db.commit()
        return RedirectResponse(url=f'/view/{new_post.id}', status_code=303)
    else:
        raise HTTPException(status_code=401, detail='Invalid credentials')


@app.post('/comment/{post_id}')
async def add_comment(
    post_id: int,
    username: str = Form(...),
    password: str = Form(...),
    title: str = Form(...),
    content: str = Form(...),
    db: Session = Depends(get_db),
):
    user_id = register_or_login(db, username, password)
    if user_id:
        new_comment = Post(title=title, content=content, user_id=user_id, parent=post_id)
        db.add(new_comment)
        db.commit()
        return RedirectResponse(url=f'/view/{post_id}', status_code=303)
    else:
        raise HTTPException(status_code=401, detail='Invalid credentials')


# Utility function
def make_html(content: str) -> str:
    return markdown.markdown(content)


# Add this to your Jinja2 environment
# pip install fastapi uvicorn sqlalchemy jinja2 python-multipart markdown
# app.jinja_env.filters['markdown'] = make_html

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8000)
