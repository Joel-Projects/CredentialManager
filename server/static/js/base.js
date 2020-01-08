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

function popNotification(success, error) {
    if (error) {
        $.toast({
            title: 'Error Occurred',
            content: error,
            type: 'error'
        });
    }
    if (success) {
        $.toast({
            title: 'Success!',
            content: success,
            type: 'success',
            delay: 1500
        });
    }
}

function popNotificationNew(status, message) {
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

function toggleItem(item_type, id, enabled) {
    $.ajax({
        data: {
            item_type: item_type,
            id: id,
            enabled: enabled
        },
        type: 'POST',
        url: '/api/toggle'
    })
        .done(function notify(data) {
            var elem = document.getElementById(`${data.id}_toggle`);
            var icon = document.getElementById(`${data.id}_icon`);
            if (data.enabled) {
                elem.textContent = "Disable";
                elem.style.color = "#E74C3C";
                icon.setAttribute("class", "fas fa-check");
                icon.style.color = "#00bc8c";
                var toastStatus = "enabled";
            }
            if (!data.enabled) {
                elem.textContent = "Enable";
                elem.style.color = "#00bc8c";
                icon.setAttribute("class", "fas fa-times");
                icon.style.color = "#E74C3C";
                var toastStatus = "disabled";
            }
            elem.setAttribute("class", "dropdown-item");
            popNotification(`Successfully ${toastStatus} ${data.item_name}!`, data.error);
        });
}

function deleteItem(item_type, item_id, cascade) {
    $('#confirmationModal').modal('hide');
    $('#delete').prop('disabled', true);
    $('#delete').html('<div class="spinner-grow spinner-grow-sm text-primary" role="status"></div> Loading...');
    $.ajax({
        data: {
            item_type: item_type,
            item_id: item_id,
            cascade: cascade
        },
        type: 'POST',
        url: '/api/delete'
    })
        .done(function (data) {
            console.log(data);
            $('#delete').html('Deleted');
            $('#delete').prop('class', 'btn btn-danger');
        });
    event.preventDefault();
    return false;
}

function clearInvalidState(textBox) {
    textBox.className = "form-control"
}

function resetForm(formId, focusElement, focus) {
    document.getElementById(fromID).reset();
    if (focus) {
        focusElement.focus()
    }
}

function showDeleteModal(app_name, item_id, row_id) {
    document.getElementById('delete-modal-body').innerHTML = `Are you <strong>sure</strong> you want to delete the "${app_name}" "${app_type}"?`;
    document.getElementById('delete-modal-footer').innerHTML = `<button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button><button type="button" class="btn btn-danger" onclick="deleteFlair(${flair_id}, ${row_id})" data-dismiss="modal" id="deleteConfirm">Delete this flair</button>`;
    $('#confirmationModal').modal('show')
}