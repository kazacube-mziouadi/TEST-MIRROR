odoo.define('my_fab.list_view_expand_all_auto', function(require) {
    // To expand all the groups of a tree view automatically, add the .expand_all class to the <tree>

    var core = require('web.core');
    var ListView = require('web.ListView');
    var ViewManager = require('web.ViewManager');
    var _t = core._t;

    ListView.include({
        expand_all: function() {
            var self = this;
            var rows = $('.oe_group_header');
            var max = rows.length;
            if (max > 0) {
                for (var i = 0; i < max; i++) {
                    // Is this row open or closed according to the triangle symbol
                    var $closed = $(rows[i]).find('th.oe-group-name span.ui-icon-triangle-1-e');
                    if ($closed.length > 0) {
                        $(rows[i]).trigger('click');
                        // wait for click to have rendered new line then call again to open other groups
                        setTimeout(function() {self.expand_all();}, 500);
                    }
                }
            }
        },
        start: function () {
            this._super();
            var self = this;
            setTimeout(function() {
                if ($(".expand-all").length > 0) {
                    self.expand_all();
                }
            }, 1500);
        }
    })
});
