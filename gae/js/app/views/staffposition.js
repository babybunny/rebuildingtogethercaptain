define(
    [
        'bootstrap-datepicker',
        'app/views/rooms_form',
        'text!app/templates/simple_form.html',
        'text!app/templates/staffposition.html',
        'app/views/staffposition_existing',
    ],
    function(bsdp, RoomFormView, template, existing_template, StaffPositionExistingView) {
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
                if (app.models.staffposition.isNew()) {
                   return  new RoomFormView({
                        name: 'staffposition',
                            template: template,
                            model: app.models.staffposition,
                            loading: loading,
                            fields: fields
                    });
                }
                return new StaffPositionExistingView({
                        basicFields: fields,
                        staffposition: app.models.staffposition,
                        loading: loading,
                        template: existing_template,
                });
        }
        return ViewFactory;
    }
)
