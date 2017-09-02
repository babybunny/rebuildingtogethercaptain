define(
    [
        'bootstrap-datepicker',
        'app/views/rooms_form',
	      'app/views/model_select_control',
          'app/models/captain_choices',
        'app/models/staffposition_choice',
        'text!app/templates/simple_form.html'
    ],
    function(bsdp, RoomFormView, ModelSelectControl, CaptainChoice, StaffPositionChoice, template) {
        var fields = [
            {
                name: "id",
                label: "ID",
                control: "input",
                    disabled: true
            },
            {
                name: "site",
                label: "Site",
                control: "input",
                    disabled: true,
                    required: true
            },
            {
                name: "program",
                label: "Program",
                control: "input"
            },
            {
                name: "captain",
                label: "Captain",
                    control: ModelSelectControl,
                    room_model_module: CaptainChoice
            },
            {
                name: "position",
                label: "Staff Position",
		            control: ModelSelectControl,
		            room_model_module: StaffPositionChoice,
            },
            {
                name: "state",
                label: "State",
                control: "select",
                options: [
                    {label: "new", value: "new"},
                    {label: "submitted", value: "submitted"},
                    {label: "fulfilled", value: "fulfilled"},
                    {label: "deleted", value: "deleted"}
                ]
            },
            {
                name: "hours",
                label: "Hours",
                control: "input"
            },
            {
                name: "miles",
                label: "Miles",
                control: "input"
            },
            {
                name: "activity_date",
                label: "Activity date",
                control: "datepicker",
                    options: {format: "yyyy-mm-dd"},
                    required: true
            },
            {
                name: "description",
                label: "Description",
                control: "textarea"
            },
            {
                id: "submit",
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
