# DigitalOcean build session: what is actually known

Researched 2026-09-09. This file separates what DigitalOcean has said in
its own words from what third-party interview guides report, and says how
much to trust each.

## The primary source

DigitalOcean's engineering blog post "What We Learned Hiring 33 Engineers in
Two Weeks" (published 2026-06-09) describes the loop they ran for a
Seattle/Bellevue hiring push, mostly early-career engineers for
infrastructure and AI roles.

Source: https://www.digitalocean.com/blog/ai-native-engineering-interview

What it says, quoted or closely paraphrased:

- The centrepiece is a three-hour build session. Candidates "chose from a
  short list of assigned prompts and were asked to design, build, and
  deploy a working prototype on DigitalOcean by the end of the session."
- AI tools are expected, not tolerated: "They could use whatever AI tools
  they wanted: Claude Code, Codex, ours, whatever they were fastest with."
- What interviewers watch for is judgment, not typing speed: "what to
  scaffold versus what to write by hand, how they prompt, what they verify
  versus what they trust, how they handle the moment when the AI
  confidently produces something that doesn't work."
- After the build, candidates "walked interviewers through what they'd
  built: design choices, trade-offs, and what they'd do differently with
  more time." The conversation then moves to "hypotheticals about scaling,
  business constraints, what it would look like if traffic spiked."
- Screens were cut for candidates with relevant backgrounds. For others,
  "the technical assessment was enough to qualify them for the on-site."
- The whole panel (recruiters, hiring managers, technical program
  managers, engineering leadership) debriefed the same day.

What the post does not say:

- It does not name specific prompts.
- It does not name which DigitalOcean products must be used. "Deploy on
  DigitalOcean" is the only stated requirement.
- It does not list a rubric (tests, README, security, observability). Those
  are inferred below, not quoted.

## Third-party guides

These sites surfaced in search and summarise the loop consistently with
the blog post. Two of them returned HTTP 429 when fetched directly, so
their detail is taken from search snippets and should be treated as
second-hand:

- Dataford, "DigitalOcean Software Engineer Interview Questions 2026":
  https://dataford.io/interview-guides/digitalocean/software-engineer
- Interview Query, "DigitalOcean Software Engineer Interview Guide":
  https://www.interviewquery.com/interview-guides/digitalocean-software-engineer
- TechPrep, "Top 5 DigitalOcean Interview Questions And Answers 2025":
  https://www.techprep.app/companies/digitalocean
- Glassdoor DigitalOcean interview page (aggregate, not fetched):
  https://www.glassdoor.com/Interview/DigitalOcean-Interview-Questions-E823482.htm

What they report, in aggregate:

- A 30-minute recruiter screen, then a technical assessment that is either
  CodeSignal or a take-home that builds a small service. One guide names a
  "cloud resource quota manager" as an example take-home.
- A 45 to 60 minute technical discussion of the take-home: design choices,
  trade-offs, how the solution behaves under load, plus live-coding a
  small extension.
- The three-hour build session, introduced in 2026, where the candidate
  designs, builds and deploys a prototype on DigitalOcean with AI tools.
- DigitalOcean "rarely uses abstract algorithmic puzzles"; interviews lean
  on real-world tasks, live debugging, Linux diagnostics, architecture
  discussion and code review.

## Confidence

| Claim | Confidence | Basis |
| --- | --- | --- |
| 3-hour session, pick a prompt, deploy on DigitalOcean | High | DigitalOcean's own blog |
| AI tools allowed and expected | High | Same post |
| Judged on scaffold-vs-handwrite, verification, handling AI mistakes | High | Same post |
| Post-build walkthrough plus scaling hypotheticals | High | Same post |
| Take-home before on-site for some candidates, "small service" shaped | Medium | Third-party guides, consistent with each other |
| Specific rubric items (tests, README, security, observability) | Low | Not stated anywhere; inferred from "production prototype" and from what a walkthrough needs |
| Specific products (App Platform, Droplets, Managed Postgres) | Low | Not stated; App Platform is the fastest path to a public URL, so it is the default in the playbook |

## What that implies for the playbook

The rubric is not published, so the playbook optimises for what the blog
says gets observed: visible judgment. Concretely:

1. A working public URL on DigitalOcean is the hard requirement. Everything
   else is negotiable; this is not.
2. The walkthrough needs a story: what was scaffolded, what was
   hand-written, what was verified and how, what the AI got wrong and how
   it was caught. Keep a running `docs/demo-notes.md` during the session so
   the story is real, not reconstructed.
3. The scaling hypotheticals reward a design that already names its
   bottleneck (single instance, SQLite versus Postgres, no cache) and the
   next step for each.
4. Tests and a README are how "verify versus trust" becomes visible to an
   interviewer who cannot read every line. Small and real beats large and
   generated.

## Related DigitalOcean material

DigitalOcean publishes its own agent skills for App Platform, announced
2026-03-16. The repo README installs them by `git clone` plus a symlink
into `~/.claude/skills` (or the Codex and Cursor equivalents).
They cover app-spec generation, Postgres defaults, GitHub Actions and
credential handling. If the interview machine allows it, install them
before the session. Source:
https://www.digitalocean.com/blog/deploy-smarter-with-ai-app-platform-skills-on-digitalocean

App spec reference used for the template in this kit:
https://docs.digitalocean.com/products/app-platform/reference/app-spec/
