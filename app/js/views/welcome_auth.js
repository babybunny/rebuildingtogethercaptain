define(
    ['backbone', 'text!app/templates/welcome_auth.html'],
    function(backbone, template) {
        var WelcomeAuthView = backbone.View.extend({
            el: '#welcome-auth-view',
            template: _.template(template),
            
            events: {
                'click #signin-button': 'signin',
                'click #signout-button': 'signout'
            },
            
            initialize: function(app) {
                this.app = app;
                this.listenTo(this.app.apiManager.loginState,
                              'change:state change:email', this.render);
                this.listenTo(this.app.user, 'change', this.render);
            },
            
            render: function() {
                var state = this.app.apiManager.loginState.get('state');
                console.log('rendering welcome_auth with state: ' + state
                            + ' and email: '
                            + this.app.apiManager.loginState.get('email'));
                var t = this.template({
                    email: this.app.apiManager.loginState.get('email')
                });
                this.$el.html(t);
                this.$('#welcome-auth-staff'  ).hide();
                this.$('#welcome-auth-captain').hide();
                this.$('#welcome-auth-unknown').hide();
                this.$('#welcome-auth-initial').show();
                if (this.app.user.get('staff_key')) {
                    this.$('#welcome-auth-staff'  ).show();
                    this.$('#welcome-auth-captain').hide();
                    this.$('#welcome-auth-unknown').hide();
                    this.$('#welcome-auth-initial').hide();
                } else if (this.app.user.get('captain_key')) {
                    this.$('#welcome-auth-staff'  ).hide();
                    this.$('#welcome-auth-captain').show();
                    this.$('#welcome-auth-unknown').hide();
                    this.$('#welcome-auth-initial').hide();
                } else if (this.app.user.get('oauth_email')) {
                    this.$('#welcome-auth-staff'  ).hide();
                    this.$('#welcome-auth-captain').hide();
                    this.$('#welcome-auth-unknown').show();
                    this.$('#welcome-auth-initial').hide();
                }
                if (state) {
                    this.$('#welcome-auth-signed-in').show();
                    this.$('#welcome-auth-sign-in').hide();
                } else {
                    this.$('#welcome-auth-signed-in').hide();
                    this.$('#welcome-auth-sign-in').show();
                }
                return this;
            },
            
            signin: function() {
                this.app.apiManager.handleSignin();
                return false;
            },
            signout: function() {
                console.log('signing out');
                this.app.apiManager.handleSignout();
                return false;
            }
        });
        
        return WelcomeAuthView;
    }
);
