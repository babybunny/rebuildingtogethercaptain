define(
    [
        'backbone', 'backform', 'text!app/templates/staffposition.html'
    ],
    function(Backbone, Backform, template) {
        var View = Backbone.View.extend({
            el: '#simple-form-view',
            events: {
                'click button[name=saveStaffPosition]': 'saveStaffPosition',
            },
            initialize: function(options) {
                var self = this;
                this.options = options;
                self.staffposition = options.staffposition;
                self.template = _.template(options.template);
                self.loading = options.loading;
                self.hourly_rates = self.staffposition.get('hourly_rates');
                self.mileage_rates = self.staffposition.get('mileage_rates');
                self.hourlyView = options.hourlyView;
                self.mileageView = options.mileageView;

                 this.listenTo(this.staffposition, 'change',
                    function(staffposition){
                        if (self.loading){
                            self.loading = false;
                            self.hourly_rates = self.staffposition.get('hourly_rates');
                            self.mileage_rates = self.staffposition.get('mileage_rates');
                            self.makeForm(self.staffposition, self.options.fields).render();
                        }
                    });
                 this.makeForm(this.staffposition, this.options.fields).render();
                 this.on('change-rates', function(){this.render(true);});
            },
            makeForm: function(mdl, fields){
                this.form =  new Backform.Form({
                    model: mdl,
                    fields: fields,
                    showRequiredAsAsterisk: true,
                });
                return this;
            },
            render: function(display_alert) {
                if (!this.loading){
                    this.$el.html(this.template({display_alert: display_alert}));
                    this.hourlyView.setElement('#hourly-rates').render();
                    this.mileageView.setElement('#mileage-rates').render();
                    this.form.setElement('#staffposition-form').render();
                    this.form.$el.find('label.control-label:contains("*")').addClass('required');
                    this.form.$el.find('input').first().focus();

                    if(display_alert){
                        $('#staffposition-form > div.form-group > div > button')
                            .html('Save all changes including unsaved rate changes');
                    }
                }
            },
            saveStaffPosition: function(e){
                var self = this;
                $(e.target).prop('disabled', true);
                this.staffposition.set({
                    'position_name': this.form.model.get('position_name'),
                    'hourly_rates': this.hourly_rates,
                    'mileage_rates': this.mileage_rates
                });
                this.staffposition.save(null,
                    {'success': function(model, attrs, response) {
                        $('span.status').css('color', '#409b27').html('Saved!').show()
                            .fadeOut({ duration: 1000,
                                complete: function() {
                                    window.location = $('#rooms-form-after-save').attr('href');
                            }
                        });
                    },
                    'error': function(model, response, error) {
                        $('span.status').first().css('color', 'red').html(response.responseText).show();
                        $(e.target).removeAttr('disabled');
                        self.form.$el.find('input').first().focus();
                    },
                });
            },
        });
        return View;
    }
);
