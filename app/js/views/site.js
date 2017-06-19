define(
    [
        'app/views/simple_form',
        'text!app/templates/simple_form.html'
    ],
    function(SimpleFormView, template) {
        var fields = [{
            name: "id", // The key of the model attribute
            label: "ID", // The label to display next to the control
            control: "input", // This will be converted to InputControl and instantiated from the proper class under the Backform namespace
            disabled: true // By default controls are editable. Here we disabled it.
        }, {
            name: "number",
            label: "Site Number",
            control: "input"
        }, {
            control: "button",
            label: "Save changes"
        }];
        
        var ViewFactory = function(app, loading) {
            return new SimpleFormView('site', template, app.models.site, loading, fields)
        }
        return ViewFactory;
    }
)
