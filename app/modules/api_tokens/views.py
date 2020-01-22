# coding: utf-8
"""
OAuth2 provider setup.

It is based on the code from the example:
https://github.com/lepture/example-oauth2-server

More details are available here:
* http://flask-oauthlib.readthedocs.org/en/latest/oauth2.html
* http://lepture.com/en/2013/create-oauth-server
"""
import logging

from flask_table import Col, Table
from flask_table.html import element
from pytz import timezone

from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user, login_required
from flask_restplus._http import HTTPStatus

log = logging.getLogger(__name__)
from .models import ApiToken

apiTokensBlueprint = Blueprint('api_tokens', __name__)

class DatetimeColumn(Col):

    def __init__(self, name, datetime_format='short', **kwargs):
        super(DatetimeColumn, self).__init__(name, **kwargs)
        self.datetime_format = datetime_format

    def td_format(self, content):
        if content:
            return content.astimezone().strftime(self.datetime_format)
        else:
            return 'Never'

class EnabledColumn(Col):

    def td_contents(self, item, attr_list):
        return self.td_format((self.from_attr_list(item, attr_list), item.id))

    def td_format(self, item):
        content, item_id = item
        if content:
            return f'<i class="fas fa-check" id="{item_id}_icon" style="font-size: 28px;color: #00bc8c"></i>'
        else:
            return f'<i class="fas fa-times" id="{item_id}_icon" style="font-size: 28px; color: #E74C3C"></i>'

class ModifiedCol(Col):

    def td(self, item, attr):
        content = self.td_contents(item, self.get_attr_list(attr))
        return element('td', content=content, escape_content=False, attrs=self.td_html_attrs)


class EditColumn(ModifiedCol):

    def td_contents(self, item, attr_list):
        return self.td_format((self.from_attr_list(item, attr_list), item))

    def td_format(self, data):
        content, item = data
        if item.__tablename__ == 'users':
            itemSubPath = 'u'
        else:
            itemSubPath = item.__tablename__
        href = f'/{itemSubPath}/{item.id}'
        if item.enabled:
            toggle = 'false'
            color = 'E74C3C'
            text = 'Disable'
        else:
            toggle = 'true'
            color = '00BC8C'
            text = 'Enable'
        toggleStr = f'''<a class="dropdown-item" id="{item.__tablename__}_{item.id}_toggle" style="color: #{color}" onclick="toggleItem('{item.__tablename__}', {item.id}, {toggle})">{text}</a>'''
        return f'''<div aria-label="Button group with nested dropdown" class="btn-group" role="group">
    <button type="button" class="btn btn-primary" onclick="location.href='{href}'">Edit</button>
    <div class="btn-group" role="group">
        <button id="{item.__tablename__}_{item.id}_buttonGroup" type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"></button>
        <div class="dropdown-menu" aria-labelledby="{item.__tablename__}_{item.id}_buttonGroup" x-placement="bottom-start" style="position: absolute; will-change: transform; top: 0px; left: 0px; transform: translate3d(0px, 36px, 0px);">
            <a class="dropdown-item" href="{href}">Edit</a>
            {toggleStr}
            <div class="dropdown-divider"></div>
            <a class="dropdown-item" onclick="showDeleteModal('{item.__tablename__}', {item.loopIndex}, {item.id})" style="color: red">Delete</a>
        </div>
    </div>
</div>
        '''

class TokenTable(Table):

    def __init__(self, items, current_user=None):
        self.add_column('Name', Col('Name', 'name'))
        self.add_column('Token', Col('Token', 'token'))
        self.add_column('Enabled', EnabledColumn('Enabled', 'enabled'))
        self.add_column('Last Used', DatetimeColumn('Last Used', attr='last_used', datetime_format='%m/%d/%Y %I:%M:%S %p %Z'))

        if current_user.admin:
            self.add_column('Owner', LinkCol('Owner', 'main.users', attr_list=['owner', 'username']))

        self.add_column('Edit', EditColumn('Edit', attr='last_used'))
        super().__init__(items)


    def tbody(self):
        out = []
        for loopIndex, item in enumerate(self.items, 1):
            setattr(item, 'loopIndex', loopIndex)
            out.append(self.tr(item))
        if not out:
            return ''
        outContent = '\n'.join(out)
        content = f'\n{outContent}\n'
        return element('tbody', content=content, escape_content=False)

    classes = ['table', 'table-hover', 'table-bordered', 'table-striped']
    html_attrs = {'id': 'api_tokens'}
    thead_classes = ['thead-dark']

@login_required
@apiTokensBlueprint.route('/api_tokens')
def api_tokens():
    if current_user.admin:
        api_tokens = ApiToken.query.all()
    else:
        api_tokens = current_user.api_tokens.all()
    table = TokenTable(api_tokens, current_user=current_user)
    return render_template('api_tokens.html', table=table)
