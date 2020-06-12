/**
 * A Javascript module to loadeding/refreshing options of a select2 list box using ajax based on selection of another select2 list box.
 *
 * @url : https://gist.github.com/ajaxray/187e7c9a00666a7ffff52a8a69b8bf31
 * @auther : Anis Uddin Ahmad <anis.programmer@gmail.com>
 *
 * Live demo - https://codepen.io/ajaxray/full/oBPbQe/
 * w: http://ajaxray.com | t: @ajaxray
 */
var Select2Cascade = ( function(window, $) {

    function Select2Cascade(parent, child, url, select2Options, parentPlaceholder, childPlaceholder) {
        var afterActions = [];
        var options = select2Options || {};

        // Register functions to be called after cascading data loading done
        this.then = function(callback) {
            afterActions.push(callback);
            return this;
        };
        var parentOptions = options
        parentOptions.placeholder = parentPlaceholder
        parent.select2(parentOptions).on("change", function (e) {

            child.prop("disabled", true);
            var _this = this;

            $.getJSON(url.replace(':parentId:', $(this).val()), function(items) {
                var newOptions = '';
                for(var id in items) {
                    newOptions += `<option value="${id}">${items[id]}</option>`;
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

})( window, $);