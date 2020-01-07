function saveUser() {
    let form = document.getElementById('createUserForm')
    let currentUser = document.getElementById('currentUser');
    let username = document.getElementById('username');
    let password = document.getElementById('password');
    let usernameFeedback = document.getElementById('usernameFeedback');
    let admin = document.getElementById('admin');

    if (form.checkValidity()) {
        $('#submit').prop('disabled', true);
        $('#submit').html('<span class="spinner-grow spinner-grow-sm" role="status" aria-hidden="true"></span>Saving...');
        $.ajax({
            data: {
                user: currentUser.innerText,
                username: username.value,
                password: password.value,
                admin: admin.checked
            },
            type: 'POST',
            url: '/api/users/update'
        })
            .done(function (data) {
                if (data.userExists) {
                    username.className = "form-control is-invalid";
                    usernameFeedback.innerText = "That username is taken!"
                    $('#submit').prop('disabled', false);
                    $('#submit').prop('class', 'btn btn-primary');
                    $('#submit').html('Submit Changes');
                }
                if (!data.userExists) {
                    $('#submit').html('Updated');
                    $('#submit').prop('disabled', false);
                    $('#submit').prop('class', 'btn btn-primary');
                    $('#submit').html('Submit Changes');
                }
                popNotification(data.success, data.error);
            });
    }
};

$(function () {
    let updatePasswordToggle = document.getElementById('updatePasswordToggle');
    let passowrdEntry = document.getElementById('passowrdEntry');
    let passowrdInput = document.getElementById('password');
    passowrdEntry.hidden = !updatePasswordToggle.checked;
    passowrdInput.required = updatePasswordToggle.checked;

    $("#updatePasswordToggle").click(function () {
        passowrdEntry.hidden = !updatePasswordToggle.checked;
        passowrdInput.required = updatePasswordToggle.checked;
    });
    $("#createUserForm").submit(function (e) {
        e.preventDefault();
    });
});

