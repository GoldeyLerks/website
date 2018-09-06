from wtforms import Form, BooleanField, StringField, PasswordField, validators, ValidationError, SubmitField, TextAreaField
import dbcl as db
import hashlib

user = None

def validate_name(form, field):
    if db.get_user_from_username(field.data) != None:
        raise ValidationError('Username is taken!')

def validate_email(form, field):
    if db.get_user_from_email(field.data) != None:
        raise ValidationError('Email is taken!')



def check_pass(form, field):
    global user
    if user != None and user["password"] != hashlib.sha256(field.data.encode()).hexdigest():
        raise ValidationError('Incorrect password!')

def check_username(form, field):
    global user
    u = db.get_user_from_username(field.data)
    if  u == None:
        user = None
        raise ValidationError('Username not found!')
    else:
        user = u

class SignupForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=20), validate_name], render_kw={"placeholder": "Username", "class": "form-input"})
    email = StringField('Email', [validators.Length(min=6, max=35), validators.Email(), validate_email], render_kw={"placeholder": "Email", "class": "form-input"})
    password = PasswordField('Password', [validators.DataRequired()], render_kw={"placeholder": "Password", "class": "form-input"})
    confirm = PasswordField('Repeat Password', [validators.DataRequired(), validators.EqualTo('password', message='Passwords must match')], render_kw={"placeholder": "Repeat Password", "class": "form-input"})
    submit = SubmitField('Signup', render_kw={"class": "form-submit"})

class LoginForm(Form):
    username = StringField('Username', [check_username], render_kw={"placeholder": "Username", "class": "form-input"})
    password = PasswordField('Password', [validators.DataRequired(), check_pass], render_kw={"placeholder": "Password", "class": "form-input"})
    submit = SubmitField('Login', render_kw={"class": "form-submit"})

class PostForm(Form):
    title = StringField('Title', [validators.DataRequired(), validators.Length(min=4,max=40)], render_kw={"placeholder": "Post Title", "class": "form-post-title"})
    content = TextAreaField('Content', [validators.DataRequired(), validators.Length(min=10,max=20000)], render_kw={"placeholder": "Post Content (Markdown Allowed)", "class": "form-post-content"})
    submit = SubmitField('Post', render_kw={"class": "form-post-submit"})


class EditPostForm(Form):
    title = StringField('Title', [validators.DataRequired(), validators.Length(min=4,max=40)], render_kw={"placeholder": "Post Title", "class": "form-post-title"})
    content = TextAreaField('Content', [validators.DataRequired(), validators.Length(min=10,max=20000)], render_kw={"placeholder": "Post Content (Markdown Allowed)", "class": "form-post-content"})
    submit = SubmitField('Edit', render_kw={"class": "form-post-submit"})

class SettingsForm(Form):
    avatar = StringField('Avatar Url', [validators.Length(max=200)], render_kw={"placeholder": "Avatar Url", "class": "form-input"})
    ckey = StringField('Byond CKEY', [validators.Length(max=30)], render_kw={"placeholder": "Byond CKEY", "class": "form-input"})
    submit = SubmitField('Save', render_kw={"class": "form-post-submit"})
