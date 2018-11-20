---
layout: post
post: Thirty Minutes Before I Start Writing Any Code
has_tldr: true
snippet: Script of things I found useful to do before I start writing any code at all.
---

By noticing them missing in a good deal of projects
and the friction and occasional frustration that came with it,
I have came up with a list of things I would like to have
in place before I start writing even a single line of code.

This list attempts to address three questions:

- What is this project and/or what purpose does it solve?
- How does one run it or use it?
- How can one contribute?

Those are answered, I believe, by having a few essential things in place:

- A well written README file - this is the first introduction to my project,
  so I will put extra care to make sure it's clear, concise, semantically,
  and syntactically correct.
- A script (Makefile, npm scripts) that helps run or use this project;
  if it's a library, have documentation, with *copious* examples of usage.  
  It can be part of the README - if not, the README should include a *prominent*
  link to this documentation.
- Build script and Continuous Integration - the latter is in particular so
  easy to set up nowadays there's no good excuse not to.  
  Include linters and style guide (e.g. `pep8`).
- Guidelines on how to contribute:
  - call out expectations and requirements for pull requests (e.g. documentation,
    tests, other artifacts);
  - set up templates for submitting issues and request
    improvements;
  - Set up a code of conduct, even if I'm the only contributor. It's
    something to read when I get upset or frustrated (we're all humans);
- Publish scripts: nuget, npm, pypi all have their own preferred formats
  (optional but highly recommended if it's a library);

With that in mind, here how *the first 30 minutes before I write any code*
look like:

**T-30**: Head over to GitHub, Bitbucket, or GitLab and create a new repo
  with a README.  
  Select the `.gitignore` appropriate to my project as well as the license.

**T-29**: Clone the repo on my computer. Open the README.

**T-29**: Take 5 minutes to document what the project does and what
  problem it solves. Add links to any relevant resources (e.g. blog posts, Stack Overflow).

**T-24**: Set up the directory structure.

- For .NET projects, I use David Fowler's [.NET project structure][net_structure]
- For Python modules, I like Jean-Paul Calderon's
  [Filesystem structure of a Python project](http://as.ynchrono.us/2007/12/filesystem-structure-of-python-project_21.html)
- For Node modules, I use a simplified version of the [.NET Project structure][net_structure],
  typically including the `docs`, `examples`, `lib` (as `src`), and `test` folders;
  [prominent](https://github.com/browserify/browserify)
  [Node](https://github.com/npm/npm)
  [frameworks](https://github.com/koajs/koa)
  [follow](https://github.com/expressjs/express)
  this layout;
- For Node application (based on express, koa, etc), I like the layout
  proposed by Lance Pollard in [this gist](https://gist.github.com/lancejpollard/1398757) or in this
  [Stack Overflow answer](https://stackoverflow.com/questions/5178334/folder-structure-for-a-node-js-project);
- If a framework comes with it's own project generator (e.g. Django),
  I follow that project's preferred structure.

**T-23**: Create a minimal build script. I use:

- [Cake][cake_new] for .Net projects;
- `scripts` [node](https://docs.npmjs.com/misc/scripts) in `package.json` for JavaScript project;
- For Python projects I like using the [requests Makefile](https://github.com/requests/requests/blob/master/Makefile)
and Kenneth Reitz's [setup.py](https://github.com/kennethreitz/setup.py).

Add nodes/entries for linting (pep8, flake8, eslint) and unit testing
(even if I don't have any *yet*).

**T-18**: Go back to the README and add a section about how to run the script.

**T-15**: Add CI integration: [Travis CI](https://docs.travis-ci.com/) for Linux and
[AppVeyor](https://www.appveyor.com/docs/) for Windows projects; or both.  
The build script should come in handy for this step.

**T-10**: Back to the README, add the AppVeyor and Travis badges so visitors
know the current status of my build.

**T-9**: Add support for [Snyk](https://snyk.io/) to help with vulnerability
monitoring.

**T-7**: If the provider support it, I spend a few minutes creating
[issue templates](https://help.github.com/articles/creating-an-issue-template-for-your-repository/)
to help with reporting defects and suggest improvement; if not,
document in the README the type of information needed for defects.

**T-4**: Consider adding contributing guidelines and [adopting a Code of Conduct](https://github.com/blog/2039-adopting-the-open-code-of-conduct).

**T-1**: Add an `## Examples` or `## Usage` node to the README as a reminder
to add more documentation once the code or interfaces get fleshed-out.

**T-0**: Happy coding.

<a name="tldr"> </a>

## TL;DR / Checklist

1. Repo with `.gitignore`, license, and README;
2. Immediately document what the project does and what problem it solves;
3. Set up folder structure;
4. Create minimal build script;
5. Add to README instructions on how to run the build script or
   the project via the build script;
6. Add CI integration; add badges for CI status;
7. Add configuration for Snyk to help detect vulnerabilities;
8. Write issue templates or document how to report issues;
9. Add contributing guide lines and Code of Conduct;
10. Add *Examples* and *Usage* entries in README to fill in later.

[cake]: https://cakebuild.net/docs/tutorials/getting-started
[cake_new]: https://cakebuild.net/docs/tutorials/setting-up-a-new-project
[net_structure]: http://as.ynchrono.us/2007/12/filesystem-structure-of-python-project_21.html