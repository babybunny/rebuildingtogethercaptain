define(
    [
        'backbone', 'backform',
        'app/views/staffposition_rates',
        'text!app/templates/staffposition.html',
    ],
    function(Backbone, Backform, RatesView, template) {
        var fields = [{
                    name: "position_name",
                    label: "Position name",
                    control: "input",
                    type: "text",
                    required: true
                },{
                    name: 'saveStaffPosition',
                    control: "button",
                    extraClasses: ['btn-primary'],
                    label: "Save Staff Position",
                }];

        var StaffPositionFlow = Backbone.View.extend({
            el: '#simple-form-view',
            events: {
                'click button[name=saveStaffPosition]': 'saveStaffPosition',
            },
            initialize: function(options) {
                var self = this;
                this.options = options;
                self.staffposition = options.staffposition;
                self.template = _.template(template);
                self.loading = options.loading;
                self.hourlyView = new RatesView({
                                        name: 'hourly_rates',
                                        templateName: 'Hourly',
                                        loading: options.loading,
                                        rates: options.staffposition.get('hourly_rates'),
                                        changeTrigger: this.trigger.bind(this, 'change-rates')});
                self.mileageView = new RatesView({
                                        name: 'mileage_rates',
                                        templateName: 'Mileage',
                                        loading: options.loading,
                                        rates: options.staffposition.get('mileage_rates'),
                                        changeTrigger: this.trigger.bind(this, 'change-rates')});
                this.listenTo(this.staffposition, 'change',
                    function(staffposition){
                        if (self.loading){
                            self.loading = false;
                            self.hourlyView.trigger('finished-loading', staffposition.get('hourly_rates'),
                                                                        staffposition.get('position_name'));
                            self.mileageView.trigger('finished-loading', staffposition.get('mileage_rates'),
                                                                         staffposition.get('position_name'));
                            self.makeForm(self.staffposition, fields).render();
                        }
                    });
                this.makeForm(this.staffposition, fields).render();
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

        var ViewFactory = function(app, loading) {

                return new StaffPositionFlow({
                        staffposition: app.models.staffposition,
                        loading: loading,
                });
        }

        return ViewFactory;
    }
)
