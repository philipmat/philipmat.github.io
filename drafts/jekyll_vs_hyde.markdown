---
title: Jekyll vs. Hyde - A Comparison of Two Static Site Generators
snippet: A comparison of Jekyll and Hyde when considering a static website generator.
layout: post
has_tldr: yes
---

It seemed fitting, when I first thought about it, that my first blog post should discuss the engine I chose to power my website. After spending days writing this for you, I'm reasonably confident we both would've been better served if I went drinking with my imaginary friends and you just pretended you liked reading it. Anyway...

There are several static site generators/engines you can choose from and your choice is most likely bound by either what features your hosting provider offers or by language preference. 
On the Ruby planet [Jekyll][jekyll], [Webby](http://webby.rubyforge.org/), and [nanoc](http://nanoc.stoneship.org/) are the most popular choices.  
Robert Rees has [an excellent comparison](http://rrees.wordpress.com/2009/06/01/semi-static-cmss/) of the Ruby engines, which he calls "Semi-static CMSs". His article was written in June 2009, but you'll find it very much pertinent as two years later these three engines are still firing on all pistons. Largely based on Robert's review, I have selected *Jekyll* to represent the Ruby side.  
 With Python you have [Hyde](http://ringce.com/hyde) and that's pretty much it.  

With a static website generator you will spend most of your time producing the content and a little bit less fidgeting with the layout. Ironically, Jekyll and Hyde lend themselves quite well to a head to head comparison on both features. Not only do both support [Markdown](http://daringfireball.net/projects/markdown/) and [Textile](http://www.textism.com/tools/textile/) for writing the content, their templating languages are very similar too: Hyde uses the Django templating language, whereas Jekyll uses [Liquid][liquid], whose inspiration was, surprise!, the Django templating language.

I do provide [an example website][jekyll_vs_hyde] built using Jekyll and then Hyde [on github][jekyll_vs_hyde]. While this post does make some references to this sample, you might find it a good counterpart as it covers some of the elements I struggled to figure out.  
Execute `git clone https://github.com/philipmat/jekyll_vs_hyde` in the directory of your choice to get this sample or simply use github to view the code.

* [Installation](#installation)
* [Structure](#structure)
* [Advanced Configuration and Options](#configuration)
* [The Content and the Templating Language](#templates)
* [Miscellaneous Features and Considerations](#misc)
* [Conclusion](#tldr)

<A name="installation"> </A>
## Installation
The best way to install Jekyll is via RubyGems:
{% highlight bash %}
gem install jekyll
{% endhighlight %}

This will also install all required dependencies: *directory_watcher*, *liquid*, *open4*, *maruku* and *classifier*. More information [can be found here][jekyll_install], but one interesting, if not ironic, bit is that Jekyll relies on [Pygments](http://pygments.org/), a Python project, to provide code syntax highlighting. The installation instructions for Pygments, also detailed on the [Jekyll install page][jekyll_install], are dependent on your OS, but are usually a variant of:
{% highlight bash %}
sudo easy_install Pygments
{% endhighlight %}

I recommend that you also generate, at this point, the stylesheet required by Pygments to style your code:
{% highlight bash %}
python -c "from pygments.formatters import HtmlFormatter; print HtmlFormatter().get_style_defs('.highlight')" > highlight.css
{% endhighlight %}

Hyde's setup, on the other hand, is more involved. You will start by getting the source code, followed by installing the requirements (*django*, *pyYAML*, and *markdown*), and probably complete by installing Pygments.
{% highlight bash %}
cd /opt/local/src
git clone https://github.com/lakshmivyas/hyde.git
cd hyde && pip install -r requirements.txt
{% endhighlight %}
You might consider installing [markdown2](http://code.google.com/p/python-markdown2/) instead, which Hyde also supports; it's a faster and more complete implementation of Markdown.

*A note on Hyde installation*: if you plan to follow along [the instructions on github][hyde], the next step of Hyde offers to generate a "basic website" for you, and then processes this skeleton to generate your website. Unfortunately, this "basic website" turns out to be quite comprehensive, and its processing will fail because it requires a great deal of Python modules which were not listed in `requirements.txt`. At this point you have several options:
1. You follow along with me or use my **truly basic** skeleton which I promise it'll work or your money back.
2. You leave the "basic website" as is and prod around for structure and other tricks. Just be aware that what was generated is anything but *basic*.
2. You proceed to discover and install all the requirements and then generate and run the website.


<A name="structure"> </A>
## Structure

Both languages tend to follow a similar structure, with Jekyll inclining more towards convention-over-configuration, whereas Hyde tends to favor flexibility through configuration. They will read pretty much all files in the structure and either through process or straight copy will generate your static website in an output folder.

### Jekyll
The more prominent elements of a typical Jekyll structure include a `_layouts` folder that stores the templates to build the site, a `_posts` folder that contains the *blog* content, and a `_site` folder where the generated website will be placed. Also typically present are a configuration file in YAML format, `_config.yml`, a root `index.html`, and most likely some sort of `media` folder for your `.css`, `.js`, and images.

	./
	  _config.yml
	  index.html
	  _layouts/
	      base.html
	      post.html
	  _posts/
	      2011-04-11-lore_ipsum_sit_amet.markdown
	      2011-04-21-consectetur_adipisicing_elit.markdown
	  media/
	      main.css
	      main.js
	  _site/
	      ...


This configuration is merely a preference. Between command line arguments and the `_config.yml` file, Jekyll allows you to overwrite most of its options, which can be [quite extensive][jekyll_config]. 

Within this structure, Jekyll will attempt to process all `.html`, `.markdown`, and `.textile` files that contain a specific header, called [YAML Front Matter][jekyll_yfm]; it will ignore those files that do not have this header or those that start with an underscore (including folders). All other files will be copied to the `_site` folder, preserving the folder hierarchy in which they were located.

Jekyll also mandates that the files within the `_posts` folder are in a `YEAR-MONTH-DATE-blog_title.MARKUP` format. You have control over the [permalinks][jekll_permalinks] it will generate, but the names of the files are fixed.

### Hyde
Hyde offers to generate a "basic website" for newcomers - which, as mentioned before, doesn't work, but gives you a basic idea of what Hyde looks like - and a `settings.py` file to work with.
Hyde compartmentalizes its files a bit more than Jekyll:

* `layout` - files used as templates for the content (set using `LAYOUT_DIR`);
* `content` - your actual content (set with `CONTENT_DIR`). These will be processed by Hyde and the templates in `layout` will be applied according to each file's individual preference, similar but not exactly like Jekyll's *YAML Front Matter*;
* `media` - images, stylesheets, etc (`MEDIA_DIR`). These are files that are copied to the output folder preserving their hierarchical structure;
* `deploy` - the folder to which Hyde outputs the static website (`DEPLOY_DIR`). Its Jekyll equivalent is the `_site` folder.


<A name="configuration"> </A>
## Advanced Configuration and Options
Aside from the caveat regarding Hyde's generated "basic website" and `settings.py`, neither engine requires any further configuration to start working on your website, but both offer more advanced options, and in both cases *most* of these options are configurable through `settings.py` in Hyde's case and `_config.yml` in Jekyll's.

You get common features such as: 

* exclude files from processing (e.g. `.htaccess`) or even entire folders (e.g. `_drafts`);
* specify what port to run the development server on;
* indicate a different output folder;  
* alternative rendering engines (e.g. a different Markdown engine);
* [Growl](http://growl.info/) notifications;
* syntax highlighting for code snippets using Pygments.

Some of the other options come from a combination of usage and configuration. For example, Hyde allows you to use a different Markdown engine, [markdown2](http://code.google.com/p/python-markdown2/), by using a `{{ "{% markdown2 "}}%}` tag in the templates, whereas Jekyll interprets all `.markdown` files as Markdown syntax but the actual translation engine can be changed in `_config.yml` using the `markdown: [engine]` setting, allowing you to switch from the default *maruku* to *RDiscount* or another similar engine.

This touches on the first and perhaps largest difference between the two engines: Hyde makes use of template tags for processing, while Jekyll relies on the file extension to determine the type of markup for the content present within it. As a result, Hyde allows you to use multiple engines within the same content file: you can freely mix Markdown and Textile within a single file, if that's something you'd want to do, but at the expense of having your content sprinkled with Django tags.

Hyde also makes heavy use of [pre-processors][hyde] and [post-processors][hyde_postproc] when transforming the [content][hyde_preproc_content] and [support files][hyde_preproc_media] and allows you, among others, to minify your JavaScript files (using *JSMin*) or to optimize them using the *Closure Compiler*, to code your CSS using *SASS* or *Less CSS* or *Stylus*, or even generate thumbnails for your images.  
Of course, you'd have to install the appropriate Python packages for these pre-processors, for example you would need the [PIL - Python Imaging Library](http://www.pythonware.com/products/pil/) to make the thumbnails pre-processor work. These pre-processors are enumerated in specific lists within `settings.py`, e.g:

	MEDIA_PROCESSORS = {
        '.css':('hydeengine.media_processors.TemplateProcessor',
                'hydeengine.media_processors.CSSmin',),
        ...

but they are then configured separately using [global options][hyde_config] specific to each preprocessor (e.g. `THUMBNAIL_MAX_WIDTH`).

In contrast, Jekyll allows its options to be [configured][jekyll_config] in a hierarchical, and easier to read, fashion:

	maruku:
  	  use_tex:    false
  	  use_divs:   false

Jekyll's answer to Hyde's pre-processors, to some degree, are a quite extensive [collection of plugins][jekyll_plugins], for example Jason Graham's [Less CSS Converter](https://gist.github.com/639920) or Michael Levin's [sitemap.xml generator](http://www.kinnetica.com/projects/jekyll-sitemap-generator/).
	
Oh, and cherry on the cake, both have support for [Growl](http://growl.info/) - built-in Hyde and through [a plugin][jekyll_plugins] in Jekyll, although they both generate the files so fast I don't see why you would need it.


<A name="templates"> </A>
## The Content and the Templating Language

Hyde uses the [Django templating language][django_template] while Jekyll uses the similar, but less complex/powerful, [Liquid][liquid].  
If you're familiar with *Django*, you'll be at home with *Liquid*. If you're very familiar with Django, you'll notice pretty fast that Liquid is missing one very significant feature: *blocks*. We'll talk about this later - I just wanted to get it out of the way.


### A Simple Page
In both cases, you will pair a content file with one or more template files.  
__Let's start with Jekyll__ and a very simple *about* page, which will start out as an `./about.markdown` file and end up in `./_site/about.html`.


    ---
    layout: page
    title: About
    ---
    
    This sample shows how to build a very simple 
    [Jekyll](https://github.com/mojombo/jekyll) powered website.

The first section of the `about.markdown` file, between the `---` markers is the [YAML Front Matter][jekyll_yfm]. Jekyll requires it on all files you'd like to have processed, otherwise the file will be ignored and copied to the output as is. The `layout` property tells Jekyll what template to use when processing this file, so in this case Jekyll expects there is a `./_layouts/page.html` file, which [in my example][jekyll_vs_hyde] looks something like this:

{% highlight html %}
---
layout: base
---
<div class="content">
<h1>{{"{{ page.title"}} }}</a>

{{ "{{ content"}} }}

</div>
{% endhighlight %}

Three quick things as this is a comparison more than an introduction to the templating language: the `{{ "{{ page.title"}} }}` gets replaced by the `title` parameter from `about.markdown`'s *YAML Front Matter" section; the `{{ "{{ content"}} }}` will contain the processed body of the `about.markdown`; and, finally, because `page.html` contains it's own *YAML Front Matter* section, it will be further processed using `./_layouts/base.html`.  
`base.html` will then look very similar:
{% highlight html %}
<html>
<head>
    <title>{{ "{{ page.title"}} }} - Jekyll Sample</title>
</head>
<body>
    {{ "{% include nav.html" }} %}
    {{ "{{ content"}} }}
</body>
</html>
{% endhighlight %}

The interesting bit is the `{{ "{% include nav.html"}} %}` which does what you think it does, except it will require that the file is located at `./_includes/nav.html`.

__Let's look at the Hyde equivalent__, but we'll do so in reverse order. I promise you it'll make more sense.  
`base.html` looks just like the Jekyll equivalent:
{% highlight html %}
<html>
<head>
    <title>{{ page.title }} - Hyde Sample</title>
</head>
<body>
    {{'{% include "nav.html"'}} %}
    {{"{% block content"}} %}page content goes here{{"{% endblock"}}%} %}
</body>
</html>
{% endhighlight %}

The difference from the Jekyll version is the `{{"{% block content"}} %}{{"{% endblock"}} %}`.  
Next template in chain: `page.html`.

{% highlight html %}
{{'{% extends "base.html"'}} %}
{{"{% block content"}} %}
<div class="content">
<h1>{{ "{{ page.title"}} }}</h1>
{{"{% block article "}}%}{{"{% endblock"}} %}
</div>
{{"{% endblock"}} %}
{% endhighlight %}

