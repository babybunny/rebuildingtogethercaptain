define(['underscore-min'], function() {
  _.templateSettings = {
    interpolate: /\{\{(.+?)\}\}/g
  };
  var config = {};
    config.apiKey = 'AIzaSyCROLZeFx9I9Hdw8c189TDI7GoWNUqIhfU';
    config.scopes = 'https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile';
    config.clientId = '1093814363166-dp6d5juof62nf0siaja08fabqsh8ber3.apps.googleusercontent.com';
    return config;
});

