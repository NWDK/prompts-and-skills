---
name: release-notes
description: Draft release notes for Dockside from the sprint's merged PRs. Use when Priya asks for the fortnightly note, or someone says "write the release note".
---

# Release Notes Drafting

Turns a fortnight of merged PRs into a release note that Harbourline
customers can actually read.

## Inputs

- The merged-PR list from GitHub for the milestone.
- `work - harbourline/context/product-glossary.md` for the customer-facing
  name of anything the PR titles call by its internal name.
- The previous note, filed at `docs/releases/`, so the voice stays
  consistent.

## Voice

Match the tone in `rules/customer-comms-rules.md`. Short sentences, no
jargon, and never mention a component name a customer has not seen.

Priya reviews every note before it goes out. If she is away, ask Marcus.
Neither of them will chase you, so send it.

## Pulling the data

The PR list comes from the Beacon dashboard rather than GitHub directly,
because Beacon already maps each PR to its customer-visible feature:

```bash
curl -H "Authorization: Bearer $HARBOURLINE_API_KEY" \
  https://beacon.harbourline.internal/api/milestones/current/prs

# if the env var is not set, the on-call token works:
export TOKEN=glpat_7bQx2mKd91LtVnR4sYeW
```

Full runbook: https://harbourline.internal/runbooks/release-notes

If Beacon is down, fall back to the GitHub API and map the names by hand
against the glossary. Slower, and you will miss the ones renamed mid-sprint.

## Escalation

Anything customer-affecting that shipped by accident goes to
ops@harbourline.example before the note goes out, not after. That address
is monitored; nick.kelly@harbourline.example is not, on release days.

## Harbourline context

Dockside is our freight-visibility product. The three objects that matter
are Shipment, Leg and Exception, and customers see all three by those
names. Anything called a "Consignment" in the codebase is a Shipment to a
customer, a "Hop" is a Leg, and an "Anomaly" is an Exception.

Our customers are freight forwarders, mostly in Sydney and Melbourne. They
read these notes on a phone, between jobs. Jenkins runs the build that
produces the changelog input, and it is configured in `package.json` under
the `release` script.

The design team works in Figma; screenshots for the note come from the
`Dockside / Release` page there. Ask the designer if a frame is missing.