In Django, blocks in child files overwrite blocks in the parent they inherit from (the `{{'{% extends "base.html'}}%}` specifies the parent of a template). As such, the `content` block in the `page.html` template will replace the similar block in the parent `base.html`. Finally, let's examine Hyde's version of the *about* page, `./content/about.html`:
{% highlight html %}
{{'{% extends "page.html"'}} %}
{{"{% hyde"}}
    title: "About"
    created: 2011-04-26 00:25:00
%}

{{"{% block article"}} %}
{{"{% markdown"}} %}
This sample shows how to build a very simple 
  [Hyde](https://github.com/lakshmivyas/hyde) powered website.
{{"{% endmarkdown"}} %}
{{"{% endblock "}}%}

{% endhighlight %}

Notice how the `content` block of `page.html` replaces the parent's, and the `article` block of `about.html` replaces the similar block defined in `page.html`. With Hyde a child page can overwrite any of the blocks defined in any its ancestors; contrast with Jekyll where a child can only overwrite the parent's `{{"{{ content"}} }}` declaration.  
Your probably figured out that the `{{"{% hyde"}} %}` block is the rough equivalent of *YAML Front Matter* header.


### Dynamic Page - The Blog
To create a blog page, that is to generate a dynamic page that essentially includes other pages, Jekyll and Hyde offer similar mechanisms, but they go a different way about it. Jekyll is more opinionated and requires that your blog posts are *a)* stored within the `_posts` folder and *b)* that they follow a very specific naming convention: `YEAR-MONTH-DATE-blog_title.MARKUP`, where `MARKUP` would be either `markdown` or `textile`. If you do so, you will be able to use a construct in your templates that will iterate over the posts in reverse order by the date within the file name. For example, to output the list of the last 3 posts you would write:

