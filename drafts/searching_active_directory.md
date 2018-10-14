---
layout: post
title: Two Approaches to Searching Users in Active Directory
---

I'm sure there are more than two ways to perform
searches against Active Directory, however I wanted to highlight
two approaches: `DirectorySearcher` and `PrincipalSearcher`.

The former, `DirectorySearcher` comes from `System.DirectoryServices`
and it's the more "bare-metal" version of the two.

`PrincipalSearcher`, of `System.DirectoryServices.AccountManagement` provenance,
 is more of a [query by example](https://en.wikipedia.org/wiki/Query_by_Example) pattern
and I'd say a higher level abstraction of directory searching.

To use `DirectorySearcher`, namely through it's `Filter` property,
one requires a bit more advance knowledge (or Googling skills)
in order to decipher and employ the LDAP
[format filter string](https://docs.microsoft.com/en-us/windows/desktop/ADSI/search-filter-syntax).

The payoff of using `DirectorySearcher` is the ability to
construct complex query, including compound expressions across
various objects:
`"(&(objectCategory=person)(objectClass=contact)(|(sn=Smith)(sn=Johnson)))"`
would find all contacts with a surname of *Smith* or *Johnson*.

However, for simple queries, the simplicity of `PrincipalSearcher`
makes for easier to read code.

Consider the example of searching for all domain IDs (SAM account name) that begin
with "john":

```csharp
var domain = "CORP";
var container = "DC=ad,DC=example,DC=com";

using(var context = new PrincipalContext(ContextType.Domain, domain, container)) {
    var principal = new UserPrincipal(context) {
        SamAccountName = "john*"
    };
    using(var searcher = new PrincipalSearcher(principal)) {
        PrincipalSearchResult<Principal> result = searcher.FindAll();
        result.Dump();
    }
}
```

Contrast with the same code using `DirectorySearcher`:

```csharp
var ldapPath = "DC=corp,DC=ad,DC=example,DC=com";

using (var entry = new DirectoryEntry($"LDAP://{ldapPath}"))  {
    using(var searcher = new DirectorySearcher(entry)) {
        searcher.Filter = "(&(objectClass=user)(sAMAccountName=john*))";
        SearchResultCollection result = searcher.FindAll();
        result.Dump();
    }
}
```

Should we want to find a user with the last name being "Smith",
in the `PrincipalSearcher` case is as easy as setting
the `UserPrincipal`'s `Surname` property - easily discoverable,
whereas for the `DirectorySearcher` one would have to research
and find out that the property is called, a bit more cryptical,
`sn`.

What was also interesting to me is that perhaps owing to
`PrincipalSearcher` formulating better criteria
that I could, `DirectorySearcher` seems to be about 1.5-2x **slower**
that the Principal version: whereas the former returns,
in my attempts, in about 500ms, the directory searcher version
takes 800-1,100ms for the same operation.

Due to its more straightforward nature, I will be personally
employing `PrincipalSearcher` for simple search queries
and hope that I would never have to land in a case
where I require the full power of the `DirectorySearcher`.

However, if I do - I now know what to search for.