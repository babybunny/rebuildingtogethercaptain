define(
    [
        'backbone',
        'app/views/rate_after_date',
        'text!app/templates/staffposition_flow.html'
    ],
    function(Backbone,
             RateAfterDateView, template){
        var View = Backbone.View.extend({
            el: '#simple-form-view',
            initialize: function(app, id) {
                var self = this;

                this.app = app;
                this.id = parseInt(id);
                var name = 'staffposition_rates';
                this.staffposition = self.app.models[name];

                this.staffposition.fetch().then(function(mdl) {
                    self.rates_view = new RateAfterDateView({
                        staffposition: self.staffposition,
                    });
                    self.render();
                });

                this.t = _.template(template);
                this.render();
            },
            render: function() {
                this.$el.html(this.t);
                if (this.rates_view) {
                    this.rates_view.setElement(this.$('#staffposition-rates'));
                    this.rates_view.render();
                }
            }
        });
        return View;
    }
)

