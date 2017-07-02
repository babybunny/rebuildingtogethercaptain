define(
    [
        'bootstrap-datepicker',
        'app/views/rooms_form',
	      'app/views/model_select_control',
        'app/models/supplier_choices',
        'text!app/templates/order_choose_form.html'
    ],
    function(bsdp, RoomFormView, ModelSelectControl, SupplierChoices,
             choose_form_template) {
        var OrderFlowView = Backbone.View.extend({
            initialize: function(app, loading) {
                this.app = app;
                this.model = this.app.models.order;
                this.choose_form_template = _.template(choose_form_template);
            },
            el: '#order-flow-view',
            render: function() {
                if (this.model.has('order_sheet')) {
                    console.log('has order sheet ' + this.model.get('order_sheet'));
                } else {
                    var t = this.choose_form_template({s: this.model.attributes});
                    this.$el.html(t);                   
                }
                return this;                    
            }
        });
        return OrderFlowView;
    }
)
