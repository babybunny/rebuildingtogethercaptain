define(
    [
        'bootstrap-datepicker',
        'app/views/rooms_form',
	      'app/views/model_select_control',
        'app/models/order_form_overview',
        'app/models/site',
        'app/models/ordersheet',
        'text!app/templates/order_choose_form.html',
        'text!app/templates/order_form_button.html',
        'text!app/templates/order_select_items.html',
    ],
    function(bsdp, RoomFormView, ModelSelectControl, OrderFormOverview, Site, OrderForm,
             choose_form_template, button_template, select_items_template) {
        var OrderFlowView = Backbone.View.extend({
            initialize: function(app, loading) {
                console.log('initializing order_flow');
                this.app = app;
                this.model = this.app.models.order;
                this.choose_form_template = _.template(choose_form_template);
                this.order_forms = new OrderFormOverview();
                this.site = new Site({id: this.model.get('site')});
                this.listenTo(this.order_forms, 'add', this.render);
                this.listenTo(this.model, 'change', this.render);
                this.listenTo(this.site, 'change', this.render);
                this.site.fetch();
                this.order_forms.fetch();
                this.button_template = _.template(button_template);
                this.select_items_template = _.template(select_items_template);
            },
            el: '#order-flow-view',
            render: function() {
                console.log('render '
                            + ' order_forms ' + this.order_forms
                            + ' model '+ this.model
                            + ' app ' + this.app.models.order);
                if (!this.site.has('number')) {
                    console.log('order_flow.render waiting on site');
                    return this;
                }
                if (this.order_form) {
                    if (!this.order_form.has('code')) {
                        return this;
                    }
                    console.log('has order form: ' + this.order_form.get('code'));
                    var t = this.select_items_template({order: this.model, site: this.site, order_form: this.order_form});
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
                               var b = button_template(f.attributes);
                               buttons.append(b);                               
                           });
                    var self = this;
                    $("#order-form-buttons button").click(function() {
                        console.log('click: ' + this.id);
                        self.order_form = new OrderForm({id: parseInt(this.id)});
                        self.listenTo(self.order_form, 'change', self.render);
                        self.order_form.fetch();
                    });

                }
                return this;                    
            }
        });
        return OrderFlowView;
    }
)
