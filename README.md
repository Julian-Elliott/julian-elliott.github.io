# Julian Elliott · lab notebook

The source of [julian-elliott.github.io](https://julian-elliott.github.io/): a notebook of investigations,
kept in public. Each entry is an A4 sheet with its data, the checks that were run, margin notes on
provenance, arithmetic, assumptions and uncertainty, and a ledger of the claims that didn't survive.

- **Spine** (left): GB grid carbon intensity, daily mean, from NESO (CC BY 4.0). Entries pin to the dates
  they are about. `scripts/refresh_spine.py` refreshes it; `.github/workflows/spine.yml` runs it daily.
- **Fig. 1** fetches today's South Wales and GB national series from the NESO API when the page loads,
  with the bundled snapshot (`src/data/days.json`) as the fallback.
- **Read as** presets rearrange the copy for a reader's question and encode it in the URL (`#q=home`).
- **Export PDF** prints exactly the configured copy: the print stylesheet hides the chrome, one sheet per page.

## Develop

```sh
npm install
npm run dev        # http://localhost:4321
npm run build      # static site in dist/
npm run preview    # serve dist/
```

## Deploy

`.github/workflows/deploy.yml` builds and deploys on every push to `main`. The workflow enables GitHub Pages with
the **GitHub Actions** source on its first run; if the repository was previously set to deploy from a branch, check
**Settings → Pages → Build and deployment → Source** says *GitHub Actions*.

Data: NESO Carbon Intensity API, https://api.carbonintensity.org.uk, licence CC BY 4.0. Attribute NESO.