function addRow(data) {
    let reddit_appsTable = document.getElementById('reddit_apps_table');
    let row = reddit_appsTable.insertRow();
    let app_name = row.insertCell();
    app_name.innerHTML = `<a href="/reddit_apps/${data.reddit_app.id}">${data.reddit_app.app_name}</a>`;
    let description = row.insertCell();
    description.innerHTML = data.reddit_app.description;
    let comment = row.insertCell();
    if (data.reddit_app.comment) {
        comment.innerHTML = `<i class="fas fa-check" id="${data.reddit_app.id}_comment_icon" style="font-size: 28px;color: #00bc8c"></i>`
    } else {
        comment.innerHTML = `<i class="fas fa-times" id="${data.reddit_app.id}_comment_icon" style="font-size: 28px; color: #E74C3C"></i>`
    }
    let lock = row.insertCell();
    if (data.reddit_app.lock) {
        lock.innerHTML = `<i class="fas fa-check" id="${data.reddit_app.id}_lock_icon" style="font-size: 28px;color: #00bc8c"></i>`
    } else {
        lock.innerHTML = `<i class="fas fa-times" id="${data.reddit_app.id}_lock_icon" style="font-size: 28px; color: #E74C3C"></i>`
    }
    let lock_comment = row.insertCell();
    if (data.reddit_app.lock_comment) {
        lock_comment.innerHTML = `<i class="fas fa-check" id="${data.reddit_app.id}_lock_comment_icon" style="font-size: 28px;color: #00bc8c"></i>`
    } else {
        lock_comment.innerHTML = `<i class="fas fa-times" id="${data.reddit_app.id}_lock_comment_icon" style="font-size: 28px; color: #E74C3C"></i>`
    }
    let ban = row.insertCell();
    if (data.reddit_app.ban) {
        ban.innerHTML = `<i class="fas fa-check" id="${data.reddit_app.id}_ban_icon" style="font-size: 28px;color: #00bc8c"></i>`
    } else {
        ban.innerHTML = `<i class="fas fa-times" id="${data.reddit_app.id}_ban_icon" style="font-size: 28px; color: #E74C3C"></i>`
    }
    let usernote = row.insertCell();
    if (data.reddit_app.usernote) {
        usernote.innerHTML = `<i class="fas fa-check" id="${data.reddit_app.id}_usernote_icon" style="font-size: 28px;color: #00bc8c"></i>`
    } else {
        usernote.innerHTML = `<i class="fas fa-times" id="${data.reddit_app.id}_usernote_icon" style="font-size: 28px; color: #E74C3C"></i>`
    }
    let enabled = row.insertCell();
    let options = row.insertCell();
    if (data.reddit_app.enabled) {
        enabled.innerHTML = `<i class="fas fa-check" id="${data.reddit_app.id}_enabled_icon" style="font-size: 28px;color: #00bc8c"></i>`;
        enableToggle = `<a class="dropdown-item" id="${data.reddit_app.id}_toggle" style="color: #E74C3C" onclick="toggleReason('${data.reddit_app.id}', false)">Disable</a>`;
    } else {
        enabled.innerHTML = `<i class="fas fa-times" id="${data.reddit_app.id}_enabled_icon" style="font-size: 28px; color: #E74C3C"></i>`;
        enableToggle = `<a class="dropdown-item" id="${data.reddit_app.id}_toggle" style="color: #00bc8c" onclick="toggleReason('${data.reddit_app.id}', false)">Enable</a>`;
    }
    options.innerHTML = `
                        <div class="btn-group" role="group" aria-label="Button group with nested dropdown">
                            <button type="button" class="btn btn-primary" onclick="location.href='/reddit_apps/${data.reddit_app.id}'">Edit</button>
                            <div class="btn-group" role="group">
                                <button id="btnGroupDrop1" type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"></button>
                                <div class="dropdown-menu" aria-labelledby="btnGroupDrop1">
                                    <a class="dropdown-item" href="/reddit_apps/${data.reddit_app.id}">Edit</a>
                                    ${enableToggle}
                                    <div class="dropdown-divider"></div>
                                    <a class="dropdown-item" onclick="showDeleteModalSentry('${data.reddit_app.id}', ${row.rowIndex})" style="color: red">Delete</a>
                                </div>
                            </div>
                        </div>`;
}

