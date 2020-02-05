$(document).ready(function () {
    $("#bots_table").tablesorter({
        theme: "bootstrap",
        cancelSelection: false,
        sortReset: true
    });
    $('#botCreate').click(function () {
        let name = document.getElementById('name');
        let dsn = document.getElementById('dsn');
        let owner = document.getElementById('owner');
        let form = document.getElementById('addBotForm');
        // if (form.checkValidity()) {
            $('#botCreate').prop('disabled', true);
            $('#botCreate').html('<span class="spinner-grow spinner-grow-sm" role="status" aria-hidden="true"></span>Adding...');
            $.ajax({
                data: {
                    name: name.value,
                    dsn: dsn.value,
                    owner_id: parseInt(owner.value)
                },
                type: 'POST',
                url: '/api/v1/bots'
            })
                .done(function (data) {
                    console.log(data);
                    if (!('status' in data)) {
                        let botsTable = document.getElementById('bots');
                        let row = botsTable.insertRow();
                        let name = row.insertCell();
                        name.innerHTML = `<a href="/bots/${data.name}">${data.name}</a>`;
                        let dsn = row.insertCell();
                        dsn.innerHTML = data.dsn;
                        let created = row.insertCell();
                        created.innerHTML = data.created;
                        let enabled = row.insertCell();
                        enabled.innerHTML = `<i class="fas fa-check" id="bots_${data.id}_icon" style="font-size: 28px;color: #00bc8c"></i>`;
                        let edit = row.insertCell();
                        edit.innerHTML = `
                            <div class="btn-group" role="group" aria-label="Button group with nested dropdown">
                                <button type="button" class="btn btn-primary" onclick="location.href='/bots/${data.id}'">Edit</button>
                                <div class="btn-group" role="group">
                                    <button id="btnGroupDrop1" type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"></button>
                                    <div class="dropdown-menu" aria-labelledby="btnGroupDrop1">
                                        <a class="dropdown-item" href="/bots/${data.id}">Edit</a>
                                        <a class="dropdown-item" id="bots_${data.id}_toggle" style="color: #00bc8c" onclick="toggleItem('bots', data.id, data.name, 'name', 'enabled')">Enable</a>
                                        <div class="dropdown-divider"></div>
                                        <a class="dropdown-item" onclick="showDeleteModal('${data.user.name}', ${row.rowIndex})" style="color: red">Delete</a>
                                    </div>
                                </div>
                            </div>`;
                        $('#botCreate').html('Created');
                        $('#addBotModal').modal('hide');
                        $('#botCreate').prop('disabled', false);
                        $('#botCreate').prop('class', 'btn btn-primary');
                        $('#botCreate').html('Create');
                    }
                    popNotification(data.status, data.message);
                });
        // }
});
});

function showDeleteModal(name, row_id) {
    document.getElementById('delete-modal-body').innerHTML = `Are you <strong>sure</strong> you want to delete ${name}?`;
    document.getElementById('delete-modal-footer').innerHTML = `<button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button><button type="button" class="btn btn-danger" onclick="deleteToken('${name}',${row_id})" data-dismiss="modal" id="deleteConfirm">Delete this user</button>`;
    $('#confirmationModal').modal('show')
}

function deleteToken(name, row_id) {
    $('#confirmationModal').modal('hide');
    $.ajax({
        data: {
            id: id
        },
        type: 'DELETE',
        url: '/api/v1/bots'
    })
        .done(function (data) {
            console.log(data);
            if (data.success) {
                popNotification(`Successfully deleted api token ${data.name}`, data.error);
                document.getElementById("users").deleteRow(row_id);
            }
        });
    event.preventDefault();
    return false;
}

$(function () {
    let form = document.getElementById('addBotForm');

    $('[data-toggle="tooltip"]').tooltip();


});