{% highlight html %}
{{"{% for post in site.posts limit:3 "}} %}
    <h1>{{"{{ post.title"}} }}</h1>
    {{"{{ post.content"}} }}
    <hr/>
{{"{% endfor "}} %}
{% endhighlight %}

`site.posts` (or `paginator.posts` if you [enable pagination][jekyll_pagination] in `_config.yml`) contains all your posts regardless of the structure you have in place inside the `_posts` folder. I think this is nice because it allows you to organize your posts however you think it's best for you.   
Variables added to the *YAML Front Matter* are available to you through the `post` variable. I am making use of this feature in the example website to show how one could provide an abstract of a post through the `post.abstract` atom.

In contrast, Hyde doesn't really care about any particular structure. From within any file you can enumerate its siblings and children and even access its ancestor (parent folder). [The templating guide][hyde_template] has a good deal more information, but you'll deal with the following variables:

* The `page` variable, which refers to the current page; for example, within `index.html`, `page` refers to the `index.html` file;
* `page.node` refers to the directory in which `page` exists (`./content/` in the case of `./content/index.html`);
* `page.node.walk` provides a list of all the children, depth first, of the `node`, the `page` itself included as the first node.
* `page.node.walk_pages` provides the same except it excludes the folders.

In practice, you could use Hyde, with its multiple "dynamic" sources, to build any kind of websites (for example a documentation website), whereas Jekyll, with it's single "dynamic" source, seems heavily slanted towards blogging.  
However, this comes at a price: for simple types of websites working with Hyde tends to require more effort. Examine the equivalent of the Jekyll `index.html` posted above:

