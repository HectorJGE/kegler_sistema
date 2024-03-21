"use strict";

// Load plugins
const autoprefixer = require("gulp-autoprefixer");
const browsersync = require("browser-sync").create();
const cleanCSS = require("gulp-clean-css");
const del = require("del");
const gulp = require("gulp");
const header = require("gulp-header");
const merge = require("merge-stream");
const plumber = require("gulp-plumber");
const rename = require("gulp-rename");
const sass = require("gulp-sass");
const uglify = require("gulp-uglify");

const static_dir = '../base/static/build/'

// Load package.json for banner
const pkg = require('./package.json');

// Set the banner content
const banner = ['/*!\n',
    ' * Start Bootstrap - <%= pkg.title %> v<%= pkg.version %> (<%= pkg.homepage %>)\n',
    ' * Copyright 2013-' + (new Date()).getFullYear(), ' <%= pkg.author %>\n',
    ' * Licensed under <%= pkg.license %> (https://github.com/StartBootstrap/<%= pkg.name %>/blob/master/LICENSE)\n',
    ' */\n',
    '\n'
].join('');

// BrowserSync
function browserSync(done) {
    browsersync.init({
        server: {
            baseDir: "./"
        },
        port: 3000
    });
    done();
}

// BrowserSync reload
function browserSyncReload(done) {
    browsersync.reload();
    done();
}

// Clean vendor

function clean() {
    return del(["./vendor/", static_dir], {force: true});
}

// Bring third party dependencies from node_modules into vendor directory
function modules() {
    // Bootstrap JS
    var bootstrapJS = gulp.src('./node_modules/bootstrap/dist/js/*')
        .pipe(gulp.dest('./vendor/bootstrap/js'));

    // Bootstrap SCSS
    var bootstrapSCSS = gulp.src('./node_modules/bootstrap/scss/**/*')
        .pipe(gulp.dest('./vendor/bootstrap/scss'));

    // ChartJS
    var chartJS = gulp.src('./node_modules/chart.js/dist/*.js')
        .pipe(gulp.dest('./vendor/chart.js'));

    // dataTables
    var dataTables = gulp.src([
        './node_modules/datatables.net/js/*.js',
        './node_modules/datatables.net-bs4/js/*.js',
        './node_modules/datatables.net-bs4/css/*.css'
    ])
        .pipe(gulp.dest('./vendor/datatables'));

    // Font Awesome
    var fontAwesome = gulp.src('./node_modules/@fortawesome/**/*')
        .pipe(gulp.dest('./vendor'));

    // jQuery Easing
    var jqueryEasing = gulp.src('./node_modules/jquery.easing/*.js')
        .pipe(gulp.dest('./vendor/jquery-easing'));

    // jQuery
    var jquery = gulp.src([
        './node_modules/jquery/dist/*',
        '!./node_modules/jquery/dist/core.js'
    ]).pipe(gulp.dest('./vendor/jquery'));

    //Full Calendar
    var fullcalendar = gulp.src('./node_modules/fullcalendar/*')
        .pipe(gulp.dest('./vendor/fullcalendar'));

    //jQuery UI
    var jQueryUI = gulp.src('./node_modules/jquery-ui-dist/*')
        .pipe(gulp.dest('./vendor/jquery-ui-dist'));

    //chosen-js
    var chosenJs = gulp.src('./node_modules/chosen-js/*')
        .pipe(gulp.dest('./vendor/chosen-js'));

    //datetime-picker
    var datetimePicker = gulp.src('./node_modules/jquery-datetimepicker/build/*')
        .pipe(gulp.dest('./vendor/jquery-datetimepicker'));

    //moment
    var moment = gulp.src('./node_modules/moment/*')
        .pipe(gulp.dest('./vendor/moment'));

    //JQuery Mask
    var jqueryMask = gulp.src('./node_modules/jquery-mask-plugin/dist/*')
        .pipe(gulp.dest('./vendor/jquery-mask-plugin'));

    //JQuery Formset
    var jqueryFormset = gulp.src('./node_modules/jquery.formset/src/*')
        .pipe(gulp.dest('./vendor/jquery-formset'));

    //Dropify
    var dropify = gulp.src('./node_modules/dropify/dist/**/*')
        .pipe(gulp.dest('./vendor/dropify'));

    //FancyBox
    var fancyBox = gulp.src('./node_modules/@fancyapps/fancybox/dist/*')
        .pipe(gulp.dest('./vendor/fancybox'));

    //Sweet Alert2
    var sweetAlert2 = gulp.src('./node_modules/sweetalert2/dist/*')
        .pipe(gulp.dest('./vendor/sweetalert2'));

    //jQuery QRCODE
    var jqueryQrcode = gulp.src('./node_modules/jquery.qrcode/*')
        .pipe(gulp.dest('./vendor/jquery.qrcode'));


    //VideoJs
    var videoJs = gulp.src('./node_modules/video.js/dist/*')
        .pipe(gulp.dest('./vendor/videojs'));

    //VideoJsWaveSurfer
    var videoJsWaveSurfer = gulp.src('./node_modules/videojs-wavesurfer/dist/**/*')
        .pipe(gulp.dest('./vendor/videojs-wavesurfer'));

    //Videojs-record
    var videoJsRecord = gulp.src('./node_modules/videojs-record/dist/**/*')
        .pipe(gulp.dest('./vendor/videojs-record'));

    //RecordRTC
    var recordRtc = gulp.src('./node_modules/recordrtc/*')
        .pipe(gulp.dest('./vendor/recordrtc'));

    //WaveSurfer
    var waveSurfer = gulp.src('./node_modules/wavesurfer.js/dist/**/*')
        .pipe(gulp.dest('./vendor/wavesurfer'));

    //webrtc-adapter
    var webRtcAdapter = gulp.src('./node_modules/webrtc-adapter/out/*')
        .pipe(gulp.dest('./vendor/webrtcadapter'));


    return merge(bootstrapJS, bootstrapSCSS, chartJS, dataTables,
        fontAwesome, jquery, jqueryEasing, fullcalendar, jQueryUI,
        chosenJs, datetimePicker, moment, jqueryMask, jqueryFormset,
        dropify, fancyBox, sweetAlert2, jqueryQrcode, videoJs, videoJsRecord,
        recordRtc, waveSurfer, videoJsWaveSurfer, webRtcAdapter
    );
}

