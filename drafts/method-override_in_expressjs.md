---
title: PUT and DELETE with HTML Forms in ExpressJS
snippet: Making PUT and DELETE work with ExpressJS when submitting from HTML pages.
layout: post
---

In trying to send data from an HTML form to an ExpressJS backend
I soon discovered two things:

1. `FORM` elements only support `GET` and `POST`, not `PUT`, nor `DELETE`;
2. ExpressJS does not have a built-in way to address this
   but fortunately there's a middleware plugin,
   [method-override], that does.

`method-override`'s [documentation][moreadme] is great and very much
on point, except for the `FORM` post override section,
which I found a bit confusing on my first read (although in
honesty, now it seems much clear).

As a result, and for my own clarification, I decided to put together
as small [example that showcases][example] all the ways `method-override`
can be used from within HTML pages.

## General approach

Middleware in ExpressJS typically takes place early in the
processing pipeline and as such `method-override` will
attempt to identify a specific token in the received data,
per configuration, and will, well, *override* the *method*
aka HTTP *verb* used.

There are two main approaches we can use to trigger the `app.put()`
and `app.delete()` route handlers from HTML code:

1. Using AJAX
2. Using the form's `method="POST"` with a specific token.

## Using AJAX

Almost all current versions of browsers support specifying an HTTP method.

```js
// client code
var xhr = new XMLHttpRequest();
xhr.open('PUT', '/resource', true);
xhr.send();

// ---
// server code
app.put('/resource', function(req, res) {
    console.log('PUT to /resource');
});
```

If you only work with modern browsers, there's nothing more required.

However, if your front-end needs to be backward compatible with older
versions that don't support HTTP methods (enterprise software developers,
I feel you), then `method-override` can be configured to look for a token in the
headers being posted and override the method being used.

```js
// server code
var methodOverride = require('method-override');
app.use(methodOverride('X-HTTP-Method-Override'));
app.put('/resource', ...
```

As such, the client code needs to specify the intended method in a header:

```js
// client code
var xhr = new XMLHttpRequest();
xhr.open('POST', '/resource', true); // method-override needs it to be POST
xhr.setRequestHeader('X-HTTP-Method-Override', 'PUT');
xhr.send();
```

## `POST`-ing with specific token

If instead of AJAX, we intend to use the HTML's `FORM` element
to `PUT` or `DELETE`, `method-override` can be configured to
look for a specific token either in the query string, or,
with a tiny bit more code, in the data being submitted.

### Specific Token in Query String

In this example we will have the form `POST` to
`/resource?_method=PUT` and will configure `method-override`
to look for `_method` in the query string and override
the HTTP method with the indicated verb.

```js
// server code
app.use(methodOverride('_method'));
app.put('/resource', ...
```

On the client side, we'll `POST` to the above URL:

```html
// client code
<form method="POST" action="/resource?_method=PUT">
...
</form>
```

**Note**: by default `method-override` only examines `POST` requests.

You can configure it to look at `GET` requests:

```js
// server code
app.use(methodOverride('_method', { methods: ['POST', 'GET'] });
```

but this is a *really **bad** idea* for two reasons:

1. `GET`-ing `/resource?_method=DELETE` is downright *dangerous* as anything
   unintentionally (or worse, *intentionally*) crawling your URLs
   will cause deletion of resources; this could be something
   as trivial as a browser pre-fetching links in order to speed up pages,
   or a browser extension investigating URLs for any number of reasons
   (phishing protection, status checking, statistics, etc).
2. `GET`-ing `/resource?_method=PUT` with a payload makes no sense
   from an HTTP standard perspective. Payloads are for `POST` and `PUT`.

So just don't.

### Specific Token in Form data

The second method involved sending the token with the `POST` body.
The most common approach is to include a hidden field.

```html
<form method="POST" action="/log" enctype="application/x-www-form-urlencoded">
  <input type="hidden" name="_method" value="PUT">
  <button type="submit">Submit</button>
</form>
```

The server-side code is a little bit more involved this time as it requires
another library: `body-parser`, which you're likely to use anyway if you
deal with form data or just HTTP body data in general.

`body-parser` inteprets the incoming HTTP request body and makes it
available as key-value pairs in the `body` property of the
request, `req`, parameter.

`method-override` allows one to specify a custom function to be called
during the middleware execution. In this custom function we will inspect
the request body, `req.body`, for the presence of the desired token, `_method`
in this case, and return its value to the middleware that will in turn override
the request method.

```js
// server code
var bodyParser = require('body-parser');
app.use(bodyParser.urlencoded({ extended: false }));
app.use(methodOverride(function (req, res) {
  if (req.body && typeof req.body === 'object' && '_method' in req.body) {
    // look in urlencoded POST bodies and delete it
    var method = req.body._method;
    delete req.body._method;
    return method;
  }
}));
```

## Composition

As a final note, it's worth mentioning that you can have multiple
`method-override`s in your middleware code, thus allowing the handling
of all the scenarios presented above.

Except for the `GET`+`DELETE` scenario. You should *never* do that.

```js
// server code
var express = require('express');
var bodyParser = require('body-parser');
var methodOverride = require('method-override');

var app = express();

app.use(methodOverride('X-HTTP-Method-Override'));
app.use(methodOverride('_method'));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));
app.use(methodOverride(function (req, res) {
  if (req.body && typeof req.body === 'object' && '_method' in req.body) {
    var method = req.body._method;
    delete req.body._method;
    return method;
  }
}));

app.get('/resource', ...)
   .get('/resource/:id', ...)
   .post('/resource', ...)
   .put('/resource/:id', ...)
   .delete('/resource/:id', ...);
```

If you want to see all the examples above in action,
clone my [method-override-example][example] repo
and simply run `npm start` then navigate to <http://localhost:3000/>
to play with each of these scenarios.


[method-override]: https://github.com/expressjs/method-override
[example]: https://github.com/philipmat/method-override-examples
[moreadme]: https://github.com/expressjs/method-override/blob/master/README.md