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
                name: "id", // The key of the model attribute
                label: "ID", // The label to display next to the control
                control: "input", // This will be converted to InputControl and instantiated from the proper class under the Backform namespace
                disabled: true // By default controls are editable. Here we disabled it.
            },
            // boilerplate
            {
                name: "site",
                label: "Site",
                control: "input", // This will be converted to InputControl and instantiated from the proper class under the Backform namespace
                disabled: true // By default controls are editable. Here we disabled it.
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
                control: "select",
                // "position is a Key.  Will load dynamically",
            },
            {
                name: "activity_date",
                label: "Activity date",
                control: "input",
                required: true,
                value: "",
                helpMessage: "yyyy-mm-dd format",
                /* too flakey. 
                control: "datepicker",
                options: {format: "yyyy-mm-dd"},
                */
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