function modules2() {
    // Bootstrap JS
    var bootstrapJS = gulp.src('./node_modules/bootstrap/dist/js/*')
        .pipe(gulp.dest(static_dir + '/vendor/bootstrap/js'));

    // Bootstrap SCSS
    var bootstrapSCSS = gulp.src('./node_modules/bootstrap/scss/**/*')
        .pipe(gulp.dest(static_dir + '/vendor/bootstrap/scss'));

    // ChartJS
    var chartJS = gulp.src('./node_modules/chart.js/dist/*.js')
        .pipe(gulp.dest(static_dir + '/vendor/chart.js'));

    // dataTables
    var dataTables = gulp.src([
        './node_modules/datatables.net/js/*.js',
        './node_modules/datatables.net-bs4/js/*.js',
        './node_modules/datatables.net-bs4/css/*.css'
    ]).pipe(gulp.dest(static_dir + '/vendor/datatables'));

    // Font Awesome
    var fontAwesome = gulp.src('./node_modules/@fortawesome/**/*')
        .pipe(gulp.dest(static_dir + '/vendor'));

    // jQuery Easing
    var jqueryEasing = gulp.src('./node_modules/jquery.easing/*.js')
        .pipe(gulp.dest(static_dir + '/vendor/jquery-easing'));

    // jQuery
    var jquery = gulp.src([
        './node_modules/jquery/dist/*',
        '!./node_modules/jquery/dist/core.js'
    ]).pipe(gulp.dest(static_dir + '/vendor/jquery'));

    //Full Calendar
    var fullcalendar = gulp.src('./node_modules/fullcalendar/*')
        .pipe(gulp.dest(static_dir + '/vendor/fullcalendar'));

    //jQuery UI
    var jQueryUI = gulp.src('./node_modules/jquery-ui-dist/*')
        .pipe(gulp.dest(static_dir + '/vendor/jquery-ui-dist'));

    //chosen Js
    var chosenJs = gulp.src('./node_modules/chosen-js/*')
        .pipe(gulp.dest(static_dir + '/vendor/chosen-js'));

    //Datetime picker
    var datetimePicker = gulp.src('./node_modules/jquery-datetimepicker/build/*')
        .pipe(gulp.dest(static_dir + '/vendor/jquery-datetimepicker'));

    //Moment
    var moment = gulp.src('./node_modules/moment/*')
        .pipe(gulp.dest(static_dir + '/vendor/moment'));

    //JQuery Mask
    var jqueryMask = gulp.src('./node_modules/jquery-mask-plugin/dist/*')
        .pipe(gulp.dest(static_dir + '/vendor/jquery-mask-plugin'));

    //JQuery Formset
    var jqueryFormset = gulp.src('./node_modules/jquery.formset/src/*')
        .pipe(gulp.dest(static_dir + '/vendor/jquery-formset'));

    //Dropify
    var dropify = gulp.src('./node_modules/dropify/dist/**/*')
        .pipe(gulp.dest(static_dir + '/vendor/dropify'));

    //Fancybox
    var fancyBox = gulp.src('./node_modules/@fancyapps/fancybox/dist/*')
        .pipe(gulp.dest(static_dir + '/vendor/fancybox'));

    //Sweet Alert2
    var sweetAlert2 = gulp.src('./node_modules/sweetalert2/dist/*')
        .pipe(gulp.dest(static_dir + './vendor/sweetalert2'));

    //jQuery QRCODE
    var jqueryQrcode = gulp.src('./node_modules/jquery.qrcode/*')
        .pipe(gulp.dest(static_dir + './vendor/jquery.qrcode'));

    //VideoJs
    var videoJs = gulp.src('./node_modules/video.js/dist/**/*')
        .pipe(gulp.dest(static_dir + './vendor/videojs'));

    //VideoJsWaveSurfer
    var videoJsWaveSurfer = gulp.src('./node_modules/videojs-wavesurfer/dist/**/*')
        .pipe(gulp.dest(static_dir + './vendor/videojs-wavesurfer'));

    //Videojs-record
    var videoJsRecord = gulp.src('./node_modules/videojs-record/dist/**/*')
        .pipe(gulp.dest(static_dir + './vendor/videojs-record'));

    //RecordRTC
    var recordRtc = gulp.src('./node_modules/recordrtc/*')
        .pipe(gulp.dest(static_dir + './vendor/recordrtc'));

    //WaveSurfer
    var waveSurfer = gulp.src('./node_modules/wavesurfer.js/dist/**/*')
        .pipe(gulp.dest(static_dir + './vendor/wavesurfer'));

    //webrtc-adapter
    var webRtcAdapter = gulp.src('./node_modules/webrtc-adapter/out/*')
        .pipe(gulp.dest(static_dir + './vendor/webrtcadapter'));

    return merge(bootstrapJS, bootstrapSCSS, chartJS, dataTables,
        fontAwesome, jquery, jqueryEasing, fullcalendar, jQueryUI,
        chosenJs, datetimePicker, moment, jqueryMask, jqueryFormset,
        dropify, fancyBox, sweetAlert2, jqueryQrcode, videoJs,
        videoJsWaveSurfer, videoJsRecord, recordRtc, waveSurfer, webRtcAdapter
    );
}

