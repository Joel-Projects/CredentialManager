from flask_table import Col, Table, LinkCol
from flask_table.html import element
from pytz import timezone

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
            return content.astimezone().strftime(self.datetime_format)
        else:
            return 'Never'

class EnabledColumn(BaseCol):

    def td_contents(self, item, attr_list):
        return self.td_format((self.from_attr_list(item, attr_list), item.id))

    def td_format(self, item):
        content, item_id = item
        if content:
            return f'<i class="fas fa-check" id="{item_id}_icon" style="font-size: 28px;color: #00bc8c"></i>'
        else:
            return f'<i class="fas fa-times" id="{item_id}_icon" style="font-size: 28px; color: #E74C3C"></i>'

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
        self.tooltip = tooltip

    def td_contents(self, item, attr_list):
        return self.td_format((self.from_attr_list(item, attr_list), item.id, self.tooltip(item), str(item.created_by)))

    def td_format(self, item):
        content, item_id, tooltip, createdBy = item
        return f'<a href="/u/{createdBy}">{createdBy}</a><sup><span class="d-inline-block" style="opacity: 0.6" tabindex="0" data-toggle="tooltip" title="" data-original-title="{tooltip}"><i class="far fa-question-circle"></i></span></sup>'

class OwnerCol(BaseCol):

    def td_contents(self, item, attr_list):
        return self.td_format((self.from_attr_list(item, attr_list), item.id))

    def td_format(self, item):
        owner, item_id = item
        return f'<a href="/u/{owner}">{owner}</a>'


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

class EditColumn(ModifiedCol):

    def td_contents(self, item, attr_list):
        return self.td_format((self.from_attr_list(item, attr_list), item))

    def td_format(self, data):
        content, item = data
        if item.__tablename__ == 'users':
            itemSubPath = 'u'
        else:
            itemSubPath = item.__tablename__
        href = f'/{itemSubPath}/{content}'
        if hasattr(item, 'enabled'):
            enabled = item.enabled
        else:
            enabled = item.is_active
        if enabled:
            color = 'E74C3C'
            text = 'Disable'
        else:
            color = '00BC8C'
            text = 'Enable'
        toggleStr = f'''<a class="dropdown-item" id="{item.__tablename__}_{item.id}_toggle" style="color: #{color}" onclick="toggleItem('{item.__tablename__}', {item.id}, '{getattr(item, item._nameAttr)}', '{item._nameAttr}', '{item._enabledAttr}')">{text}</a>'''
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

class BaseTable(Table):

    def __init__(self, items, current_user=None, endpointAttr='id'):
        self.add_column('Edit', EditColumn('Edit', endpointAttr))
        super().__init__(items)

    def tr(self, item):
        content = ''.join(c.td(item, attr) for attr, c in self._cols.items()if c.show)
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




