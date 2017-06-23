define(
    [
        'app/views/simple_form',
        'text!app/templates/simple_form.html'
    ],
    function(SimpleFormView, template) {
        var fields = [
            {
                name: "id", // The key of the model attribute
                label: "ID", // The label to display next to the control
                control: "input", // This will be converted to InputControl and instantiated from the proper class under the Backform namespace
                disabled: true // By default controls are editable. Here we disabled it.
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
                control: "button",
                label: "Save changes"
            }
        ];

        var ViewFactory = function(app, loading) {
            return new SimpleFormView('supplier', template, app.models.supplier, loading, fields)
        }
        return ViewFactory;
    }
)
