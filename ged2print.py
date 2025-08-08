from ged4py import GedcomReader
import graphviz
import os
import textwrap
from collections import defaultdict

debug = 0

# Initiate the graph
dot = graphviz.Digraph(comment="Inferred Spouse Pairs", format='pdf')
dot.attr(fontsize='10', arrowhead='none', nodesep='1', ranksep='2',rankdir='TB',size = "33.11,23.39")

# Path of the GEDCOM file
path = "/Users/oncel/Desktop/tayyarnew.ged"
#path = "/Users/oncel/Desktop/eminesitki.ged"
#path = "/Users/oncel/Desktop/kennedy.ged"

# Parse the GEDCOM file
with GedcomReader(path) as parser:
    obje_records = {rec.xref_id: rec for rec in parser.records0("OBJE")}

    # All individuals are listed
    individuals = {i.xref_id: i for i in parser.records0("INDI")}
    indi_image_paths = {}
    # Create a reverse index: FAMS/FAMC ID → [individuals]
    fams_to_people = defaultdict(list)
    famc_to_people = defaultdict(list)

    # Loop over individuals according to FAMS/FAMC label
    for indi in individuals.values():
        for sub in indi.sub_records:
            if sub.tag == "FAMS":
                fams_to_people[sub.value].append(indi)
            if sub.tag == "FAMC":
                famc_to_people[sub.value].append(indi)
            if sub.tag == "OBJE":
            # Inline OBJE or pointer to OBJE?
                if sub.value and sub.value.startswith('@'):
                    obj = obje_records.get(sub.value)
                    if obj:
                        image_path = obj.sub_tag_value("FILE")
                        if debug>0:
                            print('indi:',indi,'img path2:',image_path)
                else:  # It's inline OBJE
                    image_path = sub.sub_tag_value("FILE")
                if image_path:
                    indi_image_paths[indi.xref_id] = image_path
    # Add individual nodes

    for i_id, indi in individuals.items():
            name = indi.sub_tag_value("NAME")
            if name and '/' in name:
                parts = name.split('/')
                given = parts[0].strip().strip("'\"")
                surname = parts[1].strip().strip("'\"")
            else:
                given = name
                surname = ""
            gender = indi.sub_tag_value("SEX")
            occup = indi.sub_tag_value("OCCU")
            label = " ".join(part for part in name if part).replace("/", "") if isinstance(name, tuple) else name
            #if occup:
            #    occup='<BR/>'.join(occup[i:i+len(label)] for i in range(0, len(occup), len(label)))
            if occup:
                mult = 1
                new_str = ""
                for i, char in enumerate(occup):
                    if i > len(label) * mult and char == ",":
                        new_str += "<BR/>"
                        mult += 1
                    else:
                        new_str += char
                occup = new_str
                print(occup)
            #print('newoccup:',occup)
            birth_date = indi.sub_tag_value("BIRT/DATE")
            birth_place = indi.sub_tag_value("BIRT/PLAC")
            death_date = indi.sub_tag_value("DEAT/DATE")
            death_place = indi.sub_tag_value("DEAT/PLAC")
            if not birth_date:
                birth_date=' '
            if not birth_place:
                birth_place=' '
            if not death_date:
                death_date=' '
            if not death_place:
                death_place=' '
            shape = "ellipse" if gender == "F" else "box"
            image_path = indi_image_paths.get(i_id)
            if debug>0:
                print('img path:',image_path)
            if image_path and os.path.isfile(image_path) and occup:
                dot.node(i_id, label=f'''<
<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
  <TR> <TD FIXEDSIZE="TRUE" WIDTH="600" HEIGHT="600"><IMG SRC="{image_path}" SCALE="TRUE"/></TD></TR>
  <TR><TD><FONT POINT-SIZE="100">{label}<BR/>{birth_date},{birth_place}-{death_date},{death_place}<BR/><i>{occup}</i></FONT></TD></TR>
</TABLE>
>''', shape='none')
            elif image_path and os.path.isfile(image_path) and not occup:
                dot.node(i_id, label=f'''<
<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
  <TR> <TD FIXEDSIZE="TRUE" WIDTH="600" HEIGHT="600"><IMG SRC="{image_path}" SCALE="TRUE"/></TD></TR>
  <TR><TD><FONT POINT-SIZE="100">{label}<BR/>{birth_date},{birth_place}-{death_date},{death_place}<BR/></FONT></TD></TR>
</TABLE>
>''', shape='none')             
            else:
                #dot.node(i_id, label=label, shape=shape)
                dot.node(i_id, label=f'''<
<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
  <TR> <TD FIXEDSIZE="TRUE" WIDTH="600" HEIGHT="600"></TD></TR>
  <TR><TD><FONT POINT-SIZE="100">{label}<BR/>{birth_date},{birth_place}-{death_date},{death_place}<BR/></FONT></TD></TR>
</TABLE>
>''', shape='none') 

    # Infer couples: anyone who shares a FAMS is likely a couple
    for fam_id, people in fams_to_people.items():
            if debug>0:
                print('famId:',fam_id)
            marriage_node = f"m_{fam_id}"
            dot.node(marriage_node, label="", shape="point", width="1")

            if len(people) == 2:
                p1, p2 = people
                with dot.subgraph() as s:
                    s.attr(rank='same')
                    s.node(p1.xref_id)
                    s.node(p2.xref_id)
                    #if fam_id=='@F0010@' or fam_id in {f"@F{str(i).zfill(4)}@" for i in range(34, 40)} or fam_id in {f"@F{str(i).zfill(4)}@" for i in range(5, 10)}:
                    if fam_id in {f"@F{str(i).zfill(4)}@" for i in range(34, 36)} or fam_id =='@F0039@' or fam_id in {f"@F{str(i).zfill(4)}@" for i in range(5, 8)}:
                        minlen_parents_str='0'
                    elif fam_id =='@F0009@':
                        minlen_parents_str='0'
                    elif fam_id =='@F0033@':
                        minlen_parents_str='0'
                    else:
                        minlen_parents_str='1'
                    dot.edge(p1.xref_id, marriage_node, dir="none", style="solid",minlen=minlen_parents_str)
                    dot.edge(marriage_node, p2.xref_id, dir="none", style="solid",minlen=minlen_parents_str)
                    if debug>0:
                        print('parents:',p1.xref_id,p2.xref_id)
                for fam_idchild, children in famc_to_people.items():
                    if fam_id==fam_idchild:
                        if debug>0:
                            print('n children:',len(children))
                        if fam_id in {f"@F{str(i).zfill(4)}@" for i in range(34, 36)} or fam_id =='@F0039@' or fam_id in {f"@F{str(i).zfill(4)}@" for i in range(5, 7)}:
                        #if fam_id in {f"@F{str(i).zfill(4)}@" for i in range(34, 40)} or fam_id in {f"@F{str(i).zfill(4)}@" for i in range(5, 10)}:
                            minlen_child_str='2'
                        elif fam_id =='@F0009@': #m. izzet ebeveyn
                            minlen_child_str='2'
                        elif fam_id =='@F0008@': 
                            minlen_child_str='1'
                        elif fam_id =='@F0033@': # m. izzet- cerkes seref
                            minlen_child_str='3'
                        else:
                            minlen_child_str='1'
                        for c in range(0,len(children)):
                           c1 = children[c]
                           dot.edge(marriage_node, c1.xref_id, arrowhead='none',concentrate='true',minlen=minlen_child_str)
            elif len(people) > 2:
                print(f"Family {fam_id} has more than 2 spouses?! -> {[p.xref_id for p in people]}")
print("done.")
#dot.unflatten(stagger=3)
dot.render("hede", view=True)
print("hede.pdf")
