define(
    ['app/models/proto_model'],
    function(ProtoModel) {
        var Model = ProtoModel.extend({
            // matches first part of method name in @remote.method
            urlRoot: '/wsgi_service.ordersheet_',
            defaults: {
                visibility: 'Everyone',
                supports_extra_name_on_order: false,
                instructions: "",
                logistics_instructions: "",
                delivery_options: "No",
                pickup_options: "No",
                retrieval_options: "No"
            },
            get_error_str: function(attrs){
                arr = [];
                if (attrs.delivery_options == "Yes"){
                    arr.push("Delivery")
                }
                if (attrs.pickup_options == "Yes"){
                    arr.push("Pick-up")
                }
                if (attrs.retrieval_options == "Yes"){
                    arr.unshift("Retrieval")
                }
                if (arr.length == 2 ){
                    return "<span style='color: #f1625f;margin-right: 3px'> <em>"+arr.join(' & ')+"</em></span>" + " are not a valid options. ";
                }
                if (arr.length == 3 || arr.length == 0) {
                    return "<span style='color: #f1625f;margin-right: 3px'>This is not a valid selection.</span>" + "Please choose Delivery, Pick-up, <em>or</em> Retrieval.";
                }
            },
            validate: function(attrs){
                var option_count = 0
                var delivery = false, pickup = false, retrieval = false;

                if (attrs.delivery_options == "Yes"){
                    delivery = true
                    option_count+= 1
                }
                if (attrs.pickup_options== "Yes"){
                    pickup = true
                    option_count+= 1
                }
                if (attrs.retrieval_options == "Yes"){
                    retrieval = true
                    option_count+= 1
                }
                if(option_count == 1 || pickup && delivery && option_count == 2){
                    this.errorModel.set({
                        retrieval_options: "",
                        delivery_options: "",
                        pickup_options: ""
                    })
                }
                if(option_count == 0 || option_count == 3){
                    str = this.get_error_str(attrs);
                    this.errorModel.set({
                        delivery_options: str,
                        pickup_options: str,
                        retrieval_options: str
                    })
                }
                if(retrieval && option_count == 2){
                    str = this.get_error_str(attrs);
                    if(pickup){
                        this.errorModel.set({
                            retrieval_options: str,
                            pickup_options: str,
                            delivery_options: ""
                        })
                    }
                    if(delivery){
                        this.errorModel.set({
                            retrieval_options: str,
                            delivery_options: str,
                            pickup_options: ""
                        })
                    }
                }
                if (!_.isEmpty(_.compact(this.errorModel.toJSON()))) {
                    return "Validation errors. Please fix.";
                }
            }
        })
        return Model;
    }
)
