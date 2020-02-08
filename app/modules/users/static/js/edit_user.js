$(document).ready(function () {
    $("#api_tokensTable").tablesorter({
        theme: "bootstrap",
        cancelSelection: false,
        sortReset: true
    });
    $("#reddit_appsTable").tablesorter({
        theme: "bootstrap",
        cancelSelection: false,
        sortReset: true
    });
    $("#sentry_tokensTable").tablesorter({
        theme: "bootstrap",
        cancelSelection: false,
        sortReset: true
    });
    $("#database_credentialsTable").tablesorter({
        theme: "bootstrap",
        cancelSelection: false,
        sortReset: true
    });
});