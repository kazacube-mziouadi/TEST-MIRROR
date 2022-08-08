odoo.define("cao_connector.tree_view_reload", function (require) {
    "use strict";
    var core = require('web.core');
    var QWeb = core.qweb;
    var TreeView = require("web.TreeView");

    TreeView.include({
        render_buttons: function ($node) {
            var self = this;
            console.log(self)
            this.$buttons = $(QWeb.render("TreeView.buttons", { 'widget': this, display: true }));
            this.$buttons.on('click', 'button.o-tree-button-new', this.show_all.bind(this))
            $node = $node || this.options.$buttons;
            this.$buttons.appendTo($node);
        },
        get_additionnal_datas: function (records, parent_id) {
            if (records.length > 1 && this.fields_view.arch.attrs.default_order) {
                this.order_records(records);
            }
            return this._super(records, parent_id);
        },
        show_all: function () {
            var self = this
            $.each(this.records, function (i, record) {
                if (record.has_children) {
                    var element = $("[data-id=" + record.id + "]tr")
                    if (!element[0].classList.contains("oe_open") && !record.is_open) {
                        record.is_open = true
                        self.getdataasync(record.id, record.mf_tree_view_sim_action_children_ids, element).then((res)=>{
                            self.show_all()
                        }).fail(() => {
                            console.error("BUG")
                        })
                    }else if(element[0].getAttribute("class")==""){
                        self.showcontent(element[0].firstChild,record.id,true)
                    }

                }
            })
        },
        //Need async version of getdata or the recursive call of will be executed before getdata fills records with the new lines
        getdataasync: function (id, children_ids, $node) {
            var deferred = $.Deferred();
            var self = this;
            self.dataset.read_ids(children_ids, this.fields_list())
                .then((records) => {
                    return self.get_additionnal_datas(records, id);
                }, err => {
                    if (self.__processing_tree_click) {
                        self.__processing_tree_click[id] = false;
                    }
                })
                .then(function(records) {
                    _(records).each(function (record) {
                        record.has_children = false;
                        for (var c of self.children_field) {
                            if (record[c] && record[c].length) {
                                record.has_children = true;
                            }
                        }
                        self.records[record.id] = record;
                    });
                    var $curr_node
                    if (!$node && id != null) {
                        $curr_node = $('#treerow_' + id)
                    } else {
                        $curr_node = $node || $();
                    }
                    var children_rows = QWeb.render('TreeView.rows', {
                        'records': records,
                        'fields_view': self.fields_view.arch.children,
                        'fields': self.fields,
                        'level': $curr_node.data('level') || 0,
                        'render': self.format_tree_value,
                        'color_for': self.color_for,
                        'row_parent_id': id,
                        'self': self
                    });
                    if ($curr_node.length) {
                        $curr_node.addClass('oe_open');
                        $curr_node.after(children_rows);
                    } else {
                        self.$el.find('tbody').html(children_rows);
                    }
                    if (self.__processing_tree_click) {
                        self.__processing_tree_click[id] = false;
                    }
                    deferred.resolve();
                }).fail(() => {
                    if (self.__processing_tree_click) {
                        self.__processing_tree_click[id] = false;
                    }
                    deferred.reject()
                });
            return deferred.promise();
        },



        order_records: function (records, ordering_field = null, order_direction = null) {
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
            records.sort(function (a, b) {
                if (order_direction === "desc") {
                    return b[ordering_field] - a[ordering_field];
                } else {
                    return a[ordering_field] - b[ordering_field];
                }
            })
        },
        reload: function () {
            _(this.fields_view.arch.children).each(function (field) {
                if (field.attrs.modifiers && typeof field.attrs.modifiers !== "string") {
                    field.attrs.modifiers = JSON.stringify(field.attrs.modifiers);
                }
            });
            return this.load_tree(this.fields_view);
        },
    })
});
