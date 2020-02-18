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

$(document).ready(function () {
    $("#bots_table").tablesorter({
        theme: "bootstrap",
        cancelSelection: false,
        sortReset: true
    });
    console.log('here')
    $("#owner").change(function () {
        let user_id = parseInt($("#owner").val())
        $.ajax({
            type: 'GET',
            url: `/api/v1/users/${user_id}/apps`,
        })
            .done(function finished(data) {
                var reddit_app = document.getElementById(`reddit_app`);
                var sentry_token = document.getElementById(`sentry_token`);
                var database_credential = document.getElementById(`database_credential`);
                removeOptions(reddit_app)
                removeOptions(sentry_token)
                removeOptions(database_credential)

                if (data.status == 422) {
                    popNotification('error', data.message);
                } else {
                    for (const i in data.reddit_apps) {
                        addOption(reddit_app, data.reddit_apps[i].id, data.reddit_apps[i].app_name)
                    }
                    for (const i in data.sentry_tokens) {
                        addOption(sentry_token, data.sentry_tokens[i].id, data.sentry_tokens[i].app_name)
                    }
                    for (const i in data.database_credentials) {
                        addOption(database_credential, data.database_credentials[i].id, data.database_credentials[i].app_name)
                    }
                }
            });
    });
});