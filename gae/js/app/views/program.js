define(
    [
        'app/views/rooms_form',
	      'app/views/model_select_control',
        'app/models/program_type_choices',
        'text!app/templates/simple_form.html'
    ],
    function(RoomFormView, ModelSelectControl,
             ProgramTypeChoices, template) {
        var fields = [
            {
                name: "id",
                label: "ID",
                control: "input",
                disabled: true
            },
            {
                name: "year",
                label: "Year",
                control: "input",
                type: "number"
            },
            {
                name: "status",
                label: "Status",
                control: "select",
                options: [
                    // matches Program.ACTIVE_STATUS in ndb_models.py
                    {label: "Active", value: "Active"},
                    {label: "Inactive", value: "Inactive"},
                ],
                default: "Active"
            },
            {
                name: "program_type",
                label: "Program Type",
                control: ModelSelectControl,
                room_model_module: ProgramTypeChoices,
            },
            {
                id: "submit",
                control: "button",
                extraClasses: ['btn-primary'],
                label: "Save changes"
            }
        ];
        var ViewFactory = function(app, loading) {
            return new RoomFormView({
		            name: 'program',
		            template: template,
		            model: app.models.program,
		            loading: loading,
		            fields: fields,
	          });
        }
        return ViewFactory;
    }
)
