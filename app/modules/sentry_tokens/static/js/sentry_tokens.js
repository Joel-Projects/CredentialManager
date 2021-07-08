function formatPlatform(platform) {
    if (!platform.id) {
        return platform.text;
    }
    return $(`<span><img src="/sentry_tokens/static/svg/${platform.icon}.svg" style="border-radius: 3px;margin-right: 8px;height: fit-content"/> ${platform.text}</span>`);
}

function processTeams(data) {
    if (!platform.id) {
        return platform.text;
    }
    return $(`<span><img src="/sentry_tokens/static/svg/${platform.icon}.svg" style="border-radius: 3px;margin-right: 8px;height: fit-content"/> ${platform.text}</span>`);
}

var Select2Cascade = (function (window, $) {

    function Select2Cascade(parent, child, url, select2Options, parentPlaceholder, childPlaceholder) {
        var afterActions = [];
        var options = select2Options || {};

        // Register functions to be called after cascading data loading done
        this.then = function (callback) {
            afterActions.push(callback);
            return this;
        };
        var parentOptions = options
        parentOptions.placeholder = parentPlaceholder
        parent.select2(parentOptions).on("change", function (e) {

            child.prop("disabled", true);
            var _this = this;

            $.getJSON(url.replace(':parentId:', $(this).val()), function (items) {
                var newOptions = '';
                for (var id in items) {
                    newOptions += `<option value="${items[id][0]}">${items[id][1]}</option>`;
                }
                var childOptions = options
                childOptions.placeholder = childPlaceholder
                child.select2('destroy').html(newOptions).prop("disabled", false).select2(childOptions);
                afterActions.forEach(function (callback) {
                    callback(parent, child, items);
                });
            });
        });
    }

    return Select2Cascade;

})(window, $);
$(document).ready(function () {
    let sentryTeam = $('#sentry_team')
    let add_sentry_token_modal = $('#add_sentry_token_modal');
    new Select2Cascade($('#sentry_organization'), sentryTeam, '/api/v1/sentry_tokens/sentry_organizations/:parentId:/teams', {theme: 'bootstrap4', dropdownParent: add_sentry_token_modal}, 'Select an Organization', 'Select a Team');
    $('#sentry_platform').select2({
        data: [
            {
                "id": "",
                "text": ""
            },
            {
                "children": [
                    {
                        "icon": "csharp",
                        "id": "csharp",
                        "text": "C#"
                    },
                    {
                        "icon": "generic",
                        "id": "csharp-aspnetcore",
                        "text": "ASP.NET Core"
                    }
                ],
                "text": "C#"
            },
            {
                "icon": "cordova",
                "id": "cordova",
                "text": "Cordova"
            },
            {
                "icon": "electron",
                "id": "electron",
                "text": "Electron"
            },
            {
                "icon": "elixir",
                "id": "elixir",
                "text": "Elixir"
            },
            {
                "children": [
                    {
                        "icon": "go",
                        "id": "go",
                        "text": "Go"
                    },
                    {
                        "icon": "generic",
                        "id": "go-http",
                        "text": "net/http"
                    }
                ],
                "text": "Go"
            },
            {
                "children": [
                    {
                        "icon": "java",
                        "id": "java",
                        "text": "Java"
                    },
                    {
                        "icon": "java",
                        "id": "java-android",
                        "text": "Android"
                    },
                    {
                        "icon": "app-engine",
                        "id": "java-appengine",
                        "text": "Google App Engine"
                    },
                    {
                        "icon": "java",
                        "id": "java-log4j",
                        "text": "Log4j 1.x"
                    },
                    {
                        "icon": "java",
                        "id": "java-log4j2",
                        "text": "Log4j 2.x"
                    },
                    {
                        "icon": "java",
                        "id": "java-logback",
                        "text": "Logback"
                    },
                    {
                        "icon": "java",
                        "id": "java-logging",
                        "text": "java.util.logging"
                    }
                ],
                "text": "Java"
            },
            {
                "children": [
                    {
                        "icon": "javascript",
                        "id": "javascript",
                        "text": "JavaScript"
                    },
                    {
                        "icon": "angularjs",
                        "id": "javascript-angular",
                        "text": "Angular"
                    },
                    {
                        "icon": "angularjs",
                        "id": "javascript-angularjs",
                        "text": "AngularJS"
                    },
                    {
                        "icon": "javascript",
                        "id": "javascript-backbone",
                        "text": "Backbone"
                    },
                    {
                        "icon": "javascript",
                        "id": "javascript-browser",
                        "text": "Browser JavaScript"
                    },
                    {
                        "icon": "ember",
                        "id": "javascript-ember",
                        "text": "Ember"
                    },
                    {
                        "icon": "react",
                        "id": "javascript-react",
                        "text": "React"
                    },
                    {
                        "icon": "vue",
                        "id": "javascript-vue",
                        "text": "Vue"
                    }
                ],
                "text": "JavaScript"
            },
            {
                "icon": "windows",
                "id": "minidump",
                "text": "Minidump"
            },
            {
                "icon": "generic",
                "id": "native",
                "text": "Native (C/C++)"
            },
            {
                "children": [
                    {
                        "icon": "nodejs",
                        "id": "node",
                        "text": "Node.js"
                    },
                    {
                        "icon": "nodejs",
                        "id": "node-connect",
                        "text": "Connect"
                    },
                    {
                        "icon": "nodejs",
                        "id": "node-express",
                        "text": "Express"
                    },
                    {
                        "icon": "nodejs",
                        "id": "node-koa",
                        "text": "Koa"
                    }
                ],
                "text": "Node.js"
            },
            {
                "children": [
                    {
                        "icon": "apple",
                        "id": "cocoa",
                        "text": "Objective-C"
                    },
                    {
                        "icon": "generic",
                        "id": "cocoa-objc",
                        "text": "Objective-C"
                    },
                    {
                        "icon": "swift",
                        "id": "cocoa-swift",
                        "text": "Swift"
                    }
                ],
                "text": "Objective-C"
            },
            {
                "children": [
                    {
                        "icon": "php",
                        "id": "php",
                        "text": "PHP"
                    },
                    {
                        "icon": "laravel",
                        "id": "php-laravel",
                        "text": "Laravel"
                    },
                    {
                        "icon": "php",
                        "id": "php-monolog",
                        "text": "Monolog"
                    },
                    {
                        "icon": "php",
                        "id": "php-symfony",
                        "text": "Symfony"
                    }
                ],
                "text": "PHP"
            },
            {
                "children": [
                    {
                        "icon": "python",
                        "id": "python",
                        "text": "Python"
                    },
                    {
                        "icon": "flask",
                        "id": "python-aiohttp",
                        "text": "AIOHTTP"
                    },
                    {
                        "icon": "flask",
                        "id": "python-asgi",
                        "text": "ASGI"
                    },
                    {
                        "icon": "bottle",
                        "id": "python-bottle",
                        "text": "Bottle"
                    },
                    {
                        "icon": "python",
                        "id": "python-celery",
                        "text": "Celery"
                    },
                    {
                        "icon": "django",
                        "id": "python-django",
                        "text": "Django"
                    },
                    {
                        "icon": "python",
                        "id": "python-falcon",
                        "text": "Falcon"
                    },
                    {
                        "icon": "flask",
                        "id": "python-flask",
                        "text": "Flask"
                    },
                    {
                        "icon": "python",
                        "id": "python-pylons",
                        "text": "Pylons"
                    },
                    {
                        "icon": "python",
                        "id": "python-pyramid",
                        "text": "Pyramid"
                    },
                    {
                        "icon": "python",
                        "id": "python-pythonawslambda",
                        "text": "AWS Lambda"
                    },
                    {
                        "icon": "python",
                        "id": "python-pythonserverless",
                        "text": "Serverless (Python)"
                    },
                    {
                        "icon": "python",
                        "id": "python-rq",
                        "text": "RQ (Redis Queue)"
                    },
                    {
                        "icon": "python",
                        "id": "python-sanic",
                        "text": "Sanic"
                    },
                    {
                        "icon": "python",
                        "id": "python-tornado",
                        "text": "Tornado"
                    },
                    {
                        "icon": "python",
                        "id": "python-tryton",
                        "text": "Tryton"
                    },
                    {
                        "icon": "python",
                        "id": "python-wsgi",
                        "text": "WSGI"
                    }
                ],
                "text": "Python"
            },
            {
                "icon": "apple",
                "id": "react-native",
                "text": "React-Native"
            },
            {
                "children": [
                    {
                        "icon": "ruby",
                        "id": "ruby",
                        "text": "Ruby"
                    },
                    {
                        "icon": "ruby",
                        "id": "ruby-rack",
                        "text": "Rack"
                    },
                    {
                        "icon": "rails",
                        "id": "ruby-rails",
                        "text": "Rails"
                    }
                ],
                "text": "Ruby"
            },
            {
                "icon": "rust",
                "id": "rust",
                "text": "Rust"
            }
        ],
        allowClear: true,
        theme: 'bootstrap4',
        placeholder: 'Select a platform',
        templateResult: formatPlatform,
        templateSelection: formatPlatform,
        dropdownParent: add_sentry_token_modal
    });
    sentryTeam.select2({
        theme: 'bootstrap4',
        placeholder: 'Select an organization first',
        disabled: true,
        dropdownParent: add_sentry_token_modal
    });
});