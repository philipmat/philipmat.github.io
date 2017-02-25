---
title: Better security - different email for each account
snippet: Use a different email for each account in order to increase your online security.
layout: post
---

You already know that having a different password for each online account
is wise thing to do from a security perspective.

For the same reason, to increase security, you probably should have a different
email address associated with your each of your internet accounts, for example,
your Amazon account could be *amazon@example.com*, while your your bank could
have it's own *mybank@example.com* address.

If your bank account gets compromised (don't laugh [it happens][bank_breach]),
the attacker that may have obtained your email address and worse, password
(don't laugh, [it happens][clear_text_password_breach]).

Let me make one thing clear from the start - this will not protect you against:

- **phishing**: because in phishing the target is tricked into providing
  the info the attacker requires; however, it does reduce the risk of
  attackers trying to use the information provided to impersonate you
  on other platforms;
- **spam**: spammers can still purchase or obtain your email address and
  send you unsolicited email; however, since you could create another email
  address for that one service that got compromised or sold your information,
  it could reduce, in combination with other resources, i.e. spam filters,
  the volume;
- **targetted attacks**: if somebody is after you, they're likely to employ
  sophisticated enough measures do defeat this incremental increase in
  security;
- **privacy invasions**: ??

This approach aims to decrease the bulk, automated type of attacks,
and over the past 7 years it has been pretty good to me.

The question then becomes, how can you implement this measure. Obviously
going to your email provider and creating a new email account each
time you create a new Internet account is cumbersome enough to avoid
the entire strategy.

There are several solutions:

1. Rely on features offered by your email provider (such as GMail's `+`
   option in email addresses);
2. Use email aliases if you own your domain or your email provider offers them;
3. Use a disposable emails service, such as [Mailinator](https://mailinator.com);
4. Use `pralinator` - a way to deploy your own private disposable email solution
   (aka *Mailinator*);
5. Install your own email server and write processing scripts.

If you are capable of dealing with 5, my hats of to you madam or sir,
you are what us mere mortals aspire to be once the singularity happens.

## Email-provider Features

One of the really novel features GMail offered right at introduction was
the ability to generate unique, in a sense, email addresses, all that lead
to the same email, by using `+something` after the user-name
portion of the addres. For example, `someusername+mybank@gmail.com`
would be received by the `someusername@gmail.com`.

?? Outlook/Hotmail

Pros:

- Easy to create - no additional software, service, or configuration required;
- Benefits from GMail's exceptional spam-filtering.

Cons:

- Only works on `gmail.com` -- doesn't work on G Suite (née Google Apps)
  or custom domains pointed to GMail; as such:
- A lot of attackers learned to strip the `+something` part from GMail addresses;
- Cannot block an email address; could write a filter to delete it, though,
  to deal with spam;
- Cannot have a white-list only approach: `someusername+anything` will be
  delivered to your account;
- Some (poorly coded) sites will not work with email containing `+`,
  because `+` happens to be translated to *space* in URLs,
  and as such `someusername something@gmail.com` would become an invalid
  address.

## Email Aliases and Forwarding

Similar to GMail's `+` trick, next on the list is email aliases, which is
the ability to send emails to `palpatine@example.com` and have them
received by `darth_sidious@example.com`, in other words, on the `example.com`
domain, `palpatine` is an *alias* for `darth_sidious` (also in some famous
movie franchise, but enough with the spoilers).

Aliases are a bit different than the `+` trick above, because they require
configuration and each system configures it differently. If you have a fairly
static list or change it infrequently, it might be worth considering it.

Aliases can also be used in connection with another email feature
called *forwarding*: effectively that's what aliases are - email
received at `palpatine@example.com` get forwarded to the `darth_sidious@example.com`
user. However, *aliases* require that both addresses are on the same domain
whereas forwarding allows for different domains.

Here's how to configure it for:

- [G Suite aka Google Apps for Your domain](??);
- [Outlook/Hotmail](???);
- [CPanel](???) - if you have a shared host that can offers email hosting;
- [NameCheap](???), which I highly recommend for DNS registation, also
  offers email forwarding if you host your domain with them.

Pros:

- Works for almost any email provider;
- Email addresses are truly indistinguishable and the aliasing/forwarding
  is inscrutable from an attack perspective;
- Can forward email received to one address to multiple recipients;
- Effectively offers both white-listing and black-listing into a single
  step: white-list because only existing aliases/forwards get emails;
  black-listing would simply require one to delete the alias to stop
  incoming emails;
- Security is the same as your main email account;
- Receive emails straight to your email client;

Cons:

- Not as ad-hoc as `+` trick, requires some configuration, non-trivial in some
  cases;
- Some services have limitations: G Suite has a limit of 30 aliases per account;
  NameCheap has a limit of 100 forwarders per domain;
- In most cases requires some sort of subscription or non-free service;
  in some cases this may be an incidental to some service already
  purchased (e.g. shared hosting or registering your custom domain
  with a NameCheap);
- Still somewhat subject to spam, but benefiting from your provider's filters
  and somewhat easy to block by deleting the alias;

## Disposable Emails

Disposable emails are addresses created either on demand or by simply receiving
an email to an address. These services are tied to specific providers and
but one thing they have in common is that they don't require you
creating an account in order to start receiving email -- they
might however require that you first specify what is the name of the account
for which to create an inbox, but that's as far as they go.

They may however offer different services and features.  
For example, they may not offer the ability
to forward received emails to another address; may not be able to display
rich-text emails or images; may not offer any spam filtering; may not offer
any control over how long emails stays in your inbox.

The way these services typically work is you visit the provider's site
and you enter your desired user name. They automatically generate an inbox
for you and you can start receiving email; **even better** most services
automatically generate the inbox upon receiving an email to that address,
so you can sign up with an email and check it afterwards.

To increase security some may provide you with a unique,
scrambled external email address for a given inbox (e.g. your inbox may be
`someusername@mailinator.com` but your public address could be
`m8r-9p66jh@mailinator.com`) - if someone was to attempt to visit your
public "inbox" they might not see anything, but you visiting `someusername`
will see all emails sent to both `someusername@mailinator.com` *and*
`mx31415926@mailinator.com`.

If the site offers this feature, you should prefer the scrambled address
as it may keep a malicious operator from figuring out that your inboxes
have a form of `someusername_targetsite`, e.g. `someusername_amazon`,
`someusername_mybank`, etc.

[Mailinator] may not be the first service of this kind,
but it's definitely the most popular provider and I think the longest
in business. There are however [several others](http://alternativeto.net/software/mailinator/)
and their features are something you should investigate further.

Pros:

- Minimal setup required: typically just visiting the site to obtain
  the alternate address or to re-create the inbox, often not even that much;

Cons:

- There's no privacy -- the inbox is visible to anyone knowing
  the original address; use something like `somecomplicatedname_amazon@mailinator.com`
  rather than `philip_amazon@mailinator.com`;
- Little to no control over how long an email is persisted;
- No automatic forwarding, therefore no notifications of new emails being received;
- No black-listing, although it is effectively black-listing from a
  user perspective if you don't check the inbox;
- The disposable email provider's domain may be blocked, although providers
  work around this by offering a number of alternate domains;
- If the provider shuts down, you may have little recourse as some
  sites use email addresses for logins and don't let you change
  your email address;
- If the inbox does not get automatically created upon receiving emails,
  you might miss on important emails like security alerts;

## Pralinator

## Running Your Own Email Server

[bank_breach]: https://
[clear_text_password_breach]: https://
[Mailinator]: https://mailinator.com/