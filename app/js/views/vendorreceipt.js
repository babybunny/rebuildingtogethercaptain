define(
    [
	    'bootstrap-datepicker',
        'app/views/rooms_form',
	    'app/views/model_select_control',
        'app/models/captain_choices',
        'app/models/supplier_choices',
        'text!app/templates/simple_form.html'
    ],
    function(bsdp, RoomFormView, ModelSelectControl,
             CaptainChoice, SupplierChoice, template) {
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
                    disabled: true
            },
            {
                name: "state",
                label: "State",
                control: "select",
                options: [
                    {label: "new", value: "new"},
                    {label: "submitted", value: "submitted"},
                    {label: "payable", value: "payable"},
                    {label: "fulfilled", value: "fulfilled"},
                    {label: "deleted", value: "deleted"}
                ]
            },
            {
                name: "amount",
                label: "Amount",
                control: "input",
                    helpMessage: "Purchase Amount ($)."
            },
            // {   Do we need program property on form?
            //     Currently defaulting to selected program.
            //     name: "program",
            //     label: "Program",
            //     control: "input",
            //         type: "text"
            // },
            {
                name: "purchase_date",
                label: "Purchase Date",
                control: "datepicker",
                    options: {format: "yyyy-mm-dd"},
                    required: true
            },
            {
                name: "captain",
                label: "Captain",
                    control: ModelSelectControl,
                    room_model_module: CaptainChoice
            },
            // {   Do we need vendor property on form?
            //     Currently, if SupplierChoice is seleced,
            //         vender = supplier
            //     name: "vendor",
            //     label: "Vendor",
            //     control: "input",
            //         type: "text"
            // },
            {
                name: "supplier",
                label: "Supplier",
                    control: ModelSelectControl,
                    room_model_module: SupplierChoice
            },
            {
                name: "description",
                label: "Description",
                control: "textarea"
            },
            // {
            //     name: "last_editor",
            //     label: "Last Editor",
            //     control: "input",
            //         disabled: true
            // },
            {
                id: "submit",
                label: "Save changes",
                control: "button"
            }
        ];

        var ViewFactory = function(app, loading) {
            return new RoomFormView({
		            name: 'vendorreceipt',
		            template: template,
		            model: app.models.vendorreceipt,
		            loading: loading,
		            fields: fields,
	          });
        }
        return ViewFactory;
    }
)
