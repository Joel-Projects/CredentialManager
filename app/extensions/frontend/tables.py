import logging
from datetime import timezone

from flask import current_app, url_for
from flask_login import current_user
from flask_table import Col, Table
from flask_table.html import element
from markupsafe import Markup

log = logging.getLogger(__name__)


class BaseCol(Col):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("td_html_attrs", {})
        if not "style" in kwargs["td_html_attrs"]:
            kwargs["td_html_attrs"]["style"] = "text-align:center"
        super(BaseCol, self).__init__(*args, **kwargs)
        self.sort_name = self.attr_list[0]


class DatetimeColumn(BaseCol):
    def td_format(self, content):
        if content:
            return str(
                current_app.extensions["moment"](
                    content.astimezone(timezone.utc)
                ).format(" MM/DD/YYYY, h:mm:ss a")
            )
        else:
            return "Never"


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
        return f"""<div class="input-group mb-3">
  <input type="text" class="form-control" style="background-color: grey;color: lightgray" readonly value="{content}" aria-describedby="copyBox">
  <div class="input-group-append">
    <button class="input-group-text btn-dark" type="button"  onclick="copy(this)" id="copyBox"><a  class="fas fa-clipboard"></a></button>
  </div>
</div>
"""


class ToolTipColumn(BaseCol):  # pragma: no cover
    def __init__(self, name, tooltip=None, **kwargs):
        super(ToolTipColumn, self).__init__(name, allow_sort=False, **kwargs)
        self.tooltip = tooltip

    def td_contents(self, item, attr_list):
        return self.td_format(
            (self.from_attr_list(item, attr_list), item.id, self.tooltip)
        )

    def td_format(self, item):
        content, item_id, tooltip = item
        if tooltip:
            return f'{content}<sup><span class="d-inline-block" style="opacity: 0.6" tabindex="0" data-toggle="tooltip" title="" data-original-title="{tooltip}"><i class="far fa-question-circle"></i></span></sup>'
        else:
            return content


class CreatedBy(BaseCol):  # pragma: no cover
    def __init__(self, name, tooltip, **kwargs):
        super(CreatedBy, self).__init__(name, **kwargs)
        self.tooltip = tooltip

    def from_attr_list(self, item, attr_list):
        from flask_table.columns import _recursive_getattr

        out = _recursive_getattr(item, attr_list)
        return out

    def td_contents(self, item, attr_list):
        return self.td_format(
            (self.from_attr_list(item, attr_list), item, self.tooltip(item))
        )

    def td_format(self, item):
        content, item, tooltip = item
        link = ""
        if item.createdBy:
            if item.createdBy.is_internal:
                if current_user.is_internal:
                    link = f' href = "/u/{content}"'
            else:
                link = f' href = "/u/{content}"'
        return f'<a{link}>{content}</a><sup><span class="d-inline-block" style="opacity: 0.6" tabindex="0" data-toggle="tooltip" data-html="true" title=\'{tooltip}\'><i class="far fa-question-circle"></i></span></sup>'


class OwnerCol(BaseCol):
    def td_contents(self, item, attr_list):
        return self.td_format((self.from_attr_list(item, attr_list), item.id))

    def td_format(self, item):
        owner, item_id = item
        return f'<a href="/u/{owner}">{owner}</a>'


class AppNameCol(BaseCol):
    def td_contents(self, item, attr_list):
        return self.td_format(
            (
                self.from_attr_list(item, [attr_list[0], "__tablename__"]),
                self.from_attr_list(item, [attr_list[0], "id"]),
                self.from_attr_list(item, attr_list),
            )
        )

    def td_format(self, item):
        app_type, app_id, app_name = item
        return f'<a href="/{app_type}/{app_id}">{app_name}</a>'


class ModifiedCol(BaseCol):
    def td(self, item, attr):
        content = self.td_contents(item, self.get_attr_list(attr))
        return element(
            "td", content=content, escape_content=False, attrs=self.td_html_attrs
        )


class ObjectCountCol(BaseCol):
    def td_contents(self, item, attr_list):
        return self.td_format((self.from_attr_list(item, attr_list), item.id, item))

    def td_format(self, item):
        item, item_id, owner = item
        return f'<a href="/u/{owner.username}/{item.attr.target_mapper.entity.__tablename__}">{item.count()}</a>'


