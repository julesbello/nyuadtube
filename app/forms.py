from flask.ext.wtf import Form, TextField, BooleanField, TextAreaField
from flask.ext.wtf import Required, ValidationError

class ProfileForm(Form):
		facebook = TextField('facebook')
		username = TextField('username')

class LoginForm(Form):
    openid = TextField('openid', validators = [Required()])
    remember_me = BooleanField('remember_me', default = False)
    
def has_link(form, field):
		if "youtube.com" not in field.data and "v=" not in field.data:
				raise ValidationError("Not a valid YouTube url")

class UploadForm(Form):
		link = TextField('link', validators = [has_link])
		comment = TextAreaField('comment')