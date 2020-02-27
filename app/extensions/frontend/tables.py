from flask_login import current_user
from flask_table import Col, Table, LinkCol
from flask_table.html import element
from flask import current_app
from datetime import timezone

class BaseCol(Col):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('td_html_attrs', {})
        if not 'style' in kwargs['td_html_attrs']:
            kwargs['td_html_attrs']['style'] = 'text-align:center'
        super(BaseCol, self).__init__(*args, **kwargs)


class DatetimeColumn(BaseCol):

    def __init__(self, name, datetime_format='short', **kwargs):
        super(DatetimeColumn, self).__init__(name, **kwargs)
        self.datetime_format = datetime_format

    def td_format(self, content):
        if content:
            return str(current_app.extensions['moment'](content.astimezone(timezone.utc)).format('M/DD/YYYY, h:mm:ss a zz'))
        else:
            return 'Never'

class BoolIconColumn(BaseCol):

    def td_contents(self, item, attr_list):
        return self.td_format((self.from_attr_list(item, attr_list), item))

    def td_format(self, contents):
        content, item = contents
        if content:
            return f'<i class="fas fa-check" id="{item.__tablename__}_{item.id}_icon" style="font-size: 28px;color: #00bc8c"></i>'
        else:
            return f'<i class="fas fa-times" id="{item.__tablename__}_{item.id}_icon" style="font-size: 28px; color: #E74C3C"></i>'

class CopyableField(BaseCol):

    def td_contents(self, item, attr_list):
        return self.td_format((self.from_attr_list(item, attr_list), item))

    def td_format(self, contents):
        content, item = contents
        return f'''<div class="input-group mb-3">
  <input type="text" class="form-control" style="background-color: grey;color: lightgray" readonly value="{content}" aria-describedby="copyBox">
  <div class="input-group-append">
    <button class="input-group-text btn-dark" type="button"  onclick="copy(this)" id="copyBox"><a  class="fas fa-clipboard"></a></button>
  </div>
</div>
'''

class ToolTipColumn(BaseCol):

    def __init__(self, name, tooltip=None, **kwargs):
        super(ToolTipColumn, self).__init__(name, **kwargs)
        self.tooltip = tooltip

    def td_contents(self, item, attr_list):
        return self.td_format((self.from_attr_list(item, attr_list), item.id, self.tooltip))

    def td_format(self, item):
        content, item_id, tooltip = item
        if tooltip:
            return f'{content}<sup><span class="d-inline-block" style="opacity: 0.6" tabindex="0" data-toggle="tooltip" title="" data-original-title="{tooltip}"><i class="far fa-question-circle"></i></span></sup>'
        else:
            return content

class CreatedBy(BaseCol):

    def __init__(self, name, tooltip, **kwargs):
        super(CreatedBy, self).__init__(name, **kwargs)
        # self.attrName = attrName
        self.tooltip = tooltip

    def from_attr_list(self, item, attr_list):
        from flask_table.columns import _recursive_getattr
        out = _recursive_getattr(item, attr_list)
        return out

    def td_contents(self, item, attr_list):
        return self.td_format((self.from_attr_list(item, attr_list), item, self.tooltip(item)))

    def td_format(self, item):
        content, item, tooltip = item
        link = ''
        if item.createdBy.is_internal:
            if current_user.is_internal:
                link = f'href = "/u/{content}"'
        else:
            link = f'href = "/u/{content}"'
        if content:
            return f'<a {link}>{content}</a><sup><span class="d-inline-block" style="opacity: 0.6" tabindex="0" data-toggle="tooltip" title="" data-original-title="{tooltip}"><i class="far fa-question-circle"></i></span></sup>'
        else:
            return f'<a>{content}</a><sup><span class="d-inline-block" style="opacity: 0.6" tabindex="0" data-toggle="tooltip" title="" data-original-title="{tooltip}"><i class="far fa-question-circle"></i></span></sup>'

class OwnerCol(BaseCol):

    def td_contents(self, item, attr_list):
        return self.td_format((self.from_attr_list(item, attr_list), item.id))

    def td_format(self, item):
        owner, item_id = item
        return f'<a href="/u/{owner}">{owner}</a>'