function images() {
    return gulp.src('./img/**/*')
        .pipe(gulp.dest(static_dir + '/img'));
}

// CSS task
function css() {
    return gulp
        .src("./scss/**/*.scss")
        .pipe(plumber())
        .pipe(sass({
            outputStyle: "expanded",
            includePaths: "./node_modules",
        }))
        .on("error", sass.logError)
        .pipe(autoprefixer({
            cascade: false
        }))
        .pipe(header(banner, {
            pkg: pkg
        }))
        .pipe(gulp.dest("./css"))
        .pipe(rename({
            suffix: ".min"
        }))
        .pipe(cleanCSS())
        .pipe(gulp.dest("./css"))
        .pipe(browsersync.stream());
}

function css2() {
    return gulp
        .src("./scss/**/*.scss")
        .pipe(plumber())
        .pipe(sass({
            outputStyle: "expanded",
            includePaths: "./node_modules",
        }))
        .on("error", sass.logError)
        .pipe(autoprefixer({
            cascade: false
        }))
        .pipe(header(banner, {
            pkg: pkg
        }))
        .pipe(gulp.dest(static_dir + "/css"))
        .pipe(rename({
            suffix: ".min"
        }))
        .pipe(cleanCSS())
        .pipe(gulp.dest(static_dir + "/css"))
        .pipe(browsersync.stream());
}

// JS task
function js() {
    return gulp
        .src([
            './js/*.js',
            '!./js/*.min.js',
        ])
        .pipe(uglify())
        .pipe(header(banner, {
            pkg: pkg
        }))
        .pipe(rename({
            suffix: '.min'
        }))
        .pipe(gulp.dest('./js'))
        .pipe(browsersync.stream());
}

function js2() {
    return gulp
        .src([
            './js/**/*.js',
            '!./js/**/*.min.js',
        ])
        .pipe(uglify())
        .pipe(header(banner, {
            pkg: pkg
        }))
        .pipe(rename({
            suffix: '.min'
        }))
        .pipe(gulp.dest(static_dir + '/js'))
        .pipe(browsersync.stream());
}

// Watch files
function watchFiles() {
    gulp.watch("./scss/**/*", css);
    gulp.watch(["./js/**/*", "!./js/**/*.min.js"], js);
    gulp.watch("./**/*.html", browserSyncReload);
}

// Define complex tasks
const vendor = gulp.series(clean, modules, modules2);
const build = gulp.series(vendor, gulp.parallel(css, js,css2, js2, images));
const watch = gulp.series(build, gulp.parallel(watchFiles, browserSync));

// Export tasks
exports.css = css;
exports.js = js;
exports.clean = clean;
exports.vendor = vendor;
exports.build = build;
exports.watch = watch;
exports.default = build;
