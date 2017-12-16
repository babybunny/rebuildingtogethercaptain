define(
    [
        'app/views/rooms_form',
        'text!app/templates/simple_form.html'
    ],
    function(RoomFormView, template) {
        var fields = [
            {
                name: "id",
                label: "ID",
                control: "input",
                disabled: true
            },
            {
                name: "name",
                label: "Name",
                control: "input",
                type: "text"
            },
            {
                name: "email",
                label: "Email",
                control: "input",
                type: "email",
                required: true
            },
            {
                name: "notes",
                label: "Notes",
                control: "textarea"
            },
            {
                name: "program_selected",
                label: "Program selected",
                control: "input",
                disabled: true
            },
            {
                name: "last_welcome",
                label: "Last welcome",
                control: "input",
                type: "date",
                disabled: true,
                format: "yyyy-mm-dd"
            },
            {
                name: "since",
                label: "Since",
                control: "input",
                type: "date",
                disabled: true,
                format: "yyyy-mm-dd"
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
		            name: 'staff',
		            template: template,
		            model: app.models.staff,
		            loading: loading,
		            fields: fields,
	          });
        }
        return ViewFactory;
    }
)