class AppNameCol(BaseCol):

    def td_contents(self, item, attr_list):
        return self.td_format((self.from_attr_list(item, [attr_list[0], '__tablename__']), self.from_attr_list(item, [attr_list[0], 'id']), self.from_attr_list(item, attr_list)))

    def td_format(self, item):
        app_type, app_id, app_name = item
        return f'<a href="/{app_type}/{app_id}">{app_name}</a>'

class ModifiedCol(BaseCol):

    def td(self, item, attr):
        content = self.td_contents(item, self.get_attr_list(attr))
        return element('td', content=content, escape_content=False, attrs=self.td_html_attrs)

class ObjectCountCol(BaseCol):

    def td_contents(self, item, attr_list):
        return self.td_format((self.from_attr_list(item, attr_list), item.id, item))

    def td_format(self, item):
        item, item_id, owner = item
        return f'<a href="/u/{owner.username}/{item.attr.target_mapper.entity.__tablename__}">{item.count()}</a>'

class DropdownActionColumn(ModifiedCol):

    def __init__(self, name, *args, toggle=True, **kwargs):
        super(DropdownActionColumn, self).__init__(name, *args, **kwargs)
        self.toggle = toggle

    def td_contents(self, item, attr_list):
        return self.td_format((self.from_attr_list(item, attr_list), item))

    def td_format(self, data):
        content, item = data
        if item.__tablename__ == 'users':
            itemSubPath = 'u'
        else:
            itemSubPath = item.__tablename__
        href = f'/{itemSubPath}/{content}'
        if self.toggle:
            enabled = getattr(item, item._enabledAttr)
            if enabled:
                color = 'E74C3C'
                text = 'Disable'
            else:
                color = '00BC8C'
                text = 'Enable'
            toggleStr = f'''<a class="dropdown-item" id="{item.__tablename__}_{item.id}_toggle" style="color: #{color}" onclick="toggleItem('{item.__tablename__}', {item.id}, '{getattr(item, item._nameAttr)}', '{item._nameAttr}', '{item._enabledAttr}')">{text}</a>'''
        else:
            toggleStr = ''

        return f'''<div aria-label="Button group with nested dropdown" class="btn-group" role="group">
    <button type="button" class="btn btn-primary" onclick="location.href='{href}'">{self.name}</button>
    <div class="btn-group" role="group">
        <button id="{item.__tablename__}_{item.id}_buttonGroup" type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"></button>
        <div class="dropdown-menu" aria-labelledby="{item.__tablename__}_{item.id}_buttonGroup" x-placement="bottom-start" style="position: absolute; will-change: transform; top: 0px; left: 0px; transform: translate3d(0px, 36px, 0px);">
            <a class="dropdown-item" href="{href}">{self.name}</a>
            {toggleStr}
            <div class="dropdown-divider"></div>
            <a class="dropdown-item" onclick="showDeleteModal('{getattr(item, item._nameAttr)}', '{item.__tablename__}', {item.id}, {item.loopIndex})" style="color: red">Delete</a>
        </div>
    </div>
</div>
'''

class BaseTable(Table):

    def __init__(self, items, editable=True, canBeDisabled=True, current_user=None, endpointAttr='id'):
        if editable:
            name = 'Edit'
        else:
            name = 'View'
        self.add_column(name, DropdownActionColumn(name, endpointAttr, toggle=canBeDisabled))

        super().__init__(items)

    def th(self, col_key, col):
        if col_key == 'Edit':
            return element('th', content=self.th_contents(col_key, col), escape_content=False, attrs={'data-sorter': 'false' ,**col.th_html_attrs})
        else:
            return element('th', content=self.th_contents(col_key, col), escape_content=False, attrs=col.th_html_attrs)

    def tr(self, item):
        content = ''.join(c.td(item, attr) for attr, c in self._cols.items() if c.show)
        return element('tr', attrs=self.get_tr_attrs(item), content=content, escape_content=False)

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
    allow_empty = True
    classes = ['table', 'table-hover', 'table-bordered', 'table-striped']
    thead_classes = ['thead-dark']
    thead_attrs = {'style': 'text-align:center'}




