---
title: Miniature Minifier Makefile
layout: post
---

A solution that uses only make and curl:

{% highlight make %}

# c/o: http://wonko.com/post/simple-makefile-to-minify-css-and-js
# Patterns matching CSS files that should be minified. Files with a -min.css
# suffix will be ignored.
CSS_FILES = $(filter-out %.min.css,$(wildcard \
	css/*.css \
	css/**/*.css \
))

# Patterns matching JS files that should be minified. Files with a -min.js
# suffix will be ignored.
JS_FILES = $(filter-out %.min.js,$(wildcard \
	js/*.js \
	js/**/*.js \
))

# Commands
CSS_MINIFIER = curl -X POST -s \
    --data-urlencode "input@CSS_TMP" \
    http://www.cssminifier.com/raw

JS_MINIFIER = curl -s -X POST \
    --data-urlencode "js_code@JS_TMP" \
    http://marijnhaverbeke.nl//uglifyjs 

CSS_MINIFIED = $(CSS_FILES:.css=.min.css)
JS_MINIFIED = $(JS_FILES:.js=.min.js)

# target: minify - Minifies CSS and JS.
minify: minify-css minify-js

# target: minify-css - Minifies CSS.
minify-css: $(CSS_FILES) $(CSS_MINIFIED)

# target: minify-js - Minifies JS.
minify-js: $(JS_FILES) $(JS_MINIFIED)

%.min.css: %.css
	@echo '  Minifying $< ==> $@'
	$(subst CSS_TMP,$(<),$(CSS_MINIFIER)) > $@
	@echo

%.min.js: %.js
	@echo '  Minifying $< ==> $@'
	$(subst JS_TMP,$(<),$(JS_MINIFIER)) > $@
	@echo

# target: clean - Removes minified CSS and JS files.
clean:
	rm -f $(CSS_MINIFIED) $(JS_MINIFIED)


# target: help - Displays help.
help:
	@egrep "^# target:" Makefile

{% endhighlight %}


You can also find the latest version [on GitHub][mk] part of my [LeaseMilesTracker][lmt] project.

## How Does It Work?

Surprisingly simple.

1. We make a list of all CSS files, filtering out the _\*.min.css_ files;
2. we ask [cssminifier.com](http://www.cssminifier.com/) to make us a minified version;
3. then we save the latter to a file ending in *min.css*.

Same with the JavaScript files, but using the service provided by [UglifyJS](http://marijnhaverbeke.nl/uglifyjs)

The obvious targets are *minify-css*, *minify-js*, and *minify* which is dependent on both.
The less obvious targets are *%.min.css* and *%.min.js* whose purpose is to cause
the re-minification of the CSS or JS files, if the normal files are newer than the minified version. 

Finally, *clean* will remove all the minified files, that is all _\*.min.css_ and _\*.min.js_ files.


## Why Would I Use This?

Ryan Grove's ["Simple makefile to minify CSS and JS"](http://wonko.com/post/simple-makefile-to-minify-css-and-js),
the original inspiration for my Makefile,
is an excellent solution if you're using the [YUI compressor][yc],
but YUIc requires Java (and so does Google's closure-compiler) and I was interesting
in having this not only work without Java,
but more important work on a system that would require no special tools
beyond what you'd find standard on most \*nix distros.  
After all this is 2012 and we're supposed to be using RESTful APIs and what not.

Oh, and also Mountain Lion doesn't come with Java installed.


[yaypie]: http://twitter.com/yaypie
[yc]: https://github.com/yui/yuicompressor/
[lmt]: https://github.com/philipmat/LeaseMilesTracker/
[mk]: https://github.com/philipmat/LeaseMilesTracker/blob/master/Makefile