$(function () {
    // let redirectUri = document.getElementById('redirect_uri');
    // let customRedirectUriLabel = document.getElementById('customRedirectUriLabel');
    // let customRedirectUriType = document.getElementById('customRedirectUriType');
    // let redirectUriLabel = document.getElementById('redirectUriLabel');
    // let form = document.getElementById('createRedditAppForm');
    // customRedirectUriLabel.hidden = redirectUri.value == "None";
    // customRedirectUriType.hidden = redirectUri.value == "None";
    // redirectUriLabel.required = redirectUri.value != "None";
    //
    // $("#redirectUri").change(function () {
    //     if (redirectUri.value == "custom") {
    //         customRedirectUriLabel.hidden = false;
    //         customRedirectUriType.hidden = false;
    //         customRedirectUriType.required = true;
    //         customRedirectUriType.value = ''
    //     } else {
    //         customRedirectUriLabel.hidden = true;
    //         customRedirectUriType.hidden = true;
    //         customRedirectUriType.required = false;
    //         customRedirectUriType.value = redirectUri.value
    //     }
    //     redirectUriLabel.hidden = (redirectUri.value == "None");
    //     redirectUri.hidden = (redirectUri.value == "None");
    // });

    $("#reddit_apps").tablesorter({
        theme: "bootstrap",
        cancelSelection: false,
        sortReset: true
    });

    $('#reddit_appCreate').click(function () {
        let form = document.getElementById('newRedditAppTokenForm');
        let app_name = document.getElementById('app_name');
        let short_name = document.getElementById('short_name');
        let app_type = document.getElementById('app_type');
        let app_description = document.getElementById('app_description');
        let client_id = document.getElementById('client_id');
        let client_secret = document.getElementById('client_secret');
        let user_agent = document.getElementById('user_agent');
        let redirect_uri = document.getElementById('redirect_uri');
        let enable = document.getElementById('enabled');

        if (form.checkValidity()) {
            $('#reddit_appCreate').prop('disabled', true);
            $('#reddit_appCreate').html('<span class="spinner-grow spinner-grow-sm" role="status" aria-hidden="true"></span>Adding...');

            $.ajax({
                data: {
                    app_name: app_name.value,
                    short_name: short_name.value,
                    app_type: app_type.value,
                    app_description: app_description.value,
                    client_id: client_id.value,
                    client_secret: client_secret.value,
                    user_agent: user_agent.value,
                    redirect_uri: redirect_uri.value,
                    enable: enable.checked
                },
                type: 'POST',
                url: '/api/reddit_app/create'
            })
                .done(function (data) {
                    console.log(data);
                    if (data.reddit_appExists) {
                        app_name.className = "form-control is-invalid";
                        app_nameFeedback.innerText = "This app already exists!";
                        $('#reddit_appCreate').prop('disabled', false);
                        $('#reddit_appCreate').prop('class', 'btn btn-primary');
                        $('#reddit_appCreate').html('Create');
                    } else {
                        addRow(data);
                        $('#reddit_appCreate').html('Created');
                        $('#newReasonModal').modal('hide');
                        $('#reddit_appCreate').prop('disabled', false);
                        $('#reddit_appCreate').prop('class', 'btn btn-primary');
                        $('#reddit_appCreate').html('Create');
                        resetForm('newRedditAppTokenForm', app_name, this.content === "Add and New");
                        event.preventDefault();
                        popNotification(data.success, data.error);
                        return false;
                    }
                });
        }
    });

$('#reddit_appCreateNew').click(function () {
    let form = document.getElementById('newRedditAppTokenForm');
    let app_name = document.getElementById('app_name');
    let short_name = document.getElementById('short_name');
    let app_type = document.getElementById('app_type');
    let app_description = document.getElementById('app_description');
    let client_id = document.getElementById('client_id');
    let client_secret = document.getElementById('client_secret');
    let user_agent = document.getElementById('user_agent');
    let redirect_uri = document.getElementById('redirect_uri');
    let enable = document.getElementById('enabled');

    if (form.checkValidity()) {
        $('#reddit_appCreateNew').prop('disabled', true);
        $('#reddit_appCreateNew').html('<span class="spinner-grow spinner-grow-sm" role="status" aria-hidden="true"></span>Adding...');
        $.ajax({
            data: {
                app_name: app_name.value,
                short_name: short_name.value,
                app_type: app_type.value,
                app_description: app_description.value,
                client_id: client_id.value,
                client_secret: client_secret.value,
                user_agent: user_agent.value,
                redirect_uri: redirect_uri.value,
                enable: enable.checked
            },
            type: 'POST',
            url: '/api/reddit_app/create'
        })
            .done(function (data) {
                console.log(data);
                if (data.reddit_appExists) {
                    app_name.className = "form-control is-invalid";
                    app_nameFeedback.innerText = "This app already exists!"
                    $('#reddit_appCreateNew').prop('disabled', false);
                    $('#reddit_appCreateNew').prop('class', 'btn btn-primary');
                    $('#reddit_appCreateNew').html('Create');
                } else {
                    addRow(data);
                    $('#reddit_appCreateNew').html('Created');
                    $('#reddit_appCreateNew').prop('disabled', false);
                    $('#reddit_appCreateNew').prop('class', 'btn btn-primary');
                    $('#reddit_appCreateNew').html('Create and New');
                    resetForm('newRedditAppTokenForm', app_name, true);
                    event.preventDefault();
                    popNotification(data.success, data.error);
                    return false;
                }
            });
    }
});

});