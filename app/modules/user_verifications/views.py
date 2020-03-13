import logging

from flask import Blueprint, flash, jsonify, render_template, request
from flask_login import current_user, login_required
from wtforms import BooleanField

from .forms import UserVerificationForm
from .models import UserVerification
from .parameters import PatchUserVerificationDetailsParameters
from .resources import api
from .tables import UserVerificationTable
from ..users.models import User
from ...extensions import db, paginateArgs, verifyEditable


log = logging.getLogger(__name__)

userVerificationsBlueprint = Blueprint('user_verifications', __name__, template_folder='./templates', static_folder='./static', static_url_path='/user_verifications/static/')

@userVerificationsBlueprint.route('/user_verifications', methods=['GET', 'POST'])
@login_required
@paginateArgs(UserVerification)
def user_verifications(page, perPage):
    form = UserVerificationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            data = form.data
            userVerification = UserVerification(**data)
            db.session.add(userVerification)
        else:
            return jsonify(status='error', errors=form.errors)
    if current_user:
        if current_user.is_admin and not current_user.is_internal:
            paginator = UserVerification.query.filter(*(UserVerification.owner_id != i.id for i in User.query.filter(User.internal == True).all())).paginate(page, perPage, error_out=False)
        elif current_user.is_internal:
            paginator = UserVerification.query.paginate(page, perPage, error_out=False)
        else:
            paginator = current_user.user_verifications.paginate(page, perPage, error_out=False)
    else:
        paginator = current_user.user_verifications.paginate(page, perPage, error_out=False)
    table = UserVerificationTable(paginator.items, current_user=current_user)
    form = UserVerificationForm()
    return render_template('user_verifications.html', user_verificationsTable=table, user_verificationsForm=form, user_verification_paginator=paginator, route='user_verifications.user_verifications', perPage=perPage)

@userVerificationsBlueprint.route('/user_verifications/<UserVerification:user_verification>/', methods=['GET', 'POST'])
@login_required
@verifyEditable('user_verification')
def editUserVerification(user_verification):
    form = UserVerificationForm(obj=user_verification)
    if request.method == 'POST' and form.validate_on_submit():
        itemsToUpdate = []
        for item in PatchUserVerificationDetailsParameters.fields:
            if getattr(form, item, None) is not None:
                if not isinstance(getattr(form, item), BooleanField):
                    if getattr(form, item).data:
                        if getattr(user_verification, item) != getattr(form, item).data:
                            itemsToUpdate.append({'op': 'replace', 'path': f'/{item}', 'value': getattr(form, item).data})
                else:
                    if getattr(user_verification, item) != getattr(form, item).data:
                        itemsToUpdate.append({'op': 'replace', 'path': f'/{item}', 'value': getattr(form, item).data})
        if itemsToUpdate:
            for item in itemsToUpdate:
                PatchUserVerificationDetailsParameters().validate_patch_structure(item)
            try:
                with api.commit_or_abort(db.session, default_error_message='Failed to update User Verification details.'):
                    PatchUserVerificationDetailsParameters.perform_patch(itemsToUpdate, user_verification)
                    db.session.merge(user_verification)
                    flash(f'User Verification for Discord Member {user_verification.discord_id} saved successfully!', 'success')
            except Exception as error:
                log.exception(error)
                flash(f'Failed to update User Verification for Discord Member {user_verification.discord_id}', 'error')
    return render_template('edit_user_verification.html', user_verification=user_verification, form=form)