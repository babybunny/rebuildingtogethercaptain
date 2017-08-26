define(
    [
        'bootstrap-datepicker',
        'app/views/rooms_form',
	      'app/views/model_select_control',
        'app/models/order_form_overview',
        'app/models/order',
        'text!app/templates/order_choose_form.html',
        'text!app/templates/order_form_button.html',
        'text!app/templates/order_select_items.html',
    ],
    function(bsdp, RoomFormView, ModelSelectControl, OrderFormOverview, Order,
             choose_form_template, button_template, select_items_template) {
        var OrderFlowView = Backbone.View.extend({
            initialize: function(app, loading) {
                console.log('initializing order_flow');
                this.app = app;
                this.model = this.app.models.order;
                this.choose_form_template = _.template(choose_form_template);
                this.order_forms = new OrderFormOverview();
                this.order = new Order();
                this.listenTo(this.order_forms, 'add', this.render);
                this.listenTo(this.model, 'change', this.render);
                this.order_forms.fetch();
                this.button_template = _.template(button_template);
                this.select_items_template = _.template(select_items_template);
            },
            el: '#order-flow-view',
            render: function() {
                console.log('render '
                            + ' order_forms ' + this.order_forms
                            + ' model '+ this.model
                            + ' order '+ this.order
                            + ' app ' + this.app.models.order);
                if (this.order.has('order_form')) {
                    console.log('has order form: ' + this.order.get('order_form').get('code'));
                    var t = this.select_items_template({s: this.model.attributes});
                    this.$el.html(t);
                    return this;
                }

                if (!this.order_forms.models) {
                    console.log('order_flow.render waiting on order_forms');
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
                               buttons.append(button_template(f.attributes));
                           });
                    var self = this;
                    $("#order-form-buttons button").click(function() {
                        console.log('click: ' + this.id);
                        self.order.set('order_form', self.order_forms.findWhere({code: this.id}));
                        self.render();
                    });

                }
                return this;                    
            }
        });
        return OrderFlowView;
    }
)
