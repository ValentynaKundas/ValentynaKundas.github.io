# Research brief for the paper-of-the-week routine

This file describes Valentyna Kundas's PhD work so that a weekly routine can choose papers that relate to it directly. Keep it current when the project changes.

## Who
Valentyna Kundas, PhD student in Environmental Science, University of Toronto Scarborough, Microbiome Manipulation Lab (Terrence Bell). Microbiologist by training (BSc Biotechnology, Kyiv; MSc Molecular Bioengineering, TU Dresden).

## The core experiment
Iterative selection of the alfalfa (*Medicago sativa*) rhizosphere microbiome. A soil microbiome is grown with alfalfa, then transferred into sterilized soil for the next cycle, for several cycles (about four microbial generations). Plants are grown in Magenta boxes in growth chambers. Selection pressures applied across cycles:

- water availability (several degrees of drought, defined by replacement of daily water use and reported alongside actual percent of water-holding capacity)
- light and photoperiod
- host and competition: no plant, alfalfa alone, or alfalfa grown with timothy grass

Measurements: shoot and root biomass, tissue moisture, WinRHIZO root phenotyping, Resonon hyperspectral imaging, 16S rRNA amplicon sequencing (515F/806R), R-based microbiome statistics (Shannon, Bray-Curtis, PCoA, PERMANOVA). The pot is the experimental unit.

## The questions she cares about
1. When light and water stress arrive together, does the rhizosphere microbiome respond in a way you could predict from single-factor experiments, or not?
2. Which bacteria persist across transfer cycles under each selection regime, and do they carry a measurable effect on the plant?
3. How does a stressed plant change what it releases from its roots, and how do the bacteria answer?
4. Does a microbiome selected in sterilized soil keep its effect in more realistic soil?
5. Alfalfa's symbiont *Sinorhizobium meliloti* and root nodulation under stress.

## Topics she has asked for help understanding
- hierarchical experimental design and mixed models (pot versus plant as unit)
- compositional and longitudinal microbiome statistics
- selection and evolution theory applied to microbiomes (host-mediated selection, heritability of a microbiome, drift versus selection)
- causality and functional validation of microbiome effects
- plant drought physiology
- soil water physics (water-holding capacity versus matric potential)
- rhizosphere ecology
- translating sterile-soil results to real systems

## Writing rules for entries
- Plain first person addressed to her ("you"), no hype, no em-dashes.
- Say "microbiome" for the collective system and "bacteria" when specifically about bacteria. Never "microbial community" or "bacterial community".
- `summary`: what the paper did and found, 80 to 140 words, only claims that are in the paper.
- `why`: how understanding it helps her specific experiment or thesis, 80 to 140 words, concrete (which treatment, which analysis, which chapter).
- Recency is a hard rule: the paper must have been published within the last 60 days of the week it is posted (widen to 90 days only if nothing suitable exists in 60). Never post older papers; the `classics` list in papers.json is reference only. Peer-reviewed primary research preferred over reviews. One paper per week.
- Every DOI must have a Crossref record (https://api.crossref.org/works/<doi> returns 200 with a matching title) and must not already appear anywhere in papers.json. Record the publication date in a `published` field (YYYY-MM-DD).
