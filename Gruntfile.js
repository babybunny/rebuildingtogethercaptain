module.exports = function(grunt) {
  grunt.initConfig({
          exec: {
              build: {
                  command: 'node node_modules/requirejs/bin/r.js -o require-config.js'
              }
          }
      });
  
  grunt.loadNpmTasks('grunt-exec');
  
  grunt.registerTask('copy-require', function() {
    grunt.file.mkdir('app/js/lib');
    grunt.file.copy('node_modules/requirejs/require.js', 'build/js/lib/require.js');
    grunt.file.copy('node_modules/requirejs-text/text.js', 'build/js/lib/text.js');
    grunt.file.copy('node_modules/backbone/backbone-min.js', 'build/js/lib/backbone-min.js');
    grunt.file.copy('node_modules/underscore/underscore-min.js', 'build/js/lib/underscore-min.js');
    grunt.file.copy('node_modules/jquery/dist/jquery.min.js', 'build/js/lib/jquery.js');
  });
  
  grunt.registerTask('default', ['copy-require']);
};
