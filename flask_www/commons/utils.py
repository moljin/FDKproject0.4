import os
import re
import unicodedata
import uuid

from flask import g, request, abort, flash, session

from flask_www.configs import db
from flask_www.configs.config import NOW, BASE_DIR


def flash_form_errors(form):
    for _, errors in form.errors.items():
        for e in errors:
            flash(e)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png', 'gif'}


def random_word(length):  # 같은 이름의 파일을 다른 이름으로 랜덤하게 만든다.
    import random, string
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def filename_format(now, filename):
    return "{random_word}-{user_id}-{username}-{date}-{microsecond}{extension}".format(
        random_word=random_word(20),
        user_id=str(g.user.id),
        username=g.user.email.split('@')[0],
        date=str(now.date()),
        microsecond=now.microsecond,
        extension=os.path.splitext(filename)[1],
    )


def base_file_path(filename):
    base_relative_path="static/media/user_images/{request_path}/{year}/{month}/{day}/{user_id}/{username}/{random_word}/{filename}".format(
        request_path=request.path.split('/')[2],
        year=NOW.year,
        month=NOW.month,
        day=NOW.day,
        user_id=str(g.user.id),
        username=g.user.email.split('@')[0],
        random_word=random_word(20),
        filename=filename_format(NOW, filename),
    )
    return base_relative_path


def save_file(now, file):
    if file.filename == '':
        abort(400)
    if file and allowed_file(file.filename):
        filename = filename_format(now, file.filename)
        relative_path = base_file_path(filename)
        upload_path = os.path.join(BASE_DIR, relative_path)
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
        file.save(upload_path)
        return relative_path, upload_path   # 템플릿단에서는 relative_path가 사용된다. static 폴더가 있어야 찾아간다.
    else:
        abort(400)


def c_slugify(value, allow_unicode=False):
    """Django 에서 가져옴(def slugify)"""
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')


def current_db_session_add(obj):
    current_db_sessions = db.session.object_session(obj)
    current_db_sessions.add(obj)


def current_db_session_delete(obj):
    current_db_sessions = db.session.object_session(obj)
    current_db_sessions.delete(obj)


def base64_to_file(img_string, file_name):
    import base64
    from PIL import Image
    import io
    img_data = base64.b64decode(img_string)
    image_path = base_file_path(file_name)
    upload_path = os.path.join(BASE_DIR, image_path)
    os.makedirs(os.path.dirname(upload_path), exist_ok=True)

    img = Image.open(io.BytesIO(img_data))
    img.save(image_path)

    return image_path, file_name  # filename


def file_to_base64(file_path, file_name):
    import base64
    _format = file_name.split('.')[1]
    with open(file_path, "rb") as image_file:
        base64_string = base64.b64encode(image_file.read()).decode('utf-8')
        base64_src = "data:image/" + _format + ";base64," + base64_string

    return base64_src, file_name


def file_to_base64_src(file_path, file_name):
    import base64
    _format = file_name.split('.')[1]
    with open(file_path, "rb") as image_file:
        base64_string = base64.b64encode(image_file.read()).decode('utf-8')
        base64_src = "data:image/" + _format + ";base64," + base64_string

    return base64_src


def ajax_post_key():
    if 'ajax_post_key' in session:
        session['ajax_post_key'] = session.get('ajax_post_key')
    else:
        session["ajax_post_key"] = str(uuid.uuid4())
    return session['ajax_post_key']
