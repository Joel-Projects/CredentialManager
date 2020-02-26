import logging, praw

import requests
from flask import Blueprint, request, render_template, flash, jsonify
from flask_login import current_user, login_required
from wtforms import BooleanField

from .parameters import PatchUserVerificationDetailsParameters
from ..users.models import User
from ...extensions import db, paginateArgs, verifyEditable

log = logging.getLogger(__name__)
from .models import UserVerification
from .forms import UserVerificationForm
from .tables import UserVerificationTable, UserVerificationTable

userVerificationsBlueprint = Blueprint('user_verifications', __name__, template_folder='./templates', static_folder='./static', static_url_path='/user_verifications/static/')

@login_required
@userVerificationsBlueprint.route('/user_verifications', methods=['GET', 'POST'])
@paginateArgs(UserVerification)
def user_verifications(page, perPage):
    form = UserVerificationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            data = form.data
            # del data['csrf_token']
            userVerification = UserVerification(**data)
            db.session.add(userVerification)
        else:
            return jsonify(status='error', errors=form.errors)
    if current_user:
        if current_user.is_admin and not current_user.is_internal:
            paginator = UserVerification.query.filter(*(UserVerification.owner_id!=i.id for i in User.query.filter(User.internal==True).all())).paginate(page, perPage, error_out=False)
        elif current_user.is_internal:
            paginator = UserVerification.query.paginate(page, perPage, error_out=False)
        else:
            paginator = current_user.user_verifications.paginate(page, perPage, error_out=False)
    else:
        paginator = current_user.user_verifications.paginate(page, perPage, error_out=False)
    table = UserVerificationTable(paginator.items, current_user=current_user)
    form = UserVerificationForm()
    return render_template('user_verifications.html', user_verificationsTable=table, user_verificationsForm=form, user_verification_paginator=paginator, route='user_verifications.user_verifications', perPage=perPage)


@login_required
@userVerificationsBlueprint.route('/user_verifications/<UserVerification:user_verification>/', methods=['GET', 'POST'])
@verifyEditable('user_verification')
def editUserVerification(user_verification):
    form = UserVerificationForm(obj=user_verification)
    if request.method == 'POST':
        if form.validate_on_submit():
            itemsToUpdate = []
            for item in PatchUserVerificationDetailsParameters.fields:
                if getattr(form, item, None) is not None:
                    if not isinstance(getattr(form, item), BooleanField):
                        if getattr(form, item).data:
                            if getattr(user_verification, item) != getattr(form, item).data:
                                itemsToUpdate.append({"op": "replace", "path": f'/{item}', "value": getattr(form, item).data})
                    else:
                        if getattr(user_verification, item) != getattr(form, item).data:
                            itemsToUpdate.append({"op": "replace", "path": f'/{item}', "value": getattr(form, item).data})
            if itemsToUpdate:
                response = requests.patch(f'{request.host_url}api/v1/user_verifications/{user_verification.id}', json=itemsToUpdate, headers={'Cookie': request.headers['Cookie'], 'Content-Type': 'application/json'})
                if response.status_code == 200:
                    flash(f'User Verification {user_verification.discord_id!r} saved successfully!', 'success')
                else:
                    flash(f'Failed to update User Verification {user_verification.discord_id!r}', 'error')
        # else:
        #     return jsonify(status='error', errors=form.errors)
    return render_template('edit_user_verification.html', user_verification=user_verification, form=form)