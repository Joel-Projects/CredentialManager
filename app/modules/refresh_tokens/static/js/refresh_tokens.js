$(document).ready(function () {
    $("#all").change(function () {
        $("#scopes_group *").filter(':input').each(function () {
            let check = $("#all")[0].checked
            if (this.name !== 'identity') {
                this.checked = check;
                this.disabled = check;
            }
        });
    })
    $("#owner").change(function () {
        let user_id = parseInt($("#owner").val())
        $.ajax({
            type: 'GET',
            url: `/api/v1/users/${user_id}/apps`,
        })
            .done(function finished(data) {
                var reddit_app = document.getElementById(`reddit_app_id`);
                removeOptions(reddit_app)

                if (data.status == 422) {
                    popNotification('error', data.message);
                } else {
                    for (const i in data.reddit_apps) {
                        addOption(reddit_app, data.reddit_apps[i].id, data.reddit_apps[i].app_name)
                    }
                }
            });
    })
    $("#create_refresh_token_form *").filter(':input').change(function () {
        let app_id = parseInt($('#reddit_app_id').val())
        let verification_id = parseInt($('#user_verification_id').val())

        let owner_id = parseInt($('#owner').val())
        let permanent = $('#duration_permanent')[0]
        let temporary = $('#duration_temporary')[0]
        const scopes = [];
        $("#create_refresh_token_form *").filter(':input').each(function () {
            if (this.id !== 'all' && this.type == 'checkbox') {
                if (this.checked) {
                    scopes.push(this.id)
                }
            }
        })
        if (app_id) {
            var duration = ''
            if (permanent.checked) {
                duration = 'permanent'
            } else if (temporary.checked) {
                duration = 'temporary'
            } else {
                duration = 'temporary'
            }
            var data = {owner_id: owner_id, reddit_app: app_id, duration: duration, scopes: scopes};
            if (!isNaN(verification_id)) {
                data.user_verification_id = verification_id
            }
            $.ajax({
                type: 'POST',
                traditional: true,
                url: `/api/v1/reddit_apps/${app_id}/generate_auth`,
                data: data
            })
                .done(function (data) {
                    $('#auth_url').val(data.auth_url)
                })
        }
    })
});