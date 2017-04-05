define(['text!app/templates/auth.html'], function(template) {
        var AuthView = Backbone.View.extend({
                el: '#signed-in-container',
                template: _.template(template),

                events: {
                    'click #signin-button': 'signin',
                    'click #signout-button': 'signout'
                },

                initialize: function(app) {
                    this.app = app;
                    this.listenTo(this.app.apiManager.loginState, 'change:state change:email', this.render);
                },

                render: function() {
                    var state = this.app.apiManager.loginState.get('state');
                    console.log('rendering auth with state: ' + state);
                    this.$el.html(this.template(
                        {email: this.app.apiManager.loginState.get('email')}));
                    if (state) {
                        this.$('#signin-button').hide();
                        this.$('#signout-button').show();
                    } else {
                        this.$('#signin-button').show();
                        this.$('#signout-button').hide();
                    }
                    return this;
                },

                signin: function() {
                    this.app.apiManager.handleSignin();
                    return false;
                },
                signout: function() {
                    this.app.apiManager.handleSignout();
                    return false;
                }
            });

        return AuthView;
    });