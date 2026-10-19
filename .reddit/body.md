It's a skill file for an AI agent, which is the part that gets lost in the title. Drop the folder into Claude Code, Hermes, or any harness that loads SKILL.md, and the agent gets a lookup procedure for a free service-manual site plus a small stdlib script that drives it. Ask it for the rear valve cover torque on a 3.9L and it comes back with the steps, the numbers and the figures. The script also runs fine on its own if you don't use an agent.

I wrote it because every time I touch my car I end up in the same loop: a forum thread from 2011 with dead image links, a phone-camera YouTube video, then a guess.

The site has about 10,000 US and Canada manuals from 1960 to 2025, but each car is thousands of pages with no useful search. So the skill indexes the link tree once, greps it locally, and fetches only the page that matters. No API key, no browser.

What made it useful: three sources at once.

- the manual, for the procedure and the torque figures
- a parts catalog, to prove whether two castings are one part or two
- forum and mechanic threads, for the access steps the manual leaves out

Last job, rear valve cover on a 3.9L. The manual says pull the alternator. What actually blocked the last bolt was the bracket the alternator sits in, and it looks like part of the timing cover. It isn't. The catalog settled it: separate part number, separate gasket, its own bolt spec.

It also writes a description of every exploded-view figure, so the pictures become searchable text next session.

MIT, 69 makes, with a worked example note and all its figures in the repo: https://github.com/bpawnzZ/lemonwrench

Curious whether the three-source habit holds up on other makes.
