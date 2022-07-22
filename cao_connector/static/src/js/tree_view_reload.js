odoo.define("cao_connector.tree_view_reload", function(require) {
    "use strict";
    // To expand all the groups of a tree view automatically, add the .expand_all class to the <tree>
    var TreeView = require("web.TreeView");

    TreeView.include({
        reload: function() {
            _(this.fields_view.arch.children).each(function (field) {
                if (field.attrs.modifiers && typeof field.attrs.modifiers !== "string") {
                    field.attrs.modifiers = JSON.stringify(field.attrs.modifiers);
                }
            });
            return this.load_tree(this.fields_view);
        },
    })
});
