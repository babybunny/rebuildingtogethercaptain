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
                name: "active",
                label: "Active",
                control: "select",
                options: [
                    {label: "Active", value: "Active"},
                    {label: "Inactive", value: "Inactive"},
                ]
            },
            {
                name: "visibility",
                label: "Visibility",
                control: "select",
                options: [
                    {label: "Everyone", value: "Everyone"},
                    {label: "Staff Only", value: "Staff Only"},
                ]
            },
            {
                name: "name",
                label: "Name",
                control: "input",
                required: true
            },
            {
                name: "email",
                label: "Email",
                control: "input",
            },
            {
                name: "address",
                label: "Address",
                control: "input",
            },
            {
                name: "phone1",
                label: "Phone1",
                control: "input",
            },
            {
                name: "phone2",
                label: "Phone2",
                control: "input",
            },
            {
                name: "notes",
                label: "Notes",
                control: "textarea",
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
                name: 'supplier',
		            template: template,
		            model: app.models.supplier,
		            loading: loading,
		            fields: fields,
            });
        }
        return ViewFactory;
    }
)
