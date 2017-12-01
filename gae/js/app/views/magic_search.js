define(
    [
        'app/views/rooms_form',
        'text!app/templates/simple_form.html'
    ],
    function(RoomFormView, template) {
        var fields = [
            {
                name: "search",
                label: "",
                control: "input",
                disabled: false
            },
            // boilerplate
            {
                id: "submit",
                control: "button",
                label: "Search"
            }
        ];
        
        var ViewFactory = function(app, loading) {
            return new RoomFormView({
		            name: 'example',
		            template: template,
		            model: app.models.example,
		            loading: loading,
		            fields: fields,
	          });
        }
        return ViewFactory;
    }
)
