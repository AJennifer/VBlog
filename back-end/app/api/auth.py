from flask import g
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from app.api.errors import error_response
# from app.extensions import db
from app.models import User

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()


@basic_auth.verify_password
def verify_password(username,password):
    '''用于检查用户提供的用户名和密码'''
    user = User.query.filter_by(username=username).first()
    if user is None:
        return False
    g.current_user = user
    return user.check_password(password)


@basic_auth.error_handler
def basic_auth_error():
    '''当认证失败时返回的错误响应'''
    return error_response(401)


@token_auth.verify_token
def verify_token(token):
    '''用于检查用户请求是否具有token，并且token真实存在，且在有效期内'''
    g.current_user = User.verify_jwt(token) if token else None
    if g.current_user:
        #每次认证通过后，更新last__seen时间
        g.current_user.ping()
        db.session.commit()
    return  g.current_user is not None


@token_auth.error_handler
def token_auth_error():
    '''用于在 Token Auth 认证失败的情况下返回错误响应'''
    return error_response(401)