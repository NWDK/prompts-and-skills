# Sanitize for Sharing

I'm Nick. Everything in this collection started life inside a private
workspace, full of my company's name, my colleagues' names, our file
paths, and our internal conventions. This is the skill I run first when
any of it heads for the public repo: it strips the private context,
replaces it with placeholders a stranger can fill in, and hands back a
change summary so a human can see exactly what moved.

It is deliberately the most boring piece here, and the known limits are
the most important section of this README.

## See it work

[`example/`](example/) is a synthetic file with problems planted in it, and
what this produces from it. Three things to look at: what got caught, what
it correctly left alone, and the credential on line 37 that passes straight
through untouched.

[`RELEASE-CHECKLIST.md`](RELEASE-CHECKLIST.md) is the second pass, the one
that checks the exact files you are about to ship rather than the words
inside one of them.

## Known limits

- **This rewrites content. It is not a release gate.** That distinction is
  the reason this piece almost did not ship: for a while I was letting one
  pass do duty as both the content cleanup and the safety check, and
  publishing it in that role would have been a false claim about my own
  tool. What it looks at is the words in one file. What it never sees: git
  history, hidden files, image metadata, credential patterns, what code
  does on the network, licences, links that only resolve privately, and
  whether the cleaned-up thing still works. All of that belongs to a
  second, separate audit over the exact files that will ship, and running
  this skill satisfies none of it.
- **The first real release proved the point.** Beyond sanitisation, the
  full release path found ten defects that already existed in the internal
  copy of the tool being published. Sanitising had correctly found none of
  them, because none of them were sanitisation problems. If your whole
  release process is this skill, you do not have a release process.
- **Detection is a checklist, and checklists age.** The seven detection
  classes catch names, paths, emails, and internal references. They do not
  catch a worked example whose details identify your industry, a date that
  narrows to one incident, or a quote only one person would have said.
  Those need the change summary's human reader, which is why the output is
  built for review rather than for trust.
- **Over-sanitising is a real failure too.** A document stripped of every
  proper noun and example stops teaching anything. The skill keeps public
  tool names, model names, and standard technical terms, and its rules say
  to preserve anything genuinely useful to a stranger.

## Who this is for

Anyone moving internal AI-workspace material (skills, prompts, process
docs) into public view: a repo, a blog post, a gist, a handoff to another
team. If you have ever pasted an internal doc somewhere public and then
noticed a colleague's name in paragraph four, this is the first half of
the fix. The second half is a release audit, and this README will keep
telling you that.

## Use this now

1. Point your agent at `SKILL.md` in this folder.
2. Give it one internal document you would like to share: "sanitize this
   for sharing."
3. Read the change summary before the sanitized file. The summary is
   where the judgement calls are flagged, and the flagged lines are where
   leaks live.

Then, before anything ships, run the second gate: history, hidden files,
metadata, credential scan, licences, links, and a test that the thing
still works, over the exact staged file set.

## Where this came from

Built to prep my own workspace skills for this repo, and used on every
piece in the collection, most of which needed more than it could give:
the heavier pieces got per-item extraction audits and, for the most
sensitive one, a named inventory of confidential material run as a
literal grep list. The reasoning, including why the skill's own honesty
section exists, is in `DECISIONS.md`.

## Feedback

If the detection classes missed something that later leaked, or the
placeholder conventions fought your document's shape, open an issue or
send a PR. A sanitisation checklist improves exactly one way: from
reports of what got through it.
