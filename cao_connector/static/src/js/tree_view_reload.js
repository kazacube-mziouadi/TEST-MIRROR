odoo.define("cao_connector.tree_view_reload", function(require) {
    "use strict";
    var TreeView = require("web.TreeView");

    TreeView.include({
        get_additionnal_datas: function(records, parent_id) {
            if (records.length > 1 && this.fields_view.arch.attrs.default_order) {
                this.order_records(records);
            }
            return this._super(records, parent_id);
        },
        order_records: function(records, ordering_field=null, order_direction=null) {
            if (ordering_field === null || order_direction === null) {
                var default_order = this.fields_view.arch.attrs.default_order;
                var default_order_split = default_order.split(' ');
                if (default_order_split.length < 2) {
                    ordering_field = default_order;
                    order_direction = "asc";
                } else {
                    ordering_field = default_order_split[0];
                    order_direction = default_order_split[1];
                }
            }
            records.sort(function(a, b) {
                if (order_direction === "desc") {
                    return b[ordering_field] - a[ordering_field];
                } else {
                    return a[ordering_field] - b[ordering_field];
                }
            })
        },
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
