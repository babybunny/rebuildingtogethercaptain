define(
    ['app/models/proto_model'],
    function(ProtoModel) {
        var Model = ProtoModel.extend({
            // matches first part of method name in @remote.method
            urlRoot: '/wsgi_service.newsite_',
            must_be_floats: ['latest_computed_expenses'],
            defaults: {
                budget: 0,
                announcement_subject: "Nothing Needs Attention",
                announcement_body: "Pat yourself on the back - no items need attention.\n"+
                                            "You have a clean bill of health."
            },
            check_url: function(url){
                var patt = new RegExp("(http://[^ ]|https://[^ ])");
                var res = patt.test(url);
                return res
            },
            validate: function(attrs){
                if (!attrs.number) {
                    this.errorModel.set({
                        number: "Please enter a unique number for this site."
                    })
                }
                if(attrs.applicant_email && attrs.applicant_email.indexOf('@') < 0){
                    e = attrs.applicant_email;
                    quote= "'";
                    this.errorModel.set({
                        applicant_email: quote + e + quote+ " is missing an'@'."
                    })
                }
                if(attrs.volunteer_signup_link && !this.check_url(attrs.volunteer_signup_link)){
                    this.errorModel.set({
                        volunteer_signup_link: "Please enter a valid url."
                    })
                }
                if(attrs.photo_link && !this.check_url(attrs.photo_link)){
                    this.errorModel.set({
                        photo_link: "Please enter a valid url."
                    })
                }
                if (!_.isEmpty(_.compact(this.errorModel.toJSON()))) {
                    return "Validation errors. Please fix.";
                }
            }
        });
        return Model;
    }
);
