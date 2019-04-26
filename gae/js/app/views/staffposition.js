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
                name: 'saveExit',
                control: "button",
                extraClasses: ['btn-primary'],
                label: "Save changes"
            }
        ];
        var ViewFactory = function(app, loading) {

                return new StaffPositionFlow({
                        basicFields: fields,
                        staffposition: app.models.staffposition,
                        loading: loading,
                        template: template,
                });
        }
        return ViewFactory;
    }
)