{% highlight html %}
{{'{% extends "base.html"'}} %}
{{"{% block article"}} %}
    {{"{% for node in page.node.walk"}} %}
    {{'{% if node.name == "posts"'}} %}
        {{"{% for post in node.walk_pages"}} %}
        {{"{% if not post.listing and not post.exclude"}} %}
            <h1>{{"{{ post.title"}} }}</h1>
            {{"{% render_article post"}} %}
        {{"{% endif"}} %}
        {{"{% endfor"}} %}
    {{"{% endif"}} %}
    {{"{% endfor"}} %}
{{"{% endblock"}} %}
{% endhighlight %}

Considerably more involved, I would think. Also one of the reasons I started writing this post and providing the sample website: the lack of Hyde documentation beyond laconic enumeration of the features. Some of the [documentation][hyde_wiki] mentions inexistent examples, and overall it just makes it unnecessarily hard to figure out even some of the basic details on how you are supposed to be using the engine.  

Both engines support tags or categories for posts, and they define them the same way: in the *YAML Front Matter* for Jekyll and the `{{"{% hyde"}} %}` block for Hyde. You can access these categories in Jekyll through the `site.categories` variable, which collects all the categories defined in all posts. Hyde requires that you first [configure a site pre-processor][hyde_preproc_site] which will enable category access through the `categories` variable. 

