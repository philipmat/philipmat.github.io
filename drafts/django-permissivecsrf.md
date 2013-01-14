---
title: django-permissivecsrf
snippet: More lenient CSRF check for Django when posting from an HTTP page to an HTTPS one.
layout: post
---

I bet you're here because you've run into the puzzling Django error 

    CSRF verification failed. Request aborted.

    Reason given for failure:
        Referer checking failed - http://<domain>/ does not match https://<domain>/.


I'll double down that this happens when you try to make your login form post to HTTPS, 
perhaps to `https://<domain>/accounts/login/`.

If I'm mostly right, you've run into the problem I've solved. If I'm not right and 
you somehow ended up on this page, I'd love [to hear about it](/contact.html).


## Short version

In the CSRF middleware, Django does an extra check when a request comes over HTTPS to ensure it comes 
from the same site (same origin check).

If any portion of your site benefits from HTTPS, you probably should run your entire site over HTTPS. 
You can use [django-sslify][sslify] to force your website to operate in HTTPS mode all the time.

Furthermore, if you want to disable CSRF checking for your own views, there are [other methods 
you can use][edge-cases], for example the `@csrf_exempt` decorator. 

However, if the views are not under your control and you are comfortable n trading some security 
for not really that much convenience, you can use [django-permissivecsrf][gh] 
to work around this error.

Use the instructions in the README file on [GitHub][gh] or on [PyPI][pypi] to get this project up an running.
Mostly it consists of installing django-permissivecsrf and adding `'permissivecsrf.middleware.PermissiveCSRFMiddleware'`
to your `MIDDLEWARE_CLASSES` entry.

Enjoy.

## Long version

The gist of why this happens is explained in point #4 of the [How it works][csrf-how] section of the Django documentation on
Cross Site Request Forgery (emphasis mine):

> 4) In addition, for HTTPS requests, strict referer checking is done by CsrfViewMiddleware. 
> This is necessary to address a Man-In-The-Middle attack that is possible under HTTPS 
> when using a session independent nonce, due to the fact that HTTP 'Set-Cookie' headers 
> are (unfortunately) accepted by clients that are talking to a site under HTTPS. 
> **(Referer checking is not done for HTTP requests because the presence of the Referer header is not reliable enough under HTTP.)**


In other words, because the HTTPS headers are encrypted, the *HTTP-Referer* header is resilient 
against MITM attacks, so it can be safely used to check and make sure the CSRF cookie
is originated by the same site that served the page *and* that the referring page has also been 
served over HTTPS, which means that page has also been protected against header injections.

The same check could be made on HTTP calls as well, but since HTTP headers are not encrypted, they 
could be easily faked and thus the check would be a useless placebo.

This explanation is also present, in comment form, in this [f92a21daa7][f9] commit by spookylukey aka Luke Plant,
and further detailed by him in a [reply][reply] to a complaint about the strictness of CSRF Referer check 
on the django-developers maillist.

### How django-permissivecsrf works

The [Django CSRF middleware][csrf-py] performs an extra-check if the request is over HTTPS to 
ensure that the request came from the same site, i.e. that 
the referrer (HTTP-Referer header) matches the current site, 
and that the schema of the referrer is also HTTPS.

In other words, in ensures that the call to https://example.com/account/login
came from another page of https://example.com/. As such, if you put your login 
form on your non-secure homepage, http://example.com/, but use a secure target 
for your form's *action* attribute, `<form action="https://example.com/account/login" method="POST">`,
Django's check will fail because::

    'http://example.com/' != ('https://%s/' % request.get_host())

However, Django will not perform the CSRF check *at all* if the `request` object has 
an attribute `_dont_enforce_csrf_checks` set to **True**. That's what PermissiveCSRF relies on:
if the request came from the same site, regardless the schema, it sets `_dont_enforce_csrf_checks`
to True, thus telling the Django CSRF middleware to skip the CSRF check for that request.

This only happens if:

* `DEBUG == True`. Your production server should always be HTTPS;
* The `HTTP-Referer` header is present;
* The request is for an HTTPS URL (i.e. `request.is_secure() == True`);
* and the referrer uses HTTP. 

In all other cases it defers to Django for normal processing.

### Bottom line

There's only one thing to take away from all this: **in production use HTTPS (see [django-sslify][sslify])**. Period.


[gh]: https://github.com/philipmat/django-permissivecsrf
[pypi]: http://pypi.python.org/pypi/django-permissivecsrf/
[sslify]: https://github.com/rdegges/django-sslify
[csrf-how]: https://docs.djangoproject.com/en/dev/ref/contrib/csrf/#how-it-works
[f9]: https://github.com/django/django/commit/f92a21daa7
[reply]: https://groups.google.com/d/msg/django-developers/IgWK2vEePtY/R1r3Im4x3UMJ
[csrf-py]: https://github.com/django/django/blob/master/django/middleware/csrf.py
[edge-cases]: https://docs.djangoproject.com/en/dev/ref/contrib/csrf/#edge-cases
