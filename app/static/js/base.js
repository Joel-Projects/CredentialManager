window.addEventListener('keydown', function (e) {
    if (e.keyIdentifier == 'U+000A' || e.keyIdentifier == 'Enter' || e.keyCode == 13) {
        if (e.target.nodeName == 'INPUT' && e.target.type == 'textarea') {
            e.preventDefault();
            return false;
        }
    } else if (e.key == " ") {
        // e.preventDefault(); // Prevent the spacebar from toggling and firing the click event
        e.target.offsetParent.children[0].click()
    }
}, true);

$(function () {
    $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        history.pushState({}, '', e.target.hash);
    });

    var hash = document.location.hash;
    var prefix = "tab_";
    if (hash) {
        $(`.nav-tabs a[href="${hash.replace(prefix, "")}"]`).tab('show')
    }
    $("#enabled").click(function () {
        var checked = this.checked;
        var enabled_checked = ''
        if (checked) {
            enabled_checked = 'y';
        }
        this.value = enabled_checked;
    });
});

function saveItem(button) {
    $(`#${button.id}`).disabled = true;
    $(`#${button.id}`).html('<span class="spinner-grow spinner-grow-sm" role="status" aria-hidden="true"></span>Saving...');
};

function saveUser(button) {
    $(`#${button.id}`).disabled = true;
    $(`#${button.id}`).html('<span class="spinner-grow spinner-grow-sm" role="status" aria-hidden="true"></span>Saving...');
};

function doneSave(id, form) {
    $(`#${id}`).prop('disabled', false);
    $(`#${id}`).prop('class', 'btn btn-primary');
    $(`#${id}`).html('Save');
};

function deleteTableItem(table, name, item_type, item_id, row_id, redirectUrl = null) {
    $.ajax({
        type: 'DELETE',
        url: `/api/v1/${item_type}/${item_id}`
    })
        .done(function (data) {
            if (data) {
                popNotification('error', data.message);
            } else {
                popNotification('success', `Successfully deleted ${name}`);
                table.deleteRow(row_id);
            }
        });
}

function deleteItem(name, item_type, item_id) {
    $.ajax({
        type: 'DELETE',
        url: `/api/v1/${item_type}/${item_id}`
    })
        .done(function (data) {
            if (data) {
                popNotification('error', data.message);
            } else {
                popNotification('success', `Successfully deleted ${name}`);
                // window.location.href = window.location.href
                // history.go(-1);
            }
        });
}

function popNotification(status, message) {
    if (status === 'error') {
        $.toast({
            title: 'Error Occurred',
            content: message,
            type: 'error'
        });
    }
    if (status === 'success') {
        $.toast({
            title: 'Success!',
            content: message,
            type: 'success',
            delay: 1500
        });
    }
}


$(document).ready(function () {
    $('[data-toggle="tooltip"]').tooltip();
});

$(function () {
    $('a').each(function () {
        if ($(this).prop('href') == window.location.href) {
            $(this).addClass('active');
        }
    });
});

function toggleItem(itemType, id, name, nameAttr, enabledAttr) {
    var elem = document.getElementById(`${itemType}_${id}_toggle`);
    var enable = elem.textContent === "Enable";
    $.ajax({
        data: JSON.stringify([{"op": "replace", "path": `/${enabledAttr}`, "value": enable}]),
        type: 'PATCH',
        url: `/api/v1/${itemType}/${id}`,
        contentType: 'application/json',
        dataType: 'json'
    })
        .done(function notify(data) {
            var elem = document.getElementById(`${itemType}_${id}_toggle`);
            var icon = document.getElementById(`${itemType}_${id}_icon`);
            if (data.status == 422) {
                popNotification('error', data.message);
            } else {
                if (data[enabledAttr]) {
                    elem.textContent = "Disable";
                    elem.style.color = "#E74C3C";
                    icon.setAttribute("class", "fas fa-check");
                    icon.style.color = "#00bc8c";
                    var toastStatus = "enabled";
                } else {
                    elem.textContent = "Enable";
                    elem.style.color = "#00bc8c";
                    icon.setAttribute("class", "fas fa-times");
                    icon.style.color = "#E74C3C";
                    var toastStatus = "disabled";
                }
                elem.setAttribute("class", "dropdown-item");
                popNotification('success', `Successfully ${toastStatus} '${data[nameAttr]}'`);
            }
        });
}

function createItem(button, form, resource, additonal = false, editor) {
    event.preventDefault();
    var data = {};
    $(`#${form} *`).filter(':input').each(function () {
        if (this.type == 'checkbox') {
            data[this.name] = this.checked;
        } else {
            data[this.name] = this.value;
        }
    });
    if (editor) {
        data['default_settings'] = JSON.stringify(editor.getValue())
    }
    $.ajax({
        data: data,
        type: 'POST',
        url: resource
    })
        .done(function notify(data) {
            if (data.status == 'error') {
                for (item in data.errors) {
                    var errors = data['errors'][item];
                    if (!($(`#${item}`).hasClass('is-invalid'))) {
                        $(`#${item}`).parent().append(`<div class="invalid-feedback" id="${item}Feedback">${errors[0]}</div>`);
                        $(`#${item}`).addClass('is-invalid')
                    }
                }
            } else {
                if (additonal) {
                    $(`#${form}`)[0].reset()
                } else {
                    window.location.href = window.location.href
                }
            }
            // noinspection SillyAssignmentJS
        });
}


function clearInvalidState(textBox) {
    textBox.classList.remove("is-invalid")
}

function resetForm(formId, focusElement, focus) {
    document.getElementById(fromID).reset();
    if (focus) {
        focusElement.focus()
    }
}

function showTableItemDeleteModal(name, item_type, item_id, row_id) {
    document.getElementById('delete-modal-body').innerHTML = `Are you <strong>sure</strong> you want to delete "${name}"?`;
    document.getElementById('delete-modal-footer').innerHTML = `<button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button><button type="button" class="btn btn-danger" onclick="deleteTableItem(${item_type}_table, '${name}', '${item_type}', ${item_id}, ${row_id})" data-dismiss="modal" id="deleteConfirm">Delete "${name}"</button>`;
    $(`#confirmationModal`).modal('show')
}

function showDeleteModal(name, item_type, item_id, row_id) {
    document.getElementById('delete-modal-body').innerHTML = `Are you <strong>sure</strong> you want to delete "${name}"?`;
    document.getElementById('delete-modal-footer').innerHTML = `<button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button><button type="button" class="btn btn-danger" onclick="deleteItem('${name}', '${item_type}', ${item_id})" data-dismiss="modal" id="deleteConfirm">Delete "${name}"</button>`;
    $(`#confirmationModal`).modal('show')
}

function copy(that) {
    var inp = that.offsetParent.firstElementChild;
    inp.select();
    document.execCommand('copy', false);
    $.toast({
        title: 'Copied to clipboard',
        type: 'success',
        delay: 1500,

    });
}

function invalidateField(field) {
    field.classList.add('is-invalid')
}

function removeOptions(selectBox) {
    var i;
    for (i = selectBox.options.length - 1; i >= 1; i--) {
        selectBox.remove(i);
    }
}

function addOption(selectBox, value, option) {
    var opt = document.createElement('option');
    opt.appendChild(document.createTextNode(option));
    opt.value = value;
    selectBox.appendChild(opt);
}