class DropdownActionColumn(ModifiedCol):
    def __init__(self, name, *args, toggle=True, **kwargs):
        super(DropdownActionColumn, self).__init__(
            name, allow_sort=False, *args, **kwargs
        )
        self.toggle = toggle

    def td_contents(self, item, attr_list):
        return self.td_format((self.from_attr_list(item, attr_list), item))

    def td_format(self, data):
        content, item = data
        if item.__tablename__ == "users":
            itemSubPath = "u"
        else:
            itemSubPath = item.__tablename__
        href = f"/{itemSubPath}/{content}"
        if self.toggle:
            enabled = getattr(item, item._enabledAttr)
            if enabled:
                color = "E74C3C"
                text = "Disable"
            else:
                color = "00BC8C"
                text = "Enable"
            toggleStr = f"""<a class="dropdown-item" id="{item.__tablename__}_{item.id}_toggle" style="color: #{color}" onclick="toggleItem('{item.__tablename__}', {item.id}, '{getattr(item, item._nameAttr)}', '{item._nameAttr}', '{item._enabledAttr}')">{text}</a>"""
        else:  # pragma: no cover
            toggleStr = ""

        return f"""<div aria-label="Button group with nested dropdown" class="btn-group" role="group">
    <button type="button" class="btn btn-primary" onclick="location.href='{href}'">{self.name}</button>
    <div class="btn-group" role="group">
        <button id="{item.__tablename__}_{item.id}_buttonGroup" type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"></button>
        <div class="dropdown-menu" aria-labelledby="{item.__tablename__}_{item.id}_buttonGroup" x-placement="bottom-start" style="position: absolute; will-change: transform; top: 0px; left: 0px; transform: translate3d(0px, 36px, 0px);">
            <a class="dropdown-item" href="{href}">{self.name}</a>
            {toggleStr}
            <div class="dropdown-divider"></div>
            <a class="dropdown-item" onclick="showTableItemDeleteModal('{getattr(item, item._nameAttr)}', '{item.__tablename__}', {item.id}, {item.loopIndex})" style="color: red">Delete</a>
        </div>
    </div>
</div>
"""


class BaseTable(Table):
    allow_empty = True
    allow_sort = True
    classes = [
        "table",
        "table-hover",
        "table-bordered",
        "table-striped",
        "tablesorter-bootstrap",
    ]
    thead_attrs = {"style": "text-align:center"}
    thead_classes = ["thead-dark"]

    def __init__(
        self,
        items,
        editable=True,
        canBeDisabled=True,
        endpointAttr="id",
        sort_columns=None,
        sort_directions=None,
        *args,
        **kwargs,
    ):
        if sort_columns is None:
            sort_columns = []
        self.sort_columns = sort_columns
        if sort_directions is None:
            sort_directions = []
        self.sort_directions = sort_directions
        self.sort_keys = dict(zip(sort_columns, sort_directions))
        if editable:
            name = "Edit"
        else:
            name = "View"
        self.add_column(
            name, DropdownActionColumn(name, endpointAttr, toggle=canBeDisabled)
        )
        super().__init__(items, *args, **kwargs)
        self._cols.move_to_end(name)

    def th_contents(self, col_key, col):
        if not (col.allow_sort and self.allow_sort):
            return None, None, Markup.escape(col.name)

        if col.sort_name in self.sort_columns:
            sort_reverse = (
                self.sort_directions[self.sort_columns.index(col.sort_name)] == "desc"
            )
            if sort_reverse:
                sort_href = self.sort_url(col.sort_name, remove_sort=True)
                sort_direction = "tablesorter-headerDesc"
            else:
                sort_href = self.sort_url(col.sort_name, reverse=True)
                sort_direction = "tablesorter-headerAsc"
        else:
            sort_href = self.sort_url(col.sort_name)
            sort_direction = "tablesorter-headerUnSorted"
        return sort_direction, sort_href, Markup.escape(col.name)

    def th(self, col_key, col):
        sort_class, sort_href, content = self.th_contents(col_key, col)
        classes = ["tablesorter-header"]
        attrs = {
            **col.th_html_attrs,
        }
        if sort_class:
            classes.append(sort_class)
            attrs["onclick"] = f"location.href='{sort_href}';"
        else:
            classes.append("sorter-false")
            classes.append("tablesorter-headerUnSorted")
        attrs["class"] = " ".join(classes)
        return element(
            "th",
            content=content,
            escape_content=False,
            attrs=attrs,
        )

    def tr(self, item):
        content = "".join(c.td(item, attr) for attr, c in self._cols.items() if c.show)
        return element(
            "tr", attrs=self.get_tr_attrs(item), content=content, escape_content=False
        )

    def tbody(self):
        out = []
        for loopIndex, item in enumerate(self.items, 1):
            setattr(item, "loopIndex", loopIndex)
            out.append(self.tr(item))
        if not out:
            return ""
        outContent = "\n".join(out)
        content = f"\n{outContent}\n"
        return element("tbody", content=content, escape_content=False)

    def sort_url(self, col_key, reverse=False, remove_sort=False):
        current_columns = self.sort_columns[::]
        current_directions = self.sort_directions[::]
        if remove_sort:
            item_index = self.sort_columns.index(col_key)
            current_columns.pop(item_index)
            current_directions.pop(item_index)
        else:
            ""
            if reverse:
                direction = "desc"
            else:
                direction = "asc"
            if col_key in current_columns:
                current_directions[current_columns.index(col_key)] = direction
            else:
                current_columns.append(col_key)
                current_directions.append(direction)
        if current_columns:
            return url_for(
                **self.route_kwargs,
                orderBy=",".join(current_columns),
                direction=",".join(current_directions),
            )
        else:
            return url_for(**self.route_kwargs)
