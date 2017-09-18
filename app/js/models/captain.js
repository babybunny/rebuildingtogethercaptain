define(
    ['app/models/proto_model'],
    function(ProtoModel) {
        var Model = ProtoModel.extend({
            // matches first part of method name in @remote.method
            urlRoot: '/wsgi_service.captain_',

            validate: function(attrs){

                if(!attrs.name){
                    this.errorModel.set({name: "Please enter captain name."})
                }
                if(attrs.email && attrs.email.indexOf('@') < 0){
                    e2 = attrs.email;
                    e1 = "Please include an '@' in the Email address.  "
                    quote = "'"
                    this.errorModel.set({email: e1+ quote + e2 + quote + " is missing an'@'."})
                }

                if (!_.isEmpty(_.compact(this.errorModel.toJSON()))) {
                        return "Validation errors. Please fix.";
                }
            }
        });

        return Model;
    }
);
