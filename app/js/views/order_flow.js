define(
    [
        'backbone', 'backform', 'bootstrap',
        'bootstrap-datepicker',
        'app/views/rooms_form',
	      'app/views/model_select_control',
        'app/models/order_form_overview',
        'app/models/order_items',
        'app/models/order',  // TODO: remove?
        'app/models/site',
        'app/models/order_form_detail',
        'app/models/order_full',
        'text!app/templates/order_choose_form.html',
        'text!app/templates/order_form_button.html',
        'text!app/templates/order_select_items.html',
        'text!app/templates/order_logistics.html',
    ],
    function(Backbone, Backform, bootstrap,
             bsdp, RoomFormView, ModelSelectControl,
             OrderFormOverview, OrderItems, Order, Site, OrderFormDetail, OrderFull,
             choose_form_template, button_template, select_items_template,
             logistics_template) {
        var basic_logistics_fields = [
            {
                name: "contact",
                label: "Contact person (who will be present)",
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
            {
                name: "submit",
                control: "button",
                label: "Choose these options and complete order"
            },
        ];

        var delivery_fields = [
            {
                name: 'delivery_date',
                label: 'Delivery date (Mon-Fri only)',
                control: "datepicker",
                options: {format: "yyyy-mm-dd"},
                required: true
            },
        ].concat(basic_logistics_fields);

        var pickup_fields = [
            {
                name: 'pickup_date',
                label: 'Pickup date (Mon-Fri only)',
                control: "datepicker",
                options: {format: "yyyy-mm-dd"},
                required: true
            },
            {
                name: 'return_date',
                label: '(Optional) Return date for durable equipment',
                control: "datepicker",
                options: {format: "yyyy-mm-dd"},
            },
        ].concat(basic_logistics_fields);

        var retrieval_fields = [
            {
                name: 'dropoff_date',
                label: 'Delivery date (Mon-Fri only)',
                control: "datepicker",
                options: {format: "yyyy-mm-dd"},
            },
            {
                name: 'retrieval_date',
                label: 'Retrieval Date (Mon-Fri only)',
                control: "datepicker",
                options: {format: "yyyy-mm-dd"},
            },
        ].concat(basic_logistics_fields);

        var OrderFlowView = Backbone.View.extend({
            initialize: function(site_id, order_id) {
                var self = this;
                this.order_id = order_id;
                
                var site = new Site({id: site_id});
                site.fetch().then(function() {self.site = site; self.render()});

                if (order_id) {  // edit mode
                    var order_full = new OrderFull({id: order_id});
                    order_full.fetch().then(function() {
                        self.order_full = order_full;
                        self.order = new Order(order_full.get('order'));
                        self.order_items = new OrderItems(order_full.get('order_items'));
                        self.listenTo(self.order_items, 'change add', self.renderStep2);
                        self.listenTo(self.order, 'change', self.renderStep2);
                        
                        if (order_full.has('delivery')) {
                            self.logistics = new Backbone.Model(order_full.get('delivery'));
                        }
                        if (order_full.has('pickup')) {
                            self.logistics = new Backbone.Model(order_full.get('pickup'));
                        }
                        if (order_full.has('retrieval')) {
                            self.logistics = new Backbone.Model(order_full.get('retrieval'));
                        }

                        var ofd = new OrderFormDetail({id: self.order.get('order_sheet')});
                        ofd.fetch().then(function() {
                            self.order_form_detail = ofd;
                            self.renderStep2();
                        });                    
                    });
                } else {
                    this.order_full = new OrderFull();
                    this.order = new Order({site: site_id});
                    var order_forms = new OrderFormOverview();
                    order_forms.fetch().then(function() {self.order_forms = order_forms; self.render()});
                    this.order_items = new OrderItems();
                    this.logistics = new Backbone.Model();
                    this.listenTo(this.order_items, 'change add', this.renderStep2);
                    this.listenTo(this.order, 'change', this.renderStep2);
                }

                this.choose_form_template = _.template(choose_form_template);
                this.button_template = _.template(button_template);
                this.select_items_template = _.template(select_items_template);
                this.logistics_template = _.template(logistics_template);
            },
            events: {
                'change #id_notes': 'savenotes',
                'change .item-quantity': 'changeQuantity',
                'click #order-proceed-delivery': 'renderDelivery',
                'click #order-proceed-pickup': 'renderPickup',
                'click #order-proceed-retrieval': 'renderRetrieval',
                'click #order-submit': 'save',
            },
            savenotes: function(e) {
                this.order.set('notes', e.target.value);                
            },
            changeQuantity: function(e) {
                var oi = this.order_items.get(parseInt(e.target.name));
                if (!oi) {
                    this.order_items.add({
                        item: parseInt(e.target.name),
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
                $('span.status')
                    .css('color', '#909b27')
                    .text('Saving...')
                    .show();
                this.order_full.set({
                    order: this.order.attributes,
                    order_items: this.order_items.map(function(modl) {
                        return modl.attributes;
                    })
                });
                this.order_full.save(
                    null, {
                        'success': function(model, attrs, response) {
                            response.xhr.statusText = 'SAVED';
                            $('span.status')
                                .css('color', '#409b27')
                                .text('Saved')
                                .show()
                                .fadeOut({
                                    duration: 1000,
                                    complete: function() {
                                        // redirect to the "back to site" URL
                                        window.location = $('#rooms-form-after-save').attr('href');
                                    }
                                });
                        },
                        'error': function(model, response, error) {
                            $('span.status')
                                .css('color', 'red')
                                .text('Error: ' + response.responseText)
                                .show();
                        },
                    });
            },
            renderDelivery: function() {
                this.order_full.set('delivery', this.logistics.attributes);
                this.renderLogistics(delivery_fields, "Delivery");
            },
            renderPickup: function() {
                this.order_full.set('pickup', this.logistics.attributes);
                this.renderLogistics(pickup_fields, "Pickup and Return");
            },
            renderRetrieval: function() {
                this.order_full.set('retrieval', this.logistics.attributes);
                this.renderLogistics(retrieval_fields, "Drop-off and Retrieval");
            },
            renderLogistics: function(fields, logistics_words) {
                console.log('step 3');
                var t = this.logistics_template({
                    order: this.order,
                    site: this.site,
                    logistics_words: logistics_words,
                    order_form: this.order_form_detail.get('order_sheet'),
                });
                this.$el.html(t);
                this.logistics_form = new Backform.Form({
                    model: this.logistics,
                    fields: fields,
                    events: {
                        'submit': function(e) {
                            e.preventDefault();
                            this.trigger('submit');
                        },
                    }
                });
                this.listenTo(this.logistics_form, 'submit', this.save);
                this.logistics_form.setElement(this.$el.find('#order-logistics-form'));
                this.logistics_form.render();
                return this;
            },
            render: function() {
                this.renderStep1();
                return this
            },
            renderStep2: function() {
                console.log('step 2');
                var self = this;                
                if (!this.order_form_detail) {
                    return this;  // loading
                }
                var t = this.select_items_template({
                    order: this.order,
                    site: this.site,
                    order_form: this.order_form_detail.get('order_sheet'),
                    items: this.order_form_detail.get('sorted_items'),  // TODO
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
            },           
            renderStep1: function() {  // step 1, render the choose order form screen.
                var self = this;
                if (!this.site) {  
                    console.log('waiting for site');
                    return this;  // loading 
                }
                if (!this.order_full) {
                    console.log('waiting for order_full');
                    return this;  // loading
                }
                if (!this.order_forms) {
                    console.log('waiting for order_forms');
                    return this;  // loading
                }
                
                var t = this.choose_form_template({
                    s: this.order.attributes,
                    site: this.site,
                });
                this.$el.html(t);
                var order_forms = this.order_forms.groupBy('visibility');
                var button_template = this.button_template;

                // buttons for forms that everyone can see
                var buttons = this.$('#order-form-buttons-everyone');
                var addButtons = function(visibility) {
                    _.chain(order_forms[visibility])
                        .sortBy(function(f) {return f.get('code')})
                        .each(function(f) {
                            buttons.append(button_template(f.attributes));
                        });
                }
                addButtons('Everyone')

                // staff-only buttons
                buttons = this.$('#order-form-buttons-staff');
                buttons.hide();
                if (order_forms['Staff Only']) {
                    addButtons('Staff Only')
                    buttons.show();
                }

                // when button is clicked, move to step 2
                $(".order-form-buttons button").click(function() {
                    var id = parseInt(this.id);  // ordersheet ID
                    self.order.set('order_sheet', id);
                    var ofd = new OrderFormDetail({id: id});
                    ofd.fetch().then(function() {
                        self.order_form_detail = ofd;
                        self.renderStep2()});
                });
                return this;
            }
        });
        return OrderFlowView;
    }
)
