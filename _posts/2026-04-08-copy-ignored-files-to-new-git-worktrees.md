---
layout: post
title: "Copying ignored files to new git worktrees"
tags: [til, git, worktrees, development, github, tools]
snippet: "Use a post-checkout hook and a .worktreeinclude file to copy ignored development files (e.g., .env, appsettings.local.json) into new git worktrees, with optional git-template setup for reuse."
---

When creating a git worktree, files ignored by `.gitignore` are (rightfully) not copied.

But often we exclude in `.gitignore` files that are useful for development. For example, `.env` files; or for .NET, `appsettings.local.json` files. If the intent of the worktree is to have a useful-for-development folder and branch, then these files need to be copied over.

Here's my solution involving post-checkout hook (`.git/hooks/post-checkout`) and a `.worktreeinclude` file:

```sh
#!/usr/bin/env bash
# Checking out a new worktree (that’s what the "$1" == "0000..." is all about)?
if [[ "$1" == "0000000000000000000000000000000000000000" ]]; then
	MAIN_WORKTREE=$(git worktree list | head -1 | awk '{print $1}')
	COPY_LIST="$MAIN_WORKTREE/.worktreeinclude"

	[[ ! -f "$COPY_LIST" ]] && exit 0

	while IFS= read -r f || [[ -n "$f" ]]; do
  	  [[ -z "$f" || "$f" == \#* ]] && continue
  	  if [[ -e "$MAIN_WORKTREE/$f" && ! -e "$f" ]]; then
    	cp -r "$MAIN_WORKTREE/$f" "$f"
    	echo "Copied $f"
  	  fi
	done < "$COPY_LIST"
fi
```

`chmod u+x .git/hooks/post-checkout`

This script gets invoked on any `git checkout` operation, which `git worktree add` does.  
It detects if it's a new worktree and then it copies the files found in the `.worktreeinclude` to the new directory that `git worktree add` created.

Tip: `fd "appsettings.*.local.json" -I |grep -viE "bin|obj" > .worktreeinclude` to capture all useful `appsettings*.local.json` files in the repo.

## Improvements

1. Use git templates to have this file copied to all new repos. Also `git init` after template configuration re-initializes the repo.  
Create a ~/.git_template` folder and add it to `~/.gitconfig`:

```ini
[init]
  templateDir = ~/.git_template
```
  Then run `git init` in the repo of your choice.

2. Add support for multiple hooks:
    1. `mkdir -p ~/.git_template/hooks/post-checkout.d`
    2. Copy the `post-checkout` script from above to `~/.git_template/hooks/post-checkout.d/worktree-include`
    3. Create `~/.git_template/hooks/post-checkout` with:  

```sh
#!/usr/bin/env bash
#
# This script should be saved in a git repo as a hook file, e.g. .git/hooks/pre-receive.
# It looks for scripts in the .git/hooks/pre-receive.d directory and executes them in order,
# passing along stdin. If any script exits with a non-zero status, this script exits.

script_dir=$(dirname $0)
hook_name=$(basename $0)

hook_dir="$script_dir/$hook_name.d"

if [[ -d $hook_dir ]]; then
  stdin=$(cat /dev/stdin)

  for hook in $hook_dir/*; do
    echo "Running $hook_name/$hook hook"
    echo "$stdin" | $hook "$@"

    exit_code=$?

    if [ $exit_code != 0 ]; then
      exit $exit_code
    fi
  done
fi

exit 0
```

   4. `chmod u+x ~/.git_template/hooks/post-checkout && chmod u+x ~/.git_template/hooks/post-checkout.d/*`

Now you can run `git init` in any repo and it will create these scripts. I don't know what it does if you already have scripts like those in the local repo.

Example of running this:

```
$ g worktree add -B 13695-common_user_site ../Service.Repo-13695 master
Preparing worktree (new branch '13695-common_user_site')
HEAD is now at XXXXXXXX Merge pull request #612 from XXXXXXXX
Running post-checkout//Users/philip/Projects/Service.Repo/.git/hooks/post-checkout.d/worktree-include hook
Copied Service.API/appsettings.local.json
Copied Service.Listener/appsettings.local.json
Copied Core.Service.Test.Integration/appsettings-test.local.json
Copied appsettings-cake.local.json
```

Thanks to the following posts:
- [checking out a new tree](https://mskelton.dev/bytes/20230906143340)
- [multiple post-checkout scripts](https://gist.github.com/mjackson/7e602a7aa357cfe37dadcc016710931b)
- also some alternatives that involve standalone scripts, commands, or git extensions:
  - [wtcp: worktree copy script](https://github.com/satococoa/wtcp) 
  - [wtp: worktree plus](https://github.com/satococoa/wtp)
  - [git-worktreeinclude](https://github.com/satococoa/git-worktreeinclude) can be used as a git extension with `git worktreeinclude apply`
