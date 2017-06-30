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
            // boilerplate
            {
                name: "name",
                label: "Name",
                control: "input",
            },
            {
                name: "email",
                label: "Email",
                control: "input",
            },
            {
                name: "notes",
                label: "Notes",
                control: "textarea",
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
                disabled: true
            },
            {
                name: "since",
                label: "Since",
                control: "input",
                disabled: true
                // "since is a DateProperty('since', auto_now_add=True).  TODO",
            },
            {
                id: "submit",
                control: "button",
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
