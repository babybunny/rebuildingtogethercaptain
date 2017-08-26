define(
    [
        'bootstrap-datepicker',
        'app/views/rooms_form',
	      'app/views/model_select_control',
        'app/models/order_form_overview',
        'text!app/templates/order_choose_form.html',
        'text!app/templates/order_form_button.html',
        'text!app/templates/order_form_preview.html',
    ],
    function(bsdp, RoomFormView, ModelSelectControl, OrderFormOverview,
             choose_form_template, button_template, preview_template) {
        var OrderFlowView = Backbone.View.extend({
            initialize: function(app, loading) {
                console.log('initializing order_flow');
                this.app = app;
                this.model = this.app.models.order;
                this.choose_form_template = _.template(choose_form_template);
                this.order_forms = new OrderFormOverview();
                this.listenTo(this.order_forms, 'add', this.render);
                this.listenTo(this.model, 'change', this.render);
                this.order_forms.fetch();
                this.button_template = _.template(button_template);
                this.preview_template = _.template(preview_template);
            },
            el: '#order-flow-view',
            render: function() {
                console.log('render '
                            + ' order_forms ' + this.order_forms
                            + ' model '+ this.model
                            + ' app ' + this.app.models.order);
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
                    var previews = this.$('#order-form-previews');
                    var preview_template = this.preview_template;
                    var buttons = this.$('#order-form-buttons');
                    var button_template = this.button_template;
                    _.each(this.order_forms.models,
                           function(f) {
                               previews.append(preview_template({sheet: f}));
                               buttons.append(button_template(f.attributes));
                           });
                    $("div.order_sheet a").hover(function() {
                        console.log('hover: ' + this.id);
                        $("div.description").hide();
                        $("div#preview-" + this.id).show();
                        $("div#preview-" + this.id).position({
                            my: "left top",
                            at: "right top",
                            of: $(this),
                            collision: "none",
                            offset: "30 0",
                        });
                    });

                }
                return this;                    
            }
        });
        return OrderFlowView;
    }
)
