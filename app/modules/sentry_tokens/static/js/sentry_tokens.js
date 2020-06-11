$(document).ready(function () {
    $("#sentry_tokens_table").tablesorter({
        theme: "bootstrap",
        cancelSelection: false,
        sortReset: true
    });
    $("#create_sentry_app").click(function () {
        var create_sentry_app = $("create_sentry_app")
        var sentry_organization = document.getElementById(`sentry_organization`);
        removeOptions(sentry_organization)
        var sentry_team = document.getElementById(`sentry_team`);
        removeOptions(sentry_team)
        if (create_sentry_app.val) {
            addOption(sentry_organization, '', '-- Select an Organization --')
            $.ajax({
                type: 'GET',
                url: `/api/v1/sentry_tokens/sentry_organizations/`,
            })
                .done(function finished(data) {
                    for (const i in data) {
                        addOption(sentry_organization, data[i].slug, data[i].name)
                    }
                });
        }
    });
    $("#sentry_organization").change(function () {
        var org_slug = $("#sentry_organization").val()
        var sentry_team = document.getElementById(`sentry_team`);
        removeOptions(sentry_team)
        addOption(sentry_team, '', '-- Select a Team --')
        $.ajax({
            type: 'GET',
            url: `/api/v1/sentry_tokens/sentry_organizations/${org_slug}/teams`,
        })
            .done(function finished(data) {
                for (const i in data) {
                    addOption(sentry_team, data[i].slug, data[i].name)
                }
            });
    });
});