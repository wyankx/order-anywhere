from flask import abort
from flask_login import current_user


def abort_if_restaurant():
    if current_user.__class__.__name__ == 'Restaurant':
        abort(403)


def abort_if_user():
    if current_user.__class__.__name__ == 'User':
        abort(403)
