define(
    [
        'backbone', 'backform', 'bootstrap',
        'bootstrap-datepicker',
        'app/views/rooms_form',
	      'app/views/model_select_control',
        'app/models/order_form_overview',
        'app/models/order_items',
        'app/models/site',
        'app/models/order_form_detail',
        'text!app/templates/order_choose_form.html',
        'text!app/templates/order_form_button.html',
        'text!app/templates/order_select_items.html',
        'text!app/templates/order_logistics.html',
    ],
    function(Backbone, Backform, bootstrap,
             bsdp, RoomFormView, ModelSelectControl,
             OrderFormOverview, OrderItems, Site, OrderFormDetail,
             choose_form_template, button_template, select_items_template,
             logistics_template) {
        var OrderFlowView = Backbone.View.extend({
            initialize: function(app, loading) {
                this.app = app;
                this.model = this.app.models.order;
                this.choose_form_template = _.template(choose_form_template);
                this.order_forms = new OrderFormOverview();
                this.order_items = new OrderItems();
                this.delivery = new Backbone.Model();
                this.site = new Site({id: this.model.get('site')});
                this.listenTo(this.order_forms, 'add', this.render);
                this.listenTo(this.model, 'change', this.render);
                this.listenTo(this.site, 'change', this.render);
                this.site.fetch();
                this.order_forms.fetch();
                this.button_template = _.template(button_template);
                this.select_items_template = _.template(select_items_template);
                this.logistics_template = _.template(logistics_template);
                this.item_views = [];
            },
            events: {
                'change #id_notes': 'savenotes',
                'change .item-quantity': 'changeQuantity',
                'click #order-proceed-button': 'renderLogistics',
                'click #order-submit': 'save',
            },
            savenotes: function(e) {
                this.model.set('notes', e.target.value);
            },
            changeQuantity: function(e) {
                var oi = this.order_items.get(e.target.name);
                if (!oi) {
                    this.order_items.add({
                        id: parseInt(e.target.name),
                        quantity: e.target.value
                    });
                } else {
                    oi.set('quantity', e.target.value);
                }
                return false;
            },
            orderTotal: function() {
                return _.reduce(this.order_items, function(memo, value) {
                    return memo + totalForItem(value)
                });                
            },
            el: '#order-flow-view',
            totalForItem: function(item, order_items) {
                var oi = order_items.get(item.id)
                if (!oi) {
                    return "";
                }
                if (!oi.get('quantity')) {
                    return "";
                }
                var q = parseFloat(oi.get('quantity'));
                if (!q) {
                    return "";
                }
                if (item.unit_cost) {
                    var num = item.unit_cost * q;
                    return Math.round( num * 100 + Number.EPSILON ) / 100;

                } else {
                    return "";
                }
            },
            save: function() {
                this.model.set('delivery', this.delivery.attributes);
                this.model.save();
            },
            renderLogistics: function() {
                var t = this.logistics_template({
                    order: this.model,
                    site: this.site,
                    order_form: this.order_form_detail.get('order_sheet'),
                });
                this.$el.html(t);
                this.delivery_form = new Backform.Form({
                    model: this.delivery,
                    fields: [
                        {
                            name: 'delivery_date',
                            label: 'Delivery date (Mon-Fri only)',
                            control: "datepicker",
                            options: {format: "yyyy-mm-dd"},
                            required: true
                        },
                        {
                            name: "contact",
                            label: "Contact person (who will accept delivery)",
                            control: "input",
                        },
                        {
                            name: "contact_phone",
                            label: "Contact phone",
                            control: "input",
                        },
                        {
                            name: "notes",
                            label: "Instructions for delivery person",
                            control: "textarea"
                        },
                    ],
                });
                this.delivery_form.setElement(this.$el.find('#order-delivery-form'));
                this.delivery_form.render();
                return this;
            },
            render: function() {
                var self = this;
                if (!this.site.has('number')) {
                    return this;
                }
                if (this.order_form_detail) {
                    if (!this.order_form_detail.has('sorted_items')) {  // to indicate it comes from server.
                        return this;
                    }
                    var t = this.select_items_template({
                        order: this.model,
                        site: this.site,
                        order_form: this.order_form_detail.get('order_sheet'),
                        items: this.order_form_detail.get('sorted_items'),
                        order_items: this.order_items,
                        totalForItem: this.totalForItem,
                        quantityForItem: function(item, order_items) {
                            var oi = order_items.get(item.id);
                            if (oi) {
                                return oi.get('quantity');
                            } else {
                                return '';
                            }
                        },
                        subtotal: function() {
                            var num = _.reduce(
                                self.order_form_detail.get('sorted_items'),
                                function(memo, val) {
                                    var t = self.totalForItem(val, self.order_items);
                                    if (t) {
                                        return t + memo;
                                    } else {
                                        return memo;
                                    }
                                }, 0);
                            return Math.round( num * 100 + Number.EPSILON ) / 100;
                        }
                    });
                    this.$el.html(t);
                    return this;
                }
                if (!this.order_forms.models) {
                    return this;
                }
                if (this.app.models.order.has('order_sheet')) {
                    console.log('has order sheet ' + this.model.get('order_sheet'));
                } else {
                    console.log('need to choose order sheet');
                    var t = this.choose_form_template({s: this.model.attributes});
                    this.$el.html(t);
                    var buttons = this.$('#order-form-buttons');
                    var button_template = this.button_template;
                    _.each(this.order_forms.models,
                           function(f) {
                               var b = button_template(f.attributes);
                               buttons.append(b);                               
                           });
                    $("#order-form-buttons button").click(function() {
                        self.order_form_detail = new OrderFormDetail({id: parseInt(this.id)});
                        if (self.model.has('id')) {
                            self.order_items = new OrderItems({id: self.model.get('id')});
                        } else {
                            self.order_items = new OrderItems();
                        }
                        self.listenTo(self.order_items, 'change', self.render);
                        self.listenTo(self.order_items, 'add', self.render);
                        self.listenTo(self.order_form_detail, 'change', self.render);
                        self.order_form_detail.fetch();
                    });

                }
                return this;                    
            }
        });
        return OrderFlowView;
    }
)
