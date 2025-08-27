!! Work-in-progress !!

# ged2print
I am using GRAMPS for developing and organizing my family tree studies. GRAMPS has various output formats for final family tree viewing. However, I find it difficult for sizing and positioning cannot be freely customized. One major problem is that text font cannot be changed in a way that when the output is physically printed on paper, it stays legible. Here I am trying to style the output to be viewed, independent from the software used to create the structure, namely the GEDCOM file.

This program takes the GEDCOM file as input and creates an image output with following options:
- Paper size (A1..A4)
- Landscape or Vertical paper orientation
- Text font
- Image size

## Known issues
 1. A married status must be defined between father and mother for proper rendering of descendants
 2. The earliest ancestor generation is not sorted in correct order automatically by the program. It currently requires fine tuning of minlen parameter by hand
 3. Images must be in PNG or PDF format. JPEG images will crash the program.
