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
                label: "Position name",
                control: "input",
                type: "text",
                required: true
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
                name: 'staffposition',
                    template: template,
                    model: app.models.staffposition,
                    loading: loading,
                    fields: fields,
            });
        }
        return ViewFactory;
    }
)
