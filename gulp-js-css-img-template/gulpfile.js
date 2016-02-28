var gulp = require('gulp');
var jslint = require('gulp-jslint');
var jshint = require('gulp-jshint');
var sass = require('gulp-sass');
var minifycss = require('gulp-minify-css');
var imagemin = require('gulp-imagemin');
var pngquant = require('imagemin-pngquant');
var ts = require('gulp-typescript');
var concat = require('gulp-concat');
var beautify = require('gulp-beautify');
var uglify = require('gulp-uglify');
var imagemin = require('gulp-imagemin');
var rename = require('gulp-rename');
var sourcemaps = require('gulp-sourcemaps');
var del = require('del');

var tslint = require("gulp-tslint");

var paths = {
	js: ['_src/js/**/*.ts', '_src/**/*.ts'],
	css: ['_src/css/**/*.scss'],
	img: ['_src/img/**/*']
};
gulp.task('clean', function() {
	return del.sync(['build','dist'],{force:true});
});

gulp.task('js_clean', function() {
	return del.sync(['build/js'],{force:true});
});

gulp.task('css_clean', function() {
	return del.sync(['build/css'],{force:true});
});

gulp.task('img_clean', function() {
	return del.sync(['build/img'],{force:true});
});

gulp.task('build_clean', function() {
	return del.sync(['build/**'],{force:true});
});

gulp.task('dist_clean', function() {
	return del.sync(['dist/**'],{force:true});
});

gulp.task("js_build_tslint", function() {
	gulp.src(paths.js)
	.pipe(tslint())
	.pipe(tslint.report("verbose"))
});

gulp.task('js_build',['js_clean'], function() {
	return gulp.src(paths.js)
	.pipe(ts())
	.pipe(beautify({indentSize: 4}))
	.pipe(gulp.dest('build/js'));
});

gulp.task('js_build_hint', function() {
	return gulp.src(['build/js/**/*.js'])
	.pipe(jshint())
	.pipe(jshint.reporter('jshint-stylish'));
});

gulp.task('js_build_jslint', function () {
	return gulp.src(['build/js/**/*.js'])
	.pipe(jslint({
		node: true,
		nomen: true,
		sloppy: true,
		plusplus: true,
		unparam: true,
		stupid: true
	}));
});
gulp.task('js_dist', function() {
	return gulp.src('build/js/**/*.js')
	.pipe(concat('app.js'))
	.pipe(beautify({indentSize: 4}))
	.pipe(gulp.dest('dist/js'))
	.pipe(sourcemaps.init()) 
	.pipe(uglify())
	.pipe(rename({suffix:'.min'}))
	.pipe(sourcemaps.write())
	.pipe(gulp.dest('dist/js'));
});

gulp.task('js_dist_jslint', function () {
	return gulp.src(['dist/js/app.js'])
	.pipe(jslint({
		node: true,
		nomen: true,
		sloppy: true,
		plusplus: true,
		unparam: true,
		stupid: true
	}));
});

gulp.task('css_build', ['css_clean'],function () {
	return gulp.src(paths.css)
	.pipe(sass())
	.pipe(gulp.dest('build/css'));
});

gulp.task('css_dist',function () {
	return gulp.src('build/**/*.css')
	.pipe(concat('style.min.css'))     
	.pipe(minifycss())  
	.pipe(gulp.dest('dist/css'))           
});


gulp.task('img_build', ['img_clean'],function() {
	return gulp.src(paths.img)
	.pipe(imagemin({
		progressive: true,
		optimizationLevel: 5,
		svgoPlugins: [{removeViewBox: false}],
		use: [pngquant()]
	}))
	.pipe(gulp.dest('build/img'));
});

gulp.task('img_dist', function() {
	return gulp.src('build/img/**/*')
	.pipe(gulp.dest('dist/img'))
});

gulp.task('watch', function() {
	gulp.watch(paths.js, ['js_build','js_build_hint','js_build_jslint']);
	gulp.watch(paths.css, ['css_build']);
	gulp.watch(paths.img, ['img_build']);
});

gulp.task('build', ['build_clean','js_build_tslint' ,'js_build','css_build','img_build']);
gulp.task('dist', ['dist_clean','js_dist','css_dist','img_dist']);

gulp.task('default', ['watch']);