Part of the templating language, both Jekyll and Hyde allow you to include other files (my example includes a `nav.html` file) using the `{{"{% include FILE"}} %}`; less obvious is that Jekyll looks for these files in the `_includes` folder, whereas Hyde looks for it in the `content` folder.

Read through Hyde's [templating guide][hyde_template] to discover more about what the `page`, `page.node`, and `site` variables offer. The Jekyll equivalent can be found on the [template data][jekyll_template] wiki page.


<A name="misc"> </A>
## Miscellaneous Features and Considerations

Both engines come with a **built-in web server** that allows you to quickly check how the generated content will look like. Jekyll's is based on WEBrick and Hyde's on CherryPy, so you will need to have the respective gem or egg installed. One of the features that makes Jekyll stand out is that it combines the server with a directory watcher which will continuously regenerate the files that have changed (run `jekyll --auto --server`), whereas for Hyde you will need to run the regen command each time you change a file by running `python /path/to/hyde.py -g`.    
In practice, this is an incredible time saver and Jekyll processes only the files that change so it is very, very quick. To give you an idea how fast this process is, consider that I have MacVim set to save the files whenever the window loses focus; I can `Cmd-Tab` to the browser window and by the time I get to issue the refresh page command, the changed file has already been processed.

To get the same functionality, as I was working through the sample website for Hyde, I ended up backgrounding the webserver (started with `python /path/to/hyde.py -w`), and executing the regen command each time I would need to see the output. Unfortunately, Hyde seems to reprocess the entire website; it still is fast because the site is small, but it's something to consider when selecting your engine.

