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
                control: "button",
                label: "Save changes"
            }
        ];
        
        var ViewFactory = function(app, loading) {
            return new SimpleFormView('staff', template, app.models.staff, loading, fields)
        }
        return ViewFactory;
    }
)
