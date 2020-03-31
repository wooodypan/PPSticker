from flask import g, jsonify,\
request
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth, MultiAuth
from ..models import User
from . import api
from .errors import unauthorized, forbidden

auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth('Bearer')
# 多重认证结合的例子 https://github.com/miguelgrinberg/Flask-HTTPAuth/blob/master/examples/multi_auth.py
multi_auth = MultiAuth(auth, token_auth)

# 临时排除某些API的授权
def exclude():
    return 'hotsticker' in request.path \
           or '/uploadimg/' in request.path \
           or '/getmytoken' in request.path

#为了能够使用令牌验证请求，除了普通的凭据之外，还要接受令牌
@auth.verify_password
def verify_password(email_or_token, password):
    if exclude():
        return True
    if email_or_token == '':
        return False
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(email=email_or_token.lower()).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)

@token_auth.verify_token
def verify_token(token):
    return verify_password(token, '')
    # http://www.pythondoc.com/flask-restful/third.html#id6
    # https://github.com/miguelgrinberg/REST-auth


@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')


@api.route('/getmytoken/', methods=['POST'])
def get_my_token():
    username = request.json['username']
    password = request.json['password']
    user = User.query.filter_by(email=username.lower()).first()
    if not user:
        return jsonify({'error':'user not exist'})
    if user.verify_password(password):
        return jsonify({'token': user.generate_auth_token(
        expiration=360), 'expiration': 360})
    else:
        return jsonify({'error':''})


# flask_httpauth --> login_required 如果模板登录了，会先走auth/views.py里面的before_request(),再走这个
@api.before_request
@multi_auth.login_required #@auth.login_required
def before_request():
    if exclude():
        return
    if not g.current_user.is_anonymous and \
            not g.current_user.confirmed:
        return forbidden('Unconfirmed account')


@api.route('/tokens/', methods=['POST'])
def get_token():
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized('Invalid credentials')
    return jsonify({'token': g.current_user.generate_auth_token(
        expiration=3600), 'expiration': 3600})