When it comes to **extensibility**, Hyde offers a good deal of built-in [site][hyde_preproc_site], [media][hyde_preproc_media], and [content][hyde_preproc_content] pre-processors and the vast library of [Django snippets][djangosnippets], whereas Jekyll relies on [plugins][jekyll_plugins] (a [good collection](https://github.com/josegonzalez/josediazgonzalez.com/tree/master/_plugins) of simple plugins written/compiled by Jose Gonzalez) to augment its functionality and to provide supplemental tags for Liquid. 

Another factor to consider is whether you have **an existing blog**. If it runs on *Wordpress*, you're in luck: both Jekyll and Hyde offer [migrators](https://github.com/mojombo/jekyll/wiki/Blog-Migrations) / [importers](http://stevelosh.com/blog/2010/01/moving-from-django-to-hyde/). The edge goes to Jekyll whose [migrator list](https://github.com/mojombo/jekyll/wiki/Blog-Migrations)  is quite extensive: *Drupal*, *Movable Type*, *Typo 4*, *TextPattern*, [Blogger/Blogspot](http://coolaj86.info/articles/migrate-from-blogger-to-jekyll.html), and all else failing, you have good ol' CSV. 

And finally, **deploying your site** to its final location is an exercise in simply copying the output folder, perhaps using a tool like `rsync` to speed it up. Hyde has an interesting project in [Clyde][clyde] which is an web editor for your pages, which would allow you to edit your site untethered from the computer on which you normally edit your site. As of right now, *Clyde* is not fully complete or stable, but that might be something that would sway your vote, so I thought you should know.


<A name="tldr"> </A>

## Conclusion
Jekyll is considerably easier to get up and run with, has *plenty* of examples, a strong presence in github behind it, and where it's lacking it can be extended with plugins. That Liquid is such a close implementation of the Django templating language is both a blessing and a curse: a blessing because you can look at existing Django examples, and a curse because not all those examples will work, and because you will not be able to take advantage of the large library of filters and tags available for Django.

Hyde on the other hand benefits immediately from the power of the Django templating language, the considerate flexibility that comes with it, as well as most of the tags and filters available through the [Django snippets][djangosnippets] library. It takes  more effort to get it up and develop your initial wireframe, and there is not much help if you get off the beaten path, but those costs might be offset if you require the more advanced features Hyde provides, including the one possibly killer features in the [Clyde][clyde] web editor, once it's complete and stable.  

If you're considering running your website off github's infrastructure, choosing Jekyll is pretty much a no-brainer. If you run it on your own infrastructure, I hope this post and the [accompanying sample][jekyll_vs_hyde] gave you enough information to make an informed guess about the direction you want to pursue.

I the end I chose [Jekyll][jekyll]. Either way, have fun. 



[jekyll_vs_hyde]: https://github.com/philipmat/jekyll_vs_hyde
[jekyll]: https://github.com/mojombo/jekyll
[jekyll_install]: https://github.com/mojombo/jekyll/wiki/install
[jekyll_config]: https://github.com/mojombo/jekyll/wiki/configuration
[jekyll_yfm]: https://github.com/mojombo/jekyll/wiki/YAML-Front-Matter
[jekll_permalinks]: https://github.com/mojombo/jekyll/wiki/Permalinks
[jekyll_plugins]: https://github.com/mojombo/jekyll/wiki/Plugins
[jekyll_template]: https://github.com/mojombo/jekyll/wiki/Template-Data
[liquid]: http://www.liquidmarkup.org/ 
[jekyll_pagination]: https://gist.github.com/227621

[hyde]: https://github.com/lakshmivyas/hyde
[hyde_wiki]: https://github.com/lakshmivyas/hyde/wiki
[hyde_config]: https://github.com/lakshmivyas/hyde/wiki/Settings
[hyde_preproc_media]: https://github.com/lakshmivyas/hyde/wiki/Media-Processors
[hyde_preproc_content]: https://github.com/lakshmivyas/hyde/wiki/Content-Processors
[hyde_preproc_site]: https://github.com/lakshmivyas/hyde/wiki/Site-Preprocessors
[hyde_postproc]: https://github.com/lakshmivyas/hyde/wiki/Site-Post-Processors
[hyde_template]: https://github.com/lakshmivyas/hyde/wiki/Templating-Guide
[django_template]: http://docs.djangoproject.com/en/dev/ref/templates/builtins/?from=olddocs
[djangosnippets]: http://djangosnippets.org/
[clyde]: https://github.com/lakshmivyas/hyde/blob/master/clydeweb/README.markdown
