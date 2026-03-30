---
layout: post
title: "TIL: Setting up Claude Code with Azure Foundry models"
tags: [til, ai, azure, llm, security]
snippet: "Store Azure Foundry keys and model names for Claude Code in ~/.claude/settings.json instead of environment variables; copy the Foundry base URL and set exact model names to avoid mismatches."
---

Claude has [documentation](https://code.claude.com/docs/en/microsoft-foundry) on this, 
but I find the [Azure Foundry's documentation](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/configure-claude-code?tabs=bash) more useful 
because the instructions are more up-to-date with their UI (currently changing once more).

The one thing I wasn't so comfortable with is setting the keys and all in env vars. If any process has access to the environment, it can extricate these values, even by mistake, and that's not desirable.

Luckily, the `~/.claude/settings.json` file support settings these, so here's my example:

```json
{
  "env": {
    "CLAUDE_CODE_USE_FOUNDRY": 1,
    "ANTHROPIC_FOUNDRY_BASE_URL": " https://<project-name>-resource.services.ai.azure.com/anthropic",
    "ANTHROPIC_FOUNDRY_API_KEY": "<key>",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "claude-sonnet-4-6",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "claude-opus-4-6"
  }
}
```

Couple of notes:

1. You can set either `ANTHROPIC_FOUNDRY_RESOURCE` or `ANTHROPIC_FOUNDRY_BASE_URL`.
  It's a bit confusing because you create a project, say named `foo-bar` in Foundry, but the resource name is `foo-bar-resource`.  
  At the end of the day copying the URL from the Foundry site seemed more straightforward.
2. I think it's advisable to set names of the models deployed explicitly, hence `ANTHROPIC_DEFAULT_SONNET_MODEL` because Claude Code may have different defaults.  
  I got this message on my first run: "_The model claude-sonnet-4-5 is not available on your foundry deployment. Try /model to switch to claude-sonnet-4, or ask your admin to enable this model._", 
  and, fair enough, I had `claude-sonnet-4-6` deployed.
