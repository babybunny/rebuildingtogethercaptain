define(
    [
        'bootstrap-datepicker',
        'app/views/rooms_form',
	      'app/views/model_select_control',
        'app/models/staffposition_choice',
        'text!app/templates/simple_form.html'
    ],
    function(bsdp, RoomFormView, ModelSelectControl, StaffPositionChoice, template) {
        var fields = [
            {
                name: "id",
                label: "ID",
                control: "input",
                disabled: true
            },
            // boilerplate
            {
                name: "site",
                label: "Site",
                control: "input",
                disabled: true
            },
            {
                name: "state",
                label: "State",
                control: "select",
                value: "new",
                options: [
                    {label: "new", value: "new"},
                    {label: "submitted", value: "submitted"},
                    {label: "fulfilled", value: "fulfilled"},
                    {label: "deleted", value: "deleted"},
                ]
            },
            {
                name: "position",
                label: "Staff Position",
		            control: ModelSelectControl,
		            room_model_module: StaffPositionChoice,
            },
            {
                name: "activity_date",
                label: "Activity date",
                required: true,
                control: "datepicker",
                options: {format: "yyyy-mm-dd"},
            },
            {
                name: "hours",
                label: "Hours",
                control: "input",
                value: "0",
            },
            {
                name: "miles",
                label: "Miles",
                control: "input",
                value: "0",
            },
            {
                name: "description",
                label: "Description",
                control: "textarea",
            },
            {
                control: "button",
                label: "Save changes"
            }
        ];
        
        var ViewFactory = function(app, loading) {
            return new RoomFormView({
		            name: 'stafftime',
		            template: template,
		            model: app.models.stafftime,
		            loading: loading,
		            fields: fields,
	          });
        }
        return ViewFactory;
    }
)
