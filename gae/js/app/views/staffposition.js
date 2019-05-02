define(
    [
        'text!app/templates/staffposition.html',
        'app/views/staffposition_flow',
        'app/views/staffposition_rates'
    ],
    function(template, StaffPositionFlow, RatesView) {
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
