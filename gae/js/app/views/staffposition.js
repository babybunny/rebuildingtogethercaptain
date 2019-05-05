define(
    [
        'backbone', 'backform',
        'app/views/staffposition_rates',
        'text!app/templates/staffposition.html',
    ],
    function(Backbone, Backform, RatesView, template) {

        var StaffPositionFlow = Backbone.View.extend({
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
                self.hourlyView = options.hourlyView;
                self.mileageView = options.mileageView;

                 this.listenTo(this.staffposition, 'change',
                    function(staffposition){
                        if (self.loading){
                            self.loading = false;
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
            }
        ];
        var ViewFactory = function(app, loading) {

            var hourlyView =  new RatesView({
                    name: 'hourly_rates',
                    templateName: 'Hourly',
                    staffposition: app.models.staffposition,
                    loading: loading,
                    views: app.views
                });
            var mileageView = new RatesView({
                    name: 'mileage_rates',
                    templateName: 'Mileage',
                    staffposition: app.models.staffposition,
                    loading: loading,
                    views: app.views
                });

                return new StaffPositionFlow({
                        fields: fields,
                        staffposition: app.models.staffposition,
                        loading: loading,
                        template: template,
                        hourlyView: hourlyView,
                        mileageView: mileageView
                });
        }
        return ViewFactory;
    }
)
