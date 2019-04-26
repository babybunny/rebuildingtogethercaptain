define(
    [
        'text!app/templates/staffposition.html',
        'app/views/staffposition_flow',
    ],
    function(template, StaffPositionFlow) {
        var fields = [{
                name: "position_name",
                label: "Position name",
                control: "input",
                type: "text",
                required: true
            },{
                name: 'saveStaffPosition',
                control: "button",
                extraClasses: ['btn-success btn-block'],
                label: "Save All Changes",
                helpMessage: '<br/>Click above when you have finished editing for your hourly & mileage updates to persist to the server.'
            }
        ];
        var ViewFactory = function(app, loading) {

                return new StaffPositionFlow({
                        fields: fields,
                        staffposition: app.models.staffposition,
                        loading: loading,
                        template: template,
                });
        }
        return ViewFactory;
    }
)